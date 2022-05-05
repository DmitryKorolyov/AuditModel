import time
import sys
import threading
import sys
from PyQt5 import QtGui, QtWidgets, QtCore


class MetaController:
    def __init__(self, view = None, meta_model = None):

        self.view = view
        self.meta_model = meta_model

        # self.controller1 = Controller1(self)
        # self.controller2 = Controller2(self)
        # self.xss_scanner_controller = XSS_Controller(self)
        # self.sql_scanner_controller = SQL_Controller(self)
        self.controllers = {}
        self.settings_controller = Settings_Controller(self)
        #self.controllers['controller1'] = Controller1(self)
        # self.controllers['controller2'] = Controller2(self)
        # self.controllers['xss_scanner_controller'] = XSS_Controller(self)
        # self.controllers['sql_scanner_controller'] = SQL_Controller(self)

    def set_controller(self, name, Controller):
        self.controllers[name] = Controller(self)
        self.controllers[name].label = name
        print('Имя:' + self.controllers[name].label)

    def get_controller(self, name):
        return self.controllers[name]

    def set_settings(self, data):
        print('И ДАЖЕ В КОНТРОЛЛЕР!')
        self.meta_model.set_settings(data)




    # def close(self):
    #     self.meta_model.close()

class Settings_Controller:
    def __init__(self, parent):
        self.meta_controller = parent
        self.meta_model = parent.meta_model
    def send_settings(self, data):
        print('И ДАЖЕ В КОНТРОЛЛЕР!')
        self.meta_model.set_settings(data)

class SQL_Controller:
    def __init__(self, meta_controller):
        self.meta_controller = meta_controller
        self.view = self.meta_controller.view
        self.meta_model = self.meta_controller.meta_model


    def start(self):
        input = self.view.sql_scanner_view.target_input.text()
        self.meta_model.sql_scanner_model.start(input)


class Controller1:
    def __init__(self, meta_controller):
        self.meta_controller = meta_controller
        self.view = self.meta_controller.view
        self.meta_model = self.meta_controller.meta_model
        
    def start(self):
        self.meta_model.get_model('Thread_test').start()
        self.view.get_view('Thread_test').start_button.setEnabled(False)

        

    def stop(self):
        self.meta_model.get_model('Thread_test').stop()
        self.view.get_view('Thread_test').start_button.setEnabled(True)






        

        
class Controller2:
    def __init__(self, meta_controller):
        self.meta_controller = meta_controller
        self.view = self.meta_controller.view



    def start(self):
        self.meta_controller.model.scanner1model.start()
        
    def progress_to(self, work_ev):
        for i in range(0, 100):
            if not work_ev.is_set():
                self.view.scanner2.update(i)
                print(i)
                time.sleep(0.1)
            else:
                break

    def start(self):
        #number = int(self.view.target_input.text())
        thr = threading.Thread(target = self.progress_to, args = (self.meta_controller.work_event,))
        thr.start()

        
class Plug_Controller:
    def __init__(self, parent):
        self.meta_controller = parent
        self.meta_model = parent.meta_model

class Log_controller:
    def __init__(self, parent):
        self.meta_model = parent.meta_model
    def receive_logs(self):
        print('Receive_logs_вызывается')
        self.meta_model.get_model(self.label).receive_logs()

class Usage_controller:
    def __init__(self, parent):
        self.meta_model = parent.meta_model
    def compose(self):
        print('Compose вызывается')
        self.meta_model.get_model(self.label).compose()

    

class Report_controller:
    def __init__(self, parent):
        self.meta_model = parent.meta_model

    def receive_report(self):
        print('Receive_report контроллера вызывается')
        self.meta_model.get_model(self.label).receive_report()

class Advice_controller:
    def __init__(self, parent):
        self.meta_model = parent.meta_model

    def receive_advices(self):
        print('Receive_report контроллера вызывается')
        self.meta_model.get_model(self.label).receive_advices()