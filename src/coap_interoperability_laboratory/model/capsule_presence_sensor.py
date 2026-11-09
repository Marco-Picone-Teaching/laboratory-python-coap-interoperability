import json
import random
import time


class CapsulePresenceSensor:
    """ This class represents the sensor that detects if a capsule has been correctly loaded into the Coffee Machine.
    The presence of the capsule is emulated with a random boolean value at each check """

    def __init__(self) -> None:
        """ Constructor for CapsulePresenceSensor class """

        # Unix timestamp (milliseconds) of the last check
        self.timestamp: int = 0

        # True if the capsule is loaded into the Coffee Machine
        self.value: bool = False

        # Perform the first check
        self.check_capsule_presence()

    def check_capsule_presence(self) -> None:
        """ Method to emulate a new check of the capsule presence """
        self.value = random.choice([True, False])
        self.timestamp = int(time.time() * 1000)

    def to_json(self) -> str:
        """ Convert the object to a JSON string """
        return json.dumps(self, default=lambda o: o.__dict__)
