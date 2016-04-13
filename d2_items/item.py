class Item:
    localized_name = None
    name = None
    id = None
    # pretty much every needed info from items

    def __init__(self, json):
        self.localized_name = json["localized_name"]
        self.name = json["name"]
        self.id = json["id"]

    def __str__(self):
        return "[ item : " + self.name + " ; id : " + str(self.id) + " ]"
