from pathlib import Path
from types import SimpleNamespace
import inspect
import importlib.util


config = None


def load_file(config_name: str = "config.py"):
    global config
    path = Path(config_name)
    if not path.exists():
        raise FileNotFoundError("No config.py file found!")
    spec = importlib.util.spec_from_file_location('config', str(path))
    mod = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(mod)
    except SyntaxError:
        raise Exception("Error loading config file: {}".format(str(path)))
    config = SimpleNamespace(**{k: v for k, v in inspect.getmembers(mod) if k.isupper()})


load_file()
