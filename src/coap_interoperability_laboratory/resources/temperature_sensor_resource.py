from typing import Any

import aiocoap
import aiocoap.resource as resource
from kpn_senml import SenmlPack, SenmlRecord, SenmlUnits

from coap_interoperability_laboratory.model.temperature_sensor import TemperatureSensor
from coap_interoperability_laboratory.resources.resource_utils import (SENML_JSON_CONTENT_FORMAT,
                                                                       build_not_acceptable_response,
                                                                       build_senml_json_response,
                                                                       is_senml_json_accepted)


class TemperatureSensorResource(resource.Resource):
    """ CoAP resource of the Temperature Sensor (/temperature), described with the CoRE Link Format attributes.
    It supports only the GET method and returns the current temperature as SenML JSON """

    # Resource Type of the Temperature Sensor (application specific semantic type)
    RESOURCE_TYPE = "it.unimore.device.sensor.temperature"

    def __init__(self, device_name: str) -> None:
        """ Constructor for TemperatureSensorResource class
        :param device_name: Name of the device, used as SenML Base Name
        """
        super().__init__()

        # CoRE Link Format attributes used by aiocoap to build the /.well-known/core description
        self.if_ = "core.s"                             # Interface Description: CoRE Interfaces - Sensor
        self.ct = int(SENML_JSON_CONTENT_FORMAT)        # Content-Format of the representation (110)
        self.rt = self.RESOURCE_TYPE                    # Resource Type
        self.title = "Temperature Sensor"               # Human readable title

        self.device_name = device_name
        self.temperature_sensor = TemperatureSensor()

    def get_link_description(self) -> dict[str, Any]:
        """ Extend the default link description (ct, rt, if) with the title attribute """
        link = super().get_link_description()
        link["title"] = self.title
        return link

    def build_senml_json_payload(self) -> str:
        """ Build the SenML JSON payload with the current temperature value """
        pack = SenmlPack(self.device_name)
        pack.add(SenmlRecord("temperature",
                             unit=SenmlUnits.SENML_UNIT_DEGREES_CELSIUS,
                             value=self.temperature_sensor.value,
                             time=self.temperature_sensor.timestamp / 1000))   # SenML time is in seconds
        return pack.to_json()

    async def render_get(self, request: aiocoap.Message) -> aiocoap.Message:
        """ GET /temperature: measure a new value and return it as SenML JSON (2.05 Content) """

        print("TemperatureSensorResource -> GET Request Received ...")

        if not is_senml_json_accepted(request):
            print(f"TemperatureSensorResource -> Unsupported Accept: {request.opt.accept} -> 4.06 Not Acceptable")
            return build_not_acceptable_response()

        self.temperature_sensor.measure_temperature()
        print(f"TemperatureSensorResource -> Updated Temperature Value: {self.temperature_sensor.value:.2f}")

        return build_senml_json_response(self.build_senml_json_payload())
