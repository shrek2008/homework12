import json
from collections import UserDict
from datetime import datetime, timedelta

class AddressBook(UserDict):
    def add_person(self, record):
        self.data[record.name.value] = record

    def __str__(self) -> str:
        result = {}
        for name, record in self.data.items():
            phones = ", ".join(str(phone) for phone in record.phones)
            result[name] = phones
        return str(result)

    def __iter__(self):
        return AddressBookIterator(self.data)

    def save_to_disk(self, file_path):
        with open(file_path, 'w') as file:
            json.dump(self.data, file, default=self._json_serializer)

    def load_from_disk(self, file_path):
        with open(file_path, 'r') as file:
            self.data = json.load(file, object_hook=self._json_deserializer)

    def _json_serializer(self, obj):
        if isinstance(obj, Field):
            return obj.value
        return obj.__dict__

    def _json_deserializer(self, json_dict):
        data = json_dict.copy()
        name = Name(data.pop('name'))
        phones = [Phone(phone) for phone in data.pop('phones')]
        birthday = None
        if 'birthday' in data:
            birthday = Birthday(data.pop('birthday'))
        record = Record(name, *phones, birthday=birthday)
        record.__dict__.update(data)
        return record

class AddressBookIterator:
    def __init__(self, data):
        self._data = data
        self._keys = list(self._data.keys())
        self._index = 0
        self._chunk_size = 2

    def __iter__(self):
        return self

    def __next__(self):
        if self._index >= len(self._keys):
            raise StopIteration
        chunk = self._keys[self._index : self._index + self._chunk_size]
        self._index += self._chunk_size
        return {name: self._data[name] for name in chunk}

class Record:
    def __init__(self, name, phone=None, birthday=None):
        self.name = name
        self.phones = []
        self.birthday = birthday
        if phone:
            self.phones.append(phone)

    def add_phone(self, phone):
        self.phones.append(phone)

    def change_phone(self, new_phone):
        self.phone = new_phone

    def days_to_birthday(self):
        if self.birthday:
            today = datetime.now().date()
            birthday_date = datetime.strptime(self.birthday.value, "%Y-%m-%d").date()
            next_birthday = datetime(today.year, birthday_date.month, birthday_date.day).date()
            if next_birthday < today:
                next_birthday = datetime(today.year + 1, birthday_date.month, birthday_date.day).date()
            days_left = (next_birthday - today).days
            return days_left
        return None
    
    def __str__(self) -> str:
        return f"{self.name}: {', '.join(str(phone) for phone in self.phones)}" 


class Field:
    def __init__(self, value):
        if not isinstance(value, str):
            raise ValueError("Value must be a string")
        self.value = value

    def __str__(self) -> str:
        return self.value

class Name(Field):
    pass

class Phone(Field):
    def __init__(self, value):
        if not value.startswith("+") or not value[1:].isdigit():
            raise ValueError("Invalid phone number format")
        super().__init__(value)

class Birthday(Field):
    def __init__(self, value):
        try:
            datetime.strptime(value, "%Y-%m-%d")
        except ValueError:
            raise ValueError("Invalid birthday format")
        super().__init__(value)

if __name__ == "__main__":
    ad = AddressBook()
    name = Name("Boris")
    phone = Phone("+380681486757")
    birthday = Birthday("1990-08-15")  # Example: replace with the correct birthday format
    person1 = Record(name, phone, birthday)

    person2 = Record(Name("Audi"), Phone("+30712"))

    ad.add_person(person1)
    ad.add_person(person2)

    for chunk in ad:
        print(chunk)
