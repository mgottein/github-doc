import re

tagRegexp = re.compile(r'\s*\**\s*@.*')

def isLineTag(line):
    return tagRegexp.match(line)

class Tag:
    def __init__(self, lineNum, text):
        self.components = text.split(r'\s*')
        self.lineNum = lineNum

    def __str__(self):
        return str(self.components)

    def getComponents(self):
        return self.components

    def getLineNum(self):
        return self.lineNum

javadocRegexp = re.compile(r'/\*\*.*?\*/', re.DOTALL)

def getJavadocText(f):
    java = f.read();
    javadocs = javadocRegexp.findall(java)
    return javadocs


def extractTags(javadocs):
    extractedTags = []
    extractedText = []
    for javadoc in javadocs:
        tags = []
        text = []
        lines = javadoc.split('\n')
        i = 1
        while i < len(lines):
            line = lines[i]
            if isLineTag(line):
                tags.append(Tag(i, line))
            else:
                text.append((i, line))
            i = i + 1
        extractedTags.append(tags)
        extractedText.append(text)
    return (extractedTags, extractedText)
