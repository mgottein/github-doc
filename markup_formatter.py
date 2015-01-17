'''
Header text
'''
def hx(size, text):
    return (('#' * size) + ' {}'.format(text))

'''
Bold text
'''
def bold(text):
    return '**{}**'.format(text)

'''
Italic text
'''
def italic(text):
    return '*{}*'.format(text)

'''
Image link (inline)
'''
def image(link, alt_text=None):
    if alt_text:
        return '![alt text]({} "{}")'.format(link, alt_text)
    else:
        return '![alt text]({})'.format(link)
    
'''
Quote text
'''
def quote(text, cite=None):
    if cite:
        return '> {}\n> <cite>{}</cite>'.format(text, cite)
    else:
        return '> {}'.format(text)

'''
Syntax highlighting
'''
def code(lang, text):
    return '```{}\n{}\n```'.format(lang, text)

'''
Web link
'''
def link(text, link):
    return '[{}]({})'.format(text, link)

'''
Create list from array
'''
def clist(list, numbered=False, join=False):
    for i in range(len(list)):
        if numbered:
            list[i] = '{}. {}'.format(i+1, list[i])
        else:
            list[i] = '* {}'.format(list[i])
    if join:
        return ''.join(list)
    else:
        return list