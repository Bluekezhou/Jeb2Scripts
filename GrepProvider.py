from com.pnfsoftware.jeb.client.api import IScript, IGraphicalClientContext
from com.pnfsoftware.jeb.core import RuntimeProjectUtil
from com.pnfsoftware.jeb.core.actions import Actions, ActionContext, ActionXrefsData
from com.pnfsoftware.jeb.core.units.code import ICodeUnit
from com.pnfsoftware.jeb.core.units import IXmlUnit
from Utils import Helper


show_exported = False

class GrepProvider(IScript):

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
        helper = Helper(prj)
        print('Decompiling code units of %s...' % prj)
        
        providers = helper.getComponentClasses('Provider', show_exported)

        for p in providers:
            print(p.getAddress())
