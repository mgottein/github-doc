import re

javadocRegexp = re.compile(r'/\*\*.*?\*/', re.DOTALL)

def getJavadocs(f):
    java = f.read();
    javadocs = javadocRegexp.findall(java)
    return javadocs

def extractTags(javadocs):
    extractedTags = []
    extractedText = []
    tagRegexp = re.compile(r'\s*\**\s*@.*')
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

javadocs = getJavadocs(open('Test.java', 'r'))

extracted = extractTags(javadocs)
print "Tags"
print extracted[0]
print "Text"
print extracted[1]
