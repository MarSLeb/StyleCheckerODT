import zipfile
import xml.etree.ElementTree as ET
import tempfile
from dataclasses import dataclass
from enum import Enum
from anytree import NodeMixin, RenderTree


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
    INVALID_STYLE = 13

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


class Elem_xml_tree(ET.Element, NodeMixin):
    def __init__(self, xml_elem: ET.Element, parent=None, children=None):
        super(Elem_xml_tree).__init__()
        _, _, tail = xml_elem.tag.partition('}')
        self.tag = tail
        self.xml_elem = xml_elem
        self.parent = parent
        if children:
            self.children = children

def load_children(parent: Elem_xml_tree, elem_xml: ET.Element):
    for elem in list(elem_xml):
        children = Elem_xml_tree(elem, parent=parent)
        load_children(children, elem)

def internal_text(root: Elem_xml_tree):
    return " ".join(root.xml_elem.itertext())


class StyleChecker:

    file_name: str
    styleErorrs: dict[list[ErrorType]]
    tree: list[ET.Element]
    all_errors: list[str]
    data: list[str]

    def __init__(self, name):
        self.file_name = name
        self.styleErrors = {}
        self.tree = []
        self.all_errors = []
        self.data = []

    def run(self):
        with tempfile.TemporaryDirectory() as work_dir:
            with zipfile.ZipFile("test.odt") as source_file:
                source_file.extractall(work_dir)
            file = ET.parse(work_dir + "/content.xml")
            root_tree = Elem_xml_tree(file.getroot())
            load_children(root_tree, file.getroot())

        for chapter in root_tree.children:
            if (chapter.tag ==  "font-face-decls"):
                pass 
            elif (chapter.tag == "automatic-styles"):
                for style in chapter.children:
                    self.__is_valid_style(style)
            elif (chapter.tag == "body"):
                for body_chapter in chapter.children:
                    if (body_chapter.tag == "text"):
                        self.__check_text(body_chapter)
        return self.all_errors

    def __check_text(self, root: Elem_xml_tree):
        errors = []
        for i in range(len(root.children)):
            errors += self.__check_simple_text(root.children[i])
            errors += self.__check_header(root.children[i], root.children[i + 1] \
                                  if (i + 1 != len(root.children)) else None)
            for error in errors:
                self.all_errors.append(error.pretty())
            errors = []
            if (root.children[i].tag != "p" or root.children[i].tag != "h"):
                self.__check_text(root.children[i])

    def __is_valid_style(self, elem: Elem_xml_tree):
        if (elem.tag == "style"):
            errors = []
            style = default_style
            name_style = ""

            for (tag, item) in elem.xml_elem.attrib.items():
                _, _, tail_tag = tag.partition('}')
                if (tail_tag == "name"):
                    name_style = item
            for child in elem.children:
                if (child.tag == "text-properties"):
                    for (tag, item) in child.xml_elem.attrib.items():
                        _, _, tail_tag = tag.partition('}')
                        if (tail_tag == "font-name"):
                            style.font = item
                        if (tail_tag == "font-size"):
                            style.size = item
                if (child.tag == "paragraph-properties"):
                    for(tag, item) in child.xml_elem.attrib.items():
                        _, _, tail_tag = tag.partition('}')
                        if (tail_tag == "margin-right"):
                            style.margin_right = item
                        if (tail_tag == "margin-left"):
                            style.margin_left = item
                        if (tail_tag == "text-indent"):
                            style.text_indent = item   
                        if (tail_tag == "text-align"):
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

    def __check_simple_text(self, elem: Elem_xml_tree) -> list[Error]:
        text = internal_text(elem)
        if (elem.tag == "p" and text != ""):
            for child in elem.children:
                if (child.tag == "annotation" or child.tag == "annotation-end"):
                    return []
            errors = []

            for (tag, item) in elem.xml_elem.attrib.items():
                _, _, tail_tag = tag.partition('}')
                if (tail_tag == "style-name"):
                    errors += self.__check_style(item)
            if (len(errors) != 0):
                return [Error(text, errors)]
        return []

    def __check_header(self, elem: Elem_xml_tree, next_elem: Elem_xml_tree | None) -> list[Error]:
        if (elem.tag == "h"):
            for child in elem.children:
                if (child.tag == "annotation" or child.tag == "annotation-end"):
                    return []
            text = internal_text(elem)
            errors = []

            for (tag, item) in elem.xml_elem.attrib.items():
                _, _, tail_tag = tag.partition('}')
                if (tail_tag == "style-name"):
                    errors += self.__check_style(item)

            if (text == "" or next_elem is None):
                errors.append(ErrorType.HEADER_NEWLINE)
            if (text[-1] == '.'):
                errors.append(ErrorType.HEADER_DOT)

            if (len(errors) != 0):
                return [Error(text, errors)]
        return []

    