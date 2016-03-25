class Hero:
    localized_name = None
    name = None
    id = None

    def __init__(self, json):
        self.localized_name = json["localized_name"]
        self.name = json["name"]
        self.id = json["id"]

    def __str__(self):
        return "[ hero : " + self.name + " ; id : " + str(self.id) + " ]"
