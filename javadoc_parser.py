import re
import os

class LinkParser:
    aRe = re.compile(r'\<a\s+href\=\".*\"\>.*\</a\>')
    def parse(self, text):
        if text[0] == '"':
            return StringLink(text)
        elif LinkParser.aRe.search(text):
            return HtmlLink(text)
        else:
            return JavadocLink(text)
'''
String link to nowhere
'''
class StringLink:
    strRe = re.compile(r'\".*\"')
    def __init__(self, text):
        self.str = None
        strM = StringLink.strRe.search(text)
        if strM:
            self.str = strM.group(0)[1:-1]

    def getStr(self):
        return self.str

    def __repr__(self):
        return "StringLink: {}".format(self.str)
'''
HTML link to another webpage
'''
class HtmlLink:
    aRe = re.compile(r'\<a\s+href\=\".*\"\>')
    hrefRe = re.compile(r'\".*\"')
    labelRe = re.compile(r'\>.*\<')
    def __init__(self, text):
        self.href = None
        self.label = None
        aM = HtmlLink.aRe.search(text)
        if aM:
            a = aM.group(0)
            hrefM = HtmlLink.hrefRe.search(a)
            if hrefM:
                self.href = hrefM.group(0)[1:-1]
        labelM = HtmlLink.labelRe.search(text)
        if labelM:
            self.label = labelM.group(0)[1:-1]

    def getHref(self):
        return self.href

    def getLabel(self):
        return self.label

    def __repr__(self):
        return "HtmlLink: {} {}".format(self.href, self.label)

'''
Javadoc link to another javadoc
'''
class JavadocLink:
    classRe = re.compile(r'^[^#\s]*')
    fieldRe = re.compile(r'#[^\s\(]+')
    methodRe = re.compile(r'#[^\s^\(]*\(.*\)')

    def __init__(self, text):
        self.cls = None
        self.method = None
        self.field = None
        classM = JavadocLink.classRe.search(text)
        if classM:
            self.cls = classM.group(0)
        methodM = JavadocLink.methodRe.search(text)
        if methodM:
            self.method = methodM.group(0)[1:]
        else:
            fieldM = JavadocLink.fieldRe.search(text)
            if fieldM:
                self.field = fieldM.group(0)[1:]

    def getCls(self):
        return self.cls

    def getMethod(self):
        return self.method

    def getField(self):
        return self.field

    def __repr__(self):
        return "JavadocLink: {}#{}/{}".format(self.cls, self.method, self.field)

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
    linkParser = LinkParser()
    whitespaceRe = re.compile(r'\s+')
    def __init__(self, text):
        self.name = None
        self.text = None
        self.link = None
        self.parse(text)

    def getName(self):
        return self.name

    def getText(self):
        return self.text

    def getLink(self):
        return self.link

    def __repr__(self):
        if self.link:
            return "{}: Name {} {} {}".format(self.__class__.__name__, self.name, self.text, self.link)
        else:
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
        if self.name == 'link':
            self.link = Tag.linkParser.parse(self.text)

class SourceLineFactory:
    def __init__(self):
        self.classRe = re.compile(r'(class|interface)\s*[^\{]+\{')
        self.methodRe = re.compile(r'\([^\)]*\)\s*\{')
        self.fieldRe = re.compile(r';')

    def parse(self, sourceLine):
        if sourceLine:
            if self.classRe.search(sourceLine):
                return ClassLine(sourceLine)
            elif self.methodRe.search(sourceLine):
                return MethodLine(sourceLine)
            elif self.fieldRe.search(sourceLine):
                return FieldLine(sourceLine)
        else:
            return None

class SourceLine:
    modifiersRe = re.compile(r'(abstract|final|native|protected|public|private|static|strict|synchronized|transient|volatile)')
    def __init__(self, sourceLine):
       self.sourceLine = sourceLine
       self.modifiers = SourceLine.modifiersRe.findall(sourceLine)

    def getText(self):
        return self.sourceLine

    def getName(self):
        return self.name

    def getModifiers():
        return self.modifiers

class ClassLine(SourceLine):
    def __init__(self, sourceLine):
        SourceLine.__init__(self, sourceLine)
        components = sourceLine.split()
        self.isInterface = "interface" in sourceLine
        self.name = components[len(self.modifiers) + 1]

    def __repr__(self):
        return "{} {} {}".format(' '.join(self.modifiers), "interface" if self.isInterface else "class", self.name)

class MethodLine(SourceLine):
    typeParamsRe = re.compile(r'\<.+\>')
    signatureRe = re.compile(r'\w+\s+\w+\(.*\)')
    argsRe = re.compile(r'\(.*\)')
    nameRe = re.compile(r'\s+.+(?=\()')
    retTypeRe = re.compile(r'[^\s]+\s')
    def __init__(self, sourceLine):
        SourceLine.__init__(self, sourceLine)
        self.typeParams = []
        self.name = None
        self.args = []
        self.retType = None
        typeParamsM = MethodLine.typeParamsRe.search(sourceLine)
        if typeParamsM:
            self.typeParams = [typeParam.strip() for typeParam in typeParamsM.group(0).strip()[1:-1].split(',')]
        signatureM = MethodLine.signatureRe.search(sourceLine)
        if signatureM:
            signature = signatureM.group(0).strip()
            argsM = MethodLine.argsRe.search(signature)
            nameM = MethodLine.nameRe.search(signature)
            retTypeM = MethodLine.retTypeRe.search(signature)
            if argsM:
                self.args = [arg.strip() for arg in argsM.group(0).strip()[1:-1].split(',')]
            if nameM:
                self.name = nameM.group(0).strip()
            if retTypeM:
                self.retType = retTypeM.group(0).strip()

    def __repr__(self):
        return "Method: {} <{}> {} {}({})".format(' '.join(self.modifiers), ', '.join(self.typeParams), self.retType, self.name, ', '.join(self.args))

class FieldLine(SourceLine):
    def __init__(self, sourceLine):
        SourceLine.__init__(self, sourceLine)
        components = sourceLine.split()
        self.name = components[len(self.modifiers) + 1]
        self.type = components[len(self.modifiers)]

    def __repr__(self):
        return "Field: {} {} {}".format(' '.join(self.modifiers), self.type, self.name)

'''
Context of where a javadoc is (package / class)
Package can be none (default package)
Class can be none (top level class javadoc)
'''
class Context:
    def __init__(self, package, cls):
        self.package = package
        self.cls = cls

    def getPackage(self):
        return self.package

    def getCls(self):
        return self.cls

    def __repr__(self):
        return "{}.{}".format(self.package, self.cls)

'''
A single javadoc comment. Can have a main description and tag section, or only one of them

Line bounds are 0-index based
'''
class JavadocComment:
    commentStripRe = re.compile(r'^[\s\*]*')
    sourceLineFactory = SourceLineFactory()
    def __init__(self, context, text, lineBounds, sourceLineInfo):
        self.context = context
        self.lineBounds = lineBounds
        self.sourceLine, self.sourceBoundsStart, self.sourceBoundsEnd = sourceLineInfo
        self.sourceLine = JavadocComment.sourceLineFactory.parse(self.sourceLine)
        lines = text.splitlines()[1:-1]
        strippedLines = [JavadocComment.commentStripRe.sub('', line) for line in lines]
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

    def getSourceBounds(self):
        return (self.sourceBoundsStart, self.sourceBoundsEnd)

    def getSourceLine(self):
        return self.sourceLine

    def getEdges(self):
        if self.mainDesc:
            for content in self.mainDesc.getContent():
                if isinstance(content, InlineTag) and content.getLink():
                    yield content.getLink()
        if self.blockTags:
            for blockTag in self.blockTags:
                if blockTag.getLink():
                    yield blockTag.getLink()
                for content in blockTag.getText().getContent():
                    if isinstance(content, InlineTag) and content.getLink():
                        yield content.getLink()

    def __repr__(self):
        #return "JavaDocComment: LineBounds? {} SourceLine? {} MainDesc? {} BlockTags? {}".format(self.lineBounds, self.sourceLine, self.mainDesc, self.blockTags)
        return "JavaDocComment: SourceLine? {} SourceBounds? {} Edges? {}".format(self.sourceLine, self.getSourceBounds(), list(self.getEdges()))

javadocRe = re.compile(r'/\*\*.*?\*/', re.DOTALL)
packageRe = re.compile(r'package\s+.*;')
sourceLineRe = re.compile(r'[^;{]*(;|{)', re.DOTALL)
bracketRe = re.compile(r'[\{\}]')


def getJavadocs(f):
    java = f.read();
    packageM = packageRe.search(java)
    package = None
    classStack = [None]
    if packageM:
        package = packageM.group(0).split()[-1][:-1]
    for javadocTextM in javadocRe.finditer(java):
        javadocText = javadocTextM.group(0)
        startLine = java.count(os.linesep, 0, javadocTextM.start())
        endLine = java.count(os.linesep, 0, javadocTextM.end())
        sourceLineM = sourceLineRe.search(java, javadocTextM.end() + 1)
        if sourceLineM:
            sourceLine = sourceLineM.group(0).strip()
            sourceBoundsStart = java.count(os.linesep, 0, sourceLineM.end())
            sourceBoundsEnd = sourceBoundsStart
            if sourceLine[-1] == '{':
                depth = 1
                for bracketM in bracketRe.finditer(java, sourceLineM.end() + 1):
                    if java[bracketM.start() - 1] == '\\':
                        continue
                    if java[bracketM.start()] == '{':
                        depth = depth + 1
                    else:
                        depth = depth - 1
                    if depth == 0:
                        sourceBoundsEnd = java.count(os.linesep, 0, bracketM.end())
                        break
        else:
            sourceLine = None
            sourceBoundsStart = -1
            sourceBoundsEnd = -1
        javadocComment = JavadocComment(Context(package, classStack[-1]), javadocText, (startLine, endLine), (sourceLine, sourceBoundsStart, sourceBoundsEnd))
        yield javadocComment
