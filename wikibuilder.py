import os
import fileinput
import distutils.core

from markup_formatter import *
from javadoc_parser import *

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
    Use the java docs to build the wiki graph network
    '''
    def buildGraph(self, javadocs):
        for javadoc in javadocs:
            if isinstance(javadoc.sourceLine, ClassLine):
                pass
            elif isinstance(javadoc.sourceLine, MethodLine):
                pass
            elif isinstance(javadoc.sourceLine, FieldLine):
                pass
        
    '''
    Use the java docs to implement the wiki pages
    '''
    def buildDocs(self, javadocs):
        currentClass = None
        for javadoc in javadocs:
            text = ''
            if isinstance(javadoc.sourceLine, ClassLine):
                currentClass = javadoc.sourceLine.name
                text += ('{}\n'.format(hx(2, javadoc.sourceLine.name)))
                text += ('**MODIFIER** {}\n\n'.format(', '.join(javadoc.sourceLine.modifiers)))
                text += ('{}\n\n'.format(self.formatTag(javadoc.blockTags)))
                text += ('{}\n\n'.format(code('java', javadoc.sourceLine.sourceLine)))
                self.createPage(javadoc.sourceLine.name, text)
            elif isinstance(javadoc.sourceLine, MethodLine):
                text += ('{}\n'.format(hx(3, javadoc.sourceLine.name)))
                text += ('**MODIFIER** {}\n\n'.format(', '.join(javadoc.sourceLine.modifiers)))
                text += ('**DESCRIPTION** {}\n\n'.format(self.formatDesc(javadoc.mainDesc.content)))
                text += ('{}\n\n'.format(self.formatTag(javadoc.blockTags, True)))
                text += ('{}\n\n'.format(code('java', javadoc.sourceLine.sourceLine)))
                self.appendPage(currentClass, text)
            elif isinstance(javadoc.sourceLine, FieldLine):
                text += ('{}\n'.format(hx(3, javadoc.sourceLine.name)))
                text += ('**MODIFIER** {}\n\n'.format(', '.join(javadoc.sourceLine.modifiers)))
                text += ('**TYPE** {}\n\n'.format(italic(javadoc.sourceLine.type)))
                text += ('{}\n\n'.format(self.formatTag(javadoc.blockTags, True)))
                text += ('{}\n\n'.format(code('java', javadoc.sourceLine.sourceLine)))
                self.appendPage(currentClass, text)
            else:
                print javadoc.sourceLine
    
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
    def formatTag(self, blockTags, italic=False):
        text = ''
        for tag in blockTags:
            text += (bold(tag.name.upper()))
            for content in tag.text.content:
                if italic and tag.name.upper() == 'PARAM':
                    content = str(content).split()
                    text += ('\t*{}*, {}\n\n').format(content[0], ' '.join(content[1:]))
                else:
                    text += ('\t' + str(content) + '\n\n')
        return text
    
    '''
    Copy template files to wiki directory
    '''
    def create(self):
        src = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'wiki-template')
        dest = self.WIKIDIR
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
    def setTag(self, tag, text):
        if isinstance(text, list):
            text = '\n'.join(text)
        for title in os.listdir(self.WIKIDIR):
            file = os.path.join(self.WIKIDIR, title)
            strbuild = '{{ %s }}' % tag
            for line in fileinput.FileInput(file, inplace=1):
                line = line.replace(strbuild, text)
                print line,        