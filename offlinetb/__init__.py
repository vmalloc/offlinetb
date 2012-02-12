from .__version__ import __version__
import linecache
import sys
import types
from platform import python_version

_PY_3 = python_version() >= '3.0'

ERROR_STRING = '[ERROR]'
TOO_LARGE_ERROR_STRING = '[TOO LARGE]'
DEFAULT_LENGTH_LIMIT = 8000

_CANNOT_GET = object()

_FILTERED_TYPES = [types.MethodType, types.FunctionType, type]
if _PY_3:
    basestring = str
    iteritems = dict.items
else:
    _FILTERED_TYPES.append(types.UnboundMethodType)
    _FILTERED_TYPES.append(types.ClassType)
    iteritems = dict.iteritems

def distill(exc_info=None, num_extra_lines=5, var_depth=2, object_length_limit=DEFAULT_LENGTH_LIMIT):
    if exc_info is None:
        exc_info = sys.exc_info()
    exc_type, exc_value, exc_tb = exc_info
    returned = {}
    returned.update(
        exception=dict(
            type=str(exc_type),
            value=_safe_str(exc_value),
            vars=_distill_vars(exc_value, var_depth, object_length_limit)
            ),
        traceback=_distill_traceback(exc_tb, num_extra_lines, var_depth, object_length_limit),
        )
    return returned

def _distill_traceback(tb, num_extra_lines, var_depth, object_length_limit):
    returned = []
    while tb:
        filename = tb.tb_frame.f_code.co_filename
        lineno = tb.tb_frame.f_lineno
        lines = linecache.getlines(filename)
        lines_before, line, lines_after = _splice_lines(lines, lineno-1, num_extra_lines)
        frame = dict(
            filename = filename,
            function = tb.tb_frame.f_code.co_name,
            lineno   = lineno,
            lines_before = lines_before,
            lines_after  = lines_after,
            line = line,
            vars = _distill_vars(tb.tb_frame.f_locals, var_depth, object_length_limit)
            )
        returned.append(frame)
        tb = tb.tb_next
    return returned

def _distill_vars(vars, max_depth, object_length_limit):
    assert max_depth >= 0
    if not max_depth:
        return None
    returned = []
    for name, value in sorted(_get_vars_items(vars)):
        var_dict = dict(name=name)
        if value is _CANNOT_GET:
            var_dict.update(type=ERROR_STRING, value=ERROR_STRING)
        elif _is_object_too_long(value, object_length_limit):
            var_dict.update(type=str(type(value)), value=TOO_LARGE_ERROR_STRING)
        else:
            var_dict.update(type=str(type(value)), value=_safe_repr(value))
            if _can_query_variables(value):
                var_dict.update(vars=_distill_vars(value, max_depth-1, object_length_limit))
        returned.append(var_dict)
    return returned

_SIMPLE_SEQUENCE_TYPES = set([tuple, list, dict, set, frozenset])

def _is_object_too_long(obj, length_limit):
    return type(obj) in _SIMPLE_SEQUENCE_TYPES and len(obj) > length_limit

def _get_vars_items(vars):
    if type(vars) is dict:
        return ((str(k), v) for k, v in iteritems(vars))
    if type(vars) in (tuple, list):
        return ((str(index), value) for index, value in enumerate(vars))
    return _attribute_iterator(vars)
def _attribute_iterator(obj):
    for attr in dir(obj):
        if attr.startswith("__") and attr.endswith("__"):
            continue
        try:
            value = getattr(obj, attr)
        except:
            value = _CANNOT_GET
        if _is_attribute_filtered(value):
            continue
        yield attr, value

def _is_attribute_filtered(attribute_value):
    if any(isinstance(attribute_value, t) for t in _FILTERED_TYPES):
        return True
    return False

def _can_query_variables(var):
    if type(var) in _LEAF_TYPES:
        return False
    if isinstance(var, type):
        return False
    return True

_LEAF_TYPES = set([int, float, str, basestring, bool, types.MethodType, bytes, types.FunctionType])
if not _PY_3:
    _LEAF_TYPES.add(long)
    _LEAF_TYPES.add(unicode)
    _LEAF_TYPES.add(types.UnboundMethodType)

def _splice_lines(lines, pivot, margin):
    return (lines[max(0, pivot-margin):pivot],
            lines[pivot],
            lines[pivot+1:pivot+1+margin])
def _safe_repr(obj):
    try:
        return repr(obj)
    except:
        return ERROR_STRING
def _safe_str(obj):
    try:
        return str(obj)
    except:
        return ERROR_STRING
