from base import IBase
from lib.Addons.Plugin.Communication.ComSpec import *
from lib.Addons.Plugin.Interface.decorators import *
from lib.Commands.Properties import CSetPropertyValuesCommand
from lib.Domains.Object import CDomainObject

class IDomainObject(IBase):
    __cls__ = None
    
    def GetValue(him, path):
            res = him.GetValue(path)
            if isinstance(res, CDomainObject):
                # TODO: error
                return str(res.GetSaveInfo())
            elif isinstance(res, list):
                # TODO: error
                return '[' + ','.join(str(i.GetSaveInfo()) for i in res) + ']'
            else:
                # TODO: remove str
                return str(res)
    
    def GetAllValues(him):
        def encode(prefix, value):
            if isinstance(value, (str, unicode)):
                yield (prefix, unicode(value))
            elif isinstance(value, dict):
                for k, v in value.iteritems():
                    for i in encode(prefix + k, v):
                        yield i
            elif isinstance(value, list):
                for i, v in enumerate(value):
                    for j in encode(prefix + '[' + str(i) + '].', v):
                        yield j
        
        return list(i for i in encode('',him.GetSaveInfo()))
    
    def GetType(him):
        return him.GetType()
    
    #destructive 
    
    @destructive
    def SetValue(him, command, path, value):
        cmd = CSetPropertyValuesCommand(him, {path: value})
        command.Execute(cmd)