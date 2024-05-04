import zipfile
import xml.etree.ElementTree as ET
from os import mkdir, path, getcwd
from shutil import rmtree
from pathlib import Path
import tempfile
from dataclasses import dataclass
from enum import Enum


@dataclass
class StyleInfo:
    font: str
    size: str
    margin_right: str
    margin_left: str
    text_indent: str
    text_align: str

correct_style = StyleInfo(
    font = 'Times New Roman',
    size = '14pt',
    margin_right = '-1.85cm',
    margin_left = '-1.75cm',
    text_indent = '1.25cm',
    text_align = 'justify',
)

default_style = StyleInfo(
    font = 'Liberation Serif',
    margin_right = '0cm',
    margin_left = '0cm',
    size = '12pt',
    text_indent = '0cm',
    text_align = "",
)

class ErrorType(Enum):
    FONT = 1
    FONT_SIZE = 2
    MARGIN_LEFT = 3
    MARGIN_RIGHT = 4
    TEXT_INDENT = 5
    ALIGNMENT = 6
    LOWER_OFFSET = 7
    UPPER_OFFSET = 8
    COLOR = 9
    SPACING = 10
    HEADER_DOT = 11
    HEADER_NEWLINE = 12
    SUBHEADER_NEWLINE = 13
    INVALID_STYLE = 14

    def pretty(self) -> str:
        match self:
            case ErrorType.FONT:
                return 'шрифт Times New Roman'
            case ErrorType.FONT_SIZE:
                return 'размер шрифта 14pt'
            case ErrorType.MARGIN_RIGHT:
                return 'отступ справа 15мм'
            case ErrorType.MARGIN_LEFT:
                return 'отступ слева 25мм'
            case ErrorType.TEXT_INDENT:
                return 'абзацный отступ 125мм'
            case ErrorType.ALIGNMENT:
                return 'выравнивание по ширине'
            case ErrorType.HEADER_DOT:
                return 'заголовок должен оканчиваться точкой'
            case ErrorType.HEADER_NEWLINE:
                return 'после заглавия должна быть пропущена строка'
            case ErrorType.SUBHEADER_NEWLINE:
                return 'после подзаголовка не должно быть пропуска строки'
            case ErrorType.INVALID_STYLE:
                return '???'
            case _:
                return 'неизвестная ошибка'


@dataclass
class Error:

    text: str
    errors: list[ErrorType]

    def pretty(self) -> str:
        output = self.text +'\n'
        output += '^' * len(self.text) + '\n'
        output += 'Исправить оформление на:\n'
        for error in self.errors:
            output += f"- {error.pretty()}\n"
        return output


class StyleChecker:

    file_name: str
    styleErorrs: dict[list[ErrorType]]
    tree: list[ET.Element]
    all_errors: list[str]

    def __init__(self, name):
        self.file_name = name
        self.styleErrors = {}
        self.tree = []
        self.all_errors = []

    def run(self):
        with tempfile.TemporaryDirectory() as work_dir:
            with zipfile.ZipFile(self.file_name) as source_file:
                source_file.extractall(work_dir)

            file = ET.parse(work_dir + "/content.xml")
            root = file.getroot()

            for elem in root.iter():
                self.tree.append(elem)

        errors = []
        for i in range(0, len(self.tree)):
            self.__is_valid_style(self.tree[i])
            errors += self.__check_simple_text(self.tree[i])
            errors += self.__check_header(self.tree[i], self.tree[i + 1] if (i + 1 != len(self.tree)) else None)

        for error in errors:
            self.all_errors.append(error.pretty())
        return self.all_errors

    def __is_valid_style(self, elem: ET.Element):
        if (elem.tag.find('}style') != -1):
            errors = []
            style = default_style
            name_style = ''

            for (tag_name, item_name) in elem.attrib.items():
                if (tag_name.find('}name') != -1):
                    name_style = item_name
            for child in list(elem):
                if (child.tag.find('}text-properties') != -1):
                    for (tag, item) in child.attrib.items():
                        if (tag.find('}font-name') != -1):
                            style.font = item
                        if (tag.find('}font-size') != -1):
                            style.size = item
                if (child.tag.find('}paragraph-properties') != -1):
                    for(tag, item) in child.attrib.items():
                        if (tag.find('}margin-right') != -1):
                            style.margin_right = item
                        if (tag.find('}margin-left') != -1):
                            style.margin_left = item
                        if (tag.find('}text-indent') != -1):
                            style.text_indent = item   
                        if (tag.find('}text-align') != -1):
                            style.text_align = item 

            if (style.font != correct_style.font):
                errors.append(ErrorType.FONT)
            if (style.size != correct_style.size):
                errors.append(ErrorType.FONT_SIZE)
            if (style.margin_right != correct_style.margin_right):
                errors.append(ErrorType.MARGIN_RIGHT)
            if (style.margin_left != correct_style.margin_left):
                errors.append(ErrorType.MARGIN_LEFT)
            if (style.text_indent != correct_style.text_indent):
                errors.append(ErrorType.TEXT_INDENT)
            if (style.text_align != correct_style.text_align):
                errors.append(ErrorType.ALIGNMENT)
            self.styleErrors[name_style] = errors

    def __check_style(self, style_name: str) -> list[ErrorType]: 
        try:
            return self.styleErrors[style_name]
        except:
            return [ErrorType.INVALID_STYLE]

    def __check_simple_text(self, elem: ET.Element) -> list[Error]:
        if (elem.tag.find('}p') != -1 and not elem.text is None):
            errors = []
            for (tag, item) in elem.attrib.items():
                if (tag.find('}style-name') != -1):
                    errors += self.__check_style(item)
            if (len(errors) != 0):
                return [Error(elem.text, errors)]
        return []

    def __check_header(self, elem: ET.Element, next_elem: ET.Element | None) -> list[Error]:
        if (elem.tag.find('}h') != -1 and not elem.text is None):
            errors = []
            if (elem.text[-1] != '.'):
                errors.append(ErrorType.HEADER_DOT)

            for (tag, item) in elem.attrib.items():
                if (tag.find('}style-name') != -1):
                    errors += self.__check_style(item)
                if (tag.find('}outline-level') != -1):
                    if(item == '1'):
                        if (not next_elem.text is None or next_elem is None):
                            errors.append(ErrorType.HEADER_NEWLINE)
                    else:
                        if(next_elem is None):
                            errors.append(ErrorType.SUBHEADER_NEWLINE)
            if (len(errors) != 0):
                return [Error(elem.text, errors)]
        return []

    