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
    files = getFiles(REPODIR)
    javadocs = collateData(files)
    buildWiki(javadocs)
