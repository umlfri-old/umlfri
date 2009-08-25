from lib.Depend.gtk2 import gtk, pango

from lib.Drawing.Canvas.GtkPlus import PixmapFromPath

from common import event, CWindow

class CfrmAddons(CWindow):
    widgets = (
        'twMetamodelList', 'cmdInstallMetamodel', 'cmdUninstallMetamodel', 'cmdEnableMetamodel', 'cmdDisableMetamodel'
    )
    
    name = 'frmAddons'
    
    def __init__(self, app, wTree):
        CWindow.__init__(self, app, wTree)
        
        self.__MetamodelStore = gtk.TreeStore(gtk.gdk.Pixbuf, str, bool, str)
        self.twMetamodelList.set_model(self.__MetamodelStore)
        
        renderer = gtk.CellRendererPixbuf()
        renderer.set_property('yalign', 0)
        renderer.set_property('ypad', 3)
        column = gtk.TreeViewColumn()
        column.pack_start(renderer)
        column.add_attribute(renderer, 'pixbuf', 0)
        column.add_attribute(renderer, 'sensitive', 2)
        self.twMetamodelList.append_column(column)
        
        renderer = gtk.CellRendererText()
        renderer.set_property('wrap-mode', pango.WRAP_WORD)
        column = gtk.TreeViewColumn()
        column.pack_start(renderer)
        column.add_attribute(renderer, 'markup', 1)
        column.add_attribute(renderer, 'sensitive', 2)
        self.twMetamodelList.append_column(column)
        self.twMetamodelList.connect_after("size-allocate", self.__DoTextWrap, column, renderer)

    def Show(self):
        self.__Load()
        
        self.twMetamodelList.grab_focus()
        
        self.form.run()
        
        self.Hide()
    
    def __DoTextWrap(self, treeview, allocation, column, cell):
        otherColumns = (c for c in treeview.get_columns() if c != column)
        newWidth = allocation.width - sum(c.get_width() for c in otherColumns)
        newWidth -= treeview.style_get_property("horizontal-separator") * 2
        if cell.props.wrap_width == newWidth or newWidth <= 0:
            return
        cell.props.wrap_width = newWidth
        store = treeview.get_model()
        iter = store.get_iter_first()
        while iter and store.iter_is_valid(iter):
            store.row_changed(store.get_path(iter), iter)
            iter = store.iter_next(iter)
            treeview.set_size_request(0,-1)
    
    def __Load(self):
        self.__MetamodelStore.clear()
        
        for addon in self.application.addonManager.ListAddons():
            if addon.GetType() == 'metamodel':
                twStore = self.__MetamodelStore
            else:
                continue
            
            if addon.GetIcon() is None:
                icon = None
            else:
                icon = PixmapFromPath(addon.GetStorage(), addon.GetIcon())
            
            name = addon.GetName()
            version = addon.GetVersion()
            description = addon.GetDescription() or ""
            enabled = addon.IsEnabled()
            uri = addon.GetUri()
            
            twStore.append(None, (icon, "<b>%s</b>     %s\n%s"%(name, version, description), enabled, uri))
    
    def __GetSelectedAddon(self, treeView):
        iter = treeView.get_selection().get_selected()[1]
        if iter is None:
            return None
        
        selected = treeView.get_model().get(iter, 3)[0]
        return self.application.addonManager.GetAddon(selected)
    
    @event("cmdEnableMetamodel", "clicked")
    def on_cmdEnableMetamodel_click(self, button):
        addon = self.__GetSelectedAddon(self.twMetamodelList)
        if addon is None:
            return
        
        iter = self.twMetamodelList.get_selection().get_selected()[1]
        self.__MetamodelStore.set(iter, 2, True)
        
        addon.Enable()
        self.MetamodelChanged()
    
    @event("cmdDisableMetamodel", "clicked")
    def on_cmdDisableMetamodel_click(self, button):
        addon = self.__GetSelectedAddon(self.twMetamodelList)
        
        if addon is None:
            return
        
        iter = self.twMetamodelList.get_selection().get_selected()[1]
        self.__MetamodelStore.set(iter, 2, False)
        
        addon.Disable()
        self.MetamodelChanged()
    
    @event("twMetamodelList", "cursor-changed")
    def MetamodelChanged(self, treeView = None):
        addon = self.__GetSelectedAddon(self.twMetamodelList)
        
        if addon is None:
            self.cmdEnableMetamodel.set_sensitive(False)
            self.cmdDisableMetamodel.set_sensitive(False)
        else:
            self.cmdEnableMetamodel.set_sensitive(not addon.IsEnabled())
            self.cmdDisableMetamodel.set_sensitive(addon.IsEnabled())