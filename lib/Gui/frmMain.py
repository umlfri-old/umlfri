from lib.Depend.gtk2 import gtk

from common import CWindow, event

from lib.consts import SCALE_MIN, SCALE_MAX, SCALE_INCREASE, WEB

import os.path
from lib.Drawing import CElement, CDiagram
from lib.Elements import CElementObject, CElementType
from dialogs import CWarningDialog, CQuestionDialog, ECancelPressed
from tbToolBox import CtbToolBox
from twProjectView import CtwProjectView
from mnuItems import CmnuItems
from picDrawingArea import CpicDrawingArea
from nbProperties import CnbProperties
from tabs import CTabs
from tabStartPage import CtabStartPage
from lib.Distconfig import IMAGES_PATH
from lib.Gui.diagramPrint import CDiagramPrint
from lib.Exceptions import UserException


class CfrmMain(CWindow):
    name = 'frmMain'
    glade = 'main.glade'
    
    widgets = (
        #menu
        #############
        'mItemFile',
        'mnuOpen', 'mnuSave', 'mnuSaveAs', 'mnuPrint', 'mnuProperties', 'mnuQuit',
        #############
        'mItemEdit',
        'mnuCut', 'mnuCopy', 'mnuCopyAsImage', 'mnuPaste', 'mnuDelete',
        #############
        'mItemProject',
        #############
        'mItemDiagram',
        'mnuExport',
        #############
        'mItemView',
        'mnuViewTools', 'mnuViewCommands', 'mnuNormalSize', 'mnuZoomIn','mnuZoomOut', 'mnuBestFit',
        'hndCommandBar',
        #############
        'mnuAddons', 'mnuOptions',
        #############
        'mItemHelp',
        'mnuAbout',
        'mnuWebsite',
        'mnuError',
        #############
        'mItemElement',
        'mmShift_SendBack', 'mmShift_BringForward', 'mmShift_ToBottom', 'mmShift_ToTop',
        #############
        #toolbar
        'cmdOpen', 'cmdSave', 'cmdCopy', 'cmdCut', 'cmdPaste', 'cmdZoomOut', 'cmdZoomIn',
        #############
        #fullscreen
        'mnuMenubar', 'mnuFullscreen', 'cmdCloseFullscreen', 'vpaRight', 'sbStatus','hpaRight',
        )

    complexWidgets = (CtbToolBox, CtwProjectView, CmnuItems, CpicDrawingArea, CnbProperties, CTabs,
                      CtabStartPage, )

    def __init__(self, app, wTree):
        CWindow.__init__(self, app, wTree)
        self.form.set_icon_from_file(os.path.join(IMAGES_PATH, 'app_icon.png'))
        self.diagramPrint = CDiagramPrint()
        self.form.maximize()
        self.__sensitivity_project = None
        self.UpdateMenuSensitivity(project = False)
        self.ReloadTitle()
        
    def SetSensitiveMenuChilds(self, MenuItem, value):
        for i in MenuItem.get_submenu().get_children():
            i.set_sensitive(value)
    
    def UpdateMenuSensitivity(self, project = None, diagram = None, element = None):
        if self.__sensitivity_project is None:
            self.__sensitivity_project = [True, True, True, True, True]
        changes = 0
        if project is not None:
            if not project:
                diagram = False
            if project != self.__sensitivity_project[0]:
                changes += 1
            self.__sensitivity_project[0] = project
        else:
            project = self.__sensitivity_project[0]
        if diagram is not None:
            if not diagram:
                element = False
            if diagram != self.__sensitivity_project[1]:
                changes += 1
            self.__sensitivity_project[1] = diagram
        else:
            diagram = self.__sensitivity_project[1]
        if element is not None:
            if element != self.__sensitivity_project[2]:
                changes += 1
            self.__sensitivity_project[2] = element
        else:
            element = self.__sensitivity_project[2]
        if not self.application.GetClipboard().IsEmpty():
             changes += 1

        zoomin = diagram and (self.picDrawingArea.GetScale()+0.00001) < SCALE_MAX
        zoomout = diagram and (self.picDrawingArea.GetScale()-0.00001) > SCALE_MIN
       
        changes += zoomin != self.__sensitivity_project[3]
        changes += zoomout != self.__sensitivity_project[4]
        self.__sensitivity_project[3] = zoomin
        self.__sensitivity_project[4] = zoomout
        
        if changes == 0:
            return
        
        self.picDrawingArea.UpdateMenuSensitivity(project, diagram, element)
        
        self.SetSensitiveMenuChilds(self.mItemProject, project)
        self.SetSensitiveMenuChilds(self.mItemDiagram, diagram)
        self.SetSensitiveMenuChilds(self.mItemElement, element)
        self.mnuSave.set_sensitive(project)
        self.mnuSaveAs.set_sensitive(project)
        self.mnuPrint.set_sensitive(diagram)
        self.cmdSave.set_sensitive(project)
        self.cmdCopy.set_sensitive(element)
        self.cmdCut.set_sensitive(element)
        self.cmdPaste.set_sensitive(
            diagram and not self.application.GetClipboard().IsEmpty() and
            not bool(set(i.GetObject() for i in self.picDrawingArea.GetDiagram().GetElements()).intersection(set(i.GetObject() for i in self.application.GetClipboard().GetContent()))))
        self.cmdZoomIn.set_sensitive(diagram)
        self.cmdZoomOut.set_sensitive(diagram)
        self.mnuSave.set_sensitive(project)
        self.mnuCopy.set_sensitive(element)
        self.mnuCopyAsImage.set_sensitive(element)
        self.mnuCut.set_sensitive(element)
        self.mnuPaste.set_sensitive(diagram and not self.application.GetClipboard().IsEmpty())
        self.mnuDelete.set_sensitive(element)
        self.mnuNormalSize.set_sensitive(diagram)
        self.mnuZoomIn.set_sensitive(zoomin)
        self.cmdZoomIn.set_sensitive(zoomin)
        self.mnuZoomOut.set_sensitive(zoomout)
        self.cmdZoomOut.set_sensitive(zoomout)
        self.mnuBestFit.set_sensitive(diagram)
        self.mnuFullscreen.set_sensitive(diagram)
    
    def LoadProject(self, filenameOrTemplate, copy = None):
        self.nbTabs.CloseAll()
        self.application.ProjectInit()
        try:
            if copy is None:
                self.application.GetProject().CreateProject(filenameOrTemplate)
            else:
                self.application.GetProject().LoadProject(filenameOrTemplate, copy)
        except Exception:
            if __debug__:
                raise
            if copy is not None:
                self.application.GetRecentFiles().RemoveFile(filename)
            self.application.ProjectDelete()
            self.nbTabs.CloseAll()
            self.twProjectView.ClearProjectView()
            self.ReloadTitle()
            self.nbProperties.Fill(None)
            return CWarningDialog(self.form, _('Error opening file')).run()
            
        self.ReloadTitle()
        self.twProjectView.Redraw(True)
        self.mnuItems.Redraw()
        self.nbProperties.Fill(None)
        self.picDrawingArea.Redraw()
        self.UpdateMenuSensitivity(project = True)
        for diagram in self.application.GetProject().GetDefaultDiagrams():
            self.nbTabs.AddTab(diagram)
            self.picDrawingArea.SetDiagram(diagram)
        
    def PaintAll(self):
        if not self.nbTabs.IsStartPageActive():
            self.picDrawingArea.Paint(True)
    
    # Diagrams
    @event("mnuViewTools", "activate")
    def ActionViewTools(self, *args):
        self.tbToolBox.SetVisible(self.mnuViewTools.get_active())
    
    @event("mnuViewCommands", "activate")
    def ActionViewCommands(self, *args):
        if self.mnuViewCommands.get_active():
            self.hndCommandBar.show()
        else:
            self.hndCommandBar.hide()
    
    @event("cmdCloseFullscreen", "clicked")
    def ActionExitFullscreen(self, *args):
        self.mnuFullscreen.set_active(False)
        self.ActionFullscreen(*args)
    
    @event("mnuFullscreen", "activate")
    def ActionFullscreen(self, *args):
        if self.mnuFullscreen.get_active():
            self.mnuMenubar.hide()
            self.hndCommandBar.hide()
            self.sbStatus.hide()
            self.cmdCloseFullscreen.show()
            self.nbTabs.Hide()
            self.vpaRight.hide()
            self.form.window.fullscreen()
        else:
            self.mnuMenubar.show()
            self.ActionViewCommands()
            self.sbStatus.show()
            self.cmdCloseFullscreen.hide()
            self.nbTabs.Show()
            self.vpaRight.show()
            self.form.window.unfullscreen()

    @event("mnuAddons", "activate")
    def on_mnuAddons_activate(self, mnu):
        tmp = self.application.GetWindow('frmAddons')
        tmp.SetParent(self)
        tmp.Show()

    # Preferencies
    @event("mnuOptions", "activate")
    def on_mnuOptions_activate(self, mnu):
        tmp = self.application.GetWindow('frmOptions')
        tmp.SetParent(self)
        tmp.Show()
        self.PaintAll()

    # Help
    @event("tabStartPage","open-about-dialog")
    @event("mnuAbout", "activate")
    def on_mnuAbout_activate(self, mnu):
        tmp = self.application.GetWindow('frmAbout')
        tmp.SetParent(self)
        tmp.Show()
    
    @event("mnuWebsite", "activate")
    def on_mnuWebsite_activate(self, mnu):
        from webbrowser import open_new
        open_new(WEB)

    @event("mnuError", "activate")
    def on_mnuError_activate(self, mnu):
        text = _('This is just a test for the Exception handler window.\nYou will see this window if something really bad happens.\nSee the Help tab for more info.')
        raise Exception(text)
    
    @event('nbTabs','export-svg-from-TabMenu')
    @event('mnuExport', 'activate')
    def on_mnuExport_activate(self, widget):
        exportDialog = self.application.GetWindow('frmExport')
        exportDialog.setArea(self.picDrawingArea)        
        exportDialog.SetParent(self)
        exportDialog.Show()

    def ReloadTitle(self):
        if self.application.GetProject() is None or self.application.GetProject().GetFileName() is None:
            self.form.set_title(_('UML .FRI designer'))
        else:
            self.form.set_title(_('UML .FRI designer [%s]')%self.application.GetProject().GetFileName())

    # Actions
    @event("form", "delete-event")
    @event("mnuQuit", "activate")
    def ActionQuit(self, widget, event = None):
        try:
            if self.application.GetProject() is not None and CQuestionDialog(self.form, _('Do you want to save project?'), True).run():
                self.ActionSave(widget)
        except ECancelPressed:
            return True
        self.application.Quit()
    
    @event("tabStartPage","open-file")
    def on_open_file(self, widget, filename):
        if filename is not None:
            try:
                if self.application.GetProject() is not None and CQuestionDialog(self.form, _('Do you want to save project?'), True).run():
                    self.ActionSave(widget)
            except ECancelPressed:
                return
            self.LoadProject(filename, False)
            self.tabStartPage.Fill()

    @event("tabStartPage","open-project")
    @event("cmdOpen", "clicked")
    @event("mnuOpen", "activate")
    def ActionOpen(self, widget,tab = 0):
        filenameOrTemplate, copy = self.application.GetWindow("frmOpen").ShowDialog(self,tab)
        if filenameOrTemplate is not None:
            try:
                if self.application.GetProject() is not None and CQuestionDialog(self.form, _('Do you want to save project?'), True).run():
                    self.ActionSave(widget)
            except ECancelPressed:
                return
            self.LoadProject(filenameOrTemplate, copy)
            self.tabStartPage.Fill()
    
    @event("form", "key-press-event")
    def on_key_press_event(self, widget, event):
        if event.keyval in (gtk.keysyms.Tab, gtk.keysyms.ISO_Left_Tab):
            if event.state == (gtk.gdk.CONTROL_MASK | gtk.gdk.SHIFT_MASK):
                self.nbTabs.PreviousTab()
                self.form.emit_stop_by_name('key-press-event')
            elif event.state == gtk.gdk.CONTROL_MASK:
                self.nbTabs.NextTab()
                self.form.emit_stop_by_name('key-press-event')
        if event.state == gtk.gdk.CONTROL_MASK | gtk.gdk.SHIFT_MASK:
            if event.keyval == gtk.keysyms.F4:
                self.nbTabs.CloseAll()
        if event.state == gtk.gdk.CONTROL_MASK:
            if event.keyval  in (gtk.keysyms.F4, gtk.keysyms.w):
                self.nbTabs.CloseCurrentTab()
        if event.state == gtk.gdk.MOD1_MASK:
            Keys = [gtk.keysyms._1, gtk.keysyms._2, gtk.keysyms._3, gtk.keysyms._4, gtk.keysyms._5, 
                    gtk.keysyms._6, gtk.keysyms._7, gtk.keysyms._8, gtk.keysyms._9, gtk.keysyms._0]
            if event.keyval in Keys:
                self.nbTabs.SetCurrentPage(Keys.index(event.keyval))

    @event("nbTabs","drawing-area-set-focus")
    def on_drawing_area_set_focus(self,widget):
        self.picDrawingArea.SetFocus()
    
    @event("cmdSave", "clicked")
    @event("mnuSave", "activate")
    def ActionSave(self, widget):
        if self.application.GetProject().GetFileName() is None:
            self.ActionSaveAs(widget)
            self.tabStartPage.Fill()
        else:
            self.application.GetProject().SaveProject()

    @event("mnuSaveAs", "activate")
    def ActionSaveAs(self, widget):
        filename, isZippedFile = self.application.GetWindow("frmSave").ShowDialog(self)
        if filename is not None:
            self.application.GetProject().SaveProject(filename, isZippedFile)
            self.ReloadTitle()

    @event("mnuProperties", "activate")
    def ActionProperties(self, widget):
        self.diagramPrint.printPropertiesSetup()

    @event("mnuPrint", "activate")
    def ActionPrint(self, widget):
        self.diagramPrint.printStart(self.picDrawingArea.GetDiagram())

    @event("mnuDelete","activate")
    def on_mnuDelete_click(self, widget):
        self.picDrawingArea.DeleteElements()
        
    @event("mnuNormalSize","activate")
    def mnuNormalSize_click(self, widget):
        self.picDrawingArea.SetNormalScale()
        self.UpdateMenuSensitivity()

    @event("mnuBestFit","activate")
    def mnuBestFit_click(self, widget):
        self.picDrawingArea.BestFitScale()
        self.UpdateMenuSensitivity()

    @event("cmdZoomOut", "clicked")
    @event("mnuZoomOut","activate")
    def on_mnuZoomOut_click(self, widget):
        self.picDrawingArea.IncScale(-SCALE_INCREASE)
        self.UpdateMenuSensitivity()
    
    @event("cmdZoomIn", "clicked")
    @event("mnuZoomIn","activate")
    def on_mnuZoomIn_click(self, widget):
        self.picDrawingArea.IncScale(SCALE_INCREASE)
        self.UpdateMenuSensitivity()

    @event("cmdCut", "clicked")
    @event("mnuCut","activate")
    def on_mnuCut_click(self, widget):
        if self.picDrawingArea.HasFocus():
            self.picDrawingArea.ActionCut()
        else:
            pass
 
    @event("cmdCopy", "clicked")
    @event("mnuCopy","activate")
    def on_mnuCopy_click(self, widget):
        if self.picDrawingArea.HasFocus():
            self.picDrawingArea.ActionCopy()
            self.UpdateMenuSensitivity()
 
    @event("mnuCopyAsImage","activate")
    def on_mnuCopyAsImage_click(self, widget):
        if self.picDrawingArea.HasFocus():
            zoom, bg = self.application.GetWindow('frmCopyImage').Show()
            if zoom is None:
                return
            gtk.clipboard_get(gtk.gdk.SELECTION_CLIPBOARD).set_image(self.picDrawingArea.GetSelectionPixbuf(zoom, bg))
    
    @event("cmdPaste", "clicked")
    @event("mnuPaste","activate")
    def on_mnuPaste_click(self, widget):
        if self.picDrawingArea.HasFocus():
            try:
                self.picDrawingArea.ActionPaste()
            except UserException, e:
                if e.GetName() == "ElementAlreadyExists":
                    return CWarningDialog(self.form, _('Element is already in this diagram')).run()
                elif e.GetName() == "DiagramHasNotThisElement":
                    return CWarningDialog(self.form, _('Wrong element: ') + e.GetParameter(1).GetObject().GetType().GetId()).run()
                else:
                    return CWarningDialog(self.form, e.GetName()).run()
    
    def ActionLoadToolBar(self, widget):
        pass

    # User defined signals
    @event("twProjectView", "add-element")
    @event("mnuItems", "add-element")
    def on_directAdd_element(self, widget, element):
        """
        Add element into a project tree
        
        @param widget:  Widget
        @type widget:   CWidget
        
        @param element: Id (name) of added element
        @type element:  String
        """
        parentElement = self.twProjectView.GetSelectedNode()
        if parentElement == None:
            parentElement = self.twProjectView.GetRootNode()

        ElementType = self.application.GetProject().GetMetamodel().GetElementFactory().GetElement(element)
        ElementObject = CElementObject(ElementType)
        self.twProjectView.AddElement(ElementObject, None, parentElement)

    @event("picDrawingArea", "add-element")
    def on_add_element(self, widget, Element, diagram, parentElement):
        self.twProjectView.AddElement(Element, diagram, parentElement)

    @event("mnuItems", "create-diagram")
    @event("twProjectView","create-diagram")
    def on_mnuItems_create_diagram(self, widget, diagramId):
        diagram = CDiagram(self.application.GetProject().GetMetamodel().GetDiagramFactory().GetDiagram(diagramId))
        self.twProjectView.AddDiagram(diagram)
        self.nbTabs.AddTab(diagram)
        self.picDrawingArea.SetDiagram(diagram)
        self.tbToolBox.SetButtons(diagramId)

    @event("picDrawingArea", "get-selected")
    def on_picDrawingArea_get_selected(self, widget):
        return self.tbToolBox.GetSelected()

    @event("twProjectView", "selected_diagram")
    def on_select_diagram(self, widget, diagram):
        self.nbTabs.AddTab(diagram)
        self.picDrawingArea.SetDiagram(diagram)

    @event("twProjectView", "close-diagram")
    def on_remove_diagram(self, widget, diagram):
        self.nbTabs.CloseTab(diagram)

    @event("nbTabs", "change_current_page")
    def on_change_diagram(self, widget, diagram):
        if diagram is None:
            self.tbToolBox.SetButtons(None)
            self.UpdateMenuSensitivity(diagram = False)
        else:
            self.picDrawingArea.SetDiagram(diagram)
            self.tbToolBox.SetButtons(diagram.GetType().GetId())
            self.UpdateMenuSensitivity(diagram = True)
    
    @event("nbTabs","show-diagram-in-project")
    def on_show_diagram_in_project(self, widget, diagram):
        self.twProjectView.ShowDiagram(diagram)
    
    @event("picDrawingArea", "set-selected")
    def on_picDrawingArea_set_selected(self, widget, selected):
        self.tbToolBox.SetSelected(selected)

    @event("picDrawingArea", "selected-item")
    def on_picDrawingArea_selected_item(self, widget, selected):
        self.UpdateMenuSensitivity(element = len(selected) > 0)
        if len(selected) == 1:
            self.nbProperties.Fill(selected[0])
        else:
            self.nbProperties.Fill(None)

    @event("picDrawingArea","delete-element-from-all")
    def on_picDrawingArea_delete_selected_item(self, widget, selected):
        self.twProjectView.DeleteElement(selected)

    @event("twProjectView", "selected-item-tree")
    def on_twTreeView_selected_item(self, widget, selected):
        self.picDrawingArea.Diagram.DeselectAll()
        self.picDrawingArea.Paint()
        self.nbProperties.Fill(selected)

    @event("twProjectView", "repaint")
    def on_repaint_picDravingArea(self, widget):
        self.picDrawingArea.Paint()
    
    @event("twProjectView","selected_diagram_and_select_element")
    def on_select_diagram_and_element(self, widget, diagram, object):
        self.picDrawingArea.SetDiagram(diagram)
        self.nbTabs.AddTab(diagram)
        diagram.AddToSelection(diagram.HasElementObject(object))
        self.picDrawingArea.Paint()
    
    @event("twProjectView","show_frmFindInDiagram")
    def on_show_frmFindInDiagram(self, widget, diagrams, object):
        diagram = self.application.GetWindow('frmFindInDiagram').ShowDialog(diagrams, object)
        
        if diagram is not None:
            self.picDrawingArea.SetDiagram(diagram)
            self.nbTabs.AddTab(diagram)
            diagram.AddToSelection(diagram.HasElementObject(object))
            self.picDrawingArea.Paint()

    @event('application.bus', 'content-update')
    def on_nbProperties_content_update(self, widget, element, property):
        if isinstance(element, CDiagram):
            self.twProjectView.UpdateElement(element)
            self.nbTabs.RefreshTab(element)
        else:
            if element.GetObject().HasVisualAttribute(property):
                self.picDrawingArea.Paint()
                self.twProjectView.UpdateElement(element.GetObject())

    @event("tbToolBox", "toggled")
    def on_tbToolBox_toggled(self, widget, ItemId, ItemType):
        self.picDrawingArea.ResetAction()
        
    @event("picDrawingArea","drop-from-treeview")
    def on_drop_from_treeview(self, widget, position):
        node = self.twProjectView.GetSelectedNode()
        if node is not None:
            diagram = self.picDrawingArea.GetDiagram()
            try:
                Element = CElement(diagram, node.GetObject()).SetPosition(position)
                self.UpdateMenuSensitivity()
            except UserException, e:
                if e.GetName() == "ElementAlreadyExists":
                    return CWarningDialog(self.form, _('Unable to insert element')).run()
                elif e.GetName() == "DiagramHaveNotThisElement":
                    return CWarningDialog(self.form, _('Wrong element: ') + node.GetObject().GetType().GetId()).run()
                else:
                    return CWarningDialog(e.GetName()).run()
            
    
    @event('application.bus', 'run-dialog')
    @event("picDrawingArea", "run-dialog")
    def on_run_dialog(self, widget, type, message):
        if type == 'warning':
            return CWarningDialog(self.form, message).run()
        else:
            pass
    
    @event("picDrawingArea","show-element-in-treeView")
    def on_show_element_in_treeView(self, widget, Element):
        self.twProjectView.ShowElement(Element)
    
    @event("picDrawingArea","open-specification")
    def on_show_open_specification(self, widget, Element):
        tmp = self.application.GetWindow('frmProperties')
        tmp.SetParent(self.application.GetWindow('frmMain'))
        tmp.ShowProperties('', Element, self.picDrawingArea)
        self.picDrawingArea.Paint()
    
    #Z-Order 
    # 'mmShift_SendBack', 'mmShift_BringForward', 'mmShift_ToBottom', 'mmShift_ToTop'    
    @event("mmShift_SendBack", "activate")
    def on_mnuItems_mmShift_SendBack(self, menuItem):
        self.picDrawingArea.Shift_activate('SendBack')
        
    @event("mmShift_BringForward", "activate")
    def on_mnuItems_mmShift_BringForward(self, menuItem):
        self.picDrawingArea.Shift_activate('BringForward')
        
    @event("mmShift_ToBottom", "activate")
    def on_mnuItems_mmShift_ToBottom(self, menuItem):
        self.picDrawingArea.Shift_activate('ToBottom')
        
    @event("mmShift_ToTop", "activate")
    def on_mnuItems_mmShift_ToTop(self, menuItem):
        self.picDrawingArea.Shift_activate('ToTop')        

    @event("picDrawingArea.picEventBox", "scroll-event")
    def on_picEventBox_scroll_event(self, widget, event):
        if (event.state & gtk.gdk.CONTROL_MASK):
            self.UpdateMenuSensitivity()


