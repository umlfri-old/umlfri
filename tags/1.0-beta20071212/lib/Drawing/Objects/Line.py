from VisualObject import CVisualObject
from VBox import CVBox
import gtk.gdk

class CLine(CVisualObject):
    def __init__(self, type = "auto", color = "black"):
        CVisualObject.__init__(self)
        self.type = type
        self.color = color

    def __ComputeType(self):
        tp = self.type
        if tp == 'auto':
            if isinstance(self.parent, CVBox):
                tp = 'vertical'
            else:
                tp = 'horizontal'
        return tp

    def GetSize(self, canvas, element):
        size = element.GetCachedSize(self)
        if size is not None:
            return size
        tp = self.__ComputeType()
        if tp == 'horizontal':
            return element.CacheSize(self, (0, 1))
        else:
            return element.CacheSize(self, (1, 0))
    
    def GetResizable(self):
        tp = self.__ComputeType()
        return tp == 'horizontal', tp == 'vertical'

    def PaintShadow(self, canvas, pos, element, color, size = (None, None)):
        size = self.ComputeSize(canvas, element, size)
        tp = self.__ComputeType()
        if tp == 'horizontal' and pos[0] is not None:
            canvas.DrawLine(pos, (pos[0]+size[0], pos[1]), color)
        elif tp == 'vertical' and pos[1] is not None:
            canvas.DrawLine(pos, (pos[0], pos[1]+size[1]), color)

    def Paint(self, canvas, pos, element, size = (None, None)):
        size = self.ComputeSize(canvas, element, size)
        tp = self.__ComputeType()
        color, = self.GetVariables(element, 'color')
        if tp == 'horizontal' and pos[0] is not None:
            canvas.DrawLine(pos, (pos[0]+size[0], pos[1]), color)
        elif tp == 'vertical' and pos[1] is not None:
            canvas.DrawLine(pos, (pos[0], pos[1]+size[1]), color)