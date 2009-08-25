from lib.Commands import CBaseCommand


class CMoveConnectionPointCmd(CBaseCommand):
    def __init__(self, DragPoint, canvas, point, description = None): 
        CBaseCommand.__init__(self, description) 
        self.connection, self.index = DragPoint
        self.canvas = canvas
        self.point = point
        self.enabled = True
       

    def do (self):
        self.old_point = self.connection.GetPoint(self.canvas, self.index)
        self.old_len = len(self.connection.points)
        self.connection.MovePoint(self.canvas, self.point, self.index)
        
        if self.description == None:
            self.description = _('Moving %s connection point') %(self.connection.GetObject().GetType().GetId())
    
    def undo(self):
        if self.old_len > len(self.connection.points) :
            self.connection.InsertPoint(self.canvas, self.old_point, self.index - 1)  
            self.insertedPoint = True
        else:
            self.connection.MovePoint(self.canvas, self.old_point, self.index)
            self.insertedPoint = False
        
        
    def redo(self):
        if self.insertedPoint:
            self.connection.RemovePoint(self.canvas, self.index)  
        else:
            self.connection.MovePoint(self.canvas, self.point, self.index)
        