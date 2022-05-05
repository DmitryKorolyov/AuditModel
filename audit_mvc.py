from urllib import parse
from PyQt5 import QtWidgets, QtCore
import requests, threading, time, multiprocessing
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from pprint import PrettyPrinter, pprint
import Requestor
from config import COMMERCE_SECTION, OWASP_SECTION, SERVER_SECTION


class ModelObserverAbstract():
    def modelUpdate(self):
        raise NotImplementedError()
class ModelAbstract():
    def modelUpdate(self):
        raise NotImplementedError()

    def register_observer(self, observer):
        self.observer = observer
        print('Регистрация ' + str(self.observer))



class Audit_Step_View(QtWidgets.QWidget, ModelObserverAbstract):
    def __init__(self, parent = None, controller = None, model = None):
        # ПРИСВОЕНИЕ КОНТРОЛЛЕРА И МОДЕЛИ
        self.controller = controller
        self.parent = parent
        # ИНИЦИАЛИЗАЦИЯ ВИДЖЕТОВ
        QtWidgets.QWidget.__init__(self, parent)

        self.main_vbox = QtWidgets.QVBoxLayout()
        self.main_hbox = QtWidgets.QHBoxLayout()

        first_sect_list = []
        second_sect_list = []
        third_sect_list = []


        # self.progress_bar = QtWidgets.QProgressBar()
        # self.progress_bar.setTextVisible(False)
        # self.progress_bar.setRange(0,0)
        self.progress_bar = QtWidgets.QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setTextVisible(False)

        
        #self.progress_bar.setStyleSheet('opacity:0.8')
        #self.scroll_area = QtWidgets.QScrollArea()

        self.first_sect_vbox = QtWidgets.QVBoxLayout()
        self.first_sect_label = QtWidgets.QLabel('OWASP  ')
        self.first_sect_label.setStyleSheet('font-size: 17px; font-weight: bold; ')
        self.first_sect_label.setAlignment(QtCore.Qt.AlignCenter)
        self.first_sect_vbox.addWidget(self.first_sect_label)
        self.second_sect_vbox = QtWidgets.QVBoxLayout()
        self.second_sect_label = QtWidgets.QLabel('Сервер  ')
        self.second_sect_label.setStyleSheet('font-size: 17px; font-weight: bold; ')
        self.second_sect_label.setAlignment(QtCore.Qt.AlignCenter)
        self.second_sect_vbox.addWidget(self.second_sect_label)
        self.third_sect_vbox = QtWidgets.QVBoxLayout()
        self.third_sect_label = QtWidgets.QLabel('E-Commerce  ')
        self.third_sect_label.setStyleSheet('font-size: 17px; font-weight: bold; ')
        self.third_sect_label.setAlignment(QtCore.Qt.AlignCenter)
        self.third_sect_vbox.addWidget(self.third_sect_label)

        self.statuses_state = {}

        for view in parent.views:
            if parent.views[view].section == OWASP_SECTION:
                self.statuses_state[view] = Module_status(self, view, model)
                self.first_sect_vbox.addWidget(self.statuses_state[view])
            elif parent.views[view].section == SERVER_SECTION:
                self.statuses_state[view] = Module_status(self, view, model)
                self.second_sect_vbox.addWidget(self.statuses_state[view])
            elif parent.views[view].section == COMMERCE_SECTION:
                self.statuses_state[view] = Module_status(self, view, model)
                self.third_sect_vbox.addWidget(self.statuses_state[view])

        self.first_sect_vbox.addStretch()
        self.second_sect_vbox.addStretch()
        self.third_sect_vbox.addStretch()

        self.main_hbox.addStretch()
        self.main_hbox.addLayout(self.first_sect_vbox)
        self.main_hbox.addStretch()
        self.main_hbox.addLayout(self.second_sect_vbox)
        self.main_hbox.addStretch()
        self.main_hbox.addLayout(self.third_sect_vbox)
        self.main_hbox.addStretch()

        
        self.main_vbox.addWidget(self.progress_bar)
        self.main_vbox.addLayout(self.main_hbox)
        # self.start_btn = QtWidgets.QPushButton('Пуск')
        # self.start_btn.clicked.connect(self.controller.start)

        # self.main_vbox.addWidget(self.start_btn)
        self.setLayout(self.main_vbox)

    def prepare(self, callback):
        self.controller.start(callback)

    def update(self, message):
        print('WWWWWWWWWWWWWWWWWWWWW ВХОДИТ В UPDATE WWWWWWWWWWWWWWWWWWWWWWWWw')
        if message['is_done'] == True:
            self.controller.finish_progress()


class Module_status(QtWidgets.QWidget):
    def __init__(self, parent, label, model):
        self.meta_view = parent.parent
        QtWidgets.QWidget.__init__(self, parent)
        model.register_status_observer(self)
        self.hbox = QtWidgets.QHBoxLayout()
        self.label = QtWidgets.QLabel(label)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.status_indicator = QtWidgets.QLabel('   ')
        self.status_indicator.setStyleSheet('border: 2px solid #2b2a2a; width: 20px; height: 20px;border-radius:10px;background: #181513;')
        self.hbox.addWidget(self.label)
        self.hbox.addStretch()
        self.hbox.addWidget(self.status_indicator)
        self.setLayout(self.hbox)
    
    def update(self, message):
        self.meta_view.lock_side_rendering()
        try:
            if self.label.text() == message['label']:
                self.activate()
        except:
            pass   
        self.meta_view.unlock_side_rendering() 

    def activate(self):
        self.status_indicator.setStyleSheet('border: 2px solid #3b83bd; width: 20px; height: 20px;border-radius:10px;background: #42aaff;')
        self.status_indicator.repaint()

    def get_label(self):
        return self.label





class Audit_Steps_Controller:
    def __init__(self, meta_controller):
        self.meta_controller = meta_controller
        self.meta_view = self.meta_controller.view
        self.meta_model = self.meta_controller.meta_model

    def start(self, callback):
        # self.meta_view.get_view(self.label).progress_bar.setVisible(True)
        # self.meta_view.get_view(self.label).repaint()#input = self.meta_view.global_audit_view.stack.widget(0).home_url_input.text()
        # time.sleep(3)

        #home_input = self.meta_model.get_setting('start_page_url')

        self.e = threading.Event()
        self.thr = threading.Thread(target = self.show_progress, args = (self.e,))
        self.thr.start()

        self.meta_model.get_model('Аудит').start_in_thread(callback)
    

    def show_progress(self, event):
        bar = self.meta_view.get_view(self.label).progress_bar
        while not event.is_set():
            for i in range(1,21):
                self.meta_view.lock_side_rendering()
                bar.setValue(i * 5)
                self.meta_view.unlock_side_rendering()
                time.sleep(0.03)
            self.meta_view.lock_side_rendering()
            bar.setInvertedAppearance(True)
            self.meta_view.unlock_side_rendering()
            for i in range(1, 21):
                self.meta_view.lock_side_rendering()
                bar.setValue(100 - i * 5)
                self.meta_view.unlock_side_rendering()
                time.sleep(0.03)
            self.meta_view.lock_side_rendering()
            bar.setInvertedAppearance(False)
            self.meta_view.unlock_side_rendering()
        for i in range(1,21):
            self.meta_view.lock_side_rendering()
            bar.setValue(i * 5)
            self.meta_view.unlock_side_rendering()
            time.sleep(0.03)
            
    
    def finish_progress(self):
        self.e.set()
        while self.thr.is_alive():
            pass




class Audit_Steps_Model(ModelAbstract):
    def __init__(self, meta_model):
        self.meta_model = meta_model
        self.meta_State = self.meta_model.State
        self.status_observers = []
        self.observers = []


    # def start_audit(self, start_url):
    #     thr = threading.Thread(target = self.start_in_thread, args = (start_url,))
    #     thr.start()

    def start_in_thread(self, callback):

        self.owasp_models_list = []
        self.server_models_list = []
        self.commerce_models_list = []

        # Разбиение моделей по группам
        for model in self.meta_model.models:
            if self.meta_model.models[model].section == OWASP_SECTION:
                self.owasp_models_list.append(self.meta_model.models[model])
            elif self.meta_model.models[model].section == SERVER_SECTION:
                self.server_models_list.append(self.meta_model.models[model])
            if self.meta_model.models[model].section == COMMERCE_SECTION:
                self.commerce_models_list.append(self.meta_model.models[model])
        
        # Получение url-адресов сайта
        #self.meta_model.get_model('Веб-краулер').register_observer(self.meta_model.meta_view.bar_agregator)
        self.meta_model.get_model('Веб-краулер').register_observer(self)
        thr = self.meta_model.get_model('Веб-краулер').start(self.meta_model.get_setting('start_page_url'))
        thr.join()
        # Получение всех ссылок
        self.all_links = self.meta_model.get_model('Веб-краулер').get_links()
        print(self.all_links)

        # ДОБАВЛЕНИЕ / УДАЛЕНИЕ URLа шлюза из найденных
        if self.meta_model.get_setting('is_pay_gateway_check') == False:
            if self.meta_model.get_setting('gateway_url') in self.all_links:
                self.all_links.remove(self.meta_model.get_setting('gateway_url'))

        # Вызов хуков
        for label in self.meta_model.hooks:
            self.notify_progress_bar({'label': label,'data':'Выполнение перехватчика ' + label +' ... '})
            self.meta_model.hooks[label].execute(hooks = self.meta_model.hooks, links_list = self.all_links)


        # Регистрация State(хранилища) мета-модели
        for model in self.meta_model.models:
            self.meta_model.models[model].register_observer(self.meta_State)

        # Разделение поиска уязвимостей на три потока

        owasp_thr = threading.Thread(target = self.test_section, args = (self.owasp_models_list, self.all_links,))
        server_thr = threading.Thread(target = self.test_section, args = (self.server_models_list, self.all_links,))


        thr_list = []
        thr_list.append(owasp_thr)
        thr_list.append(server_thr)
        
        if self.meta_model.get_setting('is_pay_gateway_check') == True:
            gateway_url = self.meta_model.get_setting('gateway_url')
            commerce_thr = threading.Thread(target = self.test_section, args = (self.commerce_models_list, [gateway_url],))
            thr_list.append(commerce_thr)
            for label in self.meta_model.commerce_hooks:
                self.notify_progress_bar({'label': label,'data':'Выполнение перехватчика E-Commerce ' + label +' ... '})
                self.meta_model.commerce_hooks[label].execute(hooks = self.meta_model.commerce_hooks, links_list = self.all_links)
            
        
        for thr in thr_list:
            thr.start()
        for thr in thr_list:
            thr.join()
        print('=================================')
        pprint(self.meta_model.hooks['WPT_Store'].Store)
        print('=================================')
        pprint(self.meta_State.get_State())
        
        print(self.observers)
        self.notify_observers({'is_done': True})

        callback()
        
    

    def test_section(self, models_list, url_list):
        for model in models_list:
            print('Входит в первый цикл')
            for url in url_list:
                self.notify_progress_bar({'label': model.label,'data':'Проверка ' + model.label + ' в ' + url})
                thr = model.start(url)
                thr.join()
            self.update({'label': model.label})

    def notify_progress_bar(self, info):
        self.progress_bar.update(info)

    def notify_observers(self, message):
        for observer in self.observers:
            observer.update(message)

    def update(self, message):
        print('Вызов то есть')
        self.notify_status_observers(message)
        #self.notify_status_observers(label)

    def notify_status_observers(self, message):
        for observer in self.status_observers:
            observer.update(message)

    def register_status_observer(self, observer):
        self.status_observers.append(observer)

    def register_progress_bar(self, bar):
        self.progress_bar = bar

    def register_observer(self, observer):
        self.observers.append(observer)



    # def enable_step_btn(self):
    #     self.meta_model.get_view().enable_step_btn()