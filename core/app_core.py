Traceback (most recent call last):
  File "<frozen runpy>", line 189, in _run_module_as_main
  File "<frozen runpy>", line 112, in _get_module_details
  File "E:\APP\qumail\__init__.py", line 11, in <module>
    from .main import main
  File "E:\APP\qumail\main.py", line 19, in <module>
    from .core.app_core import QuMailCore
  File "E:\APP\qumail\core\__init__.py", line 6, in <module>
    from .app_core import QuMailCore
  File "E:\APP\qumail\core\app_core.py", line 21, in <module>
    from ..transport.email_handler import EmailHandler
  File "E:\APP\qumail\transport\email_handler.py", line 27, in <module>
    from utils.config import load_config
ModuleNotFoundError: No module named 'utils'

E:\APP>
