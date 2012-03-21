from ast import literal_eval
import itertools
import os
import platform
from json import JSONDecoder, JSONEncoder
try:
    from unittest2 import TestCase
except ImportError:
    from unittest import TestCase

from offlinetb import (
    distill,
    _splice_lines,
    ERROR_STRING,
    DEFAULT_LENGTH_LIMIT,
    TOO_LARGE_ERROR_STRING,
    )

_PY_3 = platform.python_version() >= '3.0'
if _PY_3:
    basestring = str
    unicode = str
    long = int

class OfflineTbTest(TestCase):
    def setUp(self):
        super(OfflineTbTest, self).setUp()
        try:
            f()
        except SomeException:
            self.offlinetb = distill(var_depth=4)
        validate_schema(self.offlinetb)
        self.tb = self.offlinetb['traceback']
        self.f_frame = self.tb[-2]
        self.g_frame = self.tb[-1]
        self.obj = self._find_var_by_name(self.f_frame['vars'], 'obj')
        self.oldstyle_obj = self._find_var_by_name(self.f_frame['vars'], 'oldstyle_obj')
    def test__depth(self):
        self.assertGreater(len(self.tb), 2)
    def test__last_function_at_bottom(self):
        self.assertEquals(self.tb[-1]['function'], 'g')
        self.assertEquals(self.tb[-2]['function'], 'f')
    def test__line(self):
        self.assertEquals(self.tb[-2]['line'].rstrip(), '    g()')
    def test__linesbefore_linesafter(self):

        self.assertEquals(self.g_frame['lines_before'][-2].rstrip(), '    g_linebefore_1')
        self.assertEquals(self.g_frame['lines_before'][-1].rstrip(), '    g_linebefore_2')
        self.assertEquals(self.g_frame['lines_after'][0].rstrip(),   '    g_lineafter_1')
        self.assertEquals(self.g_frame['lines_after'][1].rstrip(),   '    g_lineafter_2')
        self.assertEquals(self.f_frame['lines_before'][-2].rstrip(), '    f_linebefore_1')
        self.assertEquals(self.f_frame['lines_before'][-1].rstrip(), '    f_linebefore_2')
        self.assertEquals(self.f_frame['lines_after'][0].rstrip(),   '    f_lineafter_1')
        self.assertEquals(self.f_frame['lines_after'][1].rstrip(),   '    f_lineafter_2')
    def test__simple_variables(self):
        v = self._find_var_by_name(self.f_frame['vars'], 'f_value1')
        self.assertValue(v, F_VALUE1)
    def test__object_variables(self):
        self.assertEquals(self.obj['type'], repr(Object))
        self.assertEquals(self.obj['value'], repr(Object()))
        value = self._find_var_by_name(self.obj['vars'], '_value')
        self.assertValue(value, OBJ_VALUE)
        self.assertEqual(set([subvar['name'] for subvar in self.obj['vars']]),
                         set(['_value', '_subobj1', 'regular_property', 'ungettable_property', 'nested']))
    def test__properties(self):
        for obj in (self.obj, self.oldstyle_obj):
            attr = self._find_var_by_name(obj['vars'], 'regular_property')
            self.assertValue(attr, REGULAR_PROPERTY_VALUE)
    def test__ungettable_attributes(self):
        attr = self._find_var_by_name(self.obj['vars'], 'ungettable_property')
        for field in ['type', 'value']:
            self.assertEquals(attr[field], ERROR_STRING)
    def test__no_methods(self):
        for variable_name in self._traverse_variable_names():
            self.assertNotIn('method', variable_name)
    def test__nesting_limit(self):
        v = self._find_var_by_name(self.f_frame['vars'], 'obj', 'nested', 'very', 'deeply')
        self.assertIsNone(v['vars'])
    def test__types_have_no_vars(self):
        v = self._find_var_by_name(self.g_frame['vars'], 'some_type')
        self.assertNotIn('vars', v)
    def test__lists(self):
        v = self._find_var_by_name(self.g_frame['vars'], 'some_list')
        self.assertEquals([var['name'] for var in v['vars']], [str(i) for i in range(NUM_ITEMS_IN_LIST)])
        for index, var in enumerate(v['vars']):
            self.assertEquals(var['type'], str(Object))
            value = self._find_var_by_name(var['vars'], 'value')
            self.assertValue(value, index)
    def test__nonprintable_objects(self):
        v = self._find_var_by_name(self.g_frame['vars'], 'some_unprintable_obj')
        self.assertEquals(v['value'], ERROR_STRING)
        self.assertEquals(v['type'], repr(NonPrintable))
    def test__nondirable_objects(self):
        with self.assertRaises(NotImplementedError):
            dir(NonDirable())
        v = self._find_var_by_name(self.f_frame['vars'], 'nondirable')
        self.assertEquals(v['vars'], [])
    def test__size_limit(self):
        v = self._find_var_by_name(self.g_frame['vars'], 'too_large')
        self.assertEquals(v['value'], TOO_LARGE_ERROR_STRING)
        self.assertNotIn('vars', v)
    def assertValue(self, var, value):
        self.assertEquals(var['type'], repr(type(value)))
        self.assertEquals(literal_eval(var['value']), value)
        self.assertNotIn('vars', var)
    def _get_vars_as_dict(self, vars):
        return dict((var['name'], var) for var in vars)
    def _traverse_variable_names(self):
        return itertools.chain.from_iterable(
            self._traverse_vars_variable_names(tb_frame['vars'])
            for tb_frame in self.tb
            )
    def _traverse_vars_variable_names(self, vars):
        if vars == '...':
            return
        for var in vars:
            assert isinstance(var['name'], basestring)
            yield var['name']
            subvars = var.get('vars', [])
            if subvars is not None:
                for x in self._traverse_vars_variable_names(subvars):
                    yield x
    def _find_var_by_name(self, vars, *names):
        self.assertIsInstance(vars, list)
        returned = None
        for name in names:
            for variable in vars:
                if variable['name'] == name:
                    returned = variable
                    vars = variable.get('vars', None)
        if returned is None:
            self.fail("Not found")
        return returned

class RenderingExampleTest(TestCase):
    def setUp(self):
        super(RenderingExampleTest, self).setUp()
        with open(os.path.join(os.path.dirname(__file__), "..", "rendering", "example_offline_tb.js")) as f:
            self.data = f.read().split("=", 1)[-1].strip()
        assert self.data.endswith(";")
        self.data = self.data[:-1]
    def test__validates(self):
        decoded = JSONDecoder().decode(self.data)
        validate_schema(decoded)

class NonPrintableExceptionTest(TestCase):
    def setUp(self):
        super(NonPrintableExceptionTest, self).setUp()
        try:
            raise NonPrintableException()
        except NonPrintableException:
            self.offlinetb = distill()
    def test__non_printable_exception(self):
        self.assertEquals(self.offlinetb['exception']['value'], ERROR_STRING)

class NonPrintableException(Exception):
    def __repr__(self):
        raise Exception("!")
    def __str__(self):
        raise Exception("!!")

class LineSpliceTest(TestCase):
    def setUp(self):
        super(LineSpliceTest, self).setUp()
        self.nums = list(range(1, 11))
    def test__linesplice(self):
        self.assertEquals(_splice_lines(self.nums, 4, 2), ([3, 4], 5, [6, 7]))
        self.assertEquals(_splice_lines(self.nums, 1, 2), ([1], 2, [3, 4]))
        self.assertEquals(_splice_lines(self.nums, 1, 10), ([1], 2, [3, 4, 5, 6, 7, 8, 9, 10]))
        self.assertEquals(_splice_lines([], 5, 20), ([], "<missing line>", []))

def validate_schema(tb):
    assert type(tb) is dict
    assert set(tb) == set(['exception', 'traceback'])
    assert set(tb['exception']) == set(['type', 'value', 'vars'])
    _validate_types(tb)
    for tb_frame in tb['traceback']:
        _validate_tb_frame_schema(tb_frame)
    JSONEncoder().encode(tb) # should work
def _validate_types(d):
    for key, value in d.items():
        assert isinstance(key, basestring)
        assert type(value) in (int, long, str, unicode, float, type(None), list, dict)
        if type(value) is dict:
            _validate_types(value)
def _validate_tb_frame_schema(tb_frame):
    assert set(tb_frame) - set(['vars']) == set(['function', 'filename', 'lines_before', 'lines_after', 'line', 'lineno'])
    if 'vars' in tb_frame:
        _validate_vars_schema(tb_frame['vars'])

def _validate_vars_schema(vars):
    assert type(vars) is list or vars is None
    if vars is not None:
        for variable in vars:
            _validate_var_schema(variable)

def _validate_var_schema(variable):
    assert set(variable) - set(['vars']) == set(['name', 'type', 'value'])
    _validate_vars_schema(variable.get('vars', None))
    assert isinstance(variable['type'], basestring)

class Object(object):
    def __init__(self, **attrs):
        super(Object, self).__init__()
        for attr, value in attrs.items():
            setattr(self, attr, value)
    def __repr__(self):
        return 'this is the object repr'
    def __str__(self):
        return 'this is the object str'
    def regular_method(self):
        pass
    @staticmethod
    def static_method():
        pass
    @classmethod
    def class_method():
        pass
    @property
    def regular_property(self):
        return REGULAR_PROPERTY_VALUE
    @property
    def ungettable_property(self):
        raise NotImplementedError() # pragma: no cover

TOO_LARGE_OBJECT = list(range(DEFAULT_LENGTH_LIMIT + 1))

F_VALUE1, OBJ_VALUE, OLDSTYLE_OBJ_VALUE, REGULAR_PROPERTY_VALUE = range(4)
NUM_ITEMS_IN_LIST = 5

class OldStyleObj:
    def __init__(self, **attrs):
        for attr, value in attrs.items():
            setattr(self, attr, value)
    def __repr__(self):
        return 'this is the object repr'
    def __str__(self):
        return 'this is the object str'
    def regular_method(self):
        pass
    @staticmethod
    def static_method():
        pass
    @classmethod
    def class_method():
        pass
    @property
    def regular_property(self):
        return REGULAR_PROPERTY_VALUE
    @property
    def ungettable_property(self):
        raise NotImplementedError() # pragma: no cover


class LengthThrowsException(object):
    def __len__(self):
        raise Exception("!")

class NonPrintable(object):
    def __repr__(self):
        raise Exception("!")

class NonDirable(object):
    def __dir__(self):
        raise NotImplementedError() # pragma: no cover

def f():
    with_raising_len = LengthThrowsException()
    f_linebefore_2 = f_linebefore_1 = 0
    f_value1 = F_VALUE1
    obj = Object(
        _subobj1 = Object(),
        _value   = OBJ_VALUE,
        nested = Object(
            very = Object(
                deeply = Object(
                    indeed = "bla"
                    )
                )
            )
        )
    unicode_variable = unicode("hello")
    boolean = True
    nondirable = NonDirable()
    oldstyle_obj = OldStyleObj(value=OLDSTYLE_OBJ_VALUE)
    f_linebefore_1
    f_linebefore_2
    g()
    f_lineafter_1
    f_lineafter_2

def g():
    some_type = SomeException
    too_large = TOO_LARGE_OBJECT
    some_list = [Object(value=i) for i in range(NUM_ITEMS_IN_LIST)]
    some_unprintable_obj = NonPrintable()
    g_linebefore_1 = g_linebefore_2 = 0
    g_linebefore_1
    g_linebefore_2
    raise SomeException("exception_string")
    g_lineafter_1
    g_lineafter_2

class SomeException(Exception):
    pass
