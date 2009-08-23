from lib.Depend.gtk2 import gobject

class CWidget(gobject.GObject):
    widgets = ()
    complexWidgets = ()
    name = ''
    glade = None
    __allWidgets = {}
    
    def __init__(self, app, wTree):
        gobject.GObject.__init__(self)
        if self.glade is not None:
            if abspath(self.glade) in app.wTrees:
                wTree = app.wTrees[abspath(self.glade)] = gtk.glade.XML(self.glade)
            else:
                wTree = app.wTrees[abspath(self.glade)]
        events = {}
        for fnc in dir(self):
            fnc = getattr(self, fnc)
            if callable(fnc):
                if hasattr(fnc, 'events'):
                    for event in fnc.events:
                        obj, event, params = event
                        if event is None:
                            if obj == 'load':
                                gobject.idle_add(fnc)
                        else:
                            events.setdefault(obj, []).append((event, fnc, params))
        self.application = app
        for widgetName in self.widgets:
            if widgetName in self.__allWidgets:
                raise Exception, '%s cannot be used in %s (allready used in %s)'%(widgetName, self.__class__.__name__, self.__allWidgets[widgetName])
            else:
                self.__allWidgets[widgetName] = self.__class__.__name__
            obj = wTree.get_widget(widgetName)
            if obj is None:
                raise Exception, '%s could not be loaded'%(widgetName, )
            setattr(self, widgetName, obj)
        for widgetClass in self.complexWidgets:
            setattr(self, widgetClass.name, widgetClass(app, wTree))
            
        for obj, oevents in events.iteritems():
            objtxt = obj.split(".")
            obj = getattr(self, objtxt[0])
            for attr in objtxt[1:]:
                try:
                    obj = getattr(obj, attr)
                except AttributeError:
                    obj = obj.get_property(attr)
            for event, fnc, params in oevents:
                #print objtxt
                obj.connect(event, fnc, *params)
        
        self.GetRelativeFile = wTree.relative_file
