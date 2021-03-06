===============================================================
Django-compat-patcher warmly welcomes new fixers, and bugfixes
===============================================================

.. sectnum::

See "django_deprecation_timeline_notes.rst" for a list of breaking changes in Django history, and their current status in DCP.

Fixers should not be created to modify project-level code, like django settings, since these are supposed to be easily updatable by project maintainers.

Also, they should not reintroduce features which expose servers to serious security issues (like XSS attacks...), unless project maintainers can workaround these issues by a careful use of these features.


Recommendations
=================

The code must be very DRY, to minimize bugs, and so that future evolutions of this library are as painless as possible.

It must be self-documented, using decorator arguments and docstrings (we do NOT maintain a separate list of what fixers are available).

It must also be as robust as possible - this lib is supposed to workaround breakages, not introduce new ones.

Technically speaking:

- in fixers : don't do logging or warnings by yourself, use the injected :code:`utils` object instead
- also use functions from this :code:`utils` object, to patch django code, not direct assignments
- don't do global imports of django submodules or external libraries, import them from inside fixers instead
- respect python/django standards for naming objects, spacings, etc.
- make code py2/py3 compatible by using :code:`django.utils.six`, and :code:`__future__` imports in all python files


Code style
============

PEP8 is mostly respected, although for commodity, we have to enforce specific rules here and there.

Fixers
######

Name
------

- Fixers have to be decorated using :code:`register_compatibility_fixer` and the like (found in :code:`registry.py`). Hint: you can be DRY using :code:`functools.partial`
- Fixers are named using the following syntax: :code:`fix_<kind>_<path>_<element>(<utils>, \*args, \*\*kwargs)`

    - :code:`<kind>` is one of the following :
        - deletion
        - behavior
        - outsourcing

    - :code:`<path>` is the path of the module starting from 'django', but not including it
    - :code:`<element>` is the element to be patched ; you have to use the same CASE as the original element
    - :code:`<utils>` is an injected parameter, with utility functions

Example
---------

Patching the removal of the :code:`get_formsets()` method from django's :code:`ModelAdmin` (located in :code:`django.contrib.admin`):

    :code:`fix_deletion_contrib_admin_ModelAdmin_get_formsets`

- Tests for fixers use :code:`fix_<fixer_name>`
- Every fixer must have a docstring explaining what it does (what breaking changes it deals with)


Testing
=========

Simply install and run the "tox" python tool, from the root folder of the repository.

