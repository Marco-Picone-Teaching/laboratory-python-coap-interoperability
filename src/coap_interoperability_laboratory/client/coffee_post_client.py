# For this laboratory we rely on the aiocoap library (0.4.x) - https://github.com/chrysn/aiocoap
# Dependencies are managed with uv. From the project root run: uv run coffee-post-client
#
# Test client sending a POST request without payload to the Coffee Actuator (/coffee)
# to make a coffee of the default type (short).

from coap_interoperability_laboratory.config.config_manager import ConfigManager
import aiocoap
import asyncio
import logging

# Configuration variables
coffee_resource_path = "coffee"


async def make_default_coffee(config_manager: ConfigManager) -> None:

    context = await aiocoap.Context.create_client_context()

    target_uri = config_manager.build_server_uri(coffee_resource_path)
    request = aiocoap.Message(code=aiocoap.POST, uri=target_uri)
    print(f"Sending POST request to: {target_uri}")

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

    asyncio.run(make_default_coffee(config_manager))


if __name__ == "__main__":
    main()
