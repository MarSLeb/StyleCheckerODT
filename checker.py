import zipfile
import xml.etree.ElementTree as ET
import tempfile
from dataclasses import dataclass
from enum import Enum
from anytree import NodeMixin, RenderTree
from time import sleep


@dataclass
class StyleInfo:
    font: str
    size: str
    margin_right: str
    margin_left: str
    text_indent: str
    text_align: str
    padding_top: str
    padding_bottom: str
    color: str

correct_style = StyleInfo(
    font = 'Times New Roman',
    size = '14pt',
    margin_right = '-1.85cm',
    margin_left = '-1.75cm',
    text_indent = '1.251cm',
    padding_top = '0.199cm',
    padding_bottom = '0.199cm',
    text_align = 'justify',
    color = '#000000',
)

default_style = StyleInfo(
    font = 'Liberation Serif',
    margin_right = '0cm',
    margin_left = '0cm',
    size = '12pt',
    text_indent = '0cm',
    text_align = "",
    padding_top = "",
    padding_bottom = "",
    color = '#000000',
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
    SPACE_ABOVE_IMAGE = 14
    SPACE_UNDER_IMAGE = 15
    NAME_OF_IMAGE = 16

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
                return 'точка после номера и в конце названия раздела не ставится'
            case ErrorType.HEADER_NEWLINE:
                return 'после заглавия должна быть пропущена строка'
            case ErrorType.INVALID_STYLE:
                return '???'
            case ErrorType.SPACE_ABOVE_IMAGE:
                return 'при размещении страниц в тексте следует отделять рисунок от текста пустой строкой сверху'
            case ErrorType.SPACE_UNDER_IMAGE:
                return 'при размещении страниц в тексте следует отделять рисунок от текста пустой строкой снизу'
            case ErrorType.NAME_OF_IMAGE:
                return 'не найдено или неправильно оформлено имя рисунка. Рисунки нумеруются \
арабскими цифрами по схеме «рисунок номер_раздела.номер_рисунка - описание»'
            case ErrorType.COLOR:
                return 'цвет текста должен быть черным'
            case ErrorType.LOWER_OFFSET:
                return 'нижнее поле страницы должно быть 20мм'
            case ErrorType.UPPER_OFFSET:
                return 'верхнее поле страницы должно быть 20мм'
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
    return "".join(root.xml_elem.itertext())


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
            with zipfile.ZipFile(self.file_name) as source_file:
                source_file.extractall(work_dir)
            file = ET.parse(work_dir + "/content.xml")
            root_tree = Elem_xml_tree(file.getroot())
            load_children(root_tree, file.getroot())

        for chapter in root_tree.children:
            match chapter.tag:
                case "font-face-decls":
                    pass 
                case "automatic-styles":
                    for style in chapter.children:
                        self.__is_valid_style(style)
                case "body":
                    for body_chapter in chapter.children:
                        if (body_chapter.tag == "text"):
                            self.__check_text(body_chapter)
        return self.all_errors

    def __check_text(self, root: Elem_xml_tree):
        for i in range(len(root.children)):
            errors = []
            match root.children[i].tag:
                case "table":
                    pass
                case "p":
                    errors += self.__check_simple_text(root.children[i])
                    errors += self.__check_image(root, i)
                case "h":
                    errors += self.__check_header(root.children[i], root.children[i + 1] \
                                      if (i + 1 != len(root.children)) else None)
                case "table-of-content":
                    pass
                case "list":
                    pass
                
            for error in errors:
                self.all_errors.append(error.pretty())

            if (root.children[i].tag != "p" and root.children[i].tag != "h"):
                self.__check_text(root.children[i])
            
            
    def __check_image(self, node: Elem_xml_tree, num):
        for _, _, elem in RenderTree(node.children[num]):
            if (elem.tag == "annotation" or elem.tag == "annotation-end"):
                return []  
        for _, _, elem in RenderTree(node.children[num]):
            if (elem.tag == "image"):
                text = ""
                errors = []
                if (num == 0 or internal_text(node.children[num - 1]) != ""):
                    errors.append(ErrorType.SPACE_ABOVE_IMAGE)
                if (num - 1 == len(node.children) or \
                    num + 1 < len(node.children) and internal_text(node.children[num + 1]) != ""):
                    errors.append(ErrorType.SPACE_UNDER_IMAGE)
                
                i = num + 1
                while (i < len(node.children) and i < num + 3):
                    name = internal_text(node.children[i])
                    if (node.children[i].tag == "p" and name != ""):
                        for _, _, meow in RenderTree(node.children[i]):
                            if (meow.tag == "annotation" or meow.tag == "annotation-end"):
                                return []
                        match name.split():
                            case ["рисунок", _, "-", *_]:
                                text = name
                            case _:
                                errors.append(ErrorType.NAME_OF_IMAGE)
                        if (len(errors) != 0):
                            return [Error(text, errors)]
                        else:
                            return []
                    i += 1
                errors.append(ErrorType.NAME_OF_IMAGE)
                return [Error(text, errors)]
        return []

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
                        if (tag.find('}color') != -1):
                            style.color = item
                if (child.tag == "paragraph-properties"):
                    for(tag, item) in child.xml_elem.attrib.items():
                        _, _, tail_tag = tag.partition('}')
                        match tail_tag:
                            case "margin-right":
                                style.margin_right = item
                            case "margin-left":
                                style.margin_left = item
                            case "text-indent":
                                style.text_indent = item   
                            case "text-align":
                                style.text_align = item 
                            case "padding-bottom":
                                style.padding_bottom = item
                            case "padding-top":
                                style.padding_top = item

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
            if (style.padding_bottom != correct_style.padding_bottom):
                errors.append(ErrorType.LOWER_OFFSET)
            if (style.padding_top != correct_style.padding_top):
                errors.append(ErrorType.UPPER_OFFSET)
            if (style.color != correct_style.color):
                errors.append(ErrorType.COLOR)
            self.styleErrors[name_style] = errors

    def __check_style(self, style_name: str) -> list[ErrorType]: 
        try:
            return self.styleErrors[style_name]
        except:
            return [ErrorType.INVALID_STYLE]

    def __check_simple_text(self, elem: Elem_xml_tree) -> list[Error]:
        text = internal_text(elem)
        if (text != ""):
            for _, _, child in RenderTree(elem):
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
        text = internal_text(elem)
        if (text != ""):
            for _, _, child in RenderTree(elem):
                if (child.tag == "annotation" or child.tag == "annotation-end"):
                    return []                
            errors = []
            for (tag, item) in elem.xml_elem.attrib.items():
                _, _, tail_tag = tag.partition('}')
                if (tail_tag == "style-name"):
                    errors += self.__check_style(item)
            num = ""
            for i in text:
                if (i.isnumeric()):
                    num += i
            if (text == "" or next_elem is None or text[len(num)] == '.'):
                errors.append(ErrorType.HEADER_NEWLINE)
            if (text[-1] == '.'):
                errors.append(ErrorType.HEADER_DOT)
            if (len(errors) != 0):
                return [Error(text, errors)]
        return []
    

    