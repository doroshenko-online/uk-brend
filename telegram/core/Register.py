from telegram.core.City import City
from telegram.core.User import User
from init import log_message, superadmins


class Registry:
    users = {}
    cities = {}

    @classmethod
    def get_user(cls, chat_id):
        try:
            return cls.users[str(chat_id)]
        except KeyError:
            if str(chat_id) not in superadmins:
                log_message('No load user with chat id ' + str(chat_id), 2)
            return None

    @classmethod
    def get_city(cls, city_id):
        try:
            return cls.cities[int(city_id)]
        except KeyError:
            log_message('No load city with id ' + str(city_id), 2)
            return None

    @classmethod
    def load_user(cls, user: User):
        if user.chat_id not in cls.users:
            cls.users[user.chat_id] = user
            return True
        else:
            log_message('User already exists', 2)
            return False

    @classmethod
    def load_city(cls, city_id, city: City):
        city_id = int(city_id)
        if city_id not in cls.cities:
            cls.cities[city_id] = city
            return True
        else:
            log_message('City already exists', 2)
            return False

    @classmethod
    def unload_user(cls, chat_id):
        try:
            del cls.users[str(chat_id)]
        except KeyError:
            if str(chat_id) not in superadmins:
                log_message('No load user with chat id ' + str(chat_id), 2)
            return False
        else:
            return True

    @classmethod
    def unload_city(cls, city_id):
        try:
            city = cls.cities.pop(int(city_id))
        except KeyError:
            log_message('No load city with id ' + str(city_id), 2)
            return False
        else:
            return city
