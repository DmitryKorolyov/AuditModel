from config import *
import requests
from threading import Lock, Thread



class SingletonMeta(type):
    """
    Это потокобезопасная реализация класса Singleton.
    """

    _instances = {}

    _lock: Lock = Lock()
    """
    У нас теперь есть объект-блокировка для синхронизации потоков во время
    первого доступа к Одиночке.
    """

    def __call__(cls, *args, **kwargs):
        """
        Данная реализация не учитывает возможное изменение передаваемых
        аргументов в `__init__`.
        """
        # Теперь представьте, что программа была только-только запущена.
        # Объекта-одиночки ещё никто не создавал, поэтому несколько потоков
        # вполне могли одновременно пройти через предыдущее условие и достигнуть
        # блокировки. Самый быстрый поток поставит блокировку и двинется внутрь
        # секции, пока другие будут здесь его ожидать.
        with cls._lock:
            # Первый поток достигает этого условия и проходит внутрь, создавая
            # объект-одиночку. Как только этот поток покинет секцию и освободит
            # блокировку, следующий поток может снова установить блокировку и
            # зайти внутрь. Однако теперь экземпляр одиночки уже будет создан и
            # поток не сможет пройти через это условие, а значит новый объект не
            # будет создан.
            if cls not in cls._instances:
                instance = super().__call__(*args, **kwargs)
                cls._instances[cls] = instance
        return cls._instances[cls]












class Requestor(metaclass = SingletonMeta):
    def __init__(self):
        self.session = requests.Session()
        self.login(LOGIN_URL, USERNAME, PASSWORD)
        print('[!] Это сообщение должно выводиться всего один раз')
    
    def login(self, url, username, password):
        self.login_url = url
        self.login_username = username
        self.login_password = password
        login_data = {"username": username,"password": password, "Login": "submit"}
        self.session.post(url, data = login_data)


    def authorise(self):
        print('[!] Requestor.authorise Не реализован')

    def get(self, url, params = None):
        self.login(self.login_url, self.login_username, self.login_password)
        if params == None:
            return self.session.get(url)
        else:
            return self.session.get(url, params = params)
            
    def post(self, url, data):
        self.login(self.login_url, self.login_username, self.login_password)
        return self.session.post(url, data = data)