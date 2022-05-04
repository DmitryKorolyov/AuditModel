import time, threading, requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from pprint import pprint

import subprocess
from subprocess import Popen, PIPE

####################### СОБСТВЕННЫЕ МОДУЛИ ##############################
from config import *
import Requestor


class ModelAbstract():
    def modelUpdate(self):
        raise NotImplementedError()

    def register_observer(self, observer):
        self.observer = observer
        print('Регистрация ' + str(self.observer))






class MetaModel(ModelAbstract):
    def __init__(self):
        self.State = Log_Decorator(Model_State())
        print('[+] Создание мета-модели')
        self.session = Requestor.Requestor()

        self.models = {}
        self.hooks = {}
        self.commerce_hooks = {}
        self.audit_settings = {}
        self.vuln_labels = []

    def get_mutex(self):
        return self.mutex

    def get_state(self):
        return self.State.get_State()

    def get_setting(self, label):
        return self.audit_settings[label]

    def setup_session(self, url, login, password):
        print('Входим в setup session мета-модели')
        self.session.login(url, login, password)
        return True

    def set_model(self, label, section, Model, advice):
        self.models[label] = Model(self)
        self.models[label].label = label
        self.models[label].section = section
        self.models[label].advice = advice

    def get_model(self, label):
        return self.models[label]

    def get_session(self):
        return self.session

    def set_hook(self, label, hook):
        self.hooks[label] = hook(self)

    def get_hook(self, label):
        return self.hooks[label]


    def set_commerce_hook(self, label, hook):
        self.commerce_hooks[label] = hook(self)

    def get_commerce_hook(self, label):
        return self.commerce_hooks[label]

    def get_logs(self):
        return self.State.get_logs()
    
    def set_settings(self, data):
        for setting in data:
            self.audit_settings[setting] = data[setting]




class Model_State(ModelAbstract):
    def __init__(self):
        self.State = {}

    def update(self, message):
        # self.State[message['label']] = {}
        # #self.State[message['label']][message['url']] = {}
        # self.State[message['label']][message['url']] = {'data': message['data']}
        #if self.State[message['label']][message['url']] == None:
        if message['label'] in self.State:
            self.State[message['label']][message['url']] = {'data': message['data']}
        else:
            self.State[message['label']] = {}
            self.State[message['label']][message['url']] = {'data': message['data']}
        #self.State[message['label']][message['url']] = {}
        #self.State[message['label']][message['url']] = {'data': message['data']}


    def get_State(self):
        return self.State

    def get(self, index):
        return self.State

class Log_Decorator:
    def __init__(self, Decorated_state):
        self.State = Decorated_state
        self.logs = ''
    
    def update(self, message):
        try:
            if message['data'] == True:
                self.logs = self.logs + '['+ time.ctime() + ']  ' + message['label'] + ' в ' + message['url'] + ' . Атака реализуема!\n'
            elif message['data'] == False:
                self.logs = self.logs + '['+ time.ctime() + ']  ' + message['label'] + ' в ' + message['url'] + ' . Атака нереализуема.\n'
            else:
                details = ''
                for field in message['data']:
                    details = details + field + ' : ' + message['data'][field] + '\n'
                self.logs = self.logs + '['+ time.ctime() + ']  ' + message['label'] + ' в ' + message['url'] + ':\n' + details
            self.State.update(message)
        except:
            pass

    def get_State(self):
        return self.State.get_State()

    def get(self, index):
        return self.State.get(index)

    def get_logs(self):
        return self.logs

class Log_Model:
    def __init__(self, meta_model):
        self.meta_model = meta_model
        self.observers = []

    def receive_logs(self):
        logs = self.meta_model.get_logs()
        print(logs)
        self.notify_observers(logs)

    def register_observer(self, observer):
        self.observers.append(observer)

    def notify_observers(self, message):
        for observer in self.observers:
            observer.update(message)


class Usage_Model:
    def __init__(self, meta_model):
        self.meta_model = meta_model
        self.observers = []
        self.state = self.meta_model.get_state()

    def compose(self):
        print('compose в моделях тоже вызывается')
        owasp_models_list = []
        server_models_list = []
        commerce_models_list = []

        for model in self.meta_model.models:
            if self.meta_model.models[model].section == OWASP_SECTION:
                owasp_models_list.append(model)
            elif self.meta_model.models[model].section == SERVER_SECTION:
                server_models_list.append(model)
            if self.meta_model.models[model].section == COMMERCE_SECTION:
                commerce_models_list.append(model)

        self.meta_model.set_settings({'vulns_count': len(owasp_models_list) + len(server_models_list) + len(commerce_models_list)})

        print(self.state)
        pprint(owasp_models_list)
        pprint(self.compose_section(owasp_models_list))

        message = {'OWASP': self.compose_section(owasp_models_list), 'SERVER': self.compose_section(server_models_list), 'COMMERCE': self.compose_section(commerce_models_list)}

        vuln_labels = []
        for section in message:
            for label in message[section]:
                vuln_labels.append(label)

        self.meta_model.vuln_labels = vuln_labels
        self.notify_observers(message)


    def compose_section(self, section_list):
        section_content = {}
        header_str = 'Уязвимость обнаружена в:\n'
        for vuln_label in section_list:

            vuln_state = self.state[vuln_label]
            if type(list(vuln_state.items())[0][1]['data']) == bool:
                details = header_str
                for url in vuln_state:
                    if vuln_state[url]['data'] == True:
                        details = details + url + '\n'
                if details != header_str:
                    section_content[vuln_label] = details
            else:
                details = ''
                for url in vuln_state:
                    for field in vuln_state[url]['data']:
                        details = details + field + ' : ' + vuln_state[url]['data'][field] + '\n'
                section_content[vuln_label] = details
        return section_content



    def register_observer(self, observer):
        self.observers.append(observer)

    def notify_observers(self, message):
        for observer in self.observers:
            observer.update(message)



class Report_Model:
    def __init__(self, meta_model):
        self.meta_model = meta_model
        self.observers = []
        self.settings = self.meta_model.audit_settings

    def receive_report(self):
        print('receive report модели вызывается')
        pprint(self.settings)
        report = {}
        report['start_date'] = self.settings['start_date']
        report['end_time'] = time.ctime()
        report['url_count'] = self.settings['url_count']
        report['subdomain'] = self.settings['subdomain']
        report['auth_type'] = self.settings['auth_option']
        report['vulns_count'] = self.settings['vulns_count']
        report['finded_vulns'] = self.settings['finded_vulns']
        report['owasp_vulns_count'] = self.settings['owasp_vulns_count']
        report['server_vulns_count'] = self.settings['server_vulns_count']
        report['commerce_vulns_count'] = self.settings['commerce_vulns_count']
        
        vulns = ''
        for label in self.meta_model.State.get_State():
            vulns = vulns + label + ',\n'
        report['vulns'] = vulns

        pprint(report)

        self.notify_observers(report)

    def register_observer(self, observer):
        self.observers.append(observer)

    def notify_observers(self, message):
        for observer in self.observers:
            observer.update(message)

class Advice_Model:
    def __init__(self, meta_model):
        self.meta_model = meta_model
        self.observers = []


    def receive_advices(self):
        advices = {}
        
        for label in self.meta_model.vuln_labels:
            advices[label] = self.meta_model.get_model(label).advice

        pprint(advices)
        self.notify_observers(advices)

    def register_observer(self, observer):
        self.observers.append(observer)

    def notify_observers(self, message):
        for observer in self.observers:
            observer.update(message)



