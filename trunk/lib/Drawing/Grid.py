from lib.Base import CBaseObject
from lib.datatypes import CColor
from lib.config import config
from lib.Math2D.path import Path
from math import sqrt

class CGrid(CBaseObject):
    
    def __init__(self, local_settings=None):
        self.local_settings = bool(local_settings)
        self.UpdateState(local_settings)
        self.hor_spacing = 0
        self.ver_spacing = 0

    def UpdateState(self, data):
        '''
        Update the state of the grid from local source.
        '''
        # local source of settings
        if self.local_settings:
            if not data: return
            self.local_settings = data['local']
            self.active = data['active']
            self.visible = data['visible']
            self.resize_elements = data['resize_elements']
            self.snap_breakpoints = data['snap_breakpoints']
            self.old_vercital, self.old_horizontal = self.hor_spacing, self.hor_spacing
            self.hor_spacing = data['hor_space']
            self.ver_spacing = data['ver_space']
            self.line_width = data['line_width']
            self.snap_mode = data['snap_mode']
            
    def GetState(self):
        ret = {}
        ret['local'] = self.local_settings
        ret['active'] = self.active
        ret['visible'] = self.visible
        ret['resize_elements'] = self.resize_elements
        ret['snap_breakpoints'] = self.snap_breakpoints
        ret['hspace'] = self.hor_spacing
        ret['vspace'] = self.ver_spacing
        ret['linew'] = self.line_width
        ret['mode'] = self.snap_mode
        return ret
    
    def SnapPosition(self, pos):
        if not self.local_settings:
            self.hor_spacing = config['/Grid/HorSpacing']
            self.ver_spacing = config['/Grid/VerSpacing']
        x = self.hor_spacing * round(pos[0]/(float(self.hor_spacing)))# + 0.5
        y = self.ver_spacing * round(pos[1]/(float(self.ver_spacing)))# + 0.5
        return (x, y)
    
    def SnapElement(self, element, pos, canvas, override=False):
        '''
        Snaps element position according to snap mode.
        '''
        if not self.local_settings:
            self.active = config['/Grid/Active'] == 'true'
            self.resize_elements = config['/Grid/ResizeElements'] == 'true'
            self.snap_mode = config['/Grid/SnapMode']
        if self.active or override:
            if self.snap_mode == 'TOP_LEFT':
                pos = self.SnapPosition(pos)
            elif self.snap_mode == 'CENTER':
                width, height = element.GetSize(canvas)
                center = (pos[0] + width/2.0, pos[1] + height/2.0)
                newCenter = self.SnapPosition(center)
                pos = (newCenter[0]-width/2.0, newCenter[1]-height/2.0)
            elif self.snap_mode == 'CORNERS':
                if not self.local_settings:
                    self.hor_spacing = config['/Grid/HorSpacing']
                    self.ver_spacing = config['/Grid/VerSpacing']
                w, h = element.GetSize(canvas)
                # finds out which element corner is nearest to grid
                top_left = list(pos)
                new_top_left = self.SnapPosition(top_left)
                len_top_left = sqrt((top_left[0] - new_top_left[0])**2 \
                    + (top_left[1] - new_top_left[1])**2)
                
                top_right = [top_left[0] + w, top_left[1]]
                new_top_right = self.SnapPosition(top_right)
                len_top_right = sqrt((top_right[0] - new_top_right[0])**2 \
                    + (top_right[1] - new_top_right[1])**2)
                
                bottom_left = [top_left[0], top_left[1] + h]
                new_bottom_left = self.SnapPosition(bottom_left)
                len_bottom_left = sqrt((bottom_left[0]-new_bottom_left[0])**2 \
                    + (bottom_left[1] - new_bottom_left[1])**2)
                
                bottom_right = [top_left[0] + w, top_left[1] + h]
                new_bottom_right = self.SnapPosition(bottom_right)
                len_bottom_right = sqrt((bottom_right[0]-new_bottom_right[0])**2\
                    + (bottom_right[1] - new_bottom_right[1])**2)
                
                minimum = min(len_top_left, len_top_right, 
                    len_bottom_right, len_bottom_left)
                if minimum==len_top_left:
                    pos = new_top_left
                elif minimum==len_top_right:
                    pos = (new_top_right[0] - w, new_top_right[1])
                elif minimum==len_bottom_left:
                    pos = (new_bottom_left[0], new_bottom_left[1] - h)
                else:
                    pos = (new_bottom_right[0] - w, new_bottom_right[1] - h)
                
        element.SetPosition(pos)
        if self.resize_elements:
            self.ResizeElement(element, canvas)
    
    def ResizeElement(self, element, canvas):
        '''
        Resizes element to match grid spacing.
        Each corner is moved outwards to nearest grid intersection.
        '''
        if not self.local_settings:
            self.hor_spacing = config['/Grid/HorSpacing']
            self.ver_spacing = config['/Grid/VerSpacing']
        w, h = element.GetSize(canvas)
        pos = list(element.GetPosition())
        # top left corner
        size_increase = [pos[0] % self.hor_spacing, pos[1] % self.ver_spacing]
        new_pos = (pos[0] - size_increase[0], pos[1] - size_increase[1])
        # bottom right corner
        size_increase[0] += (self.hor_spacing - \
            ((pos[0]+w) % self.hor_spacing)) % self.hor_spacing
        size_increase[1] += (self.ver_spacing - \
            ((pos[1]+h) % self.ver_spacing)) % self.ver_spacing
        rel = element.GetSizeRelative()
        element.SetSizeRelative((rel[0] + size_increase[0],
            rel[1] + size_increase[1]))
        element.SetPosition(new_pos)
    
    def SnapConnection(self, conn, pos, idx, canvas, override=False):
        if not self.local_settings:
            self.hor_spacing = config['/Grid/HorSpacing']
            self.ver_spacing = config['/Grid/VerSpacing']
            self.snap_breakpoints = config['/Grid/SnapBreakpoints'] == 'true'
            self.active = config['/Grid/Active'] == 'true'
        if (self.active and self.snap_breakpoints) or override:
            pos = self.SnapPosition(pos)
        conn.MovePoint(canvas, pos, idx)
    
    def __GetGridPath(self, width, height):
        if not self.local_settings:
            self.hor_spacing = config['/Grid/HorSpacing']
            self.ver_spacing = config['/Grid/VerSpacing']
        
        w = width + 0.5
        h = height + 0.5
        current = 0.5
        path_string = ''
        
        while current <= w:
            current += self.ver_spacing
            path_string += 'M %.1f,%.1f L %.1f,%.1f ' % (0.5, current, w, current)
        current = 0.5
        while current <= h:
            current += self.hor_spacing
            path_string += 'M %.1f,%.1f L %.1f,%.1f ' % (current, 0.5, current, h)
        print path_string
        ret = Path(path_string)
        print ret
        return ret
    
    def __IsSpacingChanged(self):
        if not self.local_settings:
            self.old_horizontal = self.hor_spacing
            self.old_vertical = self.ver_spacing
            self.hor_spacing = config['/Grid/HorSpacing']
            self.ver_spacing = config['/Grid/VerSpacing']
        if self.old_vertical != self.ver_spacing:
            return True
        if self.old_horizontal != self.hor_spacing:
            return True
        
    
    def Paint(self, canvas, w, h):
    
        if not self.local_settings:
            self.visible = config['/Grid/Visible'] == 'true'
            self.line_width = config['/Grid/LineWidth']
        if not self.visible: return    
        fg1 = config['/Grid/LineColor1']
        fg2 = config['/Grid/LineColor2']
        line_style = 'solid'
        line_style1 = 'dot'
        
        if self.__IsSpacingChanged():
            self.gridPath = self.__GetGridPath(w, h)
        
        canvas.DrawPath(self.gridPath, fg1, None, self.line_width, line_style)
        canvas.DrawPath(self.gridPath, fg2, None, self.line_width, line_style1)
         
    def IsActive(self):
        return self.active
        
    def IsVisible(self):
        return self.visible
    
