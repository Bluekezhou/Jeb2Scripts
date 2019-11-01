from com.pnfsoftware.jeb.client.api import IScript, IGraphicalClientContext
from com.pnfsoftware.jeb.core import RuntimeProjectUtil
from com.pnfsoftware.jeb.core.actions import Actions, ActionContext, ActionXrefsData
from com.pnfsoftware.jeb.core.units.code import ICodeUnit, ICodeItem
from com.pnfsoftware.jeb.core.units import IXmlUnit
from com.pnfsoftware.jeb.core.actions import ActionRenameData

# Find in exported activities or not
config_find_exported = False

class FindGetIntentActivity(IScript):

    def run(self, ctx):
        engctx = ctx.getEnginesContext()
        if not engctx:
            print('Back-end engines not initialized')
            return

        projects = engctx.getProjects()
        if not projects:
            print('There is no opened project')
            return

        self.prj = projects[0]
        print('Decompiling code units of %s...' % self.prj)

        self.codeUnit = RuntimeProjectUtil.findUnitsByType(self.prj, ICodeUnit, False)[0]
        
        classes = self.codeUnit.getClasses()
        methods = self.codeUnit.getMethods()
        self.index2method = {}
        for m in methods:
            if m in self.index2method:
                print('repeated method index')
                return

            self.index2method[m.getIndex()] = m

        activities = self.getActivityByExported(config_find_exported)
        def activity_filter(cls):
            name =cls.getName(True)
            if not name.endswith('Activity'):
                return False
            
            path = self.getClassPath(cls)
            return path in activities

        classes = filter(activity_filter, classes)
        
        for cls in classes:
            
            calls = self.findGetIntent(cls)
            if calls:
                for f in cls.getFields():
                    fieldType = f.getFieldType().getName(True)
                    if 'webview' in fieldType.lower():
                        print(fieldType.center(len(fieldType) + 10, ' ').center(60, '-'))
                        self.append_type(f, fieldType)

                for call in calls:
                    print(call.getSignature(True))

    
    def getClassPath(self, cls):
        sign = cls.getSignature(True)
        path = sign[1:-1]
        path = path.replace('/', '.')
        return path

    def getActivityByExported(self, exported):
        comps = self.getComponent('activity')
        res = []
        for comp in comps:
            if comps[comp]['exported'] == exported:
                res.append(comp)
        return res

    def getComponent(self, component):
        doc = self.getTargetDoc(self.prj, "Manifest")
        
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

        # classes = self.codeUnit.getClasses()

        # for cls in classes:
        #     if cls.getName(True).endswith('Activity') and cls.getName(True) in names:
        #         print(cls.getAddress())

    def toBoolean(self, value):
        if value == 'false':
            return False
        elif value == 'true':
            return True
        else:
            return None

    def getTargetDoc(self, prj, targetXML):
        units = RuntimeProjectUtil.findUnitsByType(prj, IXmlUnit, False)
        for unit in units:
            if not unit.isProcessed():
                unit.process()
            if unit.getName() == targetXML:
                doc = unit.getDocument()
                return doc
        return None       

    def findGetIntent(self, cls):
        methods = cls.getMethods()
        callGetIntentMethods = []
        for m in methods:
            instructions = m.getInstructions()
            if not instructions:
                continue

            for inst in instructions:
                inststr = inst.format(None)
                mid = self.extractMethodIndex(inststr)
                if mid == -1:
                    continue

                invoke_method = self.index2method[mid]
                if 'getIntent' == invoke_method.getName(True):
                    callGetIntentMethods.append(m)

        return callGetIntentMethods

    def extractMethodIndex(self, s):
        if s.startswith('invoke'):
            #print(s)
            i = s.find('method@')
            if i >= 0:
                i += 7
                j = s.find(',', i)                                                                       
                if j < 0:
                    j = len(s)
                return int(s[i:j])
        return -1

    def getMethodXrefs(self, unit, itemId):
        data = ActionXrefsData()
        # careful, with query-type actions, the data is returned after the action prep'
        if unit.prepareExecution(ActionContext(unit, Actions.QUERY_XREFS, itemId, None), data):
            # clean up the DEX address, extrac the method name
            return data.getAddresses()
    
    def append_type(self, obj, otype):
        if not obj.getName(True).endswith(otype):
            new_name = obj.getName(True) + '_' + otype
            self.rename(obj, new_name)

    def rename(self, obj, new_name):
        actCntx = ActionContext(self.codeUnit, Actions.RENAME, obj.getItemId(), obj.getAddress())
        actData = ActionRenameData()
        actData.setNewName(new_name)

        if self.codeUnit.prepareExecution(actCntx, actData):
            try:
                res = self.codeUnit.executeAction(actCntx, actData)
                if not res:
                    print(u'rename failed [new_name %s]' % new_name)
                    return False

                else:
                    return True

            except Exception,e:
                print(e)
                return False
        else:
            return False
