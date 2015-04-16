from lib.Addons.Metamodel.Modifications.ModificationBundleBuilder import CMetamodelModificationBundleBuilder
from lib.Base.BaseObject import CBaseObject
from lib.Exceptions import MetamodelModificationError


class CProjectNodeModificationBundleBuilder(CBaseObject):

    def __init__(self, projectNode, bundleName):
        self.__projectNode = projectNode
        self.__modificationBundleBuilder = CMetamodelModificationBundleBuilder()
        self.__bundleBuilder = self.__modificationBundleBuilder.CreateBundle(bundleName)
        self.__bundle = None

    def GetNode(self):
        return self.__projectNode

    def ReplaceDomainAttributeBool(self, domain, id, name, default, hidden):
        return self.__ReplaceDomainAttribute(domain, id, {'type': 'bool', 'name': name, 'default': default, 'hidden': hidden})

    def ReplaceDomainAttributeInt(self, domain, id, name, default, hidden, min, max):
        return self.__ReplaceDomainAttribute(domain, id, {'type': 'int', 'name': name, 'default': default, 'hidden': hidden, 'min': min, 'max': max})

    def ReplaceDomainAttributeFloat(self, domain, id, name, default, hidden, min, max):
        return self.__ReplaceDomainAttribute(domain, id, {'type': 'float', 'name': name, 'default': default, 'hidden': hidden, 'min': min, 'max': max})

    def ReplaceDomainAttributeStr(self, domain, id, name, default, hidden, enumValues):
        return self.__ReplaceDomainAttribute(domain, id, {'type': 'str', 'name': name, 'default': default, 'hidden': hidden, 'enum': enumValues})

    def ReplaceDomainAttributeText(self, domain, id, name, default, hidden):
        return self.__ReplaceDomainAttribute(domain, id, {'type': 'text', 'name': name, 'default': default, 'hidden': hidden})

    def RemoveDomainAttribute(self, domain, attributeID):
        self.__CheckBundle()

        self.__bundleBuilder.DeleteDomainAttribute(domain, attributeID)

    def Build(self):
        self.__CheckBundle()

        self.__bundle = self.__modificationBundleBuilder.BuildBundles()[0]
        return self.__bundle

    def __ReplaceDomainAttribute(self, domain, attributeID, attributeProperties):
        self.__CheckBundle()

        self.__bundleBuilder.ReplaceDomainAttribute(domain, attributeID, attributeProperties)

    def __CheckBundle(self):
        if self.__bundle:
            raise MetamodelModificationError("Modification bundle {0} was already built, it cannot be modified".format(
                self.__bundle.GetName()))