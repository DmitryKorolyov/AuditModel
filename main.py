from brut_force_mvc import *
from crawler_mvc import Crawler_Controller, Crawler_Model, Crawler_View
from view import *
from config import *
from tls_mvc import *
from wpt_retranslator import *
from port_scanner_mvc import *

from xss_mvc import *

from signal import signal, SIGPIPE, SIG_DFL  
signal(SIGPIPE,SIG_DFL)

# ДОБАВЛЕНИЕ НОВЫХ МОДУЛЕЙ
# ИСПОЛЬЗОВАТЬ:
# metaScanner.set_component(label, section, view_component, controller_component, model_componet)
# metaScanner.set_component(label, section, view_component)
metaScanner.set_hook(label = 'WPT_Store', hook = WPT_Store)
metaScanner.set_hook(label = 'WPT_Hook', hook = WPT_Hook)

metaScanner.set_component(label = 'Secure Flag cookie', section = OWASP_SECTION, view_component = Plug_View, controller_component = Plug_Controller, model_component = WPT_Certain_model, advice = 'Secure - один из атрибутов, устанавливающихся сервером для управления обработкой cookies на стороне клиента. Флаг secure, установленный в Secure, разрешает передачу cookie только по безопасному каналу. В частности, при установленном флаге cookie не будет передаваться по протоколу HTTP, но будет по HTTPS. По умолчанию флаг не установлен. Без флага Secure в заголовке HTTP-ответа можно украсть или обработать сеанс веб-приложения и файлы cookie. Хорошая практика – установить флаг Secure в код приложения разработчика.')
metaScanner.set_component(label = 'XSS', section = OWASP_SECTION, view_component = XSS_Scanner_View, controller_component = XSS_Controller, model_component = XSS_Scanner_Model, advice = 'Основные превентивные меры:\n - валидация данных\n - преобразование вывода\n    На практике это должно быть реализовано в виде:\n - исключения всех недоверенных данных из контекста (body, атрибуты, JavaScript, CSS или URL);\n - использование "белых списков" на строне сервера (проверка длины, формата, логики и.д.);\n - использование специализированных средств очистки данных (OWASP AntiSamy или Java HTML Sanitizer Project);\n - использование атрибута HttpOnly;\n - использование Content Security Policy.')
metaScanner.set_component(label = 'Internal Server Error', section = SERVER_SECTION, view_component = Plug_View, controller_component = Plug_Controller, model_component = WPT_Certain_model, advice = 'Internal server error может быть вызвана несколькими проблемами. Вот основные из них:\n - Ошибки в скрипте на PHP - одна из самых частых причин\n - Превышено время выполнения PHP скрипта или лимит памяти\n - Неправильные права на файлы сайтn\n - Неверная конфигурация Nginx')
metaScanner.set_component(label = 'Сканирование портов', section = SERVER_SECTION, view_component = Plug_View, controller_component = Plug_Controller, model_component = Port_Scanner_Model, advice = 'Следует оставлять открытыми порты, необходимые для работы ресурса. Подключение критическим портам должно осуществляться только после аутентификации. Все остальные порты следует держать закрытыми.')
metaScanner.set_component(label = 'SQL', section = OWASP_SECTION, view_component = SQL_Scanner_View, controller_component = SQL_Controller, model_component = SQL_Scanner_Model, advice = 'Предотвращение SQL-инъекций возможно при выполнении следующих пунктов:\n - Использование белых списков, представляющих собой допустимые ключи и значения;\n - Отказ от использования метода GET в формах;\n - Санитизация переменных(экранирование кавычек, замена служебных символов и т.д.\n - Проверка источника пришедших данных;\n - Использование PDO.')
metaScanner.set_component(label = 'HTTP Secure Headers', section = OWASP_SECTION, view_component = Plug_View, controller_component = Plug_Controller, model_component = WPT_Certain_model, advice = ' - Используйте X-Frame-Options для предотвращения встраивания вашего документа в другие приложения;\n - Используйте CORP для предотвращения возможности использования ресурсов вашего сайта другими источниками;\n - Используйте COOP для защиты вашего приложения от взаимодействия с другими приложениями;\n - Используйте CORS для управления доступом к ресурсам вашего сайта из других источников.')
metaScanner.set_component(label = 'HttpOnly Flag cookie', section = OWASP_SECTION, view_component = Plug_View, controller_component = Plug_Controller, model_component = WPT_Certain_model, advice = 'Установить флаг HttpOnly в заголовке HTTP-ответа')
metaScanner.set_component(label = 'TLS', section = OWASP_SECTION, view_component = TLS_View, controller_component = TLS_Controller, model_component = TLS_Model, advice = 'Необходимо получение сервером SSL-сертификата, версия протокола TLS в котором не ниже 1.2. Данный сертификат должен быть подписан доверенным центром сертификации.')

metaScanner.set_component(label = 'Thread_test', section = OTHER, view_component = TLS_Scanner1, controller_component = Controller1, model_component = Scanner1Model, advice = '')
metaScanner.set_component(label = 'Веб-краулер', section = OTHER, view_component = Crawler_View, controller_component = Crawler_Controller, model_component = Crawler_Model, advice = '')

metaScanner.set_component(label = 'XML External Entity', section = COMMERCE_SECTION, view_component = Plug_View, controller_component = Plug_Controller, model_component = WPT_Certain_model, advice = 'Атаки XXE можно предотвратить с помощью: \n - Использование менее сложных форматов данных, таких как JSON; \n - Обновление процессоров и библиотек XML; \n - Использование инструментов SAST.')
metaScanner.set_component(label = 'TLS Эквайера', section = COMMERCE_SECTION, view_component = TLS_View, controller_component = TLS_Controller, model_component = TLS_Model, advice = 'Необходимо получение сервером SSL-сертификата, версия протокола TLS в котором не ниже 1.2. Данный сертификат должен быть подписан доверенным центром сертификации.')

metaScanner.set_settings_tab(label = 'Cookie', view = Cookie_settings)
#metaScanner.set_component(label = 'Брутфорс', section = OTHER, view_component = BF_View, controller_component = BF_Controller, model_componet = BF_Model)

#print('В ГЛАВНОМ ФАЙЛЕ: ' + metaScanner.meta_model.get_model('Веб-краулер').label)






startScanner()
