#? name=Rename Obfuscated Classes, shortcut=Ctrl+Shift+R, author=Masata Nishida
# JEB sample script
# http://www.android-decompiler.com/
#
# RenameObfuscatedClasses.py
# Rename obfuscated class names.
#
# Copyright (c) 2013 SecureBrain
import re

from com.pnfsoftware.jeb.client.api import IScript
from com.pnfsoftware.jeb.core import RuntimeProjectUtil
from com.pnfsoftware.jeb.core.units.code import ICodeUnit
from com.pnfsoftware.jeb.core.actions import Actions, ActionContext
from com.pnfsoftware.jeb.core.actions import ActionRenameData
from com.pnfsoftware.jeb.client.api import IGraphicalClientContext


class RenameObfuscatedClasses(IScript):
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

        self.dex = codeUnits[0]
        self.jeb = ctx
        # ui = j.getUI()

        # rename obfuscated class names
        self.rename_classes()

    def rename_classes(self):
        classes = self.dex.getClasses()
        for cls in classes:
            cls_name = cls.getSignature(True)
            ret = self.rename_by_super_class(cls)
            ret2 = self.rename_by_accessor(cls)
            ret3 = self.rename_by_interfaces(cls)
            ret = ret or ret2 or ret3

            if ret:
                new_name = cls.getSignature(True)
                print "rename from '%s' to '%s'" % (cls_name, new_name)


    def append_cls_name(self, cls, append_str):
        p = re.compile("^.*\/([\w$-]+);$")
        # cls_name has package path
        cls_name = cls.getSignature(True)
        if cls_name.find(append_str) == -1:
            s = re.search(p, cls_name)
            if not s:
                return False

            simple_new_name = s.group(1) + '_' + append_str

            actCntx = ActionContext(self.dex, Actions.RENAME, cls.getItemId(), cls.getAddress())
            actData = ActionRenameData()
            actData.setNewName(simple_new_name)

            if self.dex.prepareExecution(actCntx, actData):
                try:
                    bRlt = self.dex.executeAction(actCntx, actData)
                    if(not bRlt):
                        print(u'executeAction fail!')
                        return False

                    else:
                        return True

                except Exception,e:
                    return self.jeb.renameClass(cls_name, simple_new_name)
            else:
                return False

    def rename_by_super_class(self, cls):
        rename_targets = {
            'Landroid/app/Service;': 'Service',
            'Landroid/app/Activity;': 'Activity',
            'Landroid/content/BroadcastReceiver;': 'Receiver',
            'Landroid/content/ContentProvider;': 'Provider',
            'Ljava/lang/Thread;': 'Thread',
            'Landroid/os/AsyncTask;': 'AsyncTask',
            'Ljava/util/TimerTask;': 'TimerTask',
            'Landroid/database/sqlite/SQLiteDatabase;': 'SQLiteDatabase',
            'Landroid/database/sqlite/SQLiteOpenHelper;': 'SQLiteOpenHelper',
            'Landroid/database/ContentObserver;': 'ContentObserver',
            'Landroid/os/Handler;': 'Handler',
        }
        super_cls_type = cls.getClassType()
        if super_cls_type in rename_targets.keys():
            val = rename_targets[super_cls_type]
            self.append_cls_name(cls, val)
            return True
        else:
            return False

    def rename_by_accessor(self, cls):
        flg = cls.getAccessFlags()
        ret = False
        if flg & 0x200:
            self.append_cls_name(cls, 'Interface')
            ret = True
        if flg & 0x400:
            self.append_cls_name(cls, 'Abstract')
            ret = True
        if flg & 0x4000:
            self.append_cls_name(cls, 'Enum')
            ret = True
        return ret


    def rename_by_interfaces(self, cls):
        ret = False
        for interface in cls.getImplementedInterfaces():
            if_name = interface.getSignature(True)
            if if_name.endswith('ClickListener;'):
                self.append_cls_name(cls, 'ClickListener')
                ret = True
            if if_name.endswith('CancelListener;'):
                self.append_cls_name(cls, 'CancelListener')
                ret = True
            if if_name == 'Ljava/lang/Runnable;':
                self.append_cls_name(cls, 'Runnable')
                ret = True
            if if_name == 'Landroid/os/IInterface;':
                self.append_cls_name(cls, 'IInterface')
                ret = True

        return ret
