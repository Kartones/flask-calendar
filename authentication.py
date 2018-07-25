import hashlib
import json
import os
from typing import cast, Dict


class Authentication:
    
    def __init__(self, data_folder: str, password_salt: str) -> None:
        with open(os.path.join(".", data_folder, "users.json")) as file:
            self.contents = json.load(file)
        self.password_salt = password_salt
        self.data_folder=data_folder

    def is_valid(self, username: str, password: str) -> bool:
        if username not in self.contents.keys():
            return False
        if self._hash_password(password) != self.contents[username]["password"]:
            return False
        return True

    def user_data(self, username: str) -> Dict:
        return cast(Dict, self.contents[username])

    def _hash_password(self, plaintext_password: str) -> str:
        hash_algoritm = hashlib.new('sha256')
        hash_algoritm.update((plaintext_password + self.password_salt).encode("UTF-8"))
        return hash_algoritm.hexdigest()

    def save(self) -> bool:  # save json to file
        try:
            with open(os.path.join(".", self.data_folder, "users.json"),'w') as file:  
                json.dump(self.contents,file)
            return True
        except:
            return False
    
    def addUser( self, name: str, passwd: str) -> bool:  # create and add user to json
        self.name=name
        if self.name in self.contents:
            return False
        self.passwd = self. _hash_password(passwd)         
        self.contents[name]={    'username': self.name, 
                                'password': self.passwd, 
                                'default_calendar': 'sample', 
                                'ics_key': 'an_ics_key'}
        if self.save():
            return True
        else:
            return False
        
    def delUser(self, name: str) -> bool:  # delete user
        self.contents.pop(name)
        if name in  self.contents:
            return False
        aut.save()
        return True
        
        
if __name__ == '__main__':
    import config
    aut = Authentication(data_folder=config.USERS_DATA_FOLDER, password_salt=config.PASSWORD_SALT)
    #aut.addUser('test', 'test')
    print(aut.delUser('test'))
        
