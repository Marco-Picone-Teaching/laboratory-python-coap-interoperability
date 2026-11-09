import json


class CoffeeHistory:
    """ This class keeps track of the coffees made by the Coffee Machine: the total number of coffees
    and the number of coffees for each type (short, medium, long) """

    def __init__(self) -> None:
        """ Constructor for CoffeeHistory class. The attribute names are the JSON fields of the representation """
        self.totalCount: int = 0
        self.shortCount: int = 0
        self.mediumCount: int = 0
        self.longCount: int = 0

    def increase_short_coffee(self) -> None:
        """ Register a new short coffee """
        self.totalCount += 1
        self.shortCount += 1

    def increase_medium_coffee(self) -> None:
        """ Register a new medium coffee """
        self.totalCount += 1
        self.mediumCount += 1

    def increase_long_coffee(self) -> None:
        """ Register a new long coffee """
        self.totalCount += 1
        self.longCount += 1

    def to_json(self) -> str:
        """ Convert the object to a JSON string """
        return json.dumps(self, default=lambda o: o.__dict__)
