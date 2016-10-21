"""
This module allows to create aliases between packages, so that one
can import a module under a different name (mainly for retrocompatibility purpose).

There are different ways of implementing "import aliases":

- replacing __import__ (ugly but efficient)
- using a custom module loader which creates a wrapper class (with setattr,
  getattr etc...), and injects it as a proxy in sys.modules[alias]
- using a custom module loader, which simply copies a reference to the real module
  into sys.modules (and updates its __spec__ to gives hints about this operation).
  => THIS IS THE WAY WE DO IT.

Beware about not creating loops with your aliases, as this could trigger infinite recursions.

"""

import os, sys
import importlib.machinery, importlib.abc


MODULES_ALIASES_REGISTRY = [
                            ]

def register_module_alias(module_alias, real_module):
    assert not module_alias.startswith("."), module_alias
    assert not real_module.startswith("."), real_module
    entry = (module_alias, real_module)
    if entry not in MODULES_ALIASES_REGISTRY:
        MODULES_ALIASES_REGISTRY.append(entry)
        return True
    return False

def _get_module_alias(fullname):
    for k, v in MODULES_ALIASES_REGISTRY:
        if (k == fullname) or fullname.startswith( k +"."):
            return fullname.replace(k, v)
    return None


class AliasingLoader(importlib.abc.Loader):

    target_spec_backup = None

    def __init__(self, alias_name):
        self.alias_name = alias_name

    def create_module(self, spec):
        # we do the real loading of aliased module here
        module = importlib.import_module(self.alias_name, package=None)
        assert module.__name__ == self.alias_name, module.__name__
        self.target_spec_backup = module.__spec__
        return module

    def exec_module(self, module):
        # __name__ was overridden by init_module_attrs(_force_name=True)
        assert module.__name__ != self.alias_name, module.__name__
        module.__name__ = self.alias_name
        assert module.__spec__.origin == "alias", module.__spec__  # well overridden
        assert module.__spec__.loader_state["aliased_spec"] is None
        assert self.target_spec_backup, self.target_spec_backup
        module.__spec__.loader_state["aliased_spec"] = self.target_spec_backup
        pass  # nothing else to do, module already loaded


class ModuleAliasFinder(importlib.abc.MetaPathFinder):
    """
    Note : due to new call of _init_module_attrs(spec...) on aliased
    module, its __spec__ attribute will be changed by this new import...
    """

    @classmethod
    def find_spec(cls, fullname, *args, **kwargs):
        #print("PathAliasFinder FINDSPEC", fullname, args, kwargs)
        alias_name = _get_module_alias(fullname)
        if alias_name is None:
            return None  # no alias module is known

        alias_loader = AliasingLoader(alias_name=alias_name)

        spec = importlib.machinery.ModuleSpec(name=fullname,
                                       loader=alias_loader,
                                       origin="alias",
                                       loader_state={"aliased_name": alias_name,
                                                     "aliased_spec": None},
                                       is_package=True)  # in doubt, assume...

        return spec


def install_module_alias_finder():
    """
    Add a meta path hook before all others, so that new module loadings
    may be redirected to aliased module.
    """
    assert ModuleAliasFinder not in sys.meta_path, sys.meta_path
    sys.meta_path.insert(0, ModuleAliasFinder)



if __name__ == "__main__":

    import logging.handlers

    install_module_alias_finder()

    register_module_alias("json.comments", "json.tool")
    register_module_alias("mylogging", "logging")
    register_module_alias("infinite_recursion", "infinite_recursion")

    fullname = "logging.handlers"
    print ("ALREADY THERE:", fullname, fullname in sys.modules)

    import json.comments

    fullname = "json.comments"
    print ("ALREADY THERE:", fullname, fullname in sys.modules)

    fullname = "json.tool"
    print ("ALREADY THERE:", fullname, fullname in sys.modules)

    import json.tool
    print ("JSON TOOL SPEC", json.tool.__spec__.loader_state)

    assert json.comments is json.tool, (json.comments,  json.tool)
    assert json.tool.__spec__.origin == "alias", json.tool.__spec__.origin
    assert json.tool.__name__ == "json.tool", json.tool.__name__

    from mylogging import config
    assert config.dictConfig
    assert "logging.config" in sys.modules

    from mylogging.handlers import RotatingFileHandler
    from logging.handlers import RotatingFileHandler as RotatingFileHandlerOriginal
    print("mylogging led to RotatingFileHandler", RotatingFileHandler)
    assert RotatingFileHandler is RotatingFileHandlerOriginal

    try:
        import infinite_recursion
    except RuntimeError:
        pass
    else:
        raise RuntimeError("Import should have led to infinite recursion")