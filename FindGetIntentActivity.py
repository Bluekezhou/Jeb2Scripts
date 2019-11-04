from com.pnfsoftware.jeb.client.api import IScript, IGraphicalClientContext
from com.pnfsoftware.jeb.core import RuntimeProjectUtil
from com.pnfsoftware.jeb.core.actions import Actions, ActionContext, ActionXrefsData
from com.pnfsoftware.jeb.core.units.code import ICodeUnit, ICodeItem
from com.pnfsoftware.jeb.core.units import IXmlUnit
from com.pnfsoftware.jeb.core.actions import ActionRenameData
from Utils import Helper


# show exported activities or not
show_exported = False

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
        self.helper = Helper(self.prj)
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

        def activity_filter(cls):
            name =cls.getName(True)
            # if not name.endswith('Activity'):
            if not name.endswith('Activity'):
                return False
            
            if not self.helper.checkManifest('activity', cls):
                return False

            return self.helper.checkExported('activity', cls, show_exported)

        classes = filter(activity_filter, classes)
        intent_count = 0
        webview_count = 0
        for cls in classes:
            calls = self.findGetIntent(cls)
            if not calls:
                continue
            
            intent_count += 1
            flag = False
            for f in cls.getFields():
                if not self.isSuperWebview(f):
                    continue

                fieldType = f.getFieldType().getName(True)
                print(fieldType.center(len(fieldType) + 10, ' ').center(80, '-'))
                print(f.getAddress())
                if not flag:
                    webview_count += 1
                    flag = True

            for call in calls:
                print(call.getSignature(True))
        
        print("%d Activity contain intent, %d contain webview among them " % 
              (intent_count, webview_count))
    
    def isSuperWebview(self, field):
        rootTypes = self.getRootSuperClass(field.getFieldType())
        for t in rootTypes:
            if t.getName(True) == 'WebView':
                return True

        return False

    def getRootSuperClass(self, atype):
        supers = self.getTypeSuperTypes(atype)
        ret = []
        
        while supers:
            curtype = supers.pop()
            curtype_supers = self.getTypeSuperTypes(curtype)
            if curtype_supers:
                supers.extend(curtype_supers)
            else:
                ret.append(curtype)

        return ret
    
    def getTypeSuperTypes(self, atype):
        aclass = atype.getImplementingClass()
        if not aclass:
            return []
        
        return self.getClassSupertypes(aclass)

    def getClassSupertypes(self, cls):
        res = []
        try:
            supers = cls.getSupertypes()
            res.extend(supers)
        except Exception as e:
            print(e)

        return res

    def getClassPath(self, cls):
        sign = cls.getSignature(True)
        path = sign[1:-1]
        path = path.replace('/', '.')
        return path

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
