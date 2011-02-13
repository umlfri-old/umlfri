from Container import IContainer
from lib.GenericGui import CButtonBar
from lib.Addons.Plugin.Communication.ComSpec import *
from lib.Addons.Plugin.Interface.decorators import *

class IButtonBar(IContainer):
    
    __cls__ = CButtonBar
    
    @mainthread
    @includeAddr
    def AddButton(him, guiId, callback, position, label, imagefilename=None, togglebutton=False, _addr=None):
        return him.AddButton(guiId, callback, position, label, imagefilename, togglebutton, _addr)
        
    @mainthread
    @includeAddr
    def AddStockButton(him, guiId, callback, position, stock, label=None, togglebutton=False, _addr=None):
        return him.AddStockButton(guiId, callback, position, stock, label, togglebutton, _addr)
    
    @mainthread
    @includeAddr
    def AddSeparator(him, guiId, position, _addr=None):
        return him.AddSeparator(guiId, position, _addr)
