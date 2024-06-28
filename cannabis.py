import csv

reader : csv.DictReader


class Strain():
    name : str
    type : str
    rating : str
    effects : str
    flavor : str
    description : str
    def __str__(self):
        return """
        Skunik ;D :
        Nazwa: {}
        Typ: {}
        Średnia ocena użytkowników: {}
        Efekty: {}
        Smak: {}
        Opis: {}
        """.format(self.name, self.type, self.rating, self.effects, self.flavor, self.description)
    def __repr__(self):
        return """
        Skunik ;D :
        Nazwa: {}
        Typ: {}
        Średnia ocena użytkowników: {}
        Efekty: {}
        Smak: {}
        Opis: {}
        """.format(self.name, self.type, self.rating, self.effects, self.flavor, self.description)
    def __init__(self, name="Not found", type="", rating="", effects="", flavor="", description=""):
        self.name = name
        self.type = type
        self.rating = rating
        self.effects = effects
        self.flavor = flavor
        self.description = description

def get_strain_from_row(row):
    strain = Strain (
                row[0],
                row[1],
                row[2],
                row[3],
                row[4],
                row[5])
    return strain
def get_strain(search_name:str):
    with open("./cannabis.csv") as csv_f:
        reader = csv.reader(csv_f, delimiter=',')
        for row in reader:
            strain = get_strain_from_row(row)
            if strain.name == search_name:
                return strain
        return Strain()

def get_strain_info_str(search_name:str):
    strain = get_strain(search_name)
    # Normal readable code that is fucked by newlines
    # return """
    #     Skunik ;D :
    #     Nazwa: {}
    #     Typ: {}
    #     Średnia ocena użytkowników: {}
    #     Efekty: {}
    #     Smak: {}
    #     Opis: {}
    #     """.format(strain.name, strain.type, strain.rating, strain.effects, strain.flavor, strain.description)
    return "Skunik ;D : \\nNazwa: {} \\nTyp: {} \\nŚrednia ocena użytkowników: {} \\nEfekty: {} \\nSmak: {} \\nOpis: {}".format(strain.name, strain.type, strain.rating, strain.effects, strain.flavor, strain.description)

def search_strain_names_list(search_query:str):
    search_query = search_query.lower()
    list = []
    with open("./cannabis.csv") as csv_f:
        reader = csv.reader(csv_f, delimiter=',')
        for row in reader:
            strain : str = get_strain_from_row(row)
            name = strain.name
            if search_query in name.lower():
                list.append(name)
        return list

chemol = get_strain("Chemdawg")
print("Zioło :D")