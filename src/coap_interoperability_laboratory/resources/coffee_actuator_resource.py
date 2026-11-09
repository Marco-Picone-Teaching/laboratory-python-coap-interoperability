import time
from typing import Any

import aiocoap
import aiocoap.resource as resource
from aiocoap.numbers import ContentFormat
from kpn_senml import SenmlPack, SenmlRecord, SenmlUnits

from coap_interoperability_laboratory.dto.make_coffee_request import MakeCoffeeRequest
from coap_interoperability_laboratory.model.coffee_history import CoffeeHistory
from coap_interoperability_laboratory.resources.resource_utils import (SENML_JSON_CONTENT_FORMAT,
                                                                       build_not_acceptable_response,
                                                                       build_senml_json_response,
                                                                       is_senml_json_accepted)


class CoffeeActuatorResource(resource.ObservableResource):
    """ Observable CoAP resource of the Coffee Actuator (/coffee), described with the CoRE Link Format attributes:
    - GET: return the statistics of the coffees made by the machine (SenML JSON)
    - POST (no payload): make a coffee of the default type (short)
    - PUT (JSON payload {"type": "short" | "medium" | "long"}): make a coffee of the requested type
    Every time a new coffee is made the observers receive a notification with the updated statistics """

    # Resource Type of the Coffee Actuator (application specific semantic type)
    RESOURCE_TYPE = "it.unimore.device.actuator.coffee"

    def __init__(self, device_name: str) -> None:
        """ Constructor for CoffeeActuatorResource class
        :param device_name: Name of the device, used as SenML Base Name
        """
        super().__init__()

        # CoRE Link Format attributes used by aiocoap to build the /.well-known/core description
        # (the obs attribute is added automatically by ObservableResource)
        self.if_ = "core.a"                             # Interface Description: CoRE Interfaces - Actuator
        self.ct = int(SENML_JSON_CONTENT_FORMAT)        # Content-Format of the representation (110)
        self.rt = self.RESOURCE_TYPE                    # Resource Type
        self.title = "Coffee Actuator"                  # Human readable title

        self.device_name = device_name
        self.coffee_history = CoffeeHistory()

    def get_link_description(self) -> dict[str, Any]:
        """ Extend the default link description (ct, rt, if, obs) with the title attribute """
        link = super().get_link_description()
        link["title"] = self.title
        return link

    def build_senml_json_payload(self) -> str:
        """ Build the SenML JSON payload with a Record (unit: count) for each counter of the CoffeeHistory """

        pack = SenmlPack(self.device_name)

        # Base Time (bt): all the Records refer to the current time
        pack.base_time = int(time.time())

        pack.add(SenmlRecord("short_coffee", unit=SenmlUnits.SENML_UNIT_COUNTER, value=self.coffee_history.shortCount))
        pack.add(SenmlRecord("medium_coffee", unit=SenmlUnits.SENML_UNIT_COUNTER, value=self.coffee_history.mediumCount))
        pack.add(SenmlRecord("long_coffee", unit=SenmlUnits.SENML_UNIT_COUNTER, value=self.coffee_history.longCount))
        pack.add(SenmlRecord("total_coffee", unit=SenmlUnits.SENML_UNIT_COUNTER, value=self.coffee_history.totalCount))

        return pack.to_json()

    def notify_new_coffee(self) -> aiocoap.Message:
        """ Notify the observers about the new coffee and build the response (2.04 Changed + updated statistics) """

        # aiocoap calls render_get() for each observer and sends the notification
        self.updated_state()
        print(f"CoffeeActuatorResource -> Coffee History: {self.coffee_history.to_json()}")

        return build_senml_json_response(self.build_senml_json_payload(), code=aiocoap.CHANGED)

    async def render_get(self, request: aiocoap.Message) -> aiocoap.Message:
        """ GET /coffee: return the statistics of the coffees (also used for the notifications to the observers) """

        print("CoffeeActuatorResource -> GET Request Received ...")

        if not is_senml_json_accepted(request):
            print(f"CoffeeActuatorResource -> Unsupported Accept: {request.opt.accept} -> 4.06 Not Acceptable")
            return build_not_acceptable_response()

        return build_senml_json_response(self.build_senml_json_payload())

    async def render_post(self, request: aiocoap.Message) -> aiocoap.Message:
        """ POST /coffee (no payload): make a coffee of the default type (short) """

        print("CoffeeActuatorResource -> POST Request Received -> Making a default (short) coffee ...")

        self.coffee_history.increase_short_coffee()
        return self.notify_new_coffee()

    async def render_put(self, request: aiocoap.Message) -> aiocoap.Message:
        """ PUT /coffee (JSON payload): make a coffee of the type specified in the request """

        print(f"CoffeeActuatorResource -> PUT Request Received - Payload: {request.payload!r}")

        # The payload must be JSON: 4.15 Unsupported Content-Format otherwise
        if request.opt.content_format != ContentFormat.JSON:
            print("CoffeeActuatorResource -> Unsupported Content-Format -> 4.15 Unsupported Content-Format")
            return aiocoap.Message(code=aiocoap.UNSUPPORTED_CONTENT_FORMAT)

        # Deserialize the request: 4.00 Bad Request if the payload is not valid
        try:
            make_coffee_request = MakeCoffeeRequest.from_json(request.payload.decode("utf-8"))
        except (UnicodeDecodeError, ValueError) as e:
            print(f"CoffeeActuatorResource -> Invalid Request ({e}) -> 4.00 Bad Request")
            return aiocoap.Message(code=aiocoap.BAD_REQUEST)

        print(f"CoffeeActuatorResource -> Coffee Type Requested: {make_coffee_request.coffee_type}")

        if make_coffee_request.coffee_type == MakeCoffeeRequest.COFFEE_TYPE_SHORT:
            self.coffee_history.increase_short_coffee()
        elif make_coffee_request.coffee_type == MakeCoffeeRequest.COFFEE_TYPE_MEDIUM:
            self.coffee_history.increase_medium_coffee()
        elif make_coffee_request.coffee_type == MakeCoffeeRequest.COFFEE_TYPE_LONG:
            self.coffee_history.increase_long_coffee()
        else:
            print("CoffeeActuatorResource -> Unsupported Coffee Type -> 4.00 Bad Request")
            return aiocoap.Message(code=aiocoap.BAD_REQUEST)

        return self.notify_new_coffee()
