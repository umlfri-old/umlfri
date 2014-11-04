from lib.Depend.gtk2 import pango
from lib.Depend.gtk2 import gtk

from lib.Exceptions.UserException import *
from Abstract import CAbstractCanvas

LINE_STYLES = {'solid': gtk.gdk.LINE_SOLID,
               'dot': gtk.gdk.LINE_ON_OFF_DASH,
               'doubledot': gtk.gdk.LINE_DOUBLE_DASH}

pixmaps = {}

def PixmapFromString(data):
    loader = gtk.gdk.PixbufLoader()    
    tmp = data
    loader.write(tmp)
    loader.close()
    tmp = loader.get_pixbuf()
    return tmp

def PixmapFromPath(storage, path):
    if (storage, path) in pixmaps:
        tmp = pixmaps[(storage, path)]
    else:
        if storage is None:
            tmp = gtk.gdk.pixbuf_new_from_file(unicode(path))
        else:
            pathx = storage.file(path)
            loader = gtk.gdk.PixbufLoader()
            while True:
                tmp = pathx.read(102400)
                if not tmp:
                    break
                loader.write(tmp)
            loader.close()
            tmp = loader.get_pixbuf()
        pixmaps[(storage, path)] = tmp
    return tmp

class CGtkCanvas(CAbstractCanvas):
    def __init__(self, widget, window = None, storage = None):
        self.widget = widget
        if window is None:
            self.window = widget.window
        else:
            self.window = window
        self.storage = storage
        self.pango_ctx = self.widget.create_pango_context()
        self.pango_layout = self.widget.create_pango_layout("")
        self.fonts = {}
    
    def __SetFont(self, (family, style, size), returndesc = False):
        underline = 'underline' in style
        bold = 'bold' in style
        italic = 'italic' in style
        strikeout = 'strike' in style
        font = [family]
        if italic:
            font.append('italic')
        if bold:
            font.append('bold')
        font.append(str(size)+'px')
        font = ' '.join(font)
        if font in self.fonts:
            fontobj = self.fonts[font]
        else:
            self.fonts[font] = fontobj = pango.FontDescription(font)
        if returndesc:
            return fontobj
        self.pango_layout.set_font_description(fontobj)
        
        atlist = pango.AttrList()
        if underline:
            atlist.insert(pango.AttrUnderline(pango.UNDERLINE_SINGLE, 0, 10000))
        if strikeout:
            atlist.insert(pango.AttrStrikethrough(True, 0, 10000))
        self.pango_layout.set_attributes(atlist)

    
    def DrawArc(self, pos, size, arc = (0, 360), fg = None, bg = None, line_width = None, line_style = None):
        gc = self.window.new_gc()
        if line_width is not None:
            gc.line_width = line_width
        if line_style is not None:
            gc.line_style = LINE_STYLES[line_style]
        cmap = self.window.get_colormap()
        if bg is not None:
            gc.foreground = cmap.alloc_color(bg)
            self.window.draw_arc(gc, True, int(pos[0]), int(pos[1]), int(size[0]), int(size[1]), int(arc[0]*64), int(arc[1]*64))
        if fg is not None:
            gc.foreground = cmap.alloc_color(fg)
            self.window.draw_arc(gc, False, int(pos[0]), int(pos[1]), int(size[0]), int(size[1]), int(arc[0]*64), int(arc[1]*64))
    
    def DrawLine(self, start, end, fg, line_width = None, line_style = None):
        cmap = self.window.get_colormap()
        gc = self.window.new_gc(foreground = cmap.alloc_color(fg))
        if line_width is not None:
            gc.line_width = line_width
        if line_style is not None:
            gc.line_style = LINE_STYLES[line_style]
        self.window.draw_line(gc, int(start[0]), int(start[1]), int(end[0]), int(end[1]))
    
    def DrawLines(self, points, fg, line_width = None, line_style = None):
        cmap = self.window.get_colormap()
        gc = self.window.new_gc(foreground = cmap.alloc_color(fg))
        if line_width is not None:
            gc.line_width = line_width
        if line_style is not None:
            gc.line_style = LINE_STYLES[line_style]
        self.window.draw_lines(gc, [(int(x), int(y)) for x,y in points])
    
    def DrawPolygon(self, points, fg = None, bg = None, line_width = None, line_style = None):
        gc = self.window.new_gc()
        if line_width is not None:
            gc.line_width = line_width
        if line_style is not None:
            gc.line_style = LINE_STYLES[line_style]
        cmap = self.window.get_colormap()
        points = [(int(x), int(y)) for x,y in points]
        if bg is not None:
            gc.foreground = cmap.alloc_color(bg)
            self.window.draw_polygon(gc, True, points)
        if fg is not None:
            gc.foreground = cmap.alloc_color(fg)
            self.window.draw_polygon(gc, False, points)
    
    def DrawPath(self, path, fg = None, bg = None, line_width = None, line_style = None):
        for single in path:
            t = single.GetType()
            if t == 'polygon':
                self.DrawPolygon(single, fg, bg, line_width, line_style)
            elif t == 'polyline':
                self.DrawLines(single, fg, line_width, line_style)
    
    def DrawRectangle(self, pos, size, fg = None, bg = None, line_width = None, line_style = None):
        gc = self.window.new_gc()
        if line_width is not None:
            gc.line_width = line_width
        if line_style is not None:
            gc.line_style = LINE_STYLES[line_style]
        cmap = self.window.get_colormap()
        if bg is not None:
            gc.foreground = cmap.alloc_color(bg)
            self.window.draw_rectangle(gc, True, int(pos[0]), int(pos[1]), int(size[0]), int(size[1]))
        if fg is not None:
            gc.foreground = cmap.alloc_color(fg)
            self.window.draw_rectangle(gc, False, int(pos[0]), int(pos[1]), int(size[0]), int(size[1]))
    
    def DrawText(self, pos, text, font, fg):
        self.__SetFont(font)
        
        cmap = self.window.get_colormap()
        gc = self.window.new_gc(foreground = cmap.alloc_color(fg))
        
        self.pango_layout.set_text(text)
        self.window.draw_layout(gc, x=int(pos[0]), y=int(pos[1]), layout=self.pango_layout)
    
    def GetTextSize(self, text, font):
        self.__SetFont(font)
        
        self.pango_layout.set_text(text)
        return int(self.pango_layout.get_size()[0]/float(pango.SCALE)), int(self.pango_layout.get_size()[1]/float(pango.SCALE))
    
    def GetFontBaseLine(self, font):
        fontobj = self.__SetFont(font, True)
        metrics = self.pango_ctx.get_metrics(fontobj, None)
        return metrics.get_ascent() / pango.SCALE
    
    def DrawIcon(self, pos, filename):
        if self.storage is None:
            raise DrawingError('storage')
        pixmap = PixmapFromPath(self.storage, filename)
        gc = self.window.new_gc()
        self.window.draw_pixbuf(gc, pixmap, 0, 0, pos[0], pos[1])
    
    def GetIconSize(self, filename):
        if self.storage is None:
            raise DrawingError('storage')
        pixmap = PixmapFromPath(self.storage, filename)
        return pixmap.get_width(), pixmap.get_height()
    
    def Clear(self):
        gc = self.widget.get_style().white_gc
        self.window.draw_rectangle(gc, True, 0, 0, *self.window.get_size())