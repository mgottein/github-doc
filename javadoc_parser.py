import re
import os

class LinkParser:
    aRe = re.compile(r'\<a\s+href\=\".*\"\>.*\</a\>')
    def parse(self, context, text):
        if text[0] == '"':
            return StringLink(text)
        elif LinkParser.aRe.search(text):
            return HtmlLink(text)
        else:
            return JavadocLink(context, text)

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
    def __init__(self, context, text):
        self.context = context
        self.text = text

    def __repr__(self):
        return "JavadocLink: {}".format(self.text)

'''
Text in a javadoc that may have inline tags embedded in it
'''
class Text:
    inlineTagRe = re.compile(r'\{@[^\}]*}')
    def __init__(self, context, text):
        #array looks like text -> tag -> text .....
        self.content = []
        self.context = context
        start = 0
        for m in Text.inlineTagRe.finditer(text):
            self.content.append(text[start:m.start()])
            self.content.append(InlineTag(context, m.group(0)))
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
    def __init__(self, context, text):
        self.name = None
        self.context = context
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
    def __init__(self,context, text):
        Tag.__init__(self,context, text)

    def parse(self, text):
        m = Tag.whitespaceRe.search(text)
        self.name = text[1:m.start()]
        self.text = Text(self.context, text[m.end():].strip())

'''
Inline tag in a javadoc. Inside free-form text and has text associated with it
'''
class InlineTag(Tag):
    def __init__(self,context,text):
        Tag.__init__(self,context,text)

    def parse(self, text):
        m = Tag.whitespaceRe.search(text)
        self.name = text[2:m.start()]
        self.text = text[m.end():-1].strip()
        if self.name == 'link':
            self.link = Tag.linkParser.parse(self.context, self.text)

class SourceLineFactory:
    def __init__(self, f):
        self.f = f
        self.classRe = re.compile(r'(class|interface)\s+[^\s]+\s+{')
        self.methodRe = re.compile(r'\([^\)]*\)\s*[\{;]')
        self.fieldRe = re.compile(r';')

    def create(self, java, match):
        sourceLine = match.group(0).strip()
        sourceBoundsStart = java.count('\n', 0, match.end())
        sourceBoundsEnd = sourceBoundsStart
        if bracketRe.search(sourceLine):
            depth = 1
            for bracketM in bracketRe.finditer(java, match.end() + 1):
                if java[bracketM.start() - 1] == '\\':
                    continue
                if java[bracketM.start()] == '{':
                    depth = depth + 1
                else:
                    depth = depth - 1
                if depth == 0:
                    sourceBoundsEnd = java.count('\n', 0, bracketM.end())
                    break
        return self.parse(sourceLine, (sourceBoundsStart, sourceBoundsEnd))

    def parse(self, sourceLine, sourceBounds):
        if sourceLine:
            if self.classRe.search(sourceLine):
                searchM = re.search('\s+\{', sourceLine)
                if searchM:
                    sourceLine = sourceLine[:searchM.start()]
                return ClassLine(self.f, sourceLine, sourceBounds)
            elif self.methodRe.search(sourceLine):
                searchM = re.search('\s*[\{;]', sourceLine)
                if searchM:
                    sourceLine = sourceLine[:searchM.start()]
                return MethodLine(self.f, sourceLine, sourceBounds)
            elif self.fieldRe.search(sourceLine):
                searchM = re.search('\s*[;|\=]', sourceLine)
                if searchM:
                    sourceLine = sourceLine[:searchM.start()]
                return FieldLine(self.f, sourceLine, sourceBounds)
        else:
            return None

class SourceLine:
    modifiersRe = re.compile(r'(abstract|final|native|protected|public|private|static|strict|synchronized|transient|volatile)')
    def __init__(self, f, sourceLine, sourceBounds):
       self.f = f
       self.sourceLine = sourceLine
       self.sourceBounds = sourceBounds
       self.modifiers = SourceLine.modifiersRe.findall(sourceLine)

    def getText(self):
        return self.sourceLine

    def getBounds(self):
        return self.sourceBounds

    def getName(self):
        return self.name

    def getModifiers(self):
        return self.modifiers

    def getFileName(self):
        return self.f

class ClassLine(SourceLine):
    def __init__(self, f, sourceLine, sourceBounds):
        SourceLine.__init__(self, f, sourceLine, sourceBounds)
        components = sourceLine.split()
        self.isInterface = "interface" in sourceLine
        self.name = components[len(self.modifiers) + 1]

    def getSourceLine(self):
        return self

    def getName(self):
        return self.name

    def getDisplay(self):
        return "{} {} {}".format(' '.join(self.modifiers), "interface" if self.isInterface else "class", self.name)

    def __repr__(self):
        return "{} {} {} {}".format(' '.join(self.modifiers), "interface" if self.isInterface else "class", self.name, self.sourceBounds)

class MethodLine(SourceLine):
    typeParamsRe = re.compile(r'\<.+\>')
    signatureRe = re.compile(r'\w+\s+\w+\(.*\)')
    argsRe = re.compile(r'\(.*\)')
    nameRe = re.compile(r'\s+.+(?=\()')
    retTypeRe = re.compile(r'[^\s]+\s')
    def __init__(self, f, sourceLine, sourceBounds):
        SourceLine.__init__(self, f, sourceLine, sourceBounds)
        self.typeParams = []
        self.name = ''
        self.args = []
        self.retType = ''
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

    def getSignature(self):
        return "{}({})".format(self.name, ', '.join([re.split('\s+', arg)[0] for arg in self.args]))

    def getDisplay(self):
        return "{} {}".format(self.retType, self.getSignature())

    def __repr__(self):
        return "Method: {} <{}> {} {}({})".format(' '.join(self.modifiers), ', '.join(self.typeParams), self.retType, self.name, ', '.join(self.args))

class FieldLine(SourceLine):
    def __init__(self, f, sourceLine, sourceBounds):
        SourceLine.__init__(self, f, sourceLine, sourceBounds)
        components = sourceLine.split()
        self.name = components[len(self.modifiers) + 1]
        self.type = components[len(self.modifiers)]

    def getDisplay(self):
        return "{} {}".format(self.type, self.name)

    def __repr__(self):
        return "Field: {} {} {}".format(' '.join(self.modifiers), self.type, self.name)

'''
Context of where a javadoc is (package / class)
Package can be none (default package)
Class can be none (top level class javadoc)
'''
class Context:
    def __init__(self, f, package, clsStack):
        self.package = package
        self.clsStack = clsStack
        self.f = f

    def getPackage(self):
        return self.package

    def getClsStack(self):
        return self.clsStack

    def getClsName(self):
        return '.'.join([cls.getName() for cls in self.clsStack])

    def getFileName(self):
        return self.f

    def getFullName(self):
        if self.package:
            return "{}.{}".format(self.package, self.getClsName())
        else:
            return self.getClsName()

    def __repr__(self):
        return self.getFullName()

'''
A single javadoc comment. Can have a main description and tag section, or only one of them

Line bounds are 0-index based
'''
class JavadocComment:
    commentStripRe = re.compile(r'^[\s\*]*')

    @staticmethod
    def createdummyclass(context, sourceLine):
        dummy = JavadocComment()
        dummy.context = context
        dummy.sourceLine = sourceLine
        dummy.lineBounds = None
        dummy.mainDesc = None
        dummy.blockTags = None
        return dummy

    @staticmethod
    def create(context, text, lineBounds, sourceLine):
        real = JavadocComment()
        real.parse(context, text, lineBounds, sourceLine)
        return real

    def parse(self, context, text, lineBounds, sourceLine):
        self.context = context
        self.lineBounds = lineBounds
        self.sourceLine = sourceLine
        lines = text.splitlines()[1:-1]
        strippedLines = [JavadocComment.commentStripRe.sub('', line) for line in lines]
        self.mainDesc = None
        self.blockTags = []
        curBlockTagText = None
        for line in strippedLines:
            if len(line) > 0:
                if line[0] == '@':
                    if curBlockTagText:
                        self.blockTags.append(BlockTag(context, curBlockTagText))
                    curBlockTagText = line
                else:
                    if curBlockTagText:
                        curBlockTagText = '\n'.join([curBlockTagText, line])
                    else:
                        if self.mainDesc:
                            self.mainDesc = '\n'.join([self.mainDesc, line])
                        else:
                            self.mainDesc = line
        if curBlockTagText:
            self.blockTags.append(BlockTag(context, curBlockTagText))
        if self.mainDesc:
            self.mainDesc = Text(context, self.mainDesc)

    def getContext(self):
        return self.context

    def getFileName(self):
        return self.context.getFileName()

    def getClassName(self):
        return self.context.getClsStack()[-1]

    def getMainDesc(self):
        return self.mainDesc

    def getBlockTags(self):
        return self.blockTags

    def getLineBounds(self):
        return self.lineBounds

    def getSourceLine(self):
        return self.sourceLine

    def getName(self):
        return self.sourceLine.getName()

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
        return "JavaDocComment: Context? {} SourceLine? {} Edges? {} Javadoc Link? {}".format(self.context, self.sourceLine, list(self.getEdges()), JavadocLink.fromComment(self))

javadocRe = re.compile(r'/\*\*.*?\*/', re.DOTALL)
packageRe = re.compile(r'package\s+.*;')
sourceLineRe = re.compile(r'[^;\{]*[;\{]', re.DOTALL)
bracketRe = re.compile(r'[\{\}]')

def getClasses(f, java):
    sourceLineFactory = SourceLineFactory(f)
    classList = []
    for sourceLineM in sourceLineFactory.classRe.finditer(java):
        classList.append(sourceLineFactory.create(java, sourceLineM))
    return classList

def getClassStack(classList, sourceLine):
    classStack = []
    for cls in classList:
        if cls.getBounds()[0] <= sourceLine.getBounds()[0] and cls.getBounds()[1] >= sourceLine.getBounds()[1]:
            classStack.append(cls)
    return classStack

def getPackage(java):
    packageM = packageRe.search(java)
    package = None
    if packageM:
        package = packageM.group(0).split()[-1][:-1]

def getJavadocs(java, f, package, classList):
    sourceLineFactory = SourceLineFactory(f)
    for javadocTextM in javadocRe.finditer(java):
        javadocText = javadocTextM.group(0)
        startLine = java.count('\n', 0, javadocTextM.start())
        endLine = java.count('\n', 0, javadocTextM.end())
        sourceLineM = sourceLineRe.search(java, javadocTextM.end() + 1)
        if sourceLineM:
            sourceLine = sourceLineFactory.create(java, sourceLineM)
            if sourceLine:
                javadocComment = JavadocComment.create(Context(f, package, getClassStack(classList, sourceLine)), javadocText, (startLine, endLine), sourceLine)
                yield javadocComment

'''
Return list of all .java paths
'''
def getFiles(root):
    files = []
    for dirpath, dirnames, filenames in os.walk(root):
        for filename in [f for f in filenames if f.endswith('.java')]:
            files.append(os.path.join(dirpath, filename))
    return files

class JavadocGraph:
    def __init__(self, root):
        self.javadocs = []
        for f in getFiles(root):
            java = open(f, 'r').read()
            package = getPackage(java)
            fileClassList = getClasses(f, java)
            addedClassList = []
            for javadoc in getJavadocs(java, f, package, fileClassList):
                if isinstance(javadoc.getSourceLine(), ClassLine):
                    addedClassList.append(javadoc.getSourceLine())
                self.javadocs.append(javadoc)
            for cls in getClasses(f, java):
                if cls not in addedClassList:
                    dummyJavadoc = JavadocComment.createdummyclass(Context(f, package, getClassStack(fileClassList, cls)), cls)
                    self.javadocs.append(dummyJavadoc)

    def getTopLevelClasses(self):
        for javadoc in self.javadocs:
            if isinstance(javadoc.getSourceLine(), ClassLine):
                if len(javadoc.getContext().getClsStack()) == 1:
                    yield javadoc

    def getMethods(self, javadocClass):
        for javadoc in self.javadocs:
            if isinstance(javadoc.getSourceLine(), MethodLine):
                if javadocClass.getSourceLine().getBounds() == javadoc.getContext().getClsStack()[-1].getBounds():
                    yield javadoc

    def getFields(self, javadocClass):
        for javadoc in self.javadocs:
            if isinstance(javadoc.getSourceLine(), FieldLine):
                if javadocClass.getSourceLine().getBounds()  == javadoc.getContext().getClsStack()[-1].getBounds():
                    yield javadoc

    def getInnerClasses(self, javadocClass):
        outerBounds = javadocClass.getSourceLine().getBounds()
        for javadoc in self.javadocs:
            if isinstance(javadoc.getSourceLine(), ClassLine):
                innerBounds = javadoc.getSourceLine().getBounds()
                if outerBounds[0] < innerBounds[0] and outerBounds[1] > innerBounds[1]:
                    yield javadoc

    def resolveLink(self, javadocLink):
        linkText = javadocLink.text
        linkComponents = javadocLink.text.split('#')
        linkClass = None
        if linkText[0] == '#':
            linkClass = javadocLink.context.getFullName()
        else:
            for javadoc in self.javadocs:
                if isinstance(javadoc.getSourceLine(), ClassLine):
                    if javadoc.getContext().getFullName().endswith(linkComponents[0]):
                        linkClass = javadoc.getContext().getFullName()
        '''
        if linkClass and len(linkComponents) > 1:
            for javadoc in self.getMethods(linkClass):
                if re.sub('\s+', '', javadoc.getSourceLine().getSignature()) == re.sub('\s+', '', linkComponents[1]):
                    return javadoc
            for javadoc in self.getFields(linkClass):
                if javadoc.getSourceLine().getName() == linkComponents[1].strip():
                    return javadoc
        '''
        return linkClass
