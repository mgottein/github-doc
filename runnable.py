from os import path
from javadoc_parser import *
from wikibuilder import *

APPNAME = 'testapp'
REPODIR = path.join(path.dirname(path.realpath(__file__)), APPNAME)

'''
Generate the wiki structure
'''
def generateGraph():
    graph = JavadocGraph(REPODIR)
    
    wikidir = os.path.join(REPODIR, (APPNAME + '.wiki'))
    wiki = Wiki(wikidir)
    
    def genClass(classNode):
        wiki.buildClass(classNode)
        wiki.addToHomePage(classNode, 0)
        for methodNode in graph.getMethods(classNode):
            wiki.buildMethod(methodNode, classNode)
            wiki.addToHomePage(methodNode, 1)
        for fieldNode in graph.getFields(classNode):
            wiki.buildField(fieldNode, classNode)
            wiki.addToHomePage(fieldNode, 2)
        for innerClassNode in graph.getInnerClasses(classNode):
            genClass(innerClassNode)
    
    for topLevelClass in graph.getTopLevelClasses():
        genClass(topLevelClass)

if __name__ == '__main__':
    generateGraph()