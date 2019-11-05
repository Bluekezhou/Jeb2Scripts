from com.pnfsoftware.jeb.client.api import IScript, IGraphicalClientContext
from com.pnfsoftware.jeb.core import RuntimeProjectUtil
from Utils import Helper


class GrepService(IScript):

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
        exported = helper.getComponentClasses(Helper.COMPONENT_SERVICE, True)
        for s in exported:
            print(s.getAddress())

        print("unexported".center(15, ' ').center(60, '-'))
        unexported = helper.getComponentClasses(Helper.COMPONENT_SERVICE, False)
        for s in unexported:
            print(s.getAddress())

        print("total %d services, %d exported" % (len(exported) + len(unexported), 
                                                 len(exported)))
