import re
from lib.Addons.Plugin.Interface import Reference
from lib.Addons.Plugin.Interface.decorators import *
from lib.Addons.Plugin.Interface.meta import Meta
from lib.Addons.Plugin.Client import classes


IDENTIFIER = 'UML.FRI'
VERSION = '0.1'
FIRST_LINE_PLUGIN = re.compile(r'(?P<command>\w+) +(?P<type>[\w#:.]+) +%s/(?P<version>\d+\.\d+)\r?$' % IDENTIFIER)
FIRST_LINE_MAIN = re.compile(r'%s/(?P<version>\d+\.\d+) +(?P<code>\d{3})( (?P<text>[ \w]+))?\r?$' % IDENTIFIER)
PARAM_LINE = re.compile(r'(?P<key>[A-Za-z_]\w*): *(?P<value>[^\r\n]+)\r?$')
EMPTY_LINE = re.compile(r'(\r|\n|\r\n)$')

RESP_NOTIFY = 100
RESP_GUI_ACTIVATED = 101
RESP_DOMAIN_VALUE_CHANGED = 102
RESP_FINALIZE = 103


RESP_OK = 200
RESP_GUI_ADDED = 201
RESP_GUI_SENSITIVE = 202
RESP_GUI_INSENSITIVE = 203
RESP_METAMODEL_DESCRIPTION = 204
RESP_RESULT = 205

RESP_UNKONWN_COMMAND = 400
RESP_UNSUPPORTED_VERSION = 401
RESP_INVALID_COMMAND_TYPE = 402
RESP_MISSING_PARAMETER = 403
RESP_INVALID_PARAMETER = 404
RESP_INVALID_OBJECT = 405
RESP_UNKNOWN_METHOD = 406
RESP_PROJECT_NOT_LOADED = 407
RESP_UNKNOWN_CONSTRUCTOR = 408
RESP_TRANSACTION_PENDING = 409
RESP_OUT_OF_TRANSACTION = 410
RESP_TRANSACTION_MODE_UNSPECIFIED = 411

RESP_UNHANDELED_EXCEPTION = 500

def tc_object(val, conn = None):
    return val.GetId()

def t_2intTuple(val, conn = None):
    try:
        assert len(x) > 4 and x[0] == '(' and x[-1] == ')'
        result = tuple(int(i)for i in x[1:-1].split(','))
        assert len(result) == 2
        return result
    except (AssertionError, ):
        raise ValueError()

@reverse(tc_object)
def t_object(val, conn = None):
    if val == 'project':
        return Reference.GetProject()
    elif re.match(r'#[0-9]+$', val) is not None:
        return Reference.GetObject(int(val[1:]))
    elif val == 'None':
        return None
    else:
        match = re.match(r'[ ]*(?P<clsname>[a-zA-Z][a-zA-Z0-9_]+)[(](?P<params>.*)[)][ ]*$', val)
        if match is not None and Meta.HasConstructor(match.groupdict()['clsname']):
            paramstr = match.groupdict()['params']
            braces = {'(': 0, '[': 0, '{': 0}
            reverse = {')':'(', ']':'[', '}':'{'}
            splits = [-1]
            for i, c in enumerate(paramstr):
                if c == ',' and all(j == 0 for j in braces.itervalues()):
                    splits.append(i)
                elif c in braces:
                    braces[c] += 1
                elif c in reverse:
                    braces[reverse[c]] -= 1
            splits.append(len(paramstr))
            params = []
            for i in xrange(1, len(splits)):
                params.append(paramstr[splits[i - 1] + 1 : splits[i]])
            return Meta.Create(match.groupdict()['clsname'], params)
        else:
            raise ValueError()

@reverse(tc_object)
def t_classobject(cls):
    def check(val, conn = None):
        res = t_object(val)
        if isinstance(res, cls):
            return res
        else:
            raise ValueError()
    return check

def t_bool(val, conn = None):
    if val == 'True':
        return True
    elif val == 'False':
        return False
    else:
        raise ValueError()

def t_str(val, conn = None):
    return str(val)

t_str = reverse(t_str)(t_str)
r_str = t_str

def t_elementType(val, conn = None):
    try:
        f = Reference.GetProject().GetMetamodel().GetElementFactory()
        if f.HasType(val):
            return f.GetElement(val)
        else:
            raise ValueError()
    except AttributeError:
        raise ValueError()

def t_2x2intTuple(val, conn = None):
    match = re.match(r'\(\((?P<a>[0-9]+),(?P<b>[0-9]+)\),\((?P<c>[0-9]+),(?P<d>[0-9]+)\)\)$', val)
    if match is not None:
        d = match.groupdict()
        return ((int(d['a']), int(d['b'])), (int(d['c']), int(d['d'])))
    else:
        raise ValueError()

def rc_object(val, connection):
    return classes[connection.Execute('exec', val+'.GetClass', {})()](val, connection)
    
def rc_objectlist(val, connection):
    return [rc_object(i, connection) for i in val[1:-1].split(',') if i != '']
    

@reverse(rc_object)
def r_object(val, conn = None):
    return '#%i' % (val.GetPluginId(), ) if val is not None else 'None'

@reverse(rc_objectlist)
def r_objectlist(val, conn = None):
    return '[' + ','.join(r_object(i) for i in val) + ']'

@reverse(t_bool)
def r_bool(val, conn = None):
    return str(bool(val))

t_bool = reverse(r_bool)(t_bool)

@reverse(t_2intTuple)
def r_2intTuple(val, conn = None):
    assert type(val) == tuple and len(val) == 2 and all(type(i) == int for i in val)
    return '(%i,%i)' % val
    
t_2intTuple = reverse(r_2intTuple)(t_2intTuple)

@reverse(t_2x2intTuple)
def r_2x2intTuple(val, conn = None):
    return '((%i,%i),(%i,%i))' % (val[0] + val[1])

t_2x2intTuple = reverse(r_2x2intTuple)

@reverse(lambda val, conn = None: None)
def r_none(val, conn = None):
    if val is None:
        return 'None'
    else:
        raise ValueError()

def rc_eval(val, con=None):
    return eval(val, {}, {'__builtins__': {}})
    
@reverse(rc_eval)
def r_eval(val, con=None):
    return str(val)
