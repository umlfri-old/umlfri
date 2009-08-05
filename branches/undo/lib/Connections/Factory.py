from lib.Depend.etree import etree, HAVE_LXML

import os
import os.path
from lib.Exceptions.DevException import *
from Type import CConnectionType
from Line import CConnectionLine
from Arrow import CConnectionArrow
from lib.consts import METAMODEL_NAMESPACE
from lib.Drawing.Objects import ALL
from lib.config import config

#if lxml.etree is imported successfully, we use xml validation with xsd schema
if HAVE_LXML:
    xmlschema_doc = etree.parse(os.path.join(config['/Paths/Schema'], "metamodel.xsd"))
    xmlschema = etree.XMLSchema(xmlschema_doc)


class CConnectionFactory(object):
    """
    Creates connection types from metamodel XMLs
    """
    def __init__(self, storage, path, domainfactory):
        """
        Parse metamodel XMLs and creates connection types
        
        @param storage: Storage in which is file located
        @type  storage: L{CAbstractStorage<lib.Storages.AbstractStorage.CAbstractStorage>}
        
        @param path: Path to directory with connection metamodel XMLs
        @type path: string
        """
        self.types = {}
        self.path = path
        self.domainfactory = domainfactory
        
        self.storage = storage
        for file in storage.listdir(self.path):
            if file.endswith('.xml'):
                self.__Load(os.path.join(self.path, file))

    def GetConnection(self, type):
        """
        Gets connection type by its name
        
        @param type: Name of connection type
        @type  type: string
        
        @return: Connection type of given name
        @rtype:  L{CConnectionType<Type.CConnectionType>}
        """
        if not type in self.types:
            raise FactoryError('unrecognized connectionType name "%s"' % type)
        return self.types[type]
    
    def IterTypes(self):
        '''
        iterator over connection types
        
        @rtype: L{CConnectionType<CConnectionType>}
        '''
        for type in self.types.itervalues():
            yield type
            
    def __Load(self, file_path):
        """
        Load an XMLs from given path
        
        @param file_path: Path to connections metamodel (within storage)
        @type  file_path: string
        """
        
        root = etree.XML(self.storage.read_file(file_path))

        #xml (version) file is validate with xsd schema (metamodel.xsd)
        if HAVE_LXML:
            if not xmlschema.validate(root):
                raise FactoryError("XMLError", xmlschema.error_log.last_error)

        id = root.get('id')
        
        sarr = {}
        darr = {}
        ls = {}
        icon = None
        labels = []
        attrs = []
        domain = None
        identity = None
        for element in root:
            if element.tag == METAMODEL_NAMESPACE+'Icon':
                icon = element.get('path')
            elif element.tag == METAMODEL_NAMESPACE+'SrcArrow':
                sarr['possible'] = element.get('possible')
                sarr['default'] = element.get('default')
            elif element.tag == METAMODEL_NAMESPACE+'DestArrow':
                darr['possible'] = element.get('possible')
                darr['default'] = element.get('default')
            elif element.tag == METAMODEL_NAMESPACE+'Domain':
                domain = self.domainfactory.GetDomain(element.get('id'))
                identity = element.get('identity')
            elif element.tag == METAMODEL_NAMESPACE+'Appearance':
                for subelem in element:
                    if subelem.tag == METAMODEL_NAMESPACE+'LineStyle':
                        ls['color'] = subelem.get('color')
                        ls['style'] = subelem.get('style')
                        if subelem.get('width') is not None:
                            ls['width'] = subelem.get('width')
                    elif subelem.tag == METAMODEL_NAMESPACE+'ArrowStyle':
                        darr['fill'] = sarr['fill'] = subelem.get('fill')
                        darr['color'] = sarr['color'] = subelem.get('color')
                        darr['style'] = sarr['style'] = subelem.get('style')
                        if subelem.get('size') is not None:
                            darr['size'] = sarr['size'] = subelem.get('size')
                    elif subelem.tag == METAMODEL_NAMESPACE+'Label':
                        tmp = None
                        for k in subelem:
                            tmp = k
                        labels.append((subelem.get('position'), self.__LoadAppearance(tmp)))

        tmp = self.types[id] = CConnectionType(id, CConnectionLine(**ls),
                                    CConnectionArrow(**sarr), CConnectionArrow(**darr), icon, domain, identity)
        for pos, lbl in labels:
            tmp.AddLabel(pos, lbl)
        
    def __LoadAppearance(self, root):
        """
        Loads an appearance section of an XML file
        
        @param root: Appearance element
        @type  root: L{Element<lxml.etree.Element>}
        
        @return: Visual object representing this section
        @rtype:  L{CVisualObject<lib.Drawing.Objects.VisualObject.CVisualObject>}
        """

        if root.tag.split("}")[1] not in ALL:
            raise FactoryError("XMLError", root.tag)
        
        cls = ALL[root.tag.split("}")[1]]
        params = {}
        for attr in root.attrib.items():
            params[attr[0]] = attr[1]
        obj = cls(**params)
        if hasattr(obj, "LoadXml"):
            obj.LoadXml(root)
        else:
            for child in root:
                obj.AppendChild(self.__LoadAppearance(child))
        return obj