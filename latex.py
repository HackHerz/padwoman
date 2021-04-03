# convert html document to LaTeX
# https://tex.stackexchange.com/questions/167523/html-to-latex-how-can-i-use-python-and-lxml-to-convert-an-html-document-to-late
from lxml import etree
from io import StringIO


# fill in this function to catch and convert html tags
def html2latex(el, tabs=0):
    result = []
    t = '\t' * tabs

    if el.text:
        result.append(el.text)

    for sel in el:
        if False:  # get info
            print('tag', sel.tag)
            print('text', sel.text)
            print('tail', sel.tail)
            print('attrib', sel.attrib)

        elif sel.tag in ["br"]:  # newline
            result.append("\n")

        elif sel.tag in ["strong"]:  # bold
            result.append('\\textbf{%s}' % html2latex(sel))

        elif sel.tag in ["em"]:  # italics
            result.append('\\textit{%s}' % html2latex(sel))

        elif sel.tag in ["u"]:  # underline
            result.append('\\underline{%s}' % html2latex(sel))

        elif sel.tag in ["a"]:  # url
            result.append('\\url{%s}' % html2latex(sel))

        # enumerations
        elif sel.tag in ["ol"]:
            result.append(('\n' + t + '\\begin{enumerate}\n%s' + t + '\\end{enumerate}') %
                          html2latex(sel, tabs+1))

        # itemize
        elif sel.tag in ["ul"]:
            result.append(('\n' + t + '\\begin{itemize}\n%s' + t + '\\end{itemize}') %
                          html2latex(sel, tabs+1))

        elif sel.tag in ["li"]:
            result.append(t + '\\item %s\n' % html2latex(sel, tabs))

        else:
            result.append(html2latex(sel))

        if sel.tail:
            result.append(sel.tail)
    return "".join(result)


def latex(html):
    print(html)
    parser = etree.HTMLParser()
    tree = etree.parse(StringIO(html), parser)  # expects a file, use StringIO
    root = tree.getroot()
    latex = html2latex(root)
    return latex
