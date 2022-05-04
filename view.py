from PyQt5 import QtGui, QtWidgets, QtCore
import PyQt5
from config import *
from brut_force_mvc import *
from controller import *
from pilot_model import *
from audit_mvc import *

import copy

class ModelObserverAbstract():
    def modelUpdate(self):
        raise NotImplementedError()


class MetaView(QtWidgets.QMainWindow, ModelObserverAbstract):
    def __init__(self, parent = None, MetaController = None, MetaModel = None):
        QtWidgets.QMainWindow.__init__(self, parent)

        self.mutex = threading.Lock()

        # ПРИСВОЕНИЕ КОНТРОЛЛЕРОВ И МОДЕЛЕЙ
        #Мета-контроллер и мета-модель
        self.meta_model = MetaModel()
        self.meta_model.register_observer(self)
        self.meta_controller = MetaController(view = self, meta_model = self.meta_model)

        # Создание глобального представления аудита
        self.global_audit_view = Global_Audit_View(parent = self, controller = self.meta_controller.settings_controller)
        #Создание представлений
        self.views = {}

        # # Сбор в группу меню
        self.stack = QtWidgets.QStackedWidget()

        self.stack.addWidget(Disclaimer(self))
        self.stack.addWidget(self.global_audit_view)

        # МЕНЮ 
        self._create_menu()

        self.status_bar = self.statusBar()
        self.status_bar.setStyleSheet("background-color : #044857")
        
                

        # Статусбар
        self.session_label = QtWidgets.QLabel('Сессия')
        self.session_status = QtWidgets.QLabel('   ')
        self.session_status.setStyleSheet('border: 2px solid #2b2a2a; width: 20px; height: 20px;border-radius:10px;background: #181513;')
        self.bar_hb = QtWidgets.QHBoxLayout()

        self.status_label = QtWidgets.QLabel('                                                                                                                                                                 ')
        self.bar_hb.addWidget(self.status_label)
        self.bar_hb.addStretch()
        self.bar_hb.addWidget(self.session_label)
        self.bar_hb.addWidget(self.session_status)
        self.bar_frame = QtWidgets.QFrame()
        self.bar_frame.setFixedWidth(995)
        self.bar_frame.setLayout(self.bar_hb)
        self.status_bar.addWidget(self.bar_frame)
        self.status_bar.setVisible(False)

        self.bar_agregator = Status_Bar_Agregator(self)

    
    def lock_side_rendering(self):
        self.mutex.acquire()

    def unlock_side_rendering(self):
        self.mutex.release()

    def set_crawler(self, label, section, view_component, controller_component, model_component):
        self.set_component(self, label, section, view_component, controller_component, model_component)


    def set_brute_force(self, label, section, view_component, controller_component, model_component, advice):
        self.set_component(label = label, section = section, view_component = view_component, controller_component = controller_component, model_component = model_component)

        self.meta_controller.set_controller('Audit_' + label, controller_component)
        self.meta_model.set_model('Audit_' + label, section, model_component, advice)
        self._set_view('Audit_' + label, section, view_component, self.meta_controller.get_controller('Audit_' + label))
        self.meta_model.get_model('Audit_' + label).register_observer(self.get_view('Audit_' + label))
        self.global_audit_view.stack.addWidget(self.get_view('Audit_' + label))

    def set_audit_step(self, label, section, view_component, controller_component = None, model_component = None, advice = None):
        self.meta_controller.set_controller(label, controller_component)
        self.meta_model.set_model(label, section, model_component, advice)
        view = view_component(parent = self, controller = self.meta_controller.get_controller(label), model = self.meta_model.get_model(label))
        view.label = label
        self.views[label] = view
        self.meta_model.get_model(label).register_observer(view)
        self.global_audit_view.stack.addWidget(view)

    def set_settings_tab(self, label = None, view = None):
        self.global_audit_view.stack.widget(0).set_tab(view(parent = self), label)

    def set_hook(self, label, hook):
        self.meta_model.set_hook(label, hook)

    def set_commerce_hook(self, label, hook):
        self.meta_model.set_commerce_hook(label, hook)
    
    def set_settings(self, data):
        self.meta_controller.set_settings(data)



    def session_lamp_off(self):
        self.session_status.setStyleSheet('border: 2px solid #2b2a2a; width: 20px; height: 20px;border-radius:10px;background: #181513;')
        try:
            self.session_status.repaint()
        except AttributeError:
            pass

    def session_lamp_on(self):
        self.session_status.setStyleSheet('border: 2px solid #3b83bd; width: 20px; height: 20px;border-radius:10px;background: #42aaff;')
        try:
            self.session_status.repaint()
        except AttributeError:
            pass

    def session_lamp_half_on(self):
        self.session_status.setStyleSheet('border: 2px solid #3b83bd; width: 20px; height: 20px;border-radius:10px;background: #0000FF;')
        try:
            self.session_status.repaint()
        except AttributeError:
            pass

    def session_lamp_activate(self):
        
        for i in range(0, 4):
            self.session_lamp_half_on()
            time.sleep(0.1)
            self.session_lamp_off()
            time.sleep(0.3)
        self.session_lamp_half_on()
        time.sleep(0.5)
        self.session_lamp_on()
        
    def _create_menu(self):
        self.menubar = self.menuBar()
        self.menubar.setStyleSheet('background-color : #1d2b36;')
        
        tool = QtWidgets.QAction('Аудит', self)
        tool.triggered.connect(lambda: self.stack.setCurrentWidget(self.global_audit_view))
        self.audit_menu = self.menubar.addAction(tool)

        self.modules_menu = self.menubar.addMenu('Модули')
        self.OWASP_Bar_menu = self.modules_menu.addMenu(OWASP_SECTION)
        self.Server_IS_menu = self.modules_menu.addMenu(SERVER_SECTION)
        self.E_commerce_menu = self.modules_menu.addMenu(COMMERCE_SECTION)
        self.other_modules_menu = self.modules_menu.addMenu(OTHER)
        self.settings_menu = self.menubar.addMenu('Настройки')
        self.menubar.setVisible(False)

    def set_menu_visible(self):
        self.menubar.setVisible(True)

    def set_status_bar_visible(self):
        self.status_bar.setVisible(True)

    def userfunc(self):
        print('WORKS!')

    def _set_view(self, label, section, View, controller = None):
        self.views[label] = View(parent = self, controller = self.meta_controller.get_controller(label))
        self.views[label].label = label
        self.views[label].section = section

    def get_view(self, label):
        return self.views[label]

    def set_component(self, label, section, view_component, controller_component = None, model_component = None, advice = None):
        if controller_component == None and model_component == None:
            self._set_view(label, section, view_component)
        if controller_component != None and model_component != None:
            # Распределение контроллера и модели
            self.meta_controller.set_controller(label, controller_component)
            self.meta_model.set_model(label, section, model_component, advice)
            # Привязка составных частей компонента друг к другу
            self._set_view(label, section, view_component, self.meta_controller.get_controller(label))
            self.meta_model.get_model(label).register_observer(self.get_view(label))
            # Расположение компонента в меню
            self.stack.addWidget(self.get_view(label))
            tool = QtWidgets.QAction(label, self)
            tool.triggered.connect(lambda: self.stack.setCurrentWidget(self.get_view(label)))
            if section == OWASP_SECTION:
                self.OWASP_Bar_menu.addAction(tool)
                print(section)
            elif section == SERVER_SECTION:
                self.Server_IS_menu.addAction(tool)
            elif section == COMMERCE_SECTION:
                self.E_commerce_menu.addAction(tool)
            elif section == OTHER:
                self.other_modules_menu.addAction(tool)       

class Status_Bar_Agregator(QtWidgets.QMainWindow, ModelObserverAbstract):
    def __init__(self, main_view):
        self.main_view = main_view
        self.label = main_view.status_label
    def update(self, message):
        self.main_view.lock_side_rendering()
        self.label.setText(message['data'])
        self.label.repaint()
        self.main_view.unlock_side_rendering()


class Global_Audit_View(QtWidgets.QWidget, ModelObserverAbstract):
    def __init__(self, parent = None, controller = None):
        self.controller = controller

        QtWidgets.QWidget.__init__(self, parent)

        self.stack = QtWidgets.QStackedWidget()
        init_settings_view = Init_Settings_view(parent = self, controller = self.controller)
        self.stack.addWidget(init_settings_view)
        # Формирование линии шагов и кнопки далее, их размещение вместе с виджетом шагов аудита stack 
        self.steps_line = Steps_Line(parent = self)
        self.main_vbox = QtWidgets.QVBoxLayout()
        self.main_vbox.addWidget(self.steps_line)
        self.main_vbox.addWidget(self.stack)
        self.main_vbox.addStretch()
        self.next_step_btn = QtWidgets.QPushButton('Далее')
        self.next_btn_layout = QtWidgets.QHBoxLayout()
        self.next_btn_layout.addStretch()
        self.next_btn_layout.addWidget(self.next_step_btn)
        self.next_step_btn.setIcon(self.style().standardIcon(getattr(QtWidgets.QStyle, 'SP_ToolBarHorizontalExtensionButton')))
        self.next_step_btn.clicked.connect(self.next)
        self.main_vbox.addLayout(self.next_btn_layout)
        self.setLayout(self.main_vbox)

    def next(self):
        try:
            self.stack.currentWidget().set_settings()
        except:
            pass
        self.steps_line.next_step()
        self.stack.setCurrentIndex(self.steps_line.get_current_step())
        
        if self.stack.currentWidget().label == 'Рекомендации':
            self.next_step_btn.setVisible(False)

        if self.stack.currentWidget().label == 'Аудит':
            print('заходит!')
            self.next_step_btn.setEnabled(False)
        try:
            self.stack.currentWidget().prepare(self.enable_button_callback)
        except:
            pass

    def enable_button_callback(self):
        self.next_step_btn.setEnabled(True)

class Init_Settings_view(QtWidgets.QWidget):
        def __init__(self, parent = None, controller = None):
            self.controller = controller
            self.tabs_count = 1
            
            QtWidgets.QWidget.__init__(self, parent)

            self.main_vbox = QtWidgets.QVBoxLayout()
            self.form = QtWidgets.QFormLayout()
            self.form.setLabelAlignment(QtCore.Qt.AlignLeft)
            self.domain_input = QtWidgets.QLineEdit()
            self.domain_input.setFixedWidth(250)
            self.form.addRow('Домен цели:', self.domain_input)
            self.home_url_input = QtWidgets.QLineEdit()
            self.home_url_input.setFixedWidth(250)
            self.form.addRow('URL стартовой страницы:', self.home_url_input)
            self.gateway_input = QtWidgets.QLineEdit()
            self.gateway_input.setFixedWidth(250)
            self.form.addRow('URL платежного шлюза:', self.gateway_input)
            self.audit_format_box = QtWidgets.QGroupBox()
            self.radio_box = QtWidgets.QHBoxLayout()
            self.yes_radio = QtWidgets.QRadioButton('Да')
            self.no_radio = QtWidgets.QRadioButton('Игнорировать адрес')
            self.radio_box.addWidget(self.yes_radio)
            self.radio_box.addWidget(self.no_radio)
            self.audit_format_box.setLayout(self.radio_box)
            self.form.addRow('Проверка платежного шлюза:', self.audit_format_box)
            self.subdomain_group = QtWidgets.QGroupBox()
            self.subdomain_box = QtWidgets.QHBoxLayout()
            self.yes_subdomain_radio = QtWidgets.QRadioButton('Произвести',self)
            self.no_subdomain_radio = QtWidgets.QRadioButton('Пропустить',self)
            self.subdomain_box.addWidget(self.yes_subdomain_radio)
            self.subdomain_box.addWidget(self.no_subdomain_radio)
            self.subdomain_group.setLayout(self.subdomain_box)
            self.form.addRow('Поиск поддоменов:', self.subdomain_group)
            self.auth_option = QtWidgets.QComboBox()
            self.auth_option.addItems(['Ввод данных учетной записи', 'Брутфорс данных учетной записи'])
            self.form.addRow('Аутентификация в ресурсе:', self.auth_option)
            self.modules_view_option = QtWidgets.QComboBox()
            self.modules_view_option.addItems(['Последовательный реестр', 'Разделение на потоки'])
            self.form.addRow('Отображение модулей:', self.modules_view_option)

            
            self.main_hbox = QtWidgets.QHBoxLayout()
            self.main_hbox.addStretch()
            self.main_hbox.addLayout(self.form)
            self.main_hbox.addStretch()

            self.main_vbox.addStretch()
            self.main_vbox.addLayout(self.main_hbox)
            self.main_vbox.addStretch()

            self.main_settings_w = QtWidgets.QWidget()
            self.main_settings_w.setLayout(self.main_vbox)

            self.tab = QtWidgets.QTabWidget()
            self.tab.addTab(self.main_settings_w, 'Основные')
            
            
            self.tab_layout = QtWidgets.QVBoxLayout()
            self.tab_layout.addWidget(self.tab)
            
            self.setLayout(self.tab_layout)

        def set_tab(self, widget, label):
            self.tab.addTab(widget, label)
            self.tabs_count = self.tabs_count + 1

        def set_settings(self):
            print('ДОХОДИТ ДО СЕТ СЕТТИНГС ВО ВЬЮ')
            self.controller.send_settings({  'target_domain': self.domain_input.text(),
                                        'start_page_url': self.home_url_input.text(),
                                        'gateway_url': self.gateway_input.text(),
                                        'is_pay_gateway_check': self.yes_radio.isChecked(),
                                        'auth_option': self.auth_option.currentText(),
                                        'modul_view': self.modules_view_option.currentText(),
                                        'start_date': time.ctime()
                                        })

            for i in range(1, self.tabs_count):
                print(i)
                self.tab.widget(i).set_settings()

class Steps_Line(QtWidgets.QWidget, ModelObserverAbstract):
    def __init__(self, parent = None, controller = None):
        self.curent_index = 0
        self.steps_list = []
        # ПРИСВОЕНИЕ КОНТРОЛЛЕРА И МОДЕЛИ
        # self.model = model
        # ИНИЦИАЛИЗАЦИЯ ВИДЖЕТОВ
        QtWidgets.QWidget.__init__(self, parent)

        # Дорожка шагов аудита
        self.steps_hbox = QtWidgets.QHBoxLayout()

        self.settings_step = QtWidgets.QLabel('Настройки')
        self.steps_list.append(self.settings_step)
        self.settings_step.setAlignment(QtCore.Qt.AlignCenter)
        self.settings_step.setStyleSheet('border: 1px solid white; border-radius:5px;background-color: #42aaff;')
        self.settings_step.setFixedHeight(30)
        #self.settings_step.setStyleSheet('font-size:30px')

        self.login_step = QtWidgets.QLabel('Аутентификация')
        self.steps_list.append(self.login_step)
        self.login_step.setAlignment(QtCore.Qt.AlignCenter)
        self.login_step.setStyleSheet('border: 1px solid white; border-radius:5px')

        self.audit_step = QtWidgets.QLabel('Аудит')
        self.steps_list.append(self.audit_step)
        self.audit_step.setAlignment(QtCore.Qt.AlignCenter)
        self.audit_step.setStyleSheet('border: 1px solid white; border-radius:5px')

        self.logs_step = QtWidgets.QLabel('Логи')
        self.steps_list.append(self.logs_step)
        self.logs_step.setAlignment(QtCore.Qt.AlignCenter)
        self.logs_step.setStyleSheet('border: 1px solid white; border-radius:5px')

        self.use_step = QtWidgets.QLabel('Эксплуатация')
        self.steps_list.append(self.use_step)
        self.use_step.setAlignment(QtCore.Qt.AlignCenter)
        self.use_step.setStyleSheet('border: 1px solid white; border-radius:5px')

        self.report_step = QtWidgets.QLabel('Отчет')
        self.steps_list.append(self.report_step)
        self.report_step.setAlignment(QtCore.Qt.AlignCenter)
        self.report_step.setStyleSheet('border: 1px solid white; border-radius:5px')

        self.advice_step = QtWidgets.QLabel('Рекомендации')
        self.steps_list.append(self.advice_step)
        self.advice_step.setAlignment(QtCore.Qt.AlignCenter)
        self.advice_step.setStyleSheet('border: 1px solid white; border-radius:5px')
        
        self.steps_hbox.addWidget(self.settings_step)
        self.steps_hbox.addWidget(self.login_step)
        self.steps_hbox.addWidget(self.audit_step)
        self.steps_hbox.addWidget(self.logs_step)
        self.steps_hbox.addWidget(self.use_step)
        self.steps_hbox.addWidget(self.report_step)
        self.steps_hbox.addWidget(self.advice_step)

        self.main_vbox = QtWidgets.QVBoxLayout()
        self.main_vbox.addLayout(self.steps_hbox)
        self.main_vbox.addStretch()
        self.setLayout(self.main_vbox)

    def next_step(self):
        try:
            self.steps_list[self.curent_index].setStyleSheet('color: #999999;border: 1px solid #8a7f8e; border-radius:5px;background-color: #4c5866;')
        except:
            pass
        self.curent_index += 1
        self.steps_list[self.curent_index].setStyleSheet('border: 1px solid white; border-radius:5px;background-color: #42aaff;')
        
    def get_current_step(self):
        return self.curent_index


class Disclaimer(QtWidgets.QWidget):
    def __init__(self, parent = None):
        QtWidgets.QWidget.__init__(self, parent)
        self.meta_view = parent
        self.warning = QtWidgets.QLabel('Внимание!')
        self.warning.setStyleSheet('color: red; font-size:40px; font-weight:bold;')
        self.warning.setAlignment(QtCore.Qt.AlignCenter)
        self.text = QtWidgets.QLabel('    Автор данного программного обеспечения НЕ несёт ответственность за последствия от его использования! Нарушение федеральных законов РФ №149 "Об информации, информационных технологиях и о защите информации", №152 "О персональных данных", №98 "О коммерческой тайне", №63" Об электронной подписи", а также №187 "О безопасности критической информационной инфраструктуры Российской Федерации" уголовно наказуемо.\n    Данное программное обеспечение включает в себя стороннее программное обеспечение, распространяющееся посредством свободной лицензии GPL и используется автором исключительно в образовательных целях.')
        self.text.setWordWrap(True)
        self.text.setAlignment(QtCore.Qt.AlignJustify)
        self.agree_btn = QtWidgets.QPushButton('Понятно')
        self.agree_btn.clicked.connect(self.enable_menu_status_bars)
        self.agree_btn.setIcon(self.style().standardIcon(getattr(QtWidgets.QStyle, 'SP_DialogApplyButton')))
        self.disagree_btn = QtWidgets.QPushButton('Выйти')
        self.disagree_btn.setIcon(self.style().standardIcon(getattr(QtWidgets.QStyle, 'SP_DialogCloseButton')))
        self.disagree_btn.clicked.connect(QtWidgets.qApp.quit)
        self.btn_box = QtWidgets.QHBoxLayout()
        self.btn_box.addStretch()
        self.btn_box.addWidget(self.agree_btn)
        self.btn_box.addWidget(self.disagree_btn)
        self.btn_box.addStretch()        
        self.vbox = QtWidgets.QVBoxLayout()
        self.vbox.addStretch(1)
        self.vbox.addWidget(self.warning)
        self.vbox.addWidget(self.text)
        self.vbox.addLayout(self.btn_box)
        self.vbox.addStretch(2)
        self.setLayout(self.vbox)

    def enable_menu_status_bars(self):
        self.meta_view.set_menu_visible()
        self.meta_view.set_status_bar_visible()
        self.setVisible(False)




class TLS_Scanner1(QtWidgets.QWidget, ModelObserverAbstract):
    def __init__(self, parent = None, controller = None):

        # ПРИСВОЕНИЕ КОНТРОЛЛЕРА И МОДЕЛИ
        # self.model = model
        self.controller = controller
        

        # ИНИЦИАЛИЗАЦИЯ ВИДЖЕТОВ

        QtWidgets.QWidget.__init__(self, parent)
        #self.parent = parent

        # Первая строка - ввод IP
        self.target_label = QtWidgets.QLabel('Цель:')
        self.target_input = QtWidgets.QLineEdit()
        #self.target_input.setFixedWidth(200)
        self.target_input.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Fixed))
        #self.target_input.setMaximumSize(300, 30)
        self.start_button = QtWidgets.QPushButton('Сканировать')
        
        self.stop_button = QtWidgets.QPushButton('Стоп')
        
        #self.start_button.clicked.connect(self.controller.start())
        self.start_button.clicked.connect(self.controller.start)
        self.stop_button.clicked.connect(self.controller.stop)


        self.hbox1 = QtWidgets.QHBoxLayout()
        self.hbox1.addWidget(self.target_label)
        self.hbox1.addWidget(self.target_input)
        self.hbox1.addWidget(self.start_button)
        self.hbox1.addWidget(self.stop_button)
        #self.hbox1.addWidget(self.target_input, alignment = QtCore.Qt.AlignLeft)
        self.hbox1.insertStretch(-1)
        

        # Вторая строка - Ввод диапазона портов
        self.port_label1 = QtWidgets.QLabel('Диапазон портов от ')
        self.port_input1 = QtWidgets.QSpinBox()
        self.port_input1.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed))
        self.port_label2 = QtWidgets.QLabel(' до ')
        self.port_input2 = QtWidgets.QSpinBox()
        self.port_input2.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed))
        self.hbox2 = QtWidgets.QHBoxLayout()
        self.hbox2.addWidget(self.port_label1)
        self.hbox2.addWidget(self.port_input1)
        self.hbox2.addWidget(self.port_label2)
        self.hbox2.addWidget(self.port_input2)
        self.hbox2.insertStretch(-1)

        # Третья строка - количество потоков
        self.thread_label1 = QtWidgets.QLabel('Количество потоков: ')
        self.slider = QtWidgets.QSlider()
        self.slider.setRange(1, 100)
        self.slider.setOrientation(QtCore.Qt.Horizontal)
        self.hbox3 = QtWidgets.QHBoxLayout()
        self.hbox3.addWidget(self.thread_label1)
        self.hbox3.addWidget(self.slider)


        # Четвертая строка - вывод информации
        self.bar = QtWidgets.QProgressBar()
        self.bar.setRange(0, 100)
        self.bar.setValue(60)
        lorem = 'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum. '
        self.output_label = QtWidgets.QLabel()
        self.output_label.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Minimum))
        self.output_label.setWordWrap(True)
        self.output_label.setText(lorem)
        self.hbox4 = QtWidgets.QHBoxLayout()
        self.hbox4.addWidget(self.output_label)
        self.hbox4.addWidget(self.bar)



        # Компоновка виджетов
        self.vbox = QtWidgets.QVBoxLayout()
        self.vbox.addLayout(self.hbox1)
        self.vbox.addLayout(self.hbox2)
        self.vbox.addLayout(self.hbox3)
        self.vbox.addLayout(self.hbox4)
        self.vbox.insertStretch(-1)

        self.setLayout(self.vbox)
        #self.start_button.clicked.connect(self.bar.setValue(70))

        # СИГНАЛЫ-СЛОТЫ
    def update(self, progress):
        print('доходит')
        self.bar.setValue(progress)

class TLS_Scanner2(QtWidgets.QWidget, ModelObserverAbstract):
    def __init__(self, parent = None, controller = None):

        # # ПРИСВОЕНИЕ КОНТРОЛЛЕРА И МОДЕЛИ
        # self.model = model
        self.controller = controller
        

        # ИНИЦИАЛИЗАЦИЯ ВИДЖЕТОВ

        QtWidgets.QWidget.__init__(self, parent)
        self.parent = parent

        # Первая строка - ввод IP
        self.target_label = QtWidgets.QLabel('не оправдывает:')
        self.target_input = QtWidgets.QLineEdit()
        #self.target_input.setFixedWidth(200)
        self.target_input.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Fixed))
        #self.target_input.setMaximumSize(300, 30)
        self.start_button = QtWidgets.QPushButton('Сканировать')
        #self.start_button.clicked.connect(self.controller.start())
        self.start_button.clicked.connect(self.controller.start)


        self.hbox1 = QtWidgets.QHBoxLayout()
        self.hbox1.addWidget(self.target_label)
        self.hbox1.addWidget(self.target_input)
        self.hbox1.addWidget(self.start_button)
        #self.hbox1.addWidget(self.target_input, alignment = QtCore.Qt.AlignLeft)
        self.hbox1.insertStretch(-1)
        

        # Вторая строка - Ввод диапазона портов
        self.port_label1 = QtWidgets.QLabel('Диапазон портов от ')
        self.port_input1 = QtWidgets.QSpinBox()
        self.port_input1.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed))
        self.port_label2 = QtWidgets.QLabel(' до ')
        self.port_input2 = QtWidgets.QSpinBox()
        self.port_input2.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed))
        self.hbox2 = QtWidgets.QHBoxLayout()
        self.hbox2.addWidget(self.port_label1)
        self.hbox2.addWidget(self.port_input1)
        self.hbox2.addWidget(self.port_label2)
        self.hbox2.addWidget(self.port_input2)
        self.hbox2.insertStretch(-1)

        # Третья строка - количество потоков
        self.thread_label1 = QtWidgets.QLabel('Количество потоков: ')
        self.slider = QtWidgets.QSlider()
        self.slider.setRange(1, 100)
        self.slider.setOrientation(QtCore.Qt.Horizontal)
        self.hbox3 = QtWidgets.QHBoxLayout()
        self.hbox3.addWidget(self.thread_label1)
        self.hbox3.addWidget(self.slider)


        # Четвертая строка - вывод информации
        self.bar = QtWidgets.QProgressBar()
        self.bar.setRange(0, 100)
        self.bar.setValue(60)
        lorem = 'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum. '
        self.output_label = QtWidgets.QLabel()
        self.output_label.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Maximum))
        self.output_label.setWordWrap(True)
        self.output_label.setText(lorem)
        self.hbox4 = QtWidgets.QHBoxLayout()
        self.hbox4.addWidget(self.output_label)
        self.hbox4.addWidget(self.bar)


        # Компоновка виджетов
        self.vbox = QtWidgets.QVBoxLayout()
        self.vbox.addLayout(self.hbox1)
        self.vbox.addLayout(self.hbox2)
        self.vbox.addLayout(self.hbox3)
        self.vbox.addLayout(self.hbox4)
        self.vbox.insertStretch(-1)

        self.setLayout(self.vbox)
        #self.start_button.clicked.connect(self.bar.setValue(70))

        # СИГНАЛЫ-СЛОТЫ
    def update(self, progress):
        print('доходит')
        self.bar.setValue(progress)


class TLS_Scanner_View(QtWidgets.QWidget, ModelObserverAbstract):
    def __init__(self, parent = None, controller = None):
        # ПРИСВОЕНИЕ КОНТРОЛЛЕРА И МОДЕЛИ
        self.controller = controller
        
        # ИНИЦИАЛИЗАЦИЯ ВИДЖЕТОВ
        QtWidgets.QWidget.__init__(self, parent)
        # Первая строка
        self.target_label = QtWidgets.QLabel('URL-адрес цели:')
        self.target_input = QtWidgets.QLineEdit()
        #self.target_input.setFixedWidth(200)
        self.target_input.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed))
        #self.target_input.setMaximumSize(300, 30)
        self.start_button = QtWidgets.QPushButton('Проверить')
        self.start_button.clicked.connect(self.controller.start)
        self.output_label = QtWidgets.QLabel(' ')
        self.hbox1 = QtWidgets.QHBoxLayout()
        self.hbox1.addWidget(self.target_label)
        self.hbox1.addWidget(self.target_input)
        self.hbox1.addWidget(self.start_button)
        self.hbox1.insertStretch(-1)
        # Вторая строка
        self.hbox2 = QtWidgets.QHBoxLayout()
        self.target_label = QtWidgets.QLabel('URL-адрес цели:')

        self.vbox = QtWidgets.QVBoxLayout()
        self.vbox.addLayout(self.hbox1)
        self.vbox.addWidget(self.output_label)
        self.vbox.insertStretch(-1)
        self.setLayout(self.vbox)
    
    def update(self, isVuln):
        if isVuln:
            self.output_label.setText('XSS-атака возможна')
        else:
            self.output_label.setText('XSS-атака не реализуема')


class SQL_Scanner_View(QtWidgets.QWidget, ModelObserverAbstract):
    addTextSignal = QtCore.pyqtSignal(str)
    def __init__(self, parent = None, controller = None):
        # ПРИСВОЕНИЕ КОНТРОЛЛЕРА И МОДЕЛИ
        self.controller = controller
        
        # ИНИЦИАЛИЗАЦИЯ ВИДЖЕТОВ
        QtWidgets.QWidget.__init__(self, parent)
        # Первая строка
        self.target_label = QtWidgets.QLabel('URL-адрес:')
        self.target_input = QtWidgets.QLineEdit()
        #self.target_input.setFixedWidth(200)
        self.target_input.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed))
        #self.target_input.setMaximumSize(300, 30)
        self.start_button = QtWidgets.QPushButton('Проверить')
        self.start_button.clicked.connect(self.controller.start)
        self.output_label = QtWidgets.QLabel(' ')
        self.hbox1 = QtWidgets.QHBoxLayout()
        self.hbox1.addWidget(self.target_label)
        self.hbox1.addWidget(self.target_input)
        self.hbox1.addWidget(self.start_button)
        self.hbox1.insertStretch(-1)
        # Вторая строка


        # Вывод
        self.output_area = QtWidgets.QTextEdit()
        self.output_area.setPlainText('works!')
        self.addTextSignal.connect(self.output_area.setPlainText, QtCore.Qt.QueuedConnection)

        self.vbox = QtWidgets.QVBoxLayout()
        self.vbox.addLayout(self.hbox1)
        self.vbox.addWidget(self.output_area)
        self.vbox.insertStretch(-1)
        self.setLayout(self.vbox)
    
    def update(self, vuln_info):
        #print(vuln_info)
        self.addTextSignal.emit(vuln_info)

class Plug_View(QtWidgets.QWidget):
    def __init__(self, parent = None, controller = None):
        QtWidgets.QWidget.__init__(self, parent)
        self.hbox = QtWidgets.QHBoxLayout()
        self.vbox = QtWidgets.QVBoxLayout()
        self.notice = QtWidgets.QLabel('Данный модуль не поддерживает автономную работу и функционирует исключительно в рамках процесса аудита.')
        self.notice.setAlignment(QtCore.Qt.AlignCenter)
        self.notice.setStyleSheet('font-weight: bold;')
        self.hbox.addStretch()
        self.hbox.addWidget(self.notice)
        self.hbox.addStretch()
        self.vbox.addStretch()
        self.vbox.addLayout(self.hbox)
        self.vbox.addStretch()
        
        self.setLayout(self.vbox)

    def update(self, message):
        pass

class Log_view(QtWidgets.QWidget):
    addTextSignal = QtCore.pyqtSignal(str)
    def __init__(self, parent = None, controller = None, model = None):
        QtWidgets.QWidget.__init__(self, parent)
        self.controller = controller
        self.logs = QtWidgets.QTextEdit()
        self.logs.setReadOnly(True)
        self.addTextSignal.connect(self.logs.append, QtCore.Qt.QueuedConnection)
        self.vbox = QtWidgets.QVBoxLayout()
        self.vbox.addWidget(self.logs)
        self.setLayout(self.vbox)

    def update(self, str):
        self.addTextSignal.emit(str)

    def prepare(self, callback):
        print('Prepare вызывается')
        self.controller.receive_logs()

class Usage_view(QtWidgets.QWidget):
    def __init__(self, parent = None, controller = None, model = None):
        QtWidgets.QWidget.__init__(self, parent)
        self.controller = controller
        self.parent = parent
        self.toolBox1 = QtWidgets.QToolBox()

        self.toolBox2 = QtWidgets.QToolBox()
        self.toolBox3 = QtWidgets.QToolBox()

        self.tab = QtWidgets.QTabWidget()

        self.tab.addTab(self.toolBox1, 'OWASP')
        self.tab.addTab(self.toolBox2, 'ИБ Сервера')
        self.tab.addTab(self.toolBox3, 'E-Commerce')

        self.vbox = QtWidgets.QVBoxLayout()
        self.vbox.addWidget(self.tab)
        self.setLayout(self.vbox)

        

    def prepare(self, callback):
        self.controller.compose()

    def update(self, message):
        print('MESSAGE')
        pprint(message)

        # label = QtWidgets.QLabel(message['OWASP']['TLS'])
        # label.setWordWrap(True)
        # self.toolBox1.addItem(label, 'TLS')

        for vuln in message['OWASP']:
            print(vuln)
            label = QtWidgets.QLabel(message['OWASP'][vuln])
            label.setWordWrap(True)
            label.setAlignment(QtCore.Qt.AlignLeft)
            self.toolBox1.addItem(label, vuln)

        for vuln in message['SERVER']:
            print(vuln)
            label = QtWidgets.QLabel(message['SERVER'][vuln])
            label.setWordWrap(True)
            label.setAlignment(QtCore.Qt.AlignLeft)
            self.toolBox2.addItem(label, vuln)
            
        for vuln in message['COMMERCE']:
            print(vuln)
            label = QtWidgets.QLabel(message['COMMERCE'][vuln])
            label.setWordWrap(True)
            label.setAlignment(QtCore.Qt.AlignLeft)
            self.toolBox3.addItem(label, vuln)
        all_vulns = len(list(message['OWASP'].items())) + len(list(message['SERVER'].items())) + len(list(message['COMMERCE'].items()))
        self.parent.set_settings({'finded_vulns': all_vulns,
                                        'owasp_vulns_count': len(list(message['OWASP'].items())),
                                        'server_vulns_count': len(list(message['SERVER'].items())),
                                        'commerce_vulns_count': len(list(message['COMMERCE'].items()))})

        self.vbox.repaint()


class Report_view(QtWidgets.QWidget):
    def __init__(self, parent = None, controller = None, model = None):
        QtWidgets.QWidget.__init__(self, parent)
        self.controller = controller

        self.header = QtWidgets.QLabel('Отчет о результатах аудита информационной безопасности:')
        self.header.setStyleSheet('font-weight: bold; font-size: 18px;')
        self.header.setAlignment(QtCore.Qt.AlignCenter)

        self.form1 = QtWidgets.QFormLayout()
        self.form1.setLabelAlignment(QtCore.Qt.AlignLeft)

        self.start_date = QtWidgets.QLabel()
        self.end_time = QtWidgets.QLabel()
        self.url_count = QtWidgets.QLabel()
        self.subdomain = QtWidgets.QLabel()
        self.auth_type = QtWidgets.QLabel()
        self.vulns_count = QtWidgets.QLabel()
        self.finded_vulns = QtWidgets.QLabel()
        self.owasp_vulns_count = QtWidgets.QLabel()
        self.server_vulns_count = QtWidgets.QLabel()
        self.commerce_vulns_count = QtWidgets.QLabel()

    
        self.form1.addRow('Дата и время проведения:', self.start_date)
        self.form1.addRow('Время окончания:', self.end_time)
        self.form1.addRow('URL-адресов найдено:', self.url_count)
        self.form1.addRow('Поддоменов найдено:', self.subdomain)
        self.form1.addRow('Аутентификация:', self.auth_type)
        self.form1.addRow('Искомых уязвимостей:', self.vulns_count)
        self.form1.addRow('Уязвимостей найдено:', self.finded_vulns)
        self.form1.addRow('Из раздела "OWASP":', self.owasp_vulns_count)
        self.form1.addRow('Из раздела "ИБ Сервера":', self.server_vulns_count)
        self.form1.addRow('Из раздела "E-Commerce"', self.commerce_vulns_count)

        self.form2 = QtWidgets.QFormLayout()
        self.form2.setLabelAlignment(QtCore.Qt.AlignLeft)
        self.vulns_label = QtWidgets.QLabel()
        self.vulns_label.setWordWrap(True)
        self.form2.addRow('Проверенные уязвимости:', self.vulns_label)

        self.form_line = QtWidgets.QHBoxLayout()
        self.form_line.addStretch()
        self.form_line.addLayout(self.form1)
        self.form_line.addStretch()
        self.form_line.addLayout(self.form2)
        self.form_line.addStretch()
        



        self.vbox = QtWidgets.QVBoxLayout()
        self.vbox.addWidget(self.header)
        self.vbox.addStretch()
        self.vbox.addLayout(self.form_line)
        self.vbox.addStretch()
        self.setLayout(self.vbox)

    def update(self, message):
        self.start_date.setText(message['start_date'])
        self.end_time.setText(message['end_time'])
        self.url_count.setText(str(message['url_count']))
        self.subdomain.setText(str(message['subdomain']))
        self.auth_type.setText(str(message['auth_type']))
        self.vulns_count.setText(str(message['vulns_count']))
        self.finded_vulns.setText(str(message['finded_vulns']))
        self.owasp_vulns_count.setText(str(message['owasp_vulns_count']))
        self.server_vulns_count.setText(str(message['server_vulns_count']))
        self.commerce_vulns_count.setText(str(message['commerce_vulns_count']))

        self.vulns_label.setText(str(message['vulns']))
        self.repaint()


    def prepare(self, callback):
        print('Prepare представления вызывается')
        self.controller.receive_report()

class Advice_view(QtWidgets.QWidget):
    addTextSignal = QtCore.pyqtSignal(str)
    def __init__(self, parent = None, controller = None, model = None):
        QtWidgets.QWidget.__init__(self, parent)
        self.controller = controller
        # self.advices = QtWidgets.QLabel()
        # self.advices.setWordWrap(True)

        self.text_output = QtWidgets.QTextEdit()
        self.text_output.setReadOnly(True)
        self.addTextSignal.connect(self.text_output.setText, QtCore.Qt.QueuedConnection)
        self.vbox = QtWidgets.QVBoxLayout()
        self.vbox.addWidget(self.text_output)
    
        self.setLayout(self.vbox)

    def update(self, message):
        print('УЖЕ НА СТОРОНЕ ПРЕДСТАВЛЕНИЯ')
        pprint(message)
        text_str = ''
        counter = 1
        for label in message:
            text_str = text_str + '        ' + str(counter) + '). ' + label + '\n        ' + str(message[label]) + '\n'
            counter = counter + 1

        print(text_str)
        #self.box.addLayout(self.scroll_area)
            #self.scroll_area.setBarWidget(text)
        self.addTextSignal.emit(text_str)

        self.repaint()
        

    def prepare(self, callback):
        print('Prepare вызывается')
        self.controller.receive_advices()


class Cookie_settings(QtWidgets.QWidget):
    def __init__(self, parent = None):
        self.inputs = {}
        QtWidgets.QWidget.__init__(self, parent)
        self.parent = parent

        self.vbox = QtWidgets.QVBoxLayout()
        self.hbox = QtWidgets.QHBoxLayout()

        self.label = QtWidgets.QLabel('Количество полей:')
        self.count_input = QtWidgets.QSpinBox()
        self.count_input.setWrapping(True)
        self.count_input.setRange(1, 9)
        self.count_input.setValue(1)
        self.generate_btn = QtWidgets.QPushButton('Сгенерировать')
        self.generate_btn.clicked.connect(self.generate)

        self.fields_vbox = QtWidgets.QVBoxLayout()
        self.frame = QtWidgets.QFrame()
        self.frame.setLayout(self.fields_vbox)
        self.frame.hide()

        self.hbox.addStretch()
        self.hbox.addWidget(self.label)
        self.hbox.addWidget(self.count_input)
        self.hbox.addWidget(self.generate_btn)
        self.hbox.addWidget(self.frame)

        self.hbox.addStretch()

        self.vbox.addStretch()
        self.vbox.addLayout(self.hbox)
        self.vbox.addStretch()

        

        self.setLayout(self.vbox)

    def generate(self):
        
        
        for i in range(0, int(self.count_input.text())):
            self.inputs[i] = ['', '']

            line_box = QtWidgets.QHBoxLayout()
            line_box.addStretch()
            w = QtWidgets.QLineEdit()
            w.textChanged.connect(lambda: self.write(w.text(), i, 0))
            w.setFixedWidth(200)
            line_box.addWidget(w)
            line_box.addWidget(QtWidgets.QLabel(' : '))
            w = QtWidgets.QLineEdit()
            w.textChanged.connect(lambda: self.write(w.text(), i, 1))
            w.setFixedWidth(650)
            line_box.addWidget(w)
            line_box.addStretch()
            self.fields_vbox.addLayout(line_box)

        self.label.setVisible(False)
        self.count_input.setVisible(False)
        self.generate_btn.setVisible(False)
        self.frame.show()
        self.repaint()        

    def write(self, text, line, pos):
        self.inputs[line][pos] = text


    def set_settings(self):
        print('ВТОРАЯ ВКЛАДКА НАСТРОЙКИ ВЫЗЫВАЮТСЯ!!!')
        self.parent.set_settings({'cookies':self.inputs})




import sys
app = QtWidgets.QApplication(sys.argv)
metaScanner = MetaView(MetaController = MetaController, MetaModel = MetaModel)
metaScanner.setWindowTitle("Аудит ИБ")
metaScanner.resize(1000, 600)



def startScanner():
    global metaScanner
    global app
    metaScanner.set_brute_force(label = 'Брутфорс', section = OTHER, view_component = BF_View, controller_component = BF_Controller, model_component = BF_Model, advice = '')
    metaScanner.set_audit_step(label = 'Аудит',section = 'Аудит', view_component = Audit_Step_View, controller_component = Audit_Steps_Controller, model_component = Audit_Steps_Model, advice = '')
    metaScanner.set_audit_step(label = 'Логирование',section = 'Аудит', view_component = Log_view, controller_component = Log_controller, model_component = Log_Model, advice = '')
    metaScanner.set_audit_step(label = 'Эксплуатация',section = 'Аудит', view_component = Usage_view, controller_component = Usage_controller, model_component = Usage_Model, advice = '')
    metaScanner.set_audit_step(label = 'Отчет',section = 'Аудит', view_component = Report_view, controller_component = Report_controller, model_component = Report_Model, advice = '')
    metaScanner.set_audit_step(label = 'Рекомендации',section = 'Аудит', view_component = Advice_view, controller_component = Advice_controller, model_component = Advice_Model, advice = '')
    metaScanner.meta_model.get_model('Веб-краулер').register_observer(metaScanner.bar_agregator)
    metaScanner.meta_model.get_model('Аудит').register_progress_bar(metaScanner.bar_agregator)
    metaScanner.setCentralWidget(metaScanner.stack)
    metaScanner.show()
    sys.exit(app.exec_())

