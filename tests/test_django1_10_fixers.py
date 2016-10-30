from __future__ import absolute_import, print_function, unicode_literals

import os, sys
import pytest

sys.path.append(os.path.dirname(os.path.abspath(__file__)))


def test_fix_deletion_templatetags_future():
    from compat import render_to_string
    from django.templatetags.future import cycle, firstof
    rendered = render_to_string('core_tags/test_future_cycle_and_firstof.html')
    assert rendered.strip() == 'row1\nA'


def test_fix_deletion_template_defaulttags_ssi():
    # already tested in "test_fix_deletion_templatetags_future_ssi()"
    from django.template.defaulttags import ssi
    assert callable(ssi)


def test_fix_behaviour_urls_resolvers_RegexURLPattern():

    from django.core.urlresolvers import RegexURLPattern

    has_lookup_str = hasattr(RegexURLPattern, "lookup_str")

    def dummy_view(request):
        return 72627

    pattern = RegexURLPattern("homepage/", dummy_view)
    assert pattern.callback is dummy_view
    pattern.add_prefix("muyprefix")
    assert pattern.callback is dummy_view
    if has_lookup_str:
        assert pattern.lookup_str == "test_django1_10_fixers.dummy_view"

    pattern = RegexURLPattern("homepage/", "test_project.views.my_view")
    assert pattern.callback.__name__ == "my_view"
    if has_lookup_str:
        assert pattern.lookup_str == "test_project.views.my_view"
    pattern.add_prefix("myprefix")
    with pytest.raises(ImportError):
        pattern.callback  # bad prefix now
    if has_lookup_str:
        # CACHED property so still working!
        assert pattern.lookup_str == "test_project.views.my_view"

    pattern = RegexURLPattern("homepage/", "my_view")
    with pytest.raises(ImportError):
        pattern.callback  # missing prefix
    if has_lookup_str:
        with pytest.raises(ImportError):
            pattern.lookup_str  # missing prefix
    pattern.add_prefix("test_project.views")
    assert pattern.callback.__name__ == "my_view"
    if has_lookup_str:
        assert pattern.lookup_str == "test_project.views.my_view"


def test_fix_behaviour_core_urlresolvers_reverse_with_prefix():
    from django.urls import reverse

    view = reverse("homepage")  # by view name
    assert view == '/homepage/'

    view = reverse("test_project.views.my_view")  # by dotted path
    assert view == "/my_view/"


def test_fix_behaviour_conf_urls_url():
    from django.conf.urls import url
    url(r'^admin2/', "test_project.views.my_view", name="test_admin_abc"),


def test_fix_deletion_conf_urls_patterns():
    import django.conf.urls
    from django.conf.urls import patterns, url
    patterns("admin",
        (r'^admin1/', "test_project.views.my_view"),
        url(r'^admin2/', "test_project.views.my_view", name="test_admin_other"),
    )
    assert "patterns" in django.conf.urls.__all__
