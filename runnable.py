from os import path
from javadoc_parser import *
from wikibuilder import *

def mapwiki():
    APPNAME = 'testapp'
    REPODIR = path.join(path.dirname(path.realpath(__file__)), APPNAME)
    
    graph = JavadocGraph(REPODIR)
APPNAME = 'testapp'
REPODIR = path.join(path.dirname(path.realpath(__file__)), APPNAME)

if __name__ == "__main__":
    
    graph = JavadocGraph(REPODIR)

    wikidir = os.path.join(REPODIR, (APPNAME + '.wiki'))
    wiki = Wiki(graph, wikidir)
    def genClass(classNode, pre):
        for methodNode in graph.getMethods(classNode):
            wiki.buildMethod(methodNode)
        for fieldNode in graph.getFields(classNode):
            wiki.buildField(fieldNode)
        for innerClassNode in graph.getInnerClasses(classNode):
            wiki.buildInnerClass(innerClassNode)
            genClass(innerClassNode, "{}\t".format(pre))
    
    for topLevelClass in graph.getTopLevelClasses():
        wiki.buildClass(topLevelClass)
        genClass(topLevelClass, '')
        wiki.createPage()

