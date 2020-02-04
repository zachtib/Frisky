import importlib
import pkgutil

from frisky.plugin import FriskyPlugin

if __name__ == '__main__':
    for _, module, _ in pkgutil.walk_packages(['plugins']):
        qname = "plugins." + module
        importlib.import_module(qname)
    print(FriskyPlugin.__subclasses__())
