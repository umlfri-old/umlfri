from lib.Base import CBaseObject

class CSelectableObject(CBaseObject):
    '''Implements interface for selecting visible object'''
    def __init__(self):
        self.selected = False
        
    def Select(self):
        '''Set internal "selected" flag to True'''
        self.selected = True
    
    def Deselect(self):
        '''Set internal "selected" flag to False and call self.DeselectPoint'''
        self.selected = False
    
    def GetSelected(self):
        '''
        @return: state of "selected" flag
        @rtype:  bool
        '''
        return self.selected
        