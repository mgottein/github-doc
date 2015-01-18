import os
import fileinput
import distutils.core

from markup_formatter import *
from javadoc_parser import *
import markup_formatter
from xml.dom import HierarchyRequestErr

'''
Class to create and customize the Wiki
'''
class Wiki:
    '''
    Initialize wiki with working directory and call create
    '''
    def __init__(self, appname, repodir, graph, wikidir):
        self.appname = appname
        self.repodir = repodir
        self.wikidir = wikidir
        self.graph = graph
        self.create()
        self.pageName = None
        self.text = None
    
    '''
    Copy template files to wiki directory
    '''
    def create(self):      
        src = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'wiki-template')
        dest = self.wikidir
        if not os.path.exists(dest):
            os.makedirs(dest)        
        # Remove existing files
        for file in os.listdir(dest):
            if file[0] != '.':
                path = os.path.join(dest, file)
                try:
                    if os.path.isfile(path):
                        os.unlink(path)
                except Exception, e:
                    print e
        # Copy template directory
        distutils.dir_util.copy_tree(src, dest)
        
        self.setTemplate('title', self.appname)
        self.setTemplate('readme', self.getReadme())
        #self.createPage('_SIDEBAR', '> [Home](Home)\n\n\n')
    
    '''
    Create a new wiki page
    '''
    def createPage(self):
        file = open(os.path.join(self.wikidir, self.pageName), 'w')
        file.write(self.text)
        file.close()
        self.pageName = None
        self.text = None
    
    '''
    Append title item to wiki page
    '''
    def appendTitlePage(self, title, text):
        titlemod = title + '.md'
        file = open(os.path.join(self.wikidir, titlemod), 'a')
        file.write(text)
        file.close()

    '''
    Add a class to the wiki
    ''' 
    def buildClass(self, javadoc):
        self.pageName = javadoc.getContext().getFullName() + '.md'
        self.text = ''
        self.text += self.formatJavadoc(javadoc)
        self.text += '\n'

    def buildInnerClass(self, javadoc):
        self.text += '---\n'
        self.text += "#{}\n".format(javadoc.getSourceLine().getDisplay())
        self.text += self.formatJavadoc(javadoc)

    '''
    Add a method to the wiki
    '''
    def buildMethod(self, javadoc):
        self.text += "##{}\n".format(javadoc.getSourceLine().getName())
        self.text += "```java\n{}\n```\n".format(javadoc.getSourceLine().getText())
        self.text += self.formatJavadoc(javadoc)

    '''
    Add a field to the wiki
    '''
    def buildField(self, javadoc):
        self.text += "##{}\n".format(javadoc.getSourceLine().getName())
        self.text += "```java\n{}\n```\n".format(javadoc.getSourceLine().getText())
        self.text += self.formatJavadoc(javadoc)

    '''
    Create home page heirarchy
    '''
    def addToHomePage(self, javadoc, hierarchy):
        name = javadoc.sourceLine.name
        if hierarchy == 0:
            type = 'Class'
        elif hierarchy == 1:
            type = 'Method'
        else:
            type = 'Field'
        text = '\n{}* {}'.format(' ' * hierarchy, link(name, name))
        self.appendTitlePage('HOME', text)
        self.appendTitlePage('_SIDEBAR', text)
    
    '''
    Return project readme file
    '''
    def getReadme(self):
        path = os.path.join(self.repodir, 'README.md')
        if os.path.isfile(path):
            readmeFile = open(path, 'r')
            readme = readmeFile.read()
            readmeFile.close()
            return readme
        else:
            return None

    def formatJavadoc(self, javadoc):
        text = ''
        if javadoc:
            if javadoc.getMainDesc():
                text += "{}\n\n".format(self.formatText(javadoc.getMainDesc()))
            if javadoc.getBlockTags():
                text += self.formatTagSection(javadoc.getBlockTags())
        return "{}\n".format(text)

    '''
    Format description
    '''
    def formatText(self, mainDesc):
        text = ''
        for item in mainDesc.getContent():
            if isinstance(item, InlineTag):
                text += self.formatLink(item)
            else:
                item = re.sub(r'(<p>)+', ' ', item)
                text += str(item)
        return text

    '''
    Format links
    '''
    def formatLink(self, link):
        if isinstance(link, StringLink):
            return "\"{}\"".format(link.getStr())
        elif isinstance(link, HtmlLink):
            return "[{}]({})".format(link.getLabel(), link.getHref())
        elif isinstance(link, JavadocLink):
            clsName = self.graph.resolveLink(link)
            if clsName:
                return "[{}]({})".format(clsName, clsName)
            else:
                return link.text
        else:
            return ""
    
    '''
    Format tags
    '''
    def formatTagSection(self, blocktags, italic=False):
        text = ""
        def formatTextContent(content):
            text = ""
            for something in content:
                if isinstance(something, basestring):
                    text += something
                elif something.getLink():
                    text += self.formatLink(something.getLink())
            return text

        authorTag = [blocktag for blocktag in blocktags if blocktag.getName() == "author"]
        if len(authorTag) > 0:
            text += "###### Authored by {}\n\n".format(self.formatText(authorTag[0].getText()))
        versionTag = [blocktag for blocktag in blocktags if blocktag.getName() == "version"]
        if len(versionTag) > 0:
            text += "Version {}\n\n".format(self.formatText(versionTag[0].getText()))
        paramTags = [blocktag for blocktag in blocktags if blocktag.getName() == "param"]
        if len(paramTags) > 0:
            text += "**params**\n\n"
            for paramTag in paramTags:
                content = paramTag.getText().getContent()
                if len(content) > 0:
                    first = re.split('\s+', content[0])
                    var = first[0]
                    text += "* `{}` - {}{}\n".format(var, ' '.join(first[1:]), formatTextContent(content[1:]))
        returnTag = [blocktag for blocktag in blocktags if blocktag.getName() == "return"]
        if len(returnTag) > 0:
            content = returnTag[0].getText().getContent()
            if len(content) > 0:
                text += "\n**returns** {}\n\n".format(formatTextContent(content))
        throwsTags = [blocktag for blocktag in blocktags if blocktag.getName() == "throws"]
        if len(throwsTags) > 0:
            text += "**throws**\n\n"
            for throwsTag in throwsTags:
                content = throwsTag.getText().getContent()
                if len(content) > 0:
                    first = re.split('\s+', content[0])
                    typ = first[0]
                    text += "* `{}` {}{}\n".format(typ, ' '.join(first[1:]), formatTextContent(content[1:]))
        seeTags = [blocktag for blocktag in blocktags if blocktag.getName() == "see"]
        if len(seeTags) > 0:
            text += "**see**\n\n"
            for seeTag in seeTags:
                content = seeTag.getText().getContent()
                if len(content) > 0:
                    text += "* {}\n".format(formatTextContent(content))
        sinceTag = [blocktag for blocktag in blocktags if blocktag.getName() == "since"]
        if len(sinceTag) > 0:
            text += "\n**since** {}\n\n".format(self.formatText(sinceTag[0].getText()))
        deprecatedTag = [blocktag for blocktag in blocktags if blocktag.getName() == "deprecated"]
        if len(deprecatedTag) > 0:
            content = deprecatedTag.getText().getContent()
            if len(content) > 0:
                text += "~~deprecated~~ {}\n\n".format(formatTextContent(content))
        return text
    '''
    Modify a template tag to be a custom value
    '''

    def setTemplate(self, tag, text):
        if isinstance(text, list):
            text = '\n'.join(text)
        for title in ["HOME.md", "README.md"]:
            f = os.path.join(self.wikidir, title)
            if os.path.isfile(f):
                strbuild = '{{ %s }}' % tag
                h = open(f, 'r')
                contents = h.read()
                contents = contents.replace(strbuild, text)
                h.close()
                h = open(f, 'w')
                h.write(contents)
