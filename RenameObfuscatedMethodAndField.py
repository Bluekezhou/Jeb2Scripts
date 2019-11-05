#? name=Rename Obfuscated Classes, shortcut=Ctrl+Shift+R, author=Masata Nishida
# JEB sample script
# http://www.android-decompiler.com/
#
# RenameObfuscatedMethodAndField.py
# Rename obfuscated method and field names.
# 
# Run in Jeb2 API.
# 
# Copyright (c) 2013 SecureBrain
import re

from com.pnfsoftware.jeb.client.api import IScript
from com.pnfsoftware.jeb.core import RuntimeProjectUtil
from com.pnfsoftware.jeb.core.units.code import ICodeUnit
from com.pnfsoftware.jeb.core.actions import Actions, ActionContext
from com.pnfsoftware.jeb.core.actions import ActionRenameData
import string


class RenameObfuscatedMethodAndField(IScript):
    METHOD = 1
    FIELD = 2

    def run(self, ctx):
        engctx = ctx.getEnginesContext()
        if not engctx:
            print('Back-end engines not initialized')
            return

        prj = engctx.getProject(0)
        if not prj:
            print('There is no opened project')
            return

        codeUnits = RuntimeProjectUtil.findUnitsByType(prj, ICodeUnit, False)
        if not codeUnits:
            return

        self.unit = codeUnits[0]
        self.ctx = ctx

        # rename obfuscated names
        classes = self.unit.getClasses()
        for cls in classes:
            self.deobfuscate(cls, RenameObfuscatedMethodAndField.METHOD)
            self.deobfuscate(cls, RenameObfuscatedMethodAndField.FIELD)

    def deobfuscate(self, cls, nType):
        if nType == RenameObfuscatedMethodAndField.METHOD:
            objs = cls.getMethods()
        elif nType == RenameObfuscatedMethodAndField.FIELD:
            objs = cls.getFields()
        else:
            print("Unknown name type")
            return

        if not objs:
            return

        names = [o.getName(True) for o in objs]
        count = 1
        for o in objs:
            sign = o.getSignature(True)
            name = o.getName(True)
            if re.search('[a-zA-Z]+', name):
                continue

            while True:
                new_name = self.gen_name(count)
                count += 1
                if new_name not in names:
                    break

            if self.rename(o, new_name):
                print(u'rename ' + sign + u' to ' + new_name)

    def gen_name(self, count):
        out = u''
        
        while count:
            out += string.ascii_lowercase[count % 26]
            count /= 52

        return out
    
    def rename(self, obj, new_name):
        actCntx = ActionContext(self.unit, Actions.RENAME, obj.getItemId(), obj.getAddress())
        actData = ActionRenameData()
        actData.setNewName(new_name)

        if self.unit.prepareExecution(actCntx, actData):
            try:
                res = self.unit.executeAction(actCntx, actData)
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
