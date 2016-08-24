import pytest
import warnings

import offlinetb


def test_capture_warnings(recwarn):
    warnings.simplefilter('always')
    try:
        f()
    except CustomException:
        tb = offlinetb.distill(var_depth=4)

    [v] = [v for v in tb['traceback'][-1]['vars'] if v['name'] == 's']
    assert v['vars'][0]['value'] == "'hi'"
    assert len(recwarn) == 0


def f():
    g()


def g():
    class Something(object):

        @property
        def prop(self):
            warnings.warn('deprecated', DeprecationWarning)
            return 'hi'
    s = Something()             # pylint: disable=unused-variable
    raise CustomException()


class CustomException(Exception):
    pass
