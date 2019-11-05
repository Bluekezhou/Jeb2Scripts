from com.pnfsoftware.jeb.client.api import IScript, IGraphicalClientContext
from com.pnfsoftware.jeb.core import RuntimeProjectUtil
from com.pnfsoftware.jeb.core.actions import Actions, ActionContext, ActionXrefsData
from com.pnfsoftware.jeb.core.units.code import ICodeUnit
from com.pnfsoftware.jeb.core.units import IXmlUnit
from Utils import Helper


show_exported = False

class GrepProvider(IScript):

    def run(self, ctx):
        print("Running Script " + self.__class__.__name__)
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

        print("exported".center(15, ' ').center(60, '-'))
        exported = helper.getComponentClasses(Helper.COMPONENT_PROVIDER, True)
        for s in exported:
            print(s.getAddress())

        print("unexported".center(15, ' ').center(60, '-'))
        unexported = helper.getComponentClasses(Helper.COMPONENT_PROVIDER, False)
        for s in unexported:
            print(s.getAddress())

        print("total %d providers, %d exported" % (len(exported) + len(unexported), 
                                                 len(exported)))       
