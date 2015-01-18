import os
import fileinput
import distutils.core

from markup_formatter import *
from javadoc_parser import *
import markup_formatter

'''
Class to create and customize the Wiki
'''
class Wiki:
    
    '''
    Initialize wiki with working directory and call create
    '''
    def __init__(self, wikidir):
        self.WIKIDIR = wikidir
        self.create()
        
    '''
    Use the java docs to implement the wiki pages
    '''    
    def buildClass(self, javadoc):
        text = ''
        currentClass = javadoc.sourceLine.name
        text += self.mName(javadoc.sourceLine.name, 2)
        text += self.mLink(javadoc.getContext().getClsName())
        text += self.mModifier(javadoc.sourceLine.modifiers)
        text += self.mTags(javadoc.blockTags)
        text += self.mSource(javadoc.sourceLine.sourceLine)
        self.createPage(javadoc.sourceLine.name, text)
    
    def buildMethod(self, javadoc, currentClass):
        text = ''
        text += self.mName(javadoc.sourceLine.name, 3)
        text += self.mLink(javadoc.getContext().getClsName())
        text += self.mModifier(javadoc.sourceLine.modifiers)
        try:
            text += ('**DESCRIPTION** {}\n\n'.format(self.formatDesc(javadoc.mainDesc.content)))
        except AttributeError:
            pass
        text += self.mTags(javadoc.blockTags, True)
        text += self.mSource(javadoc.sourceLine.sourceLine)
        if currentClass.blockTags or currentClass.mainDesc:
            self.appendPage(currentClass, text)
        else:
            self.appendPage(javadoc.sourceLine.name, text)
    
    def buildField(self, javadoc, currentClass):
        text = ''
        text += self.mName(javadoc.sourceLine.name, 3)
        text += self.mLink(javadoc.getContext().getClsName())
        text += self.mModifier(javadoc.sourceLine.modifiers)
        text += self.mType(javadoc.sourceLine.type)
        text += self.mTags(javadoc.blockTags, True)
        text += self.mSource(javadoc.sourceLine.sourceLine)
        if currentClass.blockTags or currentClass.mainDesc:
            self.appendPage(currentClass, text)
        else:
            self.appendPage(javadoc.sourceLine.name, text)
    
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
            return '{}\n'.format(hx(weight, name))
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
                item = re.sub(r'(<p>)+', '\n', item)
                text += str(item)
        return text
    
    '''
    Format tags
    '''
    def formatTag(self, blocktags, italic=False):
        text = ""
        def formatTextContent(content):
            return str(content)

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
                    text += "* `{}` - {}{}\n".format(var, first[1:], formatTextContent(content[1:]))
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
                    text += "* `{}` {}{}\n".format(typ, first[1:], formatTextContent(content[1:]))
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
    
    '''
    Create a new wiki page
    '''
    def createPage(self, title, text):
        titlemod = title + '.md'
        file = open(os.path.join(self.WIKIDIR, titlemod), 'w')
        file.write(text)
        file.close()
    
    '''
    Append item to wiki page
    '''
    def appendPage(self, title, text):
        titlemod = title + '.md'
        file = open(os.path.join(self.WIKIDIR, titlemod), 'a')
        file.write(text)
        file.close()
    
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
