from lib.Addons.Metamodel.Modifications.MetamodelModification import CMetamodelModification
from lib.Addons.Metamodel.Modifications.ModificationTreeBuilder import CModificationTreeBuilder
from lib.Domains.Modifications import CReplaceAttributeModification
from lib.Domains.Modifications.DeleteAttributeModification import CDeleteAttributeModification


class CElementModificationBuilder:
    def __init__(self, projectNode):
        self.projectNode = projectNode
        self.elementTypeModifications = {}

    def AddDomainAttribute(self, elementType, domain, attributeID, attributeProperties):
        self.ReplaceDomainAttribute(elementType, domain, attributeID, attributeProperties)

    def ReplaceDomainAttribute(self, elementType, domain, attributeID, attributeProperties):
        self.__AppendDomainAttributeModification(elementType, domain,
                                                 CReplaceAttributeModification(attributeID, attributeProperties))

    def DeleteDomainAttribute(self, elementType, domain, attributeID):
        self.__AppendDomainAttributeModification(elementType, domain,
                                                 CDeleteAttributeModification(attributeID))

    def GetElementTypeModifications(self):
        return self.elementTypeModifications

    def Build(self):
        objectTypeMapping = CModificationTreeBuilder(self.projectNode,
                                                     self.elementTypeModifications).BuildTree()

        return CMetamodelModification(objectTypeMapping)

    def __AppendDomainAttributeModification(self, elementType, domain, modification):
        modifications = self.__GetElementTypeModifications(elementType)
        list = modifications.setdefault(domain, [])
        list.append(modification)

    def __GetElementTypeModifications(self, elementType):
        return self.elementTypeModifications.setdefault(elementType, {})
