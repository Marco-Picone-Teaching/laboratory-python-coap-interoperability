# For this laboratory we rely on the aiocoap library (0.4.x) - https://github.com/chrysn/aiocoap
# Dependencies are managed with uv. From the project root run: uv run coffee-observe-client
#
# Test client observing the Coffee Actuator (/coffee): it registers as observer (GET with Observe = 0)
# and prints a notification every time a new coffee is made (e.g., with coffee-post-client or coffee-put-client
# in another terminal). Stop the client with CTRL+C.

from coap_interoperability_laboratory.config.config_manager import ConfigManager
import aiocoap
import asyncio
import logging

# Configuration variables
coffee_resource_path = "coffee"


async def observe_coffee(config_manager: ConfigManager) -> None:

    context = await aiocoap.Context.create_client_context()

    # Observe option = 0 -> register as observer
    target_uri = config_manager.build_server_uri(coffee_resource_path)
    request = aiocoap.Message(code=aiocoap.GET, uri=target_uri, observe=0)
    print(f"Observing resource: {target_uri}")

    observation_request = context.request(request)

    try:
        first_response = await observation_request.response
        print(f"Current Coffee Statistics (SenML): {first_response.payload.decode('utf-8')}")

        # The response has no Observe option if the resource is not observable
        if first_response.opt.observe is None:
            print("The resource is not observable: no notifications will be received")
            return

        print("Waiting for new coffees ...")
        async for notification in observation_request.observation:
            print(f"New Coffee ! Observe: {notification.opt.observe} "
                  f"Coffee Statistics (SenML): {notification.payload.decode('utf-8')}")

    except Exception as e:
        print(f"Observation failed: {e}")
    finally:
        await context.shutdown()


def main() -> None:

    logging.basicConfig(level=logging.INFO)

    # Load the shared configuration (target server host and port) from the config.yaml file
    config_manager = ConfigManager()

    try:
        asyncio.run(observe_coffee(config_manager))
    except KeyboardInterrupt:
        print("Observation stopped")


if __name__ == "__main__":
    main()
