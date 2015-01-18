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
        def sourceSort(a, b):
            aVal = 1
            bVal = 1
            if "private" in a.getModifiers():
                aVal = 2
            if "private" in b.getModifiers():
                bVal = 2
            if "public" in a.getModifiers():
                aVal = 0
            if "public" in b.getModifiers():
                bVal = 0
            return aVal - bVal
        fields = list(graph.getFields(classNode))
        fields.sort(sourceSort)
        for field in fields:
            wiki.buildField(field)
        methods = list(graph.getMethods(classNode))
        methods.sort(sourceSort)
        for method in methods:
            wiki.buildMethod(method)
        innerClasses = list(graph.getInnerClasses(classNode))
        innerClasses.sort(sourceSort)
        for innerClass in innerClasses:
            wiki.buildInnerClass(innerClass)
            genClass(innerClass, "{}\t".format(pre))
    
    for topLevelClass in graph.getTopLevelClasses():
        wiki.buildClass(topLevelClass)
        genClass(topLevelClass, '')
        wiki.createPage()

