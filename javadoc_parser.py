import re

tagRegexp = re.compile(r'\s*\**\s*@.*')

def isLineTag(line):
    return tagRegexp.match(line)

class Tag:
    def __init__(self, text):
        atIndex = text.index('@')


class Comment:

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
            if tagRegexp.match(line):
                tags.append((i, line))
            else:
                text.append((i, line))
            i = i + 1
        extractedTags.append(tags)
        extractedText.append(text)
    return (extractedTags, extractedText)

javadocs = getJavadocs(open('testapp/Test.java', 'r'))

extracted = extractTags(javadocs)
print "Tags"
print extracted[0]
print "Text"
print extracted[1]
