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
        for line in javadoc.split('\n'):
            if tagRegexp.match(line):
                tags.append(line)
            else:
                text.append(line)
        extractedTags.append(tags)
        extractedText.append(text)
    return (extractedTags, extractedText)



javadocs = getJavadocs(open('Test.java', 'r'))

extracted = extractTags(javadocs)
print "Tags"
print extracted[0]
print "Text"
print extracted[1]
