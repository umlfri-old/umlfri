from base import IBase
from lib.Addons.Plugin.Communication.ComSpec import *
from lib.Addons.Plugin.Interface.decorators import *
from lib.Gui.GuiManager import CGuiManager

class IGuiManager(IBase):
    __cls__ = CGuiManager
    
    def GetMainMenu(him):
        return him.GetMainMenu()
        
    def GetTabMenu(him):
        return him.GetTabMenu()
        
    def GetTreeMenu(him):
        return him.GetTreeMenu()
    
    def GetDrawMenu(him):
        return him.GetDrawMenu()
    
    def GetButtonBar(him):
        return him.GetButtonBar()
    
    def DisplayWarning(him, text):
        him.DisplayWarning(text)
