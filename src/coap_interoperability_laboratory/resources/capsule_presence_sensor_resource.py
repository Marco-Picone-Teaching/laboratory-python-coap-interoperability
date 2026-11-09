from typing import Any

import aiocoap
import aiocoap.resource as resource
from kpn_senml import SenmlPack, SenmlRecord

from coap_interoperability_laboratory.model.capsule_presence_sensor import CapsulePresenceSensor
from coap_interoperability_laboratory.resources.resource_utils import (SENML_JSON_CONTENT_FORMAT,
                                                                       build_not_acceptable_response,
                                                                       build_senml_json_response,
                                                                       is_senml_json_accepted)


class CapsulePresenceSensorResource(resource.Resource):
    """ CoAP resource of the Capsule Presence Sensor (/capsule), described with the CoRE Link Format attributes.
    It supports only the GET method and returns the presence of the capsule as SenML JSON (boolean value: vb) """

    # Resource Type of the Capsule Presence Sensor (application specific semantic type)
    RESOURCE_TYPE = "it.unimore.device.sensor.capsule_presence"

    def __init__(self, device_name: str) -> None:
        """ Constructor for CapsulePresenceSensorResource class
        :param device_name: Name of the device, used as SenML Base Name
        """
        super().__init__()

        # CoRE Link Format attributes used by aiocoap to build the /.well-known/core description
        self.if_ = "core.s"                             # Interface Description: CoRE Interfaces - Sensor
        self.ct = int(SENML_JSON_CONTENT_FORMAT)        # Content-Format of the representation (110)
        self.rt = self.RESOURCE_TYPE                    # Resource Type
        self.title = "Capsule Presence Sensor"          # Human readable title

        self.device_name = device_name
        self.sensor = CapsulePresenceSensor()

    def get_link_description(self) -> dict[str, Any]:
        """ Extend the default link description (ct, rt, if) with the title attribute """
        link = super().get_link_description()
        link["title"] = self.title
        return link

    def build_senml_json_payload(self) -> str:
        """ Build the SenML JSON payload with the presence of the capsule """
        pack = SenmlPack(self.device_name)
        pack.add(SenmlRecord("capsule",
                             value=self.sensor.value,
                             time=self.sensor.timestamp / 1000))   # SenML time is in seconds
        return pack.to_json()

    async def render_get(self, request: aiocoap.Message) -> aiocoap.Message:
        """ GET /capsule: check the presence of the capsule and return it as SenML JSON (2.05 Content) """

        print("CapsulePresenceSensorResource -> GET Request Received ...")

        if not is_senml_json_accepted(request):
            print(f"CapsulePresenceSensorResource -> Unsupported Accept: {request.opt.accept} -> 4.06 Not Acceptable")
            return build_not_acceptable_response()

        self.sensor.check_capsule_presence()
        print(f"CapsulePresenceSensorResource -> Capsule Presence: {self.sensor.value}")

        return build_senml_json_response(self.build_senml_json_payload())
