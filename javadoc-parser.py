import re

javadocRegexp = re.compile(r'/\*\*.*?\*/', re.DOTALL)

def getJavadocs(f):
    java = f.read();
    javadocs = javadocRegexp.findall(java)
    return javadocs

print getJavadocs(open('Test.java', 'r'))
