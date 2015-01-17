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
    whitespaceRe = re.compile(r'\s+')
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
        m = Tag.whitespaceRe.search(text)
        self.name = text[1:m.start()]
        self.text = Text(text[m.end():].strip())

'''
Inline tag in a javadoc. Inside free-form text and has text associated with it
'''
class InlineTag(Tag):
    def __init__(self, text):
        Tag.__init__(self, text)

    def parse(self, text):
        m = Tag.whitespaceRe.search(text)
        self.name = text[2:m.start()]
        self.text = text[m.end():-1].strip()

class SourceLineFactory:
    def __init__(self):
        self.classRe = re.compile(r'class\s*[^\{]+\{')
        self.interfaceRe = re.compile(r'interface\s*[^\{]+\{')
        self.methodRe = re.compile(r'\([^\)]*\)\s*\{')
        self.fieldRe = re.compile(r';')

    def parse(self, sourceLine):
        if self.classRe.search(sourceLine):
            return ClassLine(sourceLine)
        elif self.interfaceRe.search(sourceLine):
            return InterfaceLine(sourceLine)
        elif self.methodRe.search(sourceLine):
            return MethodLine(sourceLine)
        elif self.fieldRe.search(sourceLine):
            return FieldLine(sourceLine)

class SourceLine:
    modifiersRe = re.compile(r'(abstract|final|native|protected|public|private|static|strict|synchronized|transient|volatile)')
    typeParamsRe = re.compile(r'\<.+\>')
    signatureRe = re.compile(r'\w+\s+\w+\(.*\)')
    def __init__(self, sourceLine):
       self.sourceLine = sourceLine

    def getSourceLine(self):
        return self.sourceLine

    def getName(self):
        return self.name

    def getModifiers():
        return self.modifiers

class ClassLine(SourceLine):
    def __init__(self, sourceLine):
        SourceLine.__init__(self, sourceLine)
        components = sourceLine.split()
        self.modifiers = SourceLine.modifiersRe.findall(sourceLine)
        self.name = components[len(self.modifiers) + 1]

    def __repr__(self):
        return "{} class {}".format(' '.join(self.modifiers), self.name)

class InterfaceLine(SourceLine):
    def __init__(self, sourceLine):
        SourceLine.__init__(self, sourceLine)
        components = sourceLine.split()
        self.modifiers = SourceLine.modifiersRe.findall(sourceLine)
        self.name = components[len(self.modifiers) + 1]

    def __repr__(self):
        return "{} interface {}".format(' '.join(self.modifiers), self.name)

class MethodLine(SourceLine):
    def __init__(self, sourceLine):
        SourceLine.__init__(self, sourceLine)
        self.modifiers = SourceLine.modifiersRe.findall(sourceLine)
        typeParamsM = SourceLine.typeParamsRe.search(sourceLine)
        self.typeParams = None
        self.signature = None
        if typeParamsM:
            self.typeParams = typeParamsM.group(0)
        signatureM = SourceLine.signatureRe.search(sourceLine)
        if signatureM:
            self.signature = signatureM.group(0)

    def __repr__(self):
        return "Method: {} {} {}".format(' '.join(self.modifiers), self.typeParams, self.signature)

class FieldLine(SourceLine):
    def __init__(self, sourceLine):
        SourceLine.__init__(self, sourceLine)
        self.modifiers = SourceLine.modifiersRe.findall(sourceLine)
        components = sourceLine.split()
        self.name = components[len(self.modifiers) + 1]
        self.type = components[len(self.modifiers)]

    def __repr__(self):
        return "Field: {} {} {}".format(' '.join(self.modifiers), self.type, self.name)

'''
A single javadoc comment. Can have a main description and tag section, or only one of them

Line bounds are 0-index based
'''
class JavadocComment:
    commentStripRe = re.compile(r'^[\s\*]*')
    sourceLineFactory = SourceLineFactory()
    def __init__(self, text, lineBounds, nextSourceLine):
        self.lineBounds = lineBounds
        if nextSourceLine:
            self.nextSourceLine = JavadocComment.sourceLineFactory.parse(nextSourceLine)
        else:
            self.nextSourceLine = None
        lines = text.splitlines()[1:-1]
        strippedLines = map(lambda line : JavadocComment.commentStripRe.sub('', line), lines)
        self.mainDesc = None
        self.blockTags = []
        curBlockTagText = None
        for line in strippedLines:
            if len(line) > 0:
                if line[0] == '@':
                    if curBlockTagText:
                        self.blockTags.append(BlockTag(curBlockTagText))
                    curBlockTagText = line
                else:
                    if curBlockTagText:
                        curBlockTagText = os.linesep.join([curBlockTagText, line])
                    else:
                        if self.mainDesc:
                            self.mainDesc = os.linesep.join([self.mainDesc, line])
                        else:
                            self.mainDesc = line
        if curBlockTagText:
            self.blockTags.append(BlockTag(curBlockTagText))
        if self.mainDesc:
            self.mainDesc = Text(self.mainDesc)


    def getMainDesc(self):
        return self.mainDesc

    def getBlockTags(self):
        return self.blockTags

    def getLineBounds(self):
        return self.lineBounds

    def getNextSourceLine(self):
        return self.nextSourceLine

    def __repr__(self):
        return "JavaDocComment: LineBounds? {} NextSourceLine? {} MainDesc? {} BlockTags? {}".format(self.lineBounds, self.nextSourceLine, self.mainDesc, self.blockTags)

javadocRe = re.compile(r'/\*\*.*?\*/', re.DOTALL)
nextSourceLineRe = re.compile(r'[^;{]*(;|{)', re.DOTALL)

def getJavadocs(f):
    java = f.read();
    for m in javadocRe.finditer(java):
        startLine = java.count(os.linesep, 0, m.start())
        endLine = java.count(os.linesep, 0, m.end())
        nextSourceLineM = nextSourceLineRe.search(java, m.end() + 1)
        if nextSourceLineM:
            nextSourceLine = nextSourceLineM.group(0).strip()
        else:
            nextSourceLine = None
        yield JavadocComment(m.group(0), (startLine, endLine), nextSourceLine)
