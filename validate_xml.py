import os
import sys
import re
from lxml import etree
from lxml.etree import XPathEvaluator


def validate_schema(xml_path: str, xsd_path: str) -> bool:
    """
    针对xml schema文件验证xml文件
    :param xml_path: xml文件路径
    :param xsd_path: xml schema文件路径
    :return: bool
    """
    # xmlschema_doc = etree.parse(xsd_path)
    xmlschema = etree.XMLSchema(file=xsd_path)
    xml_doc = etree.parse(xml_path)
    result = xmlschema.validate(xml_doc)
    if not result:
        print("error log:\n", xmlschema.error_log.filter_from_errors())
    return result


def validate_dtd(xml_path: str, dtd_path: str) -> bool:
    """
    针对DTD文件验证xml文件
    :param xml_path: xml文件路径
    :param dtd_path: dtd文件路径
    :return: bool
    """
    # stream = open(dtd_path)  # return file-like object
    dtd = etree.DTD(dtd_path)
    #  Return an ElementTree object loaded with source elements
    root_node = etree.parse(xml_path)
    result = dtd.validate(root_node)
    if not result:
        print("error log:\n", dtd.error_log.filter_from_errors())
    return result


def select_by_xpath(xml_path, express: str):
    tree = etree.parse(xml_path)
    # results = tree.xpath(xpath)
    # etree.XMLParser()
    # tree = etree.XML(xml_path)
    # etree.XPath()
    results = tree.xpath(express)
    print("reulst: ", results, len(results))
    for item in results:
        print("%s: %s" % (item.tag, item.text))
        print("item: ", etree.tostring(item).decode('utf-8'))
        # print("attrib: ", item.values())


def xlst_transform_html(xml_path: str, xslt_path: str):
    """
    XSLT to transform XML into HTML
    :param xml_path:
    :param xslt_path:
    :return:
    """
    xslt_doc = etree.parse(xslt_path)
    xslt_transformer = etree.XSLT(xslt_doc)

    source_doc = etree.parse(xml_path)
    output_doc = xslt_transformer(source_doc)

    print(str(output_doc))
    file_name = xslt_path.replace("xsl", "html")
    output_doc.write(file_name, pretty_print=True)


def main(args):
    if len(args) < 1:
        print("Not enough arguments given.  Expected:")
        print("\tpython validate_xml.py <xml file name> [<dtd file name>]\n")
        exit(0)
    # line = '<!DOCTYPE bookstore SYSTEM "Book.dtd">'
    # res = re.search(r'<!DOCTYPE .* ["\'](\w+\.dtd)["\']>.*', line)
    xml_path = args[0]
    define_path = None
    is_exist = os.path.exists(xml_path)
    print("xml file %s is_exist: %r" % (xml_path, is_exist))
    if not is_exist:
        print("Don't found xml file: %s" % xml_path)
        exit(1)
    xml_path_dir = os.path.dirname(xml_path)
    if len(args) == 1:
        file = open(xml_path, 'r', encoding='utf-8')
        lines = file.readlines()
        file.close()
        print("lines: ", len(lines))
        for line in lines:
            # print("line: %r" % line)
            result = re.search(r'<!DOCTYPE .* ["\'](\w+\.[dtd|xsd]+)["\']>.*', line)
            # print("result: ", result)
            if result:
                if os.path.exists(result.group(1)):
                    define_path = result.group(1)
                else:
                    define_path = os.path.join(xml_path_dir, result.group(1))
                break
    elif len(args) == 2:
        define_path = args[1]
    # print("define_path: ", define_path)
    if define_path is None or not os.path.exists(define_path):
        print("Don't found dtd file: %r" % define_path)
        exit(2)
    print('Using DTD or XML Schema: %s' % os.path.abspath(define_path))
    if define_path.endswith('dtd'):
        valid_res = validate_dtd(xml_path, define_path)
    else:
        valid_res = validate_schema(xml_path, define_path)

    if valid_res:
        print("XML was valid!")
    else:
        print("XML was not valid！")
        exit(1)


def make_test():
    print("first, please input:\n xmlfile [dtdfile|xsdfile]")
    line = input(">").strip().split()
    main(line)
    xml_path = line[0]
    while True:
        line = input(">").strip().split()
        if line[0] == 'xpath':
            select_by_xpath(xml_path, '')
        elif line[0] == 'html' and len(line) >= 3:
            xlst_transform_html(line[1], line[2])
        else:
            print("invalid input!")


if __name__ == "__main__":
    # xml_file = 'university.xml'
    xml_file = 'test_data/book.xml'
    # dtd_file = 'University.dtd'
    dtd_file = 'test_data/Book.dtd'
    xsd_file = 'test_data/Note.xsd'

    express0 = "/bookstore/book/category"
    express1 = "/bookstore/book[1]/title"
    express11 = "//title"
    express2 = "/bookstore/book/price[text()]"
    express3 = "/bookstore/book[price<30]"
    select_by_xpath(xml_file, express11)
    # xlst_transform_html("test_data/book.xml", "test_data/Book.xsl")
    # make_test()
