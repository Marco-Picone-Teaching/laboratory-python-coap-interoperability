import json
from typing import Any


class MakeCoffeeRequest:
    """ MakeCoffeeRequest class represents the JSON payload sent with a PUT request to the Coffee Actuator
    to make a coffee of a specific type, e.g., {"type": "long"} """

    # Supported coffee types
    COFFEE_TYPE_SHORT = "short"
    COFFEE_TYPE_MEDIUM = "medium"
    COFFEE_TYPE_LONG = "long"

    def __init__(self, coffee_type: str) -> None:
        """ Constructor for MakeCoffeeRequest class
        :param coffee_type: The requested type of coffee (short, medium or long)
        """
        self.coffee_type = coffee_type

    def to_json(self) -> str:
        """ Convert the object to a JSON string. The attribute coffee_type is serialized as the JSON field "type"
        (the name "type" is avoided in Python code since it is a builtin function) """
        return json.dumps({"type": self.coffee_type})

    @classmethod
    def from_json(cls, json_string: str) -> "MakeCoffeeRequest":
        """ Create a MakeCoffeeRequest from its JSON representation
        :param json_string: The JSON string received in the payload of the request
        :raises ValueError: If the string is not a valid JSON object with a string "type" field
        """
        data: Any = json.loads(json_string)  # json.JSONDecodeError is a subclass of ValueError

        if not isinstance(data, dict) or not isinstance(data.get("type"), str):
            raise ValueError("The request must be a JSON object with a string 'type' field")

        return cls(data["type"])
