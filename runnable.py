from os import path
from javadoc_parser import *
from wikibuilder import *

APPNAME = 'testapp'
REPODIR = path.join(path.dirname(path.realpath(__file__)), APPNAME)

'''
Instantiate and build the custom wiki
'''
def buildWiki(javadocs=None):
    wikidir = os.path.join(REPODIR, (APPNAME + '.wiki'))
    wiki = Wiki(wikidir)
    
    if javadocs:
        wiki.buildGraph(javadocs)
        wiki.buildDocs(javadocs)

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
    #print getClasses(open(path.join(REPODIR, 'Test.java'), 'r'))
    '''
    for javadoc in getJavadocs(open(path.join(REPODIR, 'Test.java'), 'r')):
        print javadoc
    '''
    '''
    for javadoc in genJavadocGraph(REPODIR):
        print javadoc
    '''
    graph = JavadocGraph(REPODIR)
    for javadoc in graph.getTopLevelClasses():
        methods = list(graph.getMethods(javadoc))
        if len(methods) > 0:
            print "Class",javadoc.getSourceLine().getName()
            for javadocMethod in methods:
                print "Method", javadocMethod.getSourceLine().getName()
