from SimpleContainer import CSimpleContainer
from lib.Exceptions.UserException import *

class CProportional(CSimpleContainer):
    def __init__(self, ratio):
        CSimpleContainer.__init__(self)
        self.strratio = ratio
        ratio = ratio.split(':')
        if len(ratio) != 2:
            raise XMLError("Proportional", "ratio")
        self.ratio = float(int(ratio[0]))/int(ratio[1])

    def ComputeSize(self, context):
        w, h = CSimpleContainer.ComputeSize(self, context)
        ch = int(w / self.ratio)
        cw = int(h * self.ratio)
        if ch > h:
            h = ch
        if cw > w:
            w = cw
        return (w, h)
