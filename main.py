##шрифт – Times New Roman;
##кегль – 14 pt;
##междустрочный интервал – полуторный;
##цвет шрифта – черный;
##поля страницы: левое – 25 мм, правое – 15 мм, верхнее и нижнее – 20 мм;
##выравнивание – по ширине;
##абзацный отступ – 1,25 см

import zipfile
import xml.etree.ElementTree as ET

def is_right_style(elem):
    if (elem.tag.find('}style') != -1):
        name_style = ''
        name_of_style = ''
        size = '12pt'
        for (tag_name, item_name) in elem.attrib.items():
            if (tag_name.find('}name') != -1):
                name_style = item_name
        for seach_size_and_style in elem.iter():
            if (seach_size_and_style.tag.find('}text-properties') != -1):
                for (tag, item) in seach_size_and_style.attrib.items():
                    if (tag.find('}font-name') != -1):
                        name_of_style = item
                    if (tag.find('}font-size') != -1):
                        size = item
                break
        if (name_of_style == 'Times New Roman' and size == '14pt'):
            return name_style
    return None


meow = zipfile.ZipFile('test.odt')
meow.extract('content.xml')
meow.close()

tree = ET.parse('content.xml')
root = tree.getroot()

right_styles = []

for elem in root.iter():
    maybe_right_style = is_right_style(elem)
    if (maybe_right_style != None):
        right_styles.append(maybe_right_style)
    

print(right_styles)

