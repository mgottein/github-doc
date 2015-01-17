from os import path, listdir
import fileinput
import distutils.core

class Wiki:
    def __init__(self, wikidir):
        self.WIKIDIR = wikidir
    
    def create(self):
        src = path.join(path.dirname(path.realpath(__file__)), 'wiki-template\\')
        dest = self.WIKIDIR
        distutils.dir_util.copy_tree(src, dest)
    
    def setTag(self, tag, text):
        if isinstance(text, list):
            text = '\n'.join(text)
        for title in listdir(self.WIKIDIR):
            file = path.join(self.WIKIDIR, title)
            strbuild = '{{ %s }}' % tag
            for line in fileinput.FileInput(file, inplace=1):
                line = line.replace(strbuild, text)
                print line,
