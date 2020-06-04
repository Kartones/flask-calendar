import hashlib
import json
import os
import time
from typing import Dict, cast

from cachelib.simple import SimpleCache

cache = SimpleCache()


class Authentication:

    USERS_FILENAME = "users.json"

    def __init__(self, data_folder: str, password_salt: str, failed_login_delay_base: int) -> None:
        self.contents = {}  # type: Dict
        with open(os.path.join(".", data_folder, self.USERS_FILENAME)) as file:
            self.contents = json.load(file)
        self.password_salt = password_salt
        self.failed_login_delay_base = failed_login_delay_base
        self.data_folder = data_folder

    def is_valid(self, username: str, password: str) -> bool:
        if username not in self.contents:
            self._failed_attempt(username)
            return False
        if self._hash_password(password) != self.contents[username]["password"]:
            self._failed_attempt(username)
            return False
        return True

    def user_data(self, username: str) -> Dict:
        return cast(Dict, self.contents[username])

    def add_user(self, username: str, plaintext_password: str, default_calendar: str) -> None:
        if username in self.contents:
            raise ValueError("Username {} already exists".format(username))
        hashed_password = self._hash_password(plaintext_password)
        self.contents[username] = {
            "username": username,
            "password": hashed_password,
            "default_calendar": default_calendar,
            "ics_key": "an_ics_key",
        }
        self._save()

    def delete_user(self, username: str) -> None:
        self.contents.pop(username)
        self._save()

    def _hash_password(self, plaintext_password: str) -> str:
        hash_algoritm = hashlib.new("sha256")
        hash_algoritm.update((plaintext_password + self.password_salt).encode("UTF-8"))
        return hash_algoritm.hexdigest()

    def _save(self) -> None:
        with open(os.path.join(".", self.data_folder, self.USERS_FILENAME), "w") as file:
            json.dump(self.contents, file)

    def _failed_attempt(self, username: str) -> None:
        key = "LF_{}".format(username)
        attempts = cache.get(key)
        if attempts is None:
            attempts = 0
        else:
            attempts = int(attempts) + 1
        wait = self.failed_login_delay_base ** attempts
        cache.set(key, attempts, timeout=7200)  # Keep for 2h
        time.sleep(wait)
