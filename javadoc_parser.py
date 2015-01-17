import re
import os

class BlockTag:
        def __init__(self, text):
            self.name = text[1:text.index(' ')]
            self.text = text[text.index(' '):].strip()

        def getName(self):
            return self.name

        def getText(self):
            return self.text

        def __repr__(self):
            return "BlockTag: Name {} Text {}".format(self.name, self.text)

class JavadocComment:
    commentStripRe = re.compile(r'^[\s\*]*')
    def __init__(self, text):
        lines = text.splitlines()[1:-1]
        strippedLines = map(lambda line : JavadocComment.commentStripRe.sub('', line), lines)
        i = 0
        self.hasMainDesc = False
        self.tagSectionStart = None
        self.blockTags = []
        if strippedLines[0][0] != '@':
            self.hasMainDesc = True
        curBlockTagText = None
        while i < len(strippedLines):
            if len(strippedLines[i]) > 0:
                if strippedLines[i][0] == '@':
                    if not self.tagSectionStart:
                        self.tagSectionStart = i
                    if curBlockTagText:
                        self.blockTags.append(BlockTag(curBlockTagText))
                    curBlockTagText = strippedLines[i]
                else:
                    if curBlockTagText:
                        curBlockTagText = os.linesep.join([curBlockTagText, strippedLines[i]])
            i = i + 1
        if curBlockTagText:
            self.blockTags.append(BlockTag(curBlockTagText))

    def hasMainDesc(self):
        return self.hasMainDesc

    def getTagSectionStart(self):
        return self.tagSectionStart

    def __repr__(self):
        return "JavaDocComment: MainDesc? {} TagSectionStart? {} BlockTags? {}".format(self.hasMainDesc, self.tagSectionStart, self.blockTags)


javadocRe = re.compile(r'/\*\*.*?\*/', re.DOTALL)

def getJavadocText(f):
    java = f.read();
    javadocs = javadocRe.findall(java)
    return javadocs
