from Line import CConnectionLine
from Arrow import CConnectionArrow
from math import atan2
from lib.Exceptions.UserException import *

class CConnectionType(object):
    """
    Contains part of metamodel that represents connection type
    """
    def __init__(self, id, line = None, scrArrow = None, destArrow = None, icon = None, domain = None):
        """
        Initialize connection type and fill its properties
        
        @param id: name of this connection type
        @type  id: string
        
        @param line: line style
        @type  line: L{CConnectionLine<Line.CConnectionLine>}
        
        @param scrArrow: source arrow style
        @type  scrArrow: L{CConnectionArrow<Arrow.CConnectionArrow>}
        
        @param destArrow: destination arrow style
        @type  destArrow: L{CConnectionArrow<Arrow.CConnectionArrow>}
        
        @param icon: path to connection icon within metamodel storage
        @type  icon: string
        """
        self.line = line
        self.scrArrow = scrArrow
        self.destArrow = destArrow
        self.id = id
        self.icon = icon
        self.labels = []
        self.domain = domain
    
    def GetDomain(self):
        '''
        @return: current domain type
        @rtype: L{CDomainType<lib.Domain.Type.CDomainType>}
        '''
        return self.domain
    
    def SetDomain(self, domain):
        '''
        Set current domain type
        
        @param domain: new domain type
        @type domain: L{CDomainType<lib.Domain.Type.CDomainType>}
        '''
        self.domain = domain
    
    def SetIcon(self, value):
        """
        Set icon path to new value
        
        @param value: icon path
        @type  value: string
        """
        self.icon = value
    
    def AddLabel(self, position, label):
        """
        Add label to connection type
        
        @param position: initial position of label.
            (one of source, center, destination)
        @type  position: string
        
        @param label: visual object representing the label
        @type  label: L{CVisualObject<lib.Drawing.Objects.VisualObject.CVisualObject>}
        """
        self.labels.append((position,label))
    
    def RemoveLabel(self, label):
        """
        Remove label from connection
        
        @param label: visual object representing the label
        @type  label: L{CVisualObject<lib.Drawing.Objects.VisualObject.CVisualObject>}
        """
        for id, i in enumerate(self.labels):
            if i[1] is label:
                del self.labels[id]
                return
        else:
            raise ConnectionError("LabelNotExists")
    
    def GetIcon(self):
        """
        Get the icon of this connection
        
        @return: icon path within metamodel storage
        @rtype:  string
        """
        return self.icon
    
    def GetDestArrow(self):
        """
        Get the destination arrow
        
        @return: destination arrow object
        @rtype:  L{CConnectionArrow<Arrow.CConnectionArrow>}
        """
        return self.destArrow
    
    def GetLine(self):
        """
        Get the connection line style
        
        @return: line object
        @rtype:  L{CConnectionLine<Line.CConnectionLine>}
        """
        return self.line

    def GetSrcArrow(self):
        """
        Get the source arrow
        
        @return: source arrow object
        @rtype:  L{CConnectionArrow<Arrow.CConnectionArrow>}
        """
        return self.scrArrow
    
    def GetId(self):
        """
        Return name (Id) of this connection type
        
        @return: name of connection
        @rtype:  string
        """
        return self.id
    
    def SetDestArrow(self, value):
        """
        Set destination arrow style
        
        @param value: arrow object to set as destination arrow
        @type  value: L{CConnectionArrow<Arrow.CConnectionArrow>}
        """
        self.destArrow = value
    
    def SetSrcArrow(self, value):
        """
        Set source arrow style
        
        @param value: arrow object to set as source arrow
        @type  value: L{CConnectionArrow<Arrow.CConnectionArrow>}
        """
        self.scrArrow = value

    def Paint(self, context):
        """
        Paint connection of given type on canvas
        
        @param context: context in which is connection being drawn
        @type  context: L{CDrawingContext<lib.Drawing.DrawingContext.CDrawingContext>}
        """
        dx, dy = context.GetPos()
        canvas = context.GetCanvas()
        
        tmp = [(x + dx, y + dy) for (x, y) in context.GetPoints()]
        o = tmp[0]
        for i in tmp[1:]:
            self.line.Paint(canvas, o, i)
            o = i
        
        if self.scrArrow is not None:
            X = tmp[0][0] - tmp[1][0]
            Y = tmp[0][1] - tmp[1][1]
            self.scrArrow.Paint(canvas, tmp[0], atan2(-X, Y))
        
        if self.destArrow is not None:
            X = tmp[-1][0] - tmp[-2][0]
            Y = tmp[-1][1] - tmp[-2][1]
            self.destArrow.Paint(canvas, tmp[-1], atan2(-X, Y))
    
    def GetLabels(self):
        """
        Get list of all labels on this connection type
        
        @return: all labels
        @rtype:  iterator over (string, L{CVisualObject<lib.Drawing.Objects.VisualObject.CVisualObject>}) pairs
        """
        for label in self.labels:
            yield label
    
    def GetLabel(self, idx):
        """
        Get label by its index
        
        @param idx: index
        @type  idx: integer
        
        @return: all labels
        @rtype:  (string, L{CVisualObject<lib.Drawing.Objects.VisualObject.CVisualObject>})
        """
        return self.labels[idx]
    
    def HasVisualAttribute(self, name):
        '''
        @note: This is fake function for interface compatibility reasons
        
        @return: True if name points to anything but "text" domain attribute
        @rtype: bool
        '''
        return self.GetDomain().GetAttribute(name)['type'] != 'text'