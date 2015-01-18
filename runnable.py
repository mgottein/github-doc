from os import path
from javadoc_parser import *
from wikibuilder import *

APPNAME = 'testapp'
REPODIR = path.join(path.dirname(path.realpath(__file__)), APPNAME)

if __name__ == "__main__":
    graph = JavadocGraph(REPODIR)
    
    wikidir = os.path.join(REPODIR, (APPNAME + '.wiki'))
    wiki = Wiki(wikidir)
    def genClass(classNode, pre):
        #print "{}{}".format(pre, classNode.getSourceLine().getName())
        wiki.buildClass(classNode)
        wiki.addToHomePage(classNode, 0)
        for methodNode in graph.getMethods(classNode):
            wiki.buildMethod(methodNode, classNode)
            #print "{}\t{}".format(pre, methodNode.getSourceLine().getName())
        for fieldNode in graph.getFields(classNode):
            wiki.buildField(fieldNode, classNode)
            #print "{}\t{}".format(pre, fieldNode.getSourceLine().getName())
        for innerClassNode in graph.getInnerClasses(classNode):
            genClass(innerClassNode, "{}\t".format(pre))
    
    for topLevelClass in graph.getTopLevelClasses():
        genClass(topLevelClass, '')
