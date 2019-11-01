#!/usr/bin/env python
# coding=utf-8

from com.pnfsoftware.jeb.core.units import IXmlUnit
from com.pnfsoftware.jeb.core import RuntimeProjectUtil


class Helper:
    def __init__(self, project):
        self.prj = project
        self.exported = {} 
    
    def isReceiverExported(self, receiver):
        if 'receiver' not in self.exported:
            self.exported['receiver'] = self.getExportedReceivers()

        return self.getClassPath(receiver) in self.exported['receiver']

    def getExportedReceivers(self):
        return self.getComponentNames('receiver', True)
    
    def isServiceExported(self, service):
        if 'service' not in self.exported:
            self.exported['service'] = self.getExportedServices()

        return self.getClassPath(service) in self.exported['service']

    def getExportedServices(self):
        return self.getComponentNames('service', True)

    def getComponentNames(self, compType, exported):
        comps = self.getComponent(compType)
        res = []
        for comp in comps:
            if comps[comp]['exported'] == exported:
                res.append(comp)
        return res

    def getComponent(self, component):
        doc = self.getTargetDoc("Manifest")
        
        root = doc.getElementsByTagName('manifest').item(0)
        package = root.getAttribute('package')

        elements = doc.getElementsByTagName(component)
        components = {}
        for i in range(elements.getLength()):
            node = elements.item(i)
            attr = {
                'exported': self.toBoolean(node.getAttribute("android:exported"))
            }
            
            name = node.getAttribute("android:name")
            if name.startswith('.'):
                name = package + name

            components[name] = attr

        return components

    def toBoolean(self, value):
        if value == 'false':
            return False
        elif value == 'true':
            return True
        else:
            return None

    def getTargetDoc(self, targetXML):
        units = RuntimeProjectUtil.findUnitsByType(self.prj, IXmlUnit, False)
        for unit in units:
            if not unit.isProcessed():
                unit.process()
            if unit.getName() == targetXML:
                doc = unit.getDocument()
                return doc
        return None       

    def getClassPath(self, cls):
        sign = cls.getSignature(True)
        path = sign[1:-1]
        path = path.replace('/', '.')
        return path

