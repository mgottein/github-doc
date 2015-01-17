from os import path
from javadoc_parser import *
from wikibuilder import *

APPNAME = 'testapp'
REPODIR = ''

def buildWiki():
    wikidir = REPODIR + '\\' + APPNAME + '.wiki\\'
    wiki = Wiki(wikidir)
    wiki.create()
    wiki.setTag('title', 'TEST TITLE')
    wiki.setTag('subtitle', 'test subtitle')
    wiki.setTag('readme', getReadme())
    contribs = ['me', 'you', 'bob']
    wiki.setTag('contribs', contribs)
    text = 'This is one line.\n\nThis is another. And another (jk {{ test }}).\nAnd another!'
    wiki.createPage("TEST_PAGE", text)
    wiki.setTag('test', 'UH')

def getReadme():
    readmeFile = open(path.join(REPODIR, 'README.md'), 'r')
    readme = readmeFile.read()
    readmeFile.close()
    return readme

def collateData(repodir):
    for javadoc in getJavadocs(open(path.join(repodir, 'Test.java'), 'r')):
        print javadoc

if __name__ == '__main__':
    REPODIR = path.join(path.dirname(path.realpath(__file__)), APPNAME)
    collateData(REPODIR)
    buildWiki()
