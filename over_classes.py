class JSONDataAdapter:  # work only with profiles
    @staticmethod
    def to_json(obj):
        dict_for_json = {}
        try:
            for key, value in obj.items():
                dict_for_json[key] = value.__dict__
        except AttributeError:
            print("Incorrect structure!")
        else:
            return dict_for_json

    @staticmethod
    def from_json(obj):
        dict_normalized = {}
        try:
            for key, value in obj.items():
                name = value["name"]
                surname = value["surname"]
                sex = value["sex"]
                age = value["age"]
                desc = value["desc"]
                photo = value["photo"]
                dict_normalized[int(key)] = Profile(
                    name, surname, sex, age, desc, photo
                )
        except AttributeError:
            print("Incorrect structure!")
        else:
            return dict_normalized


class Metrics:
    def __init__(self, dictionary, key, default=None):
        self.dict = dictionary
        self.key = key
        self.default = default

    @property
    def val(self):
        return self.dict.get(self.key, self.default)

    @val.setter
    def val(self, value):
        self.dict[self.key] = value


class Profile:
    def __init__(self, name="", surname="", sex=None, age=-1, description="", photo=""):
        self.name = name
        self.surname = surname
        self.sex = sex
        self.age = age
        self.desc = description
        self.photo = photo

    def __str__(self) -> str:
        short_text = lambda x: x if len(x) < 30 else x[:10] + "..." + x[-10:]
        return (
            f"Имя: {self.name}\n"
            f"Фамилия: {self.surname}\n"
            f"пол: {self.sex}\n"
            f"возраст: {self.age}\n"
            f"описание: {short_text(self.desc)}\n"
            f"фото: {self.photo[:10]+'...'+self.photo[-10:]}\n"
        )

    def __dict__(self) -> dict:
        return {
            "name": self.name,
            "surname": self.surname,
            "sex": self.sex,
            "age": self.age,
            "desc": self.desc,
            "photo": self.photo,
        }
