import re
import os

'''
Text in a javadoc that may have inline tags embedded in it
'''
class Text:
    inlineTagRe = re.compile(r'\{@[^\}]*}')
    def __init__(self, text):
        #array looks like text -> tag -> text .....
        self.content = []
        start = 0
        for m in Text.inlineTagRe.finditer(text):
            self.content.append(text[start:m.start()])
            self.content.append(InlineTag(m.group(0)))
            start = m.end()
        if start < len(text):
            self.content.append(text[start:])

    def getContent(self):
        return self.content

    def __repr__(self):
        return "Text: Content {}".format(self.content)
'''
Tag in a javadoc. Means something special
'''
class Tag:
    def __init__(self, text):
        self.parse(text)

    def getName(self):
        return self.name

    def getText(self):
        return self.text

    def __repr__(self):
        return "{}: Name {} {}".format(self.__class__.__name__, self.name, self.text)

'''
Block tag in a javadoc. Stands alone and has text associated with it that could have inline tags
'''
class BlockTag(Tag):
    def __init__(self, text):
        Tag.__init__(self, text)

    def parse(self, text):
        self.name = text[1:text.index(' ')]
        self.text = Text(text[text.index(' '):].strip())

'''
Inline tag in a javadoc. Inside free-form text and has text associated with it
'''
class InlineTag(Tag):
    def __init__(self, text):
        Tag.__init__(self, text)

    def parse(self, text):
        self.name = text[2:text.index(' ')]
        self.text = text[text.index(' '):-1].strip()

'''
A single javadoc comment. Can have a main description and tag section, or only one of them
'''
class JavadocComment:
    commentStripRe = re.compile(r'^[\s\*]*')
    def __init__(self, text):
        lines = text.splitlines()[1:-1]
        strippedLines = map(lambda line : JavadocComment.commentStripRe.sub('', line), lines)
        i = 0
        self.mainDesc = None
        self.blockTags = []
        curBlockTagText = None
        while i < len(strippedLines):
            if len(strippedLines[i]) > 0:
                if strippedLines[i][0] == '@':
                    if curBlockTagText:
                        self.blockTags.append(BlockTag(curBlockTagText))
                    curBlockTagText = strippedLines[i]
                else:
                    if curBlockTagText:
                        curBlockTagText = os.linesep.join([curBlockTagText, strippedLines[i]])
                    else:
                        if self.mainDesc:
                            self.mainDesc = os.linesep.join([self.mainDesc, strippedLines[i]])
                        else:
                            self.mainDesc = strippedLines[i]
            i = i + 1
        if curBlockTagText:
            self.blockTags.append(BlockTag(curBlockTagText))
        if self.mainDesc:
            self.mainDesc = Text(self.mainDesc)


    def getMainDesc(self):
        return self.mainDesc

    def getBlockTags(self):
        return self.blockTags

    def __repr__(self):
        return "JavaDocComment: MainDesc? {} BlockTags? {}".format(self.mainDesc, self.blockTags)


javadocRe = re.compile(r'/\*\*.*?\*/', re.DOTALL)

def getJavadocText(f):
    java = f.read();
    javadocs = javadocRe.findall(java)
    return javadocs
