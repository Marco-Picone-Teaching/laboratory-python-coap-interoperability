# For this laboratory we rely on the aiocoap library (0.4.x) - https://github.com/chrysn/aiocoap
# and on the LinkHeader library to parse the CoRE Link Format (RFC 6690).
# Dependencies are managed with uv. From the project root run: uv run coffee-discovery-client [query]
#
# Test client for the CoAP Resource Discovery: it sends a GET request to /.well-known/core and prints the path
# and the attributes of each resource of the Coffee Machine. An optional query passed as argument filters the
# resources, e.g.: uv run coffee-discovery-client if=core.a

from coap_interoperability_laboratory.config.config_manager import ConfigManager
import aiocoap
import asyncio
import link_header
import logging
import sys

# Configuration variables
WELL_KNOWN_CORE_PATH = "/.well-known/core"


async def discover_resources(config_manager: ConfigManager, query: str | None) -> None:

    context = await aiocoap.Context.create_client_context()

    target_uri = config_manager.build_server_uri(WELL_KNOWN_CORE_PATH)
    if query is not None:
        target_uri = f"{target_uri}?{query}"

    request = aiocoap.Message(code=aiocoap.GET, uri=target_uri)
    print(f"Sending Discovery request to: {target_uri}")

    try:
        response = await context.request(request).response
    except Exception as e:
        print(f"Failed to fetch resource: {e}")
    else:
        response_string = response.payload.decode("utf-8")
        print(f"Response Code: {response.code}")
        print(f"CoRE Link Format: {response_string}\n")

        # Each link has an href (the path of the resource) and a list of (name, value) attribute pairs
        for link in link_header.parse(response_string).links:
            print(f"Resource: {link.href}")
            for attribute_name, attribute_value in link.attr_pairs:
                print(f"\t{attribute_name}: {attribute_value}")
    finally:
        await context.shutdown()


def main() -> None:

    logging.basicConfig(level=logging.INFO)

    # Load the shared configuration (target server host and port) from the config.yaml file
    config_manager = ConfigManager()

    query = sys.argv[1] if len(sys.argv) > 1 else None

    asyncio.run(discover_resources(config_manager, query))


if __name__ == "__main__":
    main()
