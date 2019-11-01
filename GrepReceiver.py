from com.pnfsoftware.jeb.client.api import IScript, IGraphicalClientContext
from com.pnfsoftware.jeb.core import RuntimeProjectUtil
from com.pnfsoftware.jeb.core.actions import Actions, ActionContext, ActionXrefsData
from com.pnfsoftware.jeb.core.units.code import ICodeUnit, ICodeItem
from Utils import Helper

config_show_exported = False

class GrepReceiver(IScript):

    def run(self, ctx):
        engctx = ctx.getEnginesContext()
        if not engctx:
            print('Back-end engines not initialized')
            return

        projects = engctx.getProjects()
        if not projects:
            print('There is no opened project')
            return

        prj = projects[0]
        self.helper = Helper(prj)
        print('Decompiling code units of %s...' % prj)

        self.codeUnit = RuntimeProjectUtil.findUnitsByType(prj, ICodeUnit, False)[0]
        classes = self.codeUnit.getClasses()

        for cls in classes:
            if not cls.getName(True).endswith('Receiver'):
                continue

            if config_show_exported:
                if not self.helper.isReceiverExported(cls):
                    continue
            elif self.helper.isReceiverExported(cls):
                continue
            
            print(cls.getAddress())
