#!/usr/bin/env python
# coding=utf-8

from com.pnfsoftware.jeb.core import RuntimeProjectUtil
from com.pnfsoftware.jeb.core.units.code import ICodeUnit
from com.pnfsoftware.jeb.core.units import IXmlUnit
import re


class Helper:
    COMPONENT_ACTIVITY = 0
    COMPONENT_SERVICE = 1
    COMPONENT_PROVIDER = 2
    COMPONENT_RECEIVER = 3
    COMPONENT_ALL = 4
    
    def __init__(self, project):
        self.prj = project
        self.exported = {} 
        self.components = {}
    
    def getComponentClasses(self, component, exported=None):
        ClassAppendix = {
            Helper.COMPONENT_ACTIVITY: "Activity",
            Helper.COMPONENT_SERVICE: "Service",
            Helper.COMPONENT_PROVIDER: "Provider",
            Helper.COMPONENT_RECEIVER: "Receiver"
        }
        
        assert component in ClassAppendix
        
        compname = ClassAppendix[component].lower()
        self.codeUnit = RuntimeProjectUtil.findUnitsByType(self.prj, ICodeUnit, False)[0]
        classes = self.codeUnit.getClasses()
        ret = []
        for cls in classes:
            name = cls.getName(True)
            if component == Helper.COMPONENT_ALL:
                if not re.match(r'.*(Activity|Service|Provider|Receiver)$', name):
                    continue

            elif not name.endswith(ClassAppendix[component]):
                continue
            
            if exported == None:
                ret.append(cls)

            elif exported == True:
                if self.isComponentExported(compname, cls):
                    ret.append(cls)

            elif not self.isComponentExported(compname, cls):
                ret.append(cls)
        
        return ret
    
    def checkManifest(self, component, cls):
        if component not in self.components:
            self.components[component] = self.getComponentNames(component)
        
        cls_name = self.getClassPath(cls)
        return cls_name in self.components[component]

    def checkExported(self, component, cls, expect):
        res = self.isComponentExported(component, cls)
        if expect:
            return res
        else:
            return not res

    def isComponentExported(self, component, cls):
        component = component.lower()
        if component not in self.exported:
            self.exported[component] = self.getComponentNames(component, True)

        return self.getClassPath(cls) in self.exported[component]
        
    def isActivityExported(self, activity):
        if 'activity' not in self.exported:
            self.exported['activity'] = self.getExportedActivitys()

        return self.getClassPath(activity) in self.exported['activity']

    def isReceiverExported(self, receiver):
        if 'receiver' not in self.exported:
            self.exported['receiver'] = self.getExportedReceivers()

        return self.getClassPath(receiver) in self.exported['receiver']

    def isServiceExported(self, service):
        if 'service' not in self.exported:
            self.exported['service'] = self.getExportedServices()

        return self.getClassPath(service) in self.exported['service']

    def isProviderExported(self, provider):
        if 'provider' not in self.exported:
            self.exported['provider'] = self.getExportedProviders()

        return self.getClassPath(provider) in self.exported['provider']

    def getExportedActivitys(self):
        return self.getComponentNames('activity', True)
    
    def getExportedReceivers(self):
        return self.getComponentNames('receiver', True)
    
    def getExportedServices(self):
        return self.getComponentNames('service', True)

    def getExportedProviders(self):
        return self.getComponentNames('provider', True)

    def getComponentNames(self, compType, exported=None):
        comps = self.getComponent(compType)
        res = []
        
        if exported == None:
            for comp in comps:
                res.append(comp)
        else:
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

