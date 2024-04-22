import zipfile
import xml.etree.ElementTree as ET
from os import mkdir, path, getcwd
from shutil import rmtree
from pathlib import Path
from dataclasses import dataclass

@dataclass
class Style:

    name: str
    errors: list[str]

    def is_valid(self):
        return (len(self.errors) == 0)


class StyleChecker:

    file_name: str
    styles: list[str]
    work_dir: str
    tree: list[ET.Element]

    def __init__(self, name):
        self.file_name = name
        self.styles = []
        self.work_dir = "correct_file"
        self.tree = []
        self.__run()

    def __run(self):
        mkdir(self.work_dir)
        source_file = zipfile.ZipFile(self.file_name)
        source_file.extractall(self.work_dir)
        source_file.close()

        file = ET.parse(self.work_dir + "/content.xml")
        root = file.getroot()

        for elem in root.iter():
            self.tree.append(elem)
        
        for i in range(0, len(self.tree)):
            self.__is_valid_style(self.tree[i])
            self.__check_simple_text(self.tree[i])
            self.__check_header(self.tree[i], self.tree[i + 1] if (i + 1 != len(self.tree)) else None)

        file.write(self.work_dir + "/content.xml")
        dir = Path(self.work_dir)
        with zipfile.ZipFile('correct_' + self.file_name , "w", zipfile.ZIP_DEFLATED) as zip_file:
            for entry in dir.rglob("*"):
                zip_file.write(entry, entry.relative_to(dir))
        rmtree(path.join(getcwd(), self.work_dir))

    def __is_valid_style(self, elem: ET.Element):
        if (elem.tag.find('}style') != -1):
            errors = []
            name_style = ''
            style_name = 'Liberation Serif'
            size = '12pt'
            margin_right = '0cm'
            margin_left = '0cm'
            text_indent = '0cm'
            text_align = ""

            for (tag_name, item_name) in elem.attrib.items():
                if (tag_name.find('}name') != -1):
                    name_style = item_name
            for child in list(elem):
                if (child.tag.find('}text-properties') != -1):
                    for (tag, item) in child.attrib.items():
                        if (tag.find('}font-name') != -1):
                            style_name = item
                        if (tag.find('}font-size') != -1):
                            size = item
                if (child.tag.find('}paragraph-properties') != -1):
                    for(tag, item) in child.attrib.items():
                        if (tag.find('}margin-right') != -1):
                            margin_right = item
                        if (tag.find('}margin-left') != -1):
                            margin_left = item
                        if (tag.find('}text-indent') != -1):
                            text_indent = item   
                        if (tag.find('}text-align') != -1):
                            text_align = item 

            if (style_name != 'Times New Roman'):
                errors.append('шрифт Times New Roman')
            if (size != '14pt'):
                errors.append('размер шрифта 14pt')
            if (margin_right != '-1.85cm'):
                errors.append('отступ справа 15мм')
            if (margin_left != '-1.75cm'):
                errors.append('отступ слева 25мм')
            if (text_indent != '1.25cm'):
                errors.append('абзацный отступ 125мм')
            if (text_align != 'justify'):
                errors.append('выравнивание по ширине')
            self.styles.append(Style(name_style, errors))

    def __check_style(self, style_name: str, elem: ET.Element) -> str: 
        for style in self.styles:
            if (style_name == style.name and not style.is_valied()):
                return (', '.join(element for element in style.errors))

    def __check_simple_text(self, elem: ET.Element):
        if (elem.tag.find('}p') != -1 and not elem.text is None):
            errors = ""
            for (tag, item) in elem.attrib.items():
                if (tag.find('}style-name') != -1):
                    errors += self.__check_style(item, elem)
            if (len(errors) != 0):
                elem.text += " Исправить оформление на: " + errors

    def __check_header(self, elem: ET.Element, next_elem: ET.Element | None):
        if (elem.tag.find('}h') != -1 and not elem.text is None):
            errors = ""
            elem.text.rstrip(' ')
            if (elem.text[-1] != '.'):
                errors += " заголовок должен оканчиваться точкой"

            for (tag, item) in elem.attrib.items():
                if (tag.find('}style-name') != -1):
                    self.__check_style(item, elem)
                if (tag.find('}outline-level') != -1):
                    if(item == '1'):
                        if (not next_elem.text is None or next_elem is None):
                            errors += "," if (len(errors) != 0) else ""
                            errors += ' после заглавия должна быть пропущена строка'
                    else:
                        if(next_elem is None):
                            errors += "," if (len(errors) != 0) else ""
                            errors +=' после подзаголовка не должно быть пропуска строки'
            if (len(errors) != 0):
                elem.text += " Исправить оформление на: " + errors

    