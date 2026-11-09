# For this laboratory we rely on the aiocoap library (0.4.x) - https://github.com/chrysn/aiocoap
# Dependencies are managed with uv. From the project root run: uv run coffee-put-client [coffee_type]
#
# Test client sending a PUT request to the Coffee Actuator (/coffee) to make a coffee of a specific type.
# The type can be passed as argument: short, medium (default) or long. Any other value is rejected by the
# server with 4.00 Bad Request.

from coap_interoperability_laboratory.config.config_manager import ConfigManager
from coap_interoperability_laboratory.dto.make_coffee_request import MakeCoffeeRequest
from aiocoap.numbers import ContentFormat
import aiocoap
import asyncio
import logging
import sys

# Configuration variables
coffee_resource_path = "coffee"
default_coffee_type = MakeCoffeeRequest.COFFEE_TYPE_MEDIUM


async def make_custom_coffee(config_manager: ConfigManager, coffee_type: str) -> None:

    context = await aiocoap.Context.create_client_context()

    # Serialize the request with the MakeCoffeeRequest DTO and set the JSON Content-Format
    payload_string = MakeCoffeeRequest(coffee_type).to_json()
    target_uri = config_manager.build_server_uri(coffee_resource_path)
    request = aiocoap.Message(code=aiocoap.PUT,
                              uri=target_uri,
                              content_format=ContentFormat.JSON,
                              payload=payload_string.encode("utf-8"))
    print(f"Sending PUT request to: {target_uri} with payload: {payload_string}")

    try:
        response = await context.request(request).response
    except Exception as e:
        print(f"Failed to send the request: {e}")
    else:
        print(f"Response Code: {response.code}")
        if response.code.is_successful():
            print(f"Coffee Statistics (SenML): {response.payload.decode('utf-8')}")
    finally:
        await context.shutdown()


def main() -> None:

    logging.basicConfig(level=logging.INFO)

    # Load the shared configuration (target server host and port) from the config.yaml file
    config_manager = ConfigManager()

    coffee_type = sys.argv[1] if len(sys.argv) > 1 else default_coffee_type

    asyncio.run(make_custom_coffee(config_manager, coffee_type))


if __name__ == "__main__":
    main()
