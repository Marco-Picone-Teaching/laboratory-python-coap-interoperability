import aiocoap
from aiocoap.numbers import ContentFormat

# Content-Format of the representations of all the resources: application/senml+json (110)
SENML_JSON_CONTENT_FORMAT = ContentFormat.by_media_type("application/senml+json")


def is_senml_json_accepted(request: aiocoap.Message) -> bool:
    """ Check the Accept option of a GET request: the resources return only SenML JSON, so the request is accepted
    if the option is not present (any format) or if it asks for application/senml+json """
    return request.opt.accept is None or request.opt.accept == SENML_JSON_CONTENT_FORMAT


def build_senml_json_response(payload_string: str, code: aiocoap.numbers.codes.Code = aiocoap.CONTENT) -> aiocoap.Message:
    """ Build a response with a SenML JSON payload (2.05 Content by default) """
    return aiocoap.Message(code=code, content_format=SENML_JSON_CONTENT_FORMAT, payload=payload_string.encode("utf-8"))


def build_not_acceptable_response() -> aiocoap.Message:
    """ Build the response for a GET request asking for an unsupported representation (4.06 Not Acceptable) """
    return aiocoap.Message(code=aiocoap.NOT_ACCEPTABLE)
