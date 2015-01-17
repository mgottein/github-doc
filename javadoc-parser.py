import re

f = open('Test.java', 'r')
java = f.read()
regexp = re.compile(r'/\*\*.*?\*/', re.DOTALL)
results = regexp.findall(java)
for item in results:
    print item