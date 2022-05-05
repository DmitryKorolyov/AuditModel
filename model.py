import time, threading, requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from pprint import pprint

import subprocess
from subprocess import Popen, PIPE

class ModelAbstract():
    def modelUpdate(self):
        raise NotImplementedError()

    def register_observer(self, observer):
        self.observer = observer
        print('Регистрация ' + str(self.observer))






class MetaModel(ModelAbstract):
    def __init__(self):
        print('Создание модели')

        self.session = requests.Session()
        login_url = 'http://172.16.131.128/dvwa/login.php'
        login_data = {"username": "admin","password": "password", "Login": "submit"}
        recieve = self.session.post(login_url, data = login_data)
        print(recieve.content)
        self.scanner1model = Scanner1Model(self)
        self.scanner2model = Scanner1Model(self)
        self.xss_scanner_model = XSS_Scanner_Model(self)
        self.sql_scanner_model = SQL_Scanner_Model(self)

    def close(self):
        self.scanner1model.work_event.set()






        

