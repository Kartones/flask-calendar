#!/usr/bin/python
# -*- coding: utf-8 -*-


#############for test only################
import config
from authentication import Authentication

aut = Authentication(data_folder=config.USERS_DATA_FOLDER, password_salt=config.PASSWORD_SALT)
aut.addUser('gati','gati')


for i in aut.contents:
    print(aut.contents[i])
    

