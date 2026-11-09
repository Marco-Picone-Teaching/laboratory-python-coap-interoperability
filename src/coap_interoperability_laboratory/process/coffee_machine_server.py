# For this laboratory we rely on the aiocoap library (0.4.x) - https://github.com/chrysn/aiocoap
# Dependencies are managed with uv. From the project root run: uv run coffee-machine-server
#
# CoAP Server of the Coffee Machine exposing three resources described with the CoRE Link Format (RFC 6690)
# and returning SenML JSON representations (RFC 8428):
# - /temperature: Temperature Sensor (GET)          rt="it.unimore.device.sensor.temperature"       if="core.s"
# - /capsule: Capsule Presence Sensor (GET)         rt="it.unimore.device.sensor.capsule_presence"  if="core.s"
# - /coffee: Coffee Actuator (GET, POST, PUT, obs)  rt="it.unimore.device.actuator.coffee"          if="core.a"
# The standard /.well-known/core resource lists all the resources (CoAP Resource Discovery).

from coap_interoperability_laboratory.config.config_manager import ConfigManager
from coap_interoperability_laboratory.resources.capsule_presence_sensor_resource import CapsulePresenceSensorResource
from coap_interoperability_laboratory.resources.coffee_actuator_resource import CoffeeActuatorResource
from coap_interoperability_laboratory.resources.temperature_sensor_resource import TemperatureSensorResource
import aiocoap
import aiocoap.resource as resource
import asyncio
import logging


async def run_server(config_manager: ConfigManager) -> None:

    # Name of the device, used as SenML Base Name by all the resources
    device_name = config_manager.device_name

    # Resource tree creation
    root = resource.Site()

    # Add the /.well-known/core resource to support the standard CoAP Resource Discovery.
    # The WKCResource builds the CoRE Link Format description of all the resources of the Site
    # (get_resources_as_linkheader) using the attributes exposed by each resource (ct, rt, if, obs, title).
    # impl_info=None removes the link to the aiocoap web site that is added by default
    root.add_resource([".well-known", "core"], resource.WKCResource(root.get_resources_as_linkheader, impl_info=None))
    root.add_resource(["temperature"], TemperatureSensorResource(device_name))
    root.add_resource(["capsule"], CapsulePresenceSensorResource(device_name))
    root.add_resource(["coffee"], CoffeeActuatorResource(device_name))

    # Create the server context bound to the configured address and UDP port
    await aiocoap.Context.create_server_context(root, bind=(config_manager.server_bind_host, config_manager.server_port))

    print(f"Coffee Machine '{device_name}' listening on coap://{config_manager.server_bind_host}:{config_manager.server_port}")
    print(f"Resource Discovery: coap://{config_manager.server_bind_host}:{config_manager.server_port}/.well-known/core")

    # Keep the server running forever: the requests are served by the event loop (CTRL+C to stop the process)
    await asyncio.get_running_loop().create_future()


def main() -> None:

    # Log level of aiocoap: INFO shows the main events, DEBUG also shows every received and sent message
    logging.basicConfig(level=logging.INFO)
    # logging.getLogger("coap-server").setLevel(logging.DEBUG)

    # Load the shared configuration (bind address, port and device name) from the config.yaml file
    config_manager = ConfigManager()

    try:
        asyncio.run(run_server(config_manager))
    except KeyboardInterrupt:
        print("Coffee Machine CoAP Server stopped")


if __name__ == "__main__":
    main()
