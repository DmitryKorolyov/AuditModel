import threading
import multiprocessing
from typing import Counter
import Requestor, time
import re
from urllib.parse import urljoin
from config import *
from PyQt5 import QtGui, QtWidgets, QtCore

class ModelObserverAbstract():
    def modelUpdate(self):
        raise NotImplementedError()
class ModelAbstract():
    def modelUpdate(self):
        raise NotImplementedError()

    def register_observer(self, observer):
        self.observer = observer
        print('Регистрация ' + str(self.observer))

    def notify_observer(self):
        raise NotImplementedError()



class Crawler_View(QtWidgets.QWidget, ModelObserverAbstract):
    addTextSignal = QtCore.pyqtSignal(str)
    def __init__(self, parent = None, controller = None):
        # ПРИСВОЕНИЕ КОНТРОЛЛЕРА И МОДЕЛИ
        self.controller = controller
        
        # ИНИЦИАЛИЗАЦИЯ ВИДЖЕТОВ
        QtWidgets.QWidget.__init__(self, parent)
        # Первая строка
        self.target_label = QtWidgets.QLabel('URL-адрес начала обхода:')
        self.target_input = QtWidgets.QLineEdit()
        #self.target_input.setFixedWidth(200)
        #self.target_input.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed))
        #self.target_input.setMaximumSize(300, 30)
        self.start_button = QtWidgets.QPushButton('Старт')
        self.start_button.clicked.connect(self.controller.start)
        self.output_label = QtWidgets.QLabel(' ')
        self.hbox1 = QtWidgets.QHBoxLayout()
        self.hbox1.addWidget(self.target_label)
        self.hbox1.addWidget(self.target_input)
        self.hbox1.addWidget(self.start_button)
        #self.hbox1.insertStretch(-1)
        # Вторая строка


        # Вывод
        self.output_area = QtWidgets.QTextEdit()
        self.addTextSignal.connect(self.output_area.append, QtCore.Qt.QueuedConnection)

        #self.output_label = QtWidgets.QLabel(' ')
        #self.output_label.setWordWrap(True)



        #self.output_area.textChanged.connect(lambda: self.output_area.setPlainText(vuln_info), QtCore.Qt.QueuedConnection)
        #self.output_area.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, 700))
        self.output_area.setReadOnly(True)

        self.counter_label = QtWidgets.QLabel()

        self.vbox = QtWidgets.QVBoxLayout()
        self.vbox.addLayout(self.hbox1)
        self.vbox.addWidget(self.output_area)
        self.vbox.addWidget(self.counter_label)
        #self.vbox.insertStretch(-1)
        self.setLayout(self.vbox)
        self.url_counter = 0

    def update(self, message):
        self.addTextSignal.emit(message['data'])
        #self.output_label.setText(self.output_label.text() + '\n' + url)
        self.url_counter = self.url_counter + 1
        self.counter_label.setText('Всего уникальных адресов обнаружено:' + str(self.url_counter))




class Crawler_Controller:
    def __init__(self, meta_controller):
        self.meta_controller = meta_controller
        self.meta_view = self.meta_controller.view
        self.meta_model = self.meta_controller.meta_model

    def start(self):
        input = self.meta_view.get_view('Веб-краулер').target_input.text()
        self.meta_view.get_view('Веб-краулер').output_label.setText('')
        self.meta_model.get_model('Веб-краулер').start(input)

    
        



class Crawler_Model(ModelAbstract):
    def __init__(self, meta_model):
        self.meta_model = meta_model
        self.observers = []
        self.session = Requestor.Requestor()
        Requestor.Requestor()
        self.target_url = TARGET_URL

    def get_links(self):
        return self.all_links

    def register_observer(self, observer):
        self.observers.append(observer)

    def notify_observers(self):
        for observer in self.observers:
            observer.update({'label': self.label,'data': self.all_links[-1]})

    def start(self, url):
        self.work_event = threading.Event()
        self.thr = threading.Thread(target = self.crawl_logic, args = (url,))
        self.thr.start()
        # self.work_event = multiprocessing.Event()
        # prcs = multiprocessing.Process(target = self.crawl_logic, args = (url,))
        # prcs.start()
        return self.thr

    def crawl_logic(self, url):
        self.all_links = []
        self.crawl(url)
        self.meta_model.set_settings({'url_count': len(self.all_links), 'subdomain': 0})
        return self.all_links

    def extract_links(self, url):
        response = self.session.get(url) 
        return re.findall('(?:href=")(.*?)"', str(response.content))
        

    def filter_links(self, url, links):
        filtered = []
        for link in links:
            link = urljoin(url, link)
            if '#' in link:
                link = link.split('#')[0]
            if self.target_url in link and link not in filtered:
                filtered.append(link)
        return filtered

    def crawl(self, url):
        links = self.extract_links(url)
        for link in links:
            link = urljoin(url, link)
            if '#' in link:
                link = link.split('#')[0]
            if self.target_url in link and link not in self.all_links:
                self.all_links.append(link)
                self.notify_observers()
                
                #self.notify_observer()
                
                self.crawl(link)        




