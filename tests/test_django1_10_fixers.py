from __future__ import absolute_import, print_function, unicode_literals

import os, sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))


def test_fix_deletion_templatetags_future():
    from compat import render_to_string
    from django.templatetags.future import cycle, firstof
    rendered = render_to_string('core_tags/test_future_cycle_and_firstof.html')
    assert rendered.strip() == 'row1\nA'


def test_fix_deletion_template_defaulttags_ssi():
    # already tested in "test_fix_deletion_templatetags_future_ssi()"
    from django.template.defaulttags import ssi
