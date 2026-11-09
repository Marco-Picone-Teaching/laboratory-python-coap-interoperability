import json
import random
import time


class TemperatureSensor:
    """ This class represents the temperature sensor of the Coffee Machine, used to check that the water
    is correctly heated before making a coffee. It generates random values between 85.0 and 95.0 Celsius degrees """

    def __init__(self) -> None:
        """ Constructor for TemperatureSensor class """

        # Unix timestamp (milliseconds) of the last measurement
        self.timestamp: int = 0

        # Last measured value and its unit
        self.value: float = 0.0
        self.unit: str = "C"

        # Generate the first measurement
        self.measure_temperature()

    def measure_temperature(self) -> None:
        """ Method to emulate a new temperature measurement """
        self.value = random.uniform(85.0, 95.0)
        self.timestamp = int(time.time() * 1000)

    def to_json(self) -> str:
        """ Convert the object to a JSON string (the attributes of the object are the fields of the JSON) """
        return json.dumps(self, default=lambda o: o.__dict__)
