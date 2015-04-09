from itertools import chain
from lib.Addons.Metamodel.Modifications.ElementModificationMerger import CElementModificationMerger
from lib.Addons.Metamodel.ModifiedMetamodel import CModifiedMetamodel
from lib.Domains.ModifiedFactory import CModifiedDomainFactory
from lib.Domains.ModifiedType import CModifiedDomainType
from lib.Elements import CElementAlias
from lib.Elements.ModifiedType import CModifiedElementType


class CModifiedMetamodelBuilder(object):

    __elementModificationMerger = CElementModificationMerger()

    def BuildMetamodel(self, elementNode, modificationBundles, parentMetamodel = None):
        if parentMetamodel is None:
            parentMetamodel = elementNode.GetObject().GetType().GetMetamodel()

        elementTypeModifications = self.__GetElementTypeModifications(modificationBundles)
        if parentMetamodel.IsModified():
            inheritedElementTypeModifications = self.__GetElementTypeModifications(parentMetamodel.GetModificationBundles())

            elementTypeModifications = self.__elementModificationMerger.MergeModifications(inheritedElementTypeModifications, elementTypeModifications)

        modifiedMetamodel = CModifiedMetamodel(parentMetamodel, elementNode, elementTypeModifications, modificationBundles)

        modifiedElementFactory = modifiedMetamodel.GetElementFactory()

        # similar algorithm as above for creating element object <-> type mappings
        # - encapsulate types from elementTypes with new element factory
        # - if there are modifications for given element type, stop and process them:
        #   - create modified domain factory
        #   - create modified domain types
        # - replace types in elementTypes with the new, modified types

        for elementType in parentMetamodel.GetElementFactory().IterTypes():
            id = elementType.GetId()
            if isinstance(elementType, CElementAlias):
                continue

            modifiedElementType = CModifiedElementType(elementType, modifiedElementFactory)
            modifiedElementFactory.AddType(modifiedElementType)

            domainfactory = elementType.GetDomain().GetFactory()
            if elementTypeModifications.has_key(id):
                modifications = elementTypeModifications[id]

                domainfactory = CModifiedDomainFactory(elementType.GetDomain().GetFactory())
                self.__CreateModifiedDomainTypes(domainfactory, modifications)

            modifiedElementType.SetDomain(domainfactory.GetDomain(elementType.GetDomain().GetName()))

        return modifiedMetamodel

    def __GetElementTypeModifications(self, modificationBundles):
        modifications = {}
        for bundle in modificationBundles.itervalues():
            modifications.update(bundle.GetElementModifications())
        return modifications

    def __CreateModifiedDomainTypes(self, factory, domainModifications):
        for name, modifications in domainModifications.iteritems():
            domain = CModifiedDomainType(factory.GetDomain(name), factory, modifications)
            factory.AddDomain(domain)