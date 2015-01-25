class CDiagramType:
    def __init__(self, id):
        self.icon = None
        self.id = id
        self.attributes = {}
        self.attributeList = []
        self.elements = []
        self.connections = []
        self.swimlines = False
        self.lifelines = False
    
    def AppendElement(self, value):
        self.elements.append( value )
        
    def AppendConnection(self, value):
        self.connections.append( value )
        
    def GetConnections(self):
        return self.connections
        
    def GetElements(self):
        return self.elements
    
    def GetIcon(self):
        return self.icon
    
    def GetId(self):
        return self.id
        
    def SetSpecial(self, swimlines, lifelines):
        self.swimlines = swimlines
        self.lifelines = lifelines
        
    def AllowSwimlines(self):
        return self.swimlines
        
    def AllowLifelines(self):
        return self.lifelines
    
    def SetIcon(self, pixbuf):
        self.icon = pixbuf
    
    def SetId(self, id):
        self.id = id
    
    def AppendAttribute(self,name, type, options = []):
        self.attributes[name] = (type, options)
        self.attributeList.append(name)
    
    def GetAttributes(self):
        for i in self.attributeList:
            yield i
    
    def GetAttribute(self, key):
        return self.attributes[key]
    
    def GetDefValue(self, id):
        type, options = self.attributes[id]
        if len(options) > 0:
            temp = options[0]
        else:
            temp = None
        if type == 'int':
            if temp is None:
                return 0
            else:
                return int(temp)
        if type == 'enum':
            if temp is None:
                raise UMLException("ListNoOptions")
            else:
                return str(temp)
        elif type == 'float':
            if temp is None:
                return 0.0
            else:
                return float(temp)
        elif type == 'bool':
            if temp is None:
                return False
            else:
                return ToBool(temp)
        elif type == 'str':
            if temp is None:
                return ""
            else:
                return str(temp)
        elif type == 'note':
            if temp is None:
                return ""
            else:
                return str(temp)