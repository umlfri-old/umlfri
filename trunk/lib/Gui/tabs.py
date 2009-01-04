from lib.Depend.gtk2 import gtk
from lib.Depend.gtk2 import gobject

from common import CWidget
from common import  event
from lib.Drawing import CDiagram
from lib.Drawing.Canvas.GtkPlus import PixmapFromPath
from twProjectView import CtwProjectView

class CTabs(CWidget):
    name = 'nbTabs'
    widgets = ('nbTabs','twProjectView', 'picDrawingArea', 'tbDrawingArea',
                #Context menu
                'menuTreeElement',
                'mnuTab', 'mnuTabExportSVG', 'mnuTabPages_menu', 'mnuTabCloseDiagram', 'mnuTabCloseAllDiagram',
                'mnuTabShowInProjectView',)
    
    __gsignals__ = {
        'change_current_page':  (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT,) 
            ),
        'drawing-area-set-focus': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ()),
        'export-svg-from-TabMenu': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ()),
        'show-diagram-in-project': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT,)),
    }
    
    def __init__(self, app, wTree):
        CWidget.__init__(self, app, wTree)
        diagram = CDiagram(None,'StartPage')
        self.diagrams = [diagram]
        
        self.mnuTabExportSVG.set_sensitive(False)
        self.mnuTabCloseDiagram.set_sensitive(False)
        self.mnuTabCloseAllDiagram.set_sensitive(False)
        self.mnuTabShowInProjectView.set_sensitive(False)
        sp = self.nbTabs.get_nth_page(0)
        splbl = self.nbTabs.get_tab_label(sp)
        self.nbTabs.remove_page(0)
        self.__AddNbPage(None, splbl, sp)
        self.__RefreshEnable()
    
    def __RefreshEnable(self):
        sp = self.nbTabs.get_nth_page(0)
        if len(self.diagrams) == 1:
            sp.show()
        splbl = self.nbTabs.get_tab_label(sp)
        splbl.get_children()[-1].set_sensitive(len(self.diagrams) > 1)
    
    def __AddNbPage(self, pixbuf, label, page):
        hboxbut = gtk.HBox(spacing = 3)
        hboxbut.show()
        
        if pixbuf is not None:
            img = gtk.Image()
            img.set_from_pixbuf(pixbuf)
            img.show()
        
        if isinstance(label, (str, unicode)):
            label1 = gtk.Label(label)
            label1.show()
        else:
            label1 = label 
        
        button = gtk.Button()
        image = gtk.image_new_from_stock(gtk.STOCK_CLOSE, gtk.ICON_SIZE_SMALL_TOOLBAR)       
        image.show()
        button.add(image)
        button.set_relief(gtk.RELIEF_NONE)
        button.show()
        button.connect("clicked", self.on_button_click, page)
        
        if pixbuf is not None:
            hboxbut.add(img)
        hboxbut.add(label1)
        hboxbut.add(button)
        idx = self.nbTabs.append_page(page, hboxbut)
        
    def AddTab(self, diagram):
        for i in self.diagrams:
            if i is diagram:
                self.SetCurrentPage(self.diagrams.index(diagram))
                return
        
        page = gtk.HBox()
        page.show()
        
        self.__AddNbPage(
            PixmapFromPath(self.application.GetProject().GetStorage(), diagram.GetType().GetIcon()),
            diagram.GetName(),
            page)
        self.diagrams.append(diagram)
       
        self.SetCurrentPage(self.nbTabs.get_n_pages()-1)
        self.__RefreshEnable()
    
    def Show(self):
        self.nbTabs.show()
    
    def Hide(self):
        self.nbTabs.hide()
    
    def SetVisible(self, value):
        if value:
            self.Show()
        else:
            self.Hide()
    
    def on_button_click(self, widget, page):
        self.CloseTab(self.diagrams[self.nbTabs.page_num(page)])

    @event("nbTabs", "switch-page")
    def on_change_current_page(self, notebook, page, page_num):   
        self.diagrams[page_num].DeselectAll()
        if page_num  == 0:
            self.emit("change_current_page", None)
            self.mnuTabExportSVG.set_sensitive(False)
            self.mnuTabCloseDiagram.set_sensitive(False)
            self.mnuTabShowInProjectView.set_sensitive(False)
            if len(self.diagrams) == 1:
                self.mnuTabCloseAllDiagram.set_sensitive(False)
            for chld in self.nbTabs.get_nth_page(0).get_children():
                chld.show()
        else:
            page = self.nbTabs.get_nth_page(page_num)
            if self.tbDrawingArea.get_parent():
                self.tbDrawingArea.get_parent().remove(self.tbDrawingArea)
            page.pack_start(self.tbDrawingArea)
            self.picDrawingArea.queue_draw()
            self.emit("change_current_page", self.diagrams[page_num])
            self.mnuTabExportSVG.set_sensitive(True)
            self.mnuTabCloseDiagram.set_sensitive(True)
            self.mnuTabCloseAllDiagram.set_sensitive(True)
            self.mnuTabShowInProjectView.set_sensitive(True)
            for chld in self.nbTabs.get_nth_page(0).get_children():
                chld.hide()
           
    def IsStartPageActive(self):
        return self.nbTabs.get_current_page() == 0
    
    def CloseTab(self, diagram):
        if diagram in self.diagrams:
            num = self.diagrams.index(diagram)
            if num == 0:
                self.nbTabs.get_nth_page(0).hide()
            else:
                if num == self.nbTabs.get_current_page() and self.tbDrawingArea.get_parent():
                    self.tbDrawingArea.get_parent().remove(self.tbDrawingArea)
                self.diagrams.remove(diagram)
                #self.mnuTabPages_menu.remove(self.mnuTabPages_menu.get_children()[num])
                self.nbTabs.remove_page(num)
        self.__RefreshEnable()
    
    def CloseCurrentTab(self):
        if self.nbTabs.get_current_page() > 0:
            self.CloseTab(self.diagrams[self.nbTabs.get_current_page()])
    
    def NextTab(self):
        if len(self.diagrams) == self.nbTabs.get_current_page() + 1:
            self.SetCurrentPage(0)
        else:
            self.nbTabs.next_page()
            self.emit("drawing-area-set-focus")
    
    def PreviousTab(self):
        if self.nbTabs.get_current_page() == 0:
            self.SetCurrentPage(len(self.diagrams)-1)
        else:
            self.nbTabs.prev_page()
            if self.nbTabs.get_current_page() == 0:
                return
        self.emit("drawing-area-set-focus")
    
    def SetCurrentPage(self, page): 
        if page <= len(self.diagrams)-1:
            self.nbTabs.set_current_page(page)
    
    def CloseAll(self):
        if self.tbDrawingArea.get_parent():
            self.tbDrawingArea.get_parent().remove(self.tbDrawingArea)
        for i in xrange(1, len(self.diagrams)):
            del self.diagrams[1]
            self.nbTabs.remove_page(1)
        self.__RefreshEnable()

    def RefreshTab(self, diagram):
        if diagram in self.diagrams:
            num = self.diagrams.index(diagram)
            page = self.nbTabs.get_nth_page(num) #ebPage = event box Page
            page_label = self.nbTabs.get_tab_label(page)
            for l in page_label:
                if isinstance(l, gtk.Label):
                    label = l
            label.set_text(diagram.GetName())
    
    def on_mnuTab_activate(self, widget, diagram):
        for id, a in enumerate(self.diagrams):
            if diagram is a:
                break
        else:
            return
        if self.nbTabs.get_current_page() != id:
            self.SetCurrentPage(id)
    
    @event("nbTabs","button-press-event")
    def button_clicked(self, widget, event):
        if event.button == 3:
            for i in self.mnuTabPages_menu.get_children():
                self.mnuTabPages_menu.remove(i)
                
            for id, i in enumerate(self.diagrams):
                mi = gtk.RadioMenuItem(None,i.GetName())  
                if id > 0:
                    mi.set_group(self.mnuTabPages_menu.get_children()[0])      
                mi.show()   
                mi.connect("toggled", self.on_mnuTab_activate, i)
                self.mnuTabPages_menu.append(mi)
            
            self.mnuTabPages_menu.get_children()[self.nbTabs.get_current_page()].set_property("active",True)
            self.mnuTab.popup(None,None,None,event.button,event.time)
    
    @event("mnuTabCloseDiagram", "activate")
    def on_mnuTabCloseDiagram_activate(self, menuItem):
        if self.nbTabs.get_current_page() == 0:
            return
        else:
            self.CloseTab(self.diagrams[self.nbTabs.get_current_page()])
    
    @event("mnuTabCloseAllDiagram", "activate")
    def on_mnuTabCloseAllDiagram_activate(self, menuItem):
        self.CloseAll()
    
    @event("mnuTabShowInProjectView","activate")
    def on_mnuTabShowInProjectView_activate(self, menuItem):
        self.emit('show-diagram-in-project',self.diagrams[self.nbTabs.get_current_page()])
    
    @event("mnuTabExportSVG", "activate")
    def on_mnuTabExportSVG_activate(self, menuItem):
        if self.nbTabs.get_current_page() == 0:
            return
        else:
            self.emit("export-svg-from-TabMenu")