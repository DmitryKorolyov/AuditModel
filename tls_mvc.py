import threading, os
import multiprocessing
from typing import Counter
import Requestor, time
import re, json
from urllib.parse import urljoin
from config import *
from PyQt5 import QtGui, QtWidgets, QtCore
import subprocess
from subprocess import Popen, PIPE

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



class TLS_View(QtWidgets.QWidget, ModelObserverAbstract):
    addInfoSignal = QtCore.pyqtSignal(dict)
    def __init__(self, parent = None, controller = None):
        # ПРИСВОЕНИЕ КОНТРОЛЛЕРА И МОДЕЛИ
        self.controller = controller
        
        # ИНИЦИАЛИЗАЦИЯ ВИДЖЕТОВ
        QtWidgets.QWidget.__init__(self, parent)
        # Первая строка
        self.target_label = QtWidgets.QLabel('Адрес сервера:')
        self.target_input = QtWidgets.QLineEdit()
        self.target_input.setFixedWidth(200)
        #self.target_input.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed))
        #self.target_input.setMaximumSize(300, 30)
        self.start_button = QtWidgets.QPushButton('Старт')
        self.start_button.clicked.connect(self.controller.start)
        self.addInfoSignal.connect(self.signal_update, QtCore.Qt.QueuedConnection)
        self.output_label = QtWidgets.QLabel(' ')
        self.hbox1 = QtWidgets.QHBoxLayout()
        self.hbox1.addStretch()
        self.hbox1.addWidget(self.target_label)
        self.hbox1.addWidget(self.target_input)
        self.hbox1.addWidget(self.start_button)

        self.progress_bar = QtWidgets.QProgressBar()
        self.progress_bar.setRange(0, 0)
        self.progress_bar.setFixedWidth(100)
        self.progress_bar.setVisible(False)
        self.hbox1.addWidget(self.progress_bar)

        self.hbox1.insertStretch(-1)



        # Вторая строка

        # Форма вывода информации
        self.form = QtWidgets.QFormLayout()
        self.form.setLabelAlignment(QtCore.Qt.AlignLeft)
        self.version_output = QtWidgets.QLabel()
        self.time_output = QtWidgets.QLabel()
        self.cypers_output = QtWidgets.QLabel()
        self.sign_output = QtWidgets.QLabel()
        self.sign_output.setWordWrap(True)
    
        self.form.addRow('Версия протокола:', self.version_output)
        self.form.addRow('Срок истечения:', self.time_output)
        self.form.addRow('Комбинация шифров:', self.cypers_output)
        self.form.addRow('Подписан:', self.sign_output)

        self.form_line = QtWidgets.QHBoxLayout()
        self.form_line.addStretch()
        self.form_line.addLayout(self.form)
        self.form_line.addStretch()

        self.output_frame = QtWidgets.QFrame()
        self.output_frame.setLayout(self.form_line)
        self.output_frame.hide()
        
        self.main_vbox = QtWidgets.QVBoxLayout()

        self.main_vbox.addStretch()
        self.main_vbox.addLayout(self.hbox1)
        self.main_vbox.addWidget(self.progress_bar)
        self.main_vbox.addWidget(self.output_frame)
        self.main_vbox.addStretch()

        self.setLayout(self.main_vbox)

    def update(self, message):
        self.addInfoSignal.emit(message)

    def signal_update(self, message):
        data = message['data']    
        self.version_output.setText(data['tls_ver'])
        self.time_output.setText(data['time'])
        self.cypers_output.setText(data['crypto_ver'])
        self.sign_output.setText(data['sign'])

        self.progress_bar.setVisible(False)
        self.output_frame.show()



class TLS_Controller:
    def __init__(self, meta_controller):
        self.meta_controller = meta_controller
        self.meta_view = self.meta_controller.view
        self.meta_model = self.meta_controller.meta_model

    def start(self):
        url = self.meta_view.get_view(self.label).target_input.text()
        self.meta_view.get_view(self.label).target_label.setVisible(False)
        self.meta_view.get_view(self.label).target_input.setVisible(False)
        self.meta_view.get_view(self.label).start_button.setVisible(False)
        self.meta_view.get_view(self.label).progress_bar.setVisible(True)
        self.meta_model.get_model(self.label).start(url)
        # input = self.meta_view.get_view('Веб-краулер').target_input.text()
        # self.meta_view.get_view('Веб-краулер').output_label.setText('')
        # self.meta_model.get_model('Веб-краулер').start(input)


class TLS_Model(ModelAbstract):
    def __init__(self, meta_model):
        self.observers = []
        self.checked_urls_data = {}
        self.session = Requestor.Requestor()
        Requestor.Requestor()

    def register_observer(self, observer):
        self.observers.append(observer)

    def notify_observers(self, message):
        for observer in self.observers:
            observer.update(message)


    def start(self, url):
        thr = threading.Thread(target = self.start_thr, args = (url,))
        thr.start()
        return thr

    def start_thr(self, url):
        parsed_urls = re.findall('(?:https?\:\/\/(\w*(\.\w*)+))|([\d*]{1,3}\.[\d*]{1,3}\.[\d*]{1,3}\.[\d*]{1,3})', url)
        parsed_url = parsed_urls[0][0]       
        if parsed_url in self.checked_urls_data:
            pass
        else:
            data = self.check(parsed_url)
            self.checked_urls_data[parsed_url] = data
            self.notify_observers({'label': self.label, 'url': parsed_url, 'data': self.checked_urls_data[parsed_url]})
            
    def form_command(self, target):
        return 'python3 -m sslyze --regular ' + target + ' --json_out=results.json'

    def check(self, url):
        try:    
            result = subprocess.run(self.form_command(url), shell=True, stdout=subprocess.PIPE)
            f = open('results.json')
            jsoned_file = json.load(f)
            crypto_ver = jsoned_file['server_scan_results'][0]['server_info']['tls_probing_result']['cipher_suite_supported']
            tls_ver = jsoned_file['server_scan_results'][0]['server_info']['tls_probing_result']['highest_tls_version_supported']
            time = jsoned_file['server_scan_results'][0]['scan_commands_results']['certificate_info']['certificate_deployments'][0]['received_certificate_chain'][0]['not_valid_after']
            sign = jsoned_file['server_scan_results'][0]['scan_commands_results']['certificate_info']['certificate_deployments'][0]['received_certificate_chain'][0]['issuer']['rfc4514_string']
            os.remove('results.json')
            return {'tls_ver': tls_ver, 'time': time, 'crypto_ver': crypto_ver, 'sign': sign}
        except:       
            return {'tls_ver': 'Поддержка протокола TLS отстутствует', 'time': '-', 'crypto_ver': '-', 'sign': '-'}


