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
    APPNAME = 'testapp'
    REPODIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), APPNAME)
    
    '''
    Initialize wiki with working directory and call create
    '''
    def __init__(self, graph, wikidir):
        self.WIKIDIR = wikidir
        self.graph = graph
        self.create()
        self.pageName = None
        self.text = None
    
    '''
    Copy template files to wiki directory
    '''
    def create(self):      
        src = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'wiki-template')
        dest = self.WIKIDIR
        if not os.path.exists(dest):
            os.makedirs(dest)        
        # Remove existing files
        for file in os.listdir(dest):
            path = os.path.join(dest, file)
            try:
                if os.path.isfile(path):
                    os.unlink(path)
            except Exception, e:
                print e
        # Copy template directory
        distutils.dir_util.copy_tree(src, dest)
        
        self.setTemplate('title', self.APPNAME)
        self.setTemplate('readme', self.getReadme())
        #self.createPage('_SIDEBAR', '> [Home](Home)\n\n\n')
    
    '''
    Create a new wiki page
    '''
    def createPage(self):
        file = open(os.path.join(self.WIKIDIR, self.pageName), 'w')
        file.write(self.text)
        file.close()
        self.pageName = None
        self.text = None
    
    '''
    Append title item to wiki page
    '''
    def appendTitlePage(self, title, text):
        titlemod = title + '.md'
        file = open(os.path.join(self.WIKIDIR, titlemod), 'a')
        file.write(text)
        file.close()
    
    '''
    Add a class to the wiki
    ''' 
    def buildClass(self, javadoc):
        self.pageName = javadoc.getSourceLine().getName() + '.md'
        self.text = ''
        self.text += self.mName(javadoc.sourceLine.name, 2)
        self.text += self.mLink(javadoc.getContext().getClsName())
        self.text += self.mModifier(javadoc.sourceLine.modifiers)
        self.text += self.mTags(javadoc.blockTags)
        self.text += self.mSource(javadoc.sourceLine.sourceLine)

    '''
    Add a method to the wiki
    '''
    def buildMethod(self, javadoc):
        self.text += self.mName(javadoc.sourceLine.name, 3)
        self.text += self.mLink(javadoc.getContext().getClsName())
        self.text += self.mModifier(javadoc.sourceLine.modifiers)
        try:
            self.text += ('**DESCRIPTION** {}\n\n'.format(self.formatDesc(javadoc.mainDesc.content)))
        except AttributeError:
            pass
        self.text += self.mTags(javadoc.blockTags, True)
        self.text += self.mSource(javadoc.sourceLine.sourceLine)

    '''
    Add a field to the wiki
    '''
    def buildField(self, javadoc):
        self.text += self.mName(javadoc.sourceLine.name, 3)
        self.text += self.mLink(javadoc.getContext().getClsName())
        self.text += self.mModifier(javadoc.sourceLine.modifiers)
        self.text += self.mType(javadoc.sourceLine.type)
        self.text += self.mTags(javadoc.blockTags, True)
        self.text += self.mSource(javadoc.sourceLine.sourceLine)

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
        path = os.path.join(self.REPODIR, 'README.md')
        if os.path.isfile(path):
            readmeFile = open(path, 'r')
            readme = readmeFile.read()
            readmeFile.close()
            return readme
        else:
            return None
    
    '''
    Markdown source
    '''
    def mSource(self, source):
        if source:
            return '{}\n\n'.format(code('java', source[:-1]))
        return ''
    
    '''
    Markdown link
    '''
    def mLink(self, link):
        if link:
            links = link.split('.')
            flinks = []
            for link in links:
                link = markup_formatter.link(link, link)
                flinks.append(link)
            flinks = '[{}]'.format('] ['.join(flinks))
            return '**LINK** {}\n\n'.format(flinks)
        return ''
    
    '''
    Markdown modifier
    '''
    def mModifier(self, modifiers):
        if modifiers:
            return '**MODIFIER** {}\n\n'.format(', '.join(modifiers))
        return ''
        
    '''
    Markdown name
    '''
    def mName(self, name, weight):
        if name:
            return '{}\n\n'.format(hx(weight, name))
        return ''
        
    '''
    Markdown tags
    '''
    def mTags(self, tags, italic=False):
        if tags:
            return '{}\n\n'.format(self.formatTag(tags, italic))
        return ''
        
    '''
    Markdown type
    '''
    def mType(self, type):
        if type:
            return '**TYPE** {}\n\n'.format(italic(type))
        return ''
    
    '''
    Format description
    '''
    def formatDesc(self, content):
        text = ''
        for item in content:
            if isinstance(item, InlineTag):
                try:
                    text += link(item.link.label, item.link.href)
                except AttributeError:
                    text += link(item.text, item.link.cls)
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
                return "[{}]({})".format(link.text, "{}.md".format(clsName))
            else:
                return link.text
        else:
            return ""
    
    '''
    Format tags
    '''
    def formatTag(self, blocktags, italic=False):
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
            text += "###### Authored by {}\n".format(authorTag[0].getText())
        versionTag = [blocktag for blocktag in blocktags if blocktag.getName() == "version"]
        if len(versionTag) > 0:
            text += "Version {}\n".format(versionTag[0].getText())
        paramTags = [blocktag for blocktag in blocktags if blocktag.getName() == "param"]
        if len(paramTags) > 0:
            text += "**params**\n"
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
                text += "**returns** {}\n".format(formatTextContent(content))
        throwsTags = [blocktag for blocktag in blocktags if blocktag.getName() == "throws"]
        if len(throwsTags) > 0:
            text += "**throws**\n"
            for throwsTag in throwsTags:
                content = throwsTag.getText().getContent()
                if len(content) > 0:
                    first = re.split('\s+', content[0])
                    typ = first[0]
                    text += "* `{}` {}{}\n".format(typ, ' '.join(first[1:]), formatTextContent(content[1:]))
        seeTags = [blocktag for blocktag in blocktags if blocktag.getName() == "see"]
        if len(seeTags) > 0:
            text += "**see**\n"
            for seeTag in seeTags:
                content = seeTag.getText().getContent()
                if len(content) > 0:
                    text += "* {}\n".format(formatTextContent(content))
        sinceTag = [blocktag for blocktag in blocktags if blocktag.getName() == "since"]
        if len(sinceTag) > 0:
            text += "**since** {}\n".format(sinceTag[0].getText())
        deprecatedTag = [blocktag for blocktag in blocktags if blocktag.getName() == "deprecated"]
        if len(deprecatedTag) > 0:
            content = deprecatedTag.getText().getContent()
            if len(content) > 0:
                text += "~~deprecated~~ {}\n".format(formatTextContent(content))
        return text
    '''
    Modify a template tag to be a custom value
    '''
    def setTemplate(self, tag, text):
        if isinstance(text, list):
            text = '\n'.join(text)
        for title in os.listdir(self.WIKIDIR):
            file = os.path.join(self.WIKIDIR, title)
            strbuild = '{{ %s }}' % tag
            for line in fileinput.FileInput(file, inplace=1):
                line = line.replace(strbuild, text)
                print line,
