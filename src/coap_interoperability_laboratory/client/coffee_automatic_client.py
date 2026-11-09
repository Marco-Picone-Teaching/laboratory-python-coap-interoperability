# For this laboratory we rely on the aiocoap library (0.4.x) - https://github.com/chrysn/aiocoap
# and on the LinkHeader library to parse the CoRE Link Format (RFC 6690).
# Dependencies are managed with uv. From the project root run: uv run coffee-automatic-client [coffee_type]
#
# Autonomous client of the Coffee Machine. It does not know the paths of the resources in advance and it
# automatically performs the following steps:
# 1. Resource Discovery through /.well-known/core;
# 2. validation of the Resource Types (rt) to check that all the required sensors and actuators are available,
#    storing the path of each resource;
# 3. check of the presence of the capsule (SenML JSON response);
# 4. request of a coffee: POST (default coffee) or PUT if a coffee type is passed as argument (short, medium, long).

from coap_interoperability_laboratory.config.config_manager import ConfigManager
from coap_interoperability_laboratory.dto.make_coffee_request import MakeCoffeeRequest
from aiocoap.numbers import ContentFormat
from typing import Any
import aiocoap
import asyncio
import json
import link_header
import logging
import sys

# Configuration variables: Resource Types required to consider the device a valid Coffee Machine
RT_TEMPERATURE_SENSOR = "it.unimore.device.sensor.temperature"
RT_CAPSULE_SENSOR = "it.unimore.device.sensor.capsule_presence"
RT_COFFEE_ACTUATOR = "it.unimore.device.actuator.coffee"
WELL_KNOWN_CORE_PATH = "/.well-known/core"
SENML_JSON_CONTENT_FORMAT = ContentFormat.by_media_type("application/senml+json")


def find_senml_record(records: list[dict[str, Any]], name: str) -> dict[str, Any] | None:
    """ Return the SenML Record with the given name (n field), None if it is not available """
    for record in records:
        if record.get("n") == name:
            return record
    return None


class CoffeeMachineAutomaticClient:
    """ Autonomous client that discovers the resources of a Coffee Machine and makes a coffee """

    def __init__(self, config_manager: ConfigManager, coffee_type: str | None) -> None:
        """ Constructor for CoffeeMachineAutomaticClient class
        :param config_manager: Configuration with the address of the Coffee Machine
        :param coffee_type: Type of the coffee (PUT request) or None for the default coffee (POST request)
        """
        self.config_manager = config_manager
        self.coffee_type = coffee_type

        # Paths of the resources found with the Resource Discovery (None until they are discovered)
        self.temperature_sensor_path: str | None = None
        self.capsule_sensor_path: str | None = None
        self.coffee_actuator_path: str | None = None

    async def discover_resources(self, context: aiocoap.Context) -> str:
        """ Step 1: GET /.well-known/core and return the CoRE Link Format description of the resources """

        request = aiocoap.Message(code=aiocoap.GET, uri=self.config_manager.build_server_uri(WELL_KNOWN_CORE_PATH))
        response = await context.request(request).response

        if not response.code.is_successful():
            raise RuntimeError(f"Resource Discovery failed with code {response.code}")

        return response.payload.decode("utf-8")

    def is_device_valid(self, core_link_format: str) -> bool:
        """ Step 2: check that all the required Resource Types are available and store the path of each resource """

        for link in link_header.parse(core_link_format).links:
            for attribute_name, attribute_value in link.attr_pairs:
                if attribute_name != "rt":
                    continue
                if attribute_value == RT_TEMPERATURE_SENSOR:
                    self.temperature_sensor_path = link.href
                elif attribute_value == RT_CAPSULE_SENSOR:
                    self.capsule_sensor_path = link.href
                elif attribute_value == RT_COFFEE_ACTUATOR:
                    self.coffee_actuator_path = link.href

        print(f"Temperature Sensor Path: {self.temperature_sensor_path}")
        print(f"Capsule Presence Sensor Path: {self.capsule_sensor_path}")
        print(f"Coffee Actuator Path: {self.coffee_actuator_path}")

        return (self.temperature_sensor_path is not None
                and self.capsule_sensor_path is not None
                and self.coffee_actuator_path is not None)

    async def is_coffee_capsule_available(self, context: aiocoap.Context, capsule_sensor_path: str) -> bool:
        """ Step 3: read the Capsule Presence Sensor and return the boolean value (vb) of the "capsule" Record """

        request = aiocoap.Message(code=aiocoap.GET,
                                  uri=self.config_manager.build_server_uri(capsule_sensor_path),
                                  accept=SENML_JSON_CONTENT_FORMAT)
        response = await context.request(request).response

        if not response.code.is_successful():
            print(f"Error reading the capsule sensor: {response.code}")
            return False

        records = json.loads(response.payload.decode("utf-8"))
        capsule_record = find_senml_record(records, "capsule")

        return capsule_record is not None and capsule_record.get("vb") is True

    async def make_coffee(self, context: aiocoap.Context, coffee_actuator_path: str) -> bool:
        """ Step 4: make a coffee with a POST (default coffee) or a PUT (specific type) request """

        target_uri = self.config_manager.build_server_uri(coffee_actuator_path)

        if self.coffee_type is None:
            request = aiocoap.Message(code=aiocoap.POST, uri=target_uri)
        else:
            request = aiocoap.Message(code=aiocoap.PUT,
                                      uri=target_uri,
                                      content_format=ContentFormat.JSON,
                                      payload=MakeCoffeeRequest(self.coffee_type).to_json().encode("utf-8"))

        response = await context.request(request).response
        print(f"{request.code} {target_uri} -> {response.code}")

        if response.code.is_successful():
            print(f"Coffee Statistics (SenML): {response.payload.decode('utf-8')}")

        return response.code.is_successful()

    async def run(self) -> None:
        """ Run the complete automatic flow """

        context = await aiocoap.Context.create_client_context()

        try:
            core_link_format = await self.discover_resources(context)
            print(f"CoRE Link Format: {core_link_format}")

            if not self.is_device_valid(core_link_format) \
                    or self.capsule_sensor_path is None or self.coffee_actuator_path is None:
                print("Error: Invalid Device Detected !")
                return

            print("Valid Target Device Detected !")

            if not await self.is_coffee_capsule_available(context, self.capsule_sensor_path):
                print("Capsule Not Available ! Stopping ...")
                return

            print("Capsule Available !")

            if await self.make_coffee(context, self.coffee_actuator_path):
                print("Drink your Coffee ! :)")
            else:
                print("Error making Coffee ! Please try later ...")

        except Exception as e:
            print(f"Error communicating with the Coffee Machine: {e}")
        finally:
            await context.shutdown()


def main() -> None:

    logging.basicConfig(level=logging.INFO)

    # Load the shared configuration (target server host and port) from the config.yaml file
    config_manager = ConfigManager()

    # Optional coffee type (short, medium, long): if missing a default coffee is requested with a POST
    coffee_type = sys.argv[1] if len(sys.argv) > 1 else None

    automatic_client = CoffeeMachineAutomaticClient(config_manager, coffee_type)
    asyncio.run(automatic_client.run())


if __name__ == "__main__":
    main()
