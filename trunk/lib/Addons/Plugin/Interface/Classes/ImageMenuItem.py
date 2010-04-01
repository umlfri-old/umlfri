import lib.GenericGui
from lib.Depend.gtk2 import gtk
from MenuItem import IMenuItem
from lib.Addons.Plugin.Communication.ComSpec import *

class IImageMenuItem(IMenuItem):
    
    __cls__ = lib.GenericGui.CImageMenuItem
    
    @result(r_none)
    @parameter('filename', t_str)
    @mainthread
    def SetImageFromFile(him, filename):
        him.SetImageFromFile(filename)
