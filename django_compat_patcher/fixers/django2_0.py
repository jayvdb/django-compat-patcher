from __future__ import absolute_import, print_function, unicode_literals

from functools import partial

from ..deprecation import *
from ..registry import register_compatibility_fixer

# for backward-compatibility fixers
django1_20_bc_fixer = partial(register_compatibility_fixer,
                              fixer_reference_version="2.0",
                              fixer_applied_from_django="2.0")


# This change should not be patched, since security issues could ensue:
# "Using User.is_authenticated() and User.is_anonymous() as methods rather than properties is no longer supported."

# Preserving mark_for_escaping() and related classes would be complicated and might raise security issues, so it's not done for now.


@django1_20_bc_fixer()
def fix_deletion_django_urls_RegexURLPattern_RegexURLResolver(utils):
    """
    Preserve RegexURLPattern and RegexURLResolver in django.urls, which disappeared due to DEP 0201.
    """
    import django.urls.resolvers
    from django.urls.resolvers import RegexPattern, URLPattern, URLResolver

    class RegexURLPattern(URLPattern):
        def __init__(self, pattern, *args, **kwargs):
            # we force is_endpoint else Warnings about "$" ends in regexes...
            URLPattern.__init__(self, RegexPattern(pattern, is_endpoint=True), *args, **kwargs)

    utils.inject_class(django.urls.resolvers, "RegexURLPattern", RegexURLPattern)
    utils.inject_class(django.urls, "RegexURLPattern", RegexURLPattern)

    class RegexURLResolver(URLResolver):
        def __init__(self, pattern, *args, **kwargs):
            URLResolver.__init__(self, RegexPattern(pattern), *args, **kwargs)
    utils.inject_class(django.urls.resolvers, "RegexURLResolver", RegexURLResolver)
    utils.inject_class(django.urls, "RegexURLResolver", RegexURLResolver)


@django1_20_bc_fixer()
def fix_deletion_django_core_urlresolvers(utils):
    """
    Preserve django.core.urlresolvers module, now replaced by django.urls.
    """
    from django import urls
    utils.inject_module("django.core.urlresolvers", urls)


@django1_20_bc_fixer()
def fix_deletion_django_template_library_assignment_tag(utils):
    """
    Preserve the assignment_tag() helper, superseded by simple_tag().
    """
    import django.template.library

    def assignment_tag(self, func=None, takes_context=None, name=None):
        utils.emit_warning(
            "assignment_tag() is deprecated. Use simple_tag() instead",
            RemovedInDjango20Warning,
            stacklevel=2,
        )
        return self.simple_tag(func, takes_context, name)
    utils.inject_callable(django.template.library.Library, "assignment_tag", assignment_tag)


@django1_20_bc_fixer()
def fix_deletion_django_utils_functional_allow_lazy(utils):
    """
    Preserve the allow_lazy() utility, superseded by keep_lazy().
    """
    import django.utils.functional
    def allow_lazy(func, *resultclasses):
        from django.utils.functional import keep_lazy
        utils.emit_warning(
            "django.utils.functional.allow_lazy() is deprecated in favor of "
            "django.utils.functional.keep_lazy()",
            RemovedInDjango20Warning, 2)
        return keep_lazy(*resultclasses)(func)
    utils.inject_callable(django.utils.functional, "allow_lazy", allow_lazy)


@django1_20_bc_fixer()
def fix_deletion_django_template_context_Context_has_key(utils):
    """
    Preserve the Context.has_key() utility, replaced by "in" operator use.
    """
    import django.template.context
    def has_key(self, key):
        utils.emit_warning(
            "%s.has_key() is deprecated in favor of the 'in' operator." % self.__class__.__name__,
            RemovedInDjango20Warning
        )
        return key in self
    utils.inject_callable(django.template.context.Context, "has_key", has_key)


@django1_20_bc_fixer()
def fix_deletion_django_views_i18n_javascript_and_json_catalog(utils):
    """
    Preserve the javascript_catalog() and json_catalog() i18n views, superseded by class-based views.
    """

    from django_compat_patcher.django_legacy.django2_0.views.i18n import \
        javascript_catalog, json_catalog, render_javascript_catalog, null_javascript_catalog

    import django.views.i18n
    utils.inject_callable(django.views.i18n, "javascript_catalog", javascript_catalog)
    utils.inject_callable(django.views.i18n, "json_catalog", json_catalog)
    utils.inject_callable(django.views.i18n, "render_javascript_catalog", render_javascript_catalog)
    utils.inject_callable(django.views.i18n, "null_javascript_catalog", null_javascript_catalog)


@django1_20_bc_fixer()
def fix_behaviour_django_deb_models_fields_related_ForeignKey_OneToOneField(utils):
    """
    Let "on_delete" parameter of ForeignKey and OneToOneField be optional, defaulting to CASCADE.
    """
    from django.db.models import ForeignKey, OneToOneField, CASCADE

    original_ForeignKey_init = ForeignKey.__dict__["__init__"]

    def __init_ForeignKey__(self, to, on_delete=None, related_name=None, related_query_name=None,
                 limit_choices_to=None, parent_link=False, to_field=None,
                 db_constraint=True, **kwargs):

        if on_delete is None:
            utils.emit_warning(
                "on_delete will be a required arg for %s in Django 2.0. Set "
                "it to models.CASCADE on models and in existing migrations "
                "if you want to maintain the current default behavior. ",
                    RemovedInDjango20Warning, 2)
            on_delete = CASCADE

        original_ForeignKey_init(self, to, on_delete=on_delete, related_name=related_name,
                                 related_query_name=related_query_name, limit_choices_to=limit_choices_to,
                                 parent_link=parent_link, to_field=to_field, db_constraint=db_constraint, **kwargs)

    utils.inject_callable(ForeignKey, "__init__", __init_ForeignKey__)


    original_OneToOneField_init = OneToOneField.__dict__["__init__"]

    def __init_OneToOneField__(self, to, on_delete=None, to_field=None, **kwargs):

        if on_delete is None:
            utils.emit_warning(
                "on_delete will be a required arg for %s in Django 2.0. Set "
                "it to models.CASCADE on models and in existing migrations "
                "if you want to maintain the current default behavior. ",
                    RemovedInDjango20Warning, 2)
            on_delete = CASCADE

        original_OneToOneField_init(self, to, on_delete=on_delete, to_field=to_field, **kwargs)

    utils.inject_callable(OneToOneField, "__init__", __init_OneToOneField__)


@django1_20_bc_fixer()
def fix_behaviour_django_conf_urls_include_3tuples(utils):
    """
    Keep accepting a 3-tuple (urlconf_module, app_name, namespace) as first argument of include(),
    instead of providing namespace argument directly to include()
    """

    from django.core.exceptions import ImproperlyConfigured
    from django.conf.urls import include as original_include

    def include(arg, namespace=None):
        if isinstance(arg, tuple):
            if len(arg) == 3:
                if namespace:
                    raise ImproperlyConfigured(
                        'Cannot override the namespace for a dynamic module that provides a namespace'
                    )
                utils.emit_warning(
                    'Passing a 3-tuple to django.conf.urls.include() is deprecated. '
                    'Pass a 2-tuple containing the list of patterns and app_name, '
                    'and provide the namespace argument to include() instead.',
                    RemovedInDjango20Warning, stacklevel=2
                )
                urlconf_module, app_name, namespace = arg
                arg = (urlconf_module, app_name)
        return original_include(arg, namespace=namespace)

    import django.conf.urls
    utils.inject_callable(django.conf.urls, "include", include)
    import django.urls
    utils.inject_callable(django.urls, "include", include)
