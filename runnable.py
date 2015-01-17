from os import path
from javadoc_parser import *
from wikibuilder import *

APPNAME = 'testapp'
REPODIR = path.join(path.dirname(path.realpath(__file__)), APPNAME)

'''
Return project readme file
'''
def getReadme():
    readmeFile = open(path.join(REPODIR, 'README.md'), 'r')
    readme = readmeFile.read()
    readmeFile.close()
    return readme

'''
Parse project javadocs and read data
'''
def collateData(files):
    for file in files:
        javadocs = []
        for javadoc in getJavadocs(open(file, 'r')):
            javadocs.append(javadoc)
            print javadoc
    return javadocs

if __name__ == '__main__':
    graph = JavadocGraph(REPODIR)
    
    wikidir = os.path.join(REPODIR, (APPNAME + '.wiki'))
    wiki = Wiki(wikidir)
    
    def genClass(classNode):
        wiki.buildClass(classNode)
        for methodNode in graph.getMethods(classNode):
            wiki.buildMethod(methodNode, classNode)
        for fieldNode in graph.getFields(classNode):
            wiki.buildField(fieldNode, classNode)
        for innerClassNode in graph.getInnerClasses(classNode):
            genClass(innerClassNode)
    
    for topLevelClass in graph.getTopLevelClasses():
        genClass(topLevelClass)
