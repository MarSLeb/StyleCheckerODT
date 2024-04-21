##шрифт – Times New Roman; !
##кегль – 14 pt; !
##междустрочный интервал – полуторный;
##цвет шрифта – черный;
##поля страницы: левое – 25 мм, правое – 15 мм, верхнее и нижнее – 20 мм;
##выравнивание – по ширине;
##абзацный отступ – 1,25 см !

import zipfile
import xml.etree.ElementTree as ET
import os
import shutil
import pathlib

class Style:
    name: str
    errors: list[str]
    def __init__(self, name, errors):
        self.name = name
        self.errors = errors
    def is_valied(self):
        return (len(self.errors) == 0)

def is_right_style(elem):
    if (elem.tag.find('}style') != -1):
        errors = []
        name_style = ''
        name_of_style = 'Liberation Serif'
        size = '12pt'
        for (tag_name, item_name) in elem.attrib.items():
            if (tag_name.find('}name') != -1):
                name_style = item_name
        for seach_size_and_style in list(elem):
            if (seach_size_and_style.tag.find('}text-properties') != -1):
                for (tag, item) in seach_size_and_style.attrib.items():
                    if (tag.find('}font-name') != -1):
                        name_of_style = item
                    if (tag.find('}font-size') != -1):
                        size = item
                break
        if (name_of_style != 'Times New Roman'):
            errors.append('необходим шрифт Times New Roman')
        if (size != '14pt'):
            errors.append('необходим размер шрифта 14pt')
        return Style(name_style, errors)
    return None

def check_style(style_name, elem):
    for style in styles:
        if (style_name == style.name and not style.is_valied()):
            elem.text = str(elem.text) + \
                            ' Ошибка оформления абзаца: ' + \
                            ' ,'.join(element for element in style.errors)

def check_simple_text(elem):
    if (elem.tag.find('}p') != -1 and not elem.text is None):
        for (tag, item) in elem.attrib.items():
            if (tag.find('}style-name') != -1):
                check_style(item, elem)
    

def check_header(elem):
    if (elem.tag.find('}h') != -1 and not elem.text is None):
        elem.text.rstrip(' ')
        if (elem.text[-1] != '.'):
            elem.text = str(elem.text) + \
                            ' Ошибка оформления: заголовок должен оканчиваться точкой.'
            
        for (tag, item) in elem.attrib.items():
            if (tag.find('}style-name') != -1):
                check_style(item, elem)
            if (tag.find('}outline-level') != -1):
                if(item == '1'):
                    pass
                else:
                    pass

file_name = 'test.odt'
os.mkdir('correct_file')

source_file = zipfile.ZipFile(file_name)
source_file.extractall('correct_file')
source_file.close()

tree = ET.parse('correct_file/content.xml')
root = tree.getroot()

styles = []

for elem in root.iter():
    maybe_right_style = is_right_style(elem)
    if (not maybe_right_style is None):
        styles.append(maybe_right_style)
    check_simple_text(elem)
    check_header(elem)      
tree.write('correct_file/content.xml')
    
dir = pathlib.Path('correct_file')
with zipfile.ZipFile('correct_' + file_name , "w", zipfile.ZIP_DEFLATED) as zip_file:
    for entry in dir.rglob("*"):
        zip_file.write(entry, entry.relative_to(dir))
shutil.rmtree(os.path.join(os.getcwd(), 'correct_file/'))