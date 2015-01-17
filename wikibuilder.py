import os
import fileinput
import distutils.core

class Wiki:
    def __init__(self, wikidir):
        self.WIKIDIR = wikidir
    
    def create(self):
        src = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'wiki-template\\')
        dest = self.WIKIDIR
        distutils.dir_util.copy_tree(src, dest)
    
    def createPage(self, title, text):
        titlemod = title + '.md'
        file = open(os.path.join(self.WIKIDIR, titlemod), 'w')
        file.write(text)
        file.close()
    
    def setTag(self, tag, text):
        if isinstance(text, list):
            text = '\n'.join(text)
        for title in os.listdir(self.WIKIDIR):
            file = os.path.join(self.WIKIDIR, title)
            strbuild = '{{ %s }}' % tag
            for line in fileinput.FileInput(file, inplace=1):
                line = line.replace(strbuild, text)
                print line,