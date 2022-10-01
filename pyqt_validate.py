import os
import sys
import re

from lxml import etree

from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QLineEdit, QTextEdit, QWidget, QPushButton, \
    QHBoxLayout, QVBoxLayout, QFileDialog, QMessageBox


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("my XML")

        self.show_path_label = QLabel("file path")
        self.choose_button = QPushButton("选择xml文件")
        self.valid_button = QPushButton("验证xml文件")
        layout1 = QHBoxLayout()
        layout1.addWidget(self.show_path_label)
        layout1.addWidget(self.choose_button)
        layout1.addWidget(self.valid_button)

        self.show_path_label2 = QLabel("file path")
        self.choose_button2 = QPushButton("选择xsl文件")
        self.transform_button = QPushButton("xsl转html")
        layout12 = QHBoxLayout()
        layout12.addWidget(self.show_path_label2)
        layout12.addWidget(self.choose_button2)
        layout12.addWidget(self.transform_button)

        self.input = QLineEdit("请输入xpath查询语句")
        self.xpath_button = QPushButton("xpath查询")
        layout2 = QHBoxLayout()
        layout2.addWidget(self.input)
        layout2.addWidget(self.xpath_button)

        self.show_text = QTextEdit()
        layout3 = QVBoxLayout()
        layout3.addLayout(layout1)
        layout3.addLayout(layout12)
        layout3.addLayout(layout2)
        layout3.addWidget(self.show_text)

        container = QWidget()
        container.setLayout(layout3)

        # Set the central widget of the Window.
        self.setCentralWidget(container)
        self.setGeometry(300, 200, 600, 600)
        self.init_widget()

    def init_widget(self):
        self.valid_button.setEnabled(False)
        self.xpath_button.setEnabled(False)
        self.transform_button.setEnabled(False)
        self.choose_button.clicked.connect(self.choose_file)
        self.valid_button.clicked.connect(self.validate_xml)
        self.xpath_button.clicked.connect(self.select_by_xpath)
        self.choose_button2.clicked.connect(self.choose_file2)
        self.transform_button.clicked.connect(self.xlst_transform_html)

    def choose_file(self):
        result = QFileDialog.getOpenFileName(self, caption='xml文件', directory='./', filter='*.xml')
        file_path = result[0]
        print("result file type: ", result)
        if file_path and os.path.exists(file_path):
            self.show_path_label.setText(file_path)
            self.valid_button.setEnabled(True)

        print("file_path: ", type(file_path), file_path)

    def choose_file2(self):
        result = QFileDialog.getOpenFileName(self, caption='xml文件', directory='./', filter='*.xsl')
        # result = QFileDialog.getOpenFileName(self, caption='xsl文件', directory='./', filter='*.xsl')
        file_path = result[0]
        print("result file type: ", result)
        if file_path and os.path.exists(file_path):
            self.show_path_label2.setText(file_path)
            self.transform_button.setEnabled(True)

        print("file_path: ", type(file_path), file_path)

    def validate_xml(self):
        xml_path = self.show_path_label.text()
        print("xml_path: %s" % xml_path)
        xml_path_dir = os.path.dirname(xml_path)
        print("xml_path dir: %s" % xml_path_dir)
        define_path = None
        file = open(xml_path, 'r', encoding='utf-8')
        lines = file.readlines()
        file.close()
        # print("lines: ", len(lines))
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
        # print("define_path: ", os.path.exists(define_path), define_path)
        if define_path is None or not os.path.exists(define_path):
            msg = "Don't found dtd file: %r" % define_path
            self.show_text.setText(msg)
            return

        if define_path.endswith('dtd'):
            valid_res = self.validate_dtd(xml_path, define_path)
        else:
            valid_res = self.validate_schema(xml_path, define_path)

        if valid_res:
            self.xpath_button.setEnabled(True)
            msg = "XML was valid!"
            self.show_text.setText(msg)

    def validate_schema(self, xml_path: str, xsd_path: str) -> bool:
        """
        针对xml schema文件验证xml文件
        :param xml_path: xml文件路径
        :param xsd_path: xml schema文件路径
        :return: bool
        """
        try:
            # xmlschema_doc = etree.parse(xsd_path)
            xmlschema = etree.XMLSchema(file=xsd_path)
            xml_doc = etree.parse(xml_path)
            result = xmlschema.validate(xml_doc)
            if result:
                msg_box = QMessageBox(QMessageBox.Icon.Information, '校验成功', '此xml被dtd判定合法^-^')
                msg_box.exec()
            if not result:
                # print("error log:")
                msg = "XML was not valid！\n " + str(xmlschema.error_log.filter_from_errors())
                self.show_text.setText(msg)
            return result
        except Exception as e:
            msg = "Exception: \n %r" % e
            self.show_text.setText(msg)
            msg_box = QMessageBox(QMessageBox.Icon.Warning, 'xml校验出错', "Error")
            msg_box.exec()

    def validate_dtd(self, xml_path: str, dtd_path: str) -> bool:
        """
        针对DTD文件验证xml文件
        :param xml_path: xml文件路径
        :param dtd_path: dtd文件路径
        :return: bool
        """
        try:
            # stream = open(dtd_path)  # return file-like object
            dtd = etree.DTD(dtd_path)
            #  Return an ElementTree object loaded with source elements
            root_node = etree.parse(xml_path)
            result = dtd.validate(root_node)
            if not result:
                # print("error log:\n", )
                msg = "XML was not valid！\n "
                for item in dtd.error_log.filter_from_errors():
                    msg += str(item) + '\n'
                print("msg: ", msg)
                self.show_text.setText(msg)
            return result
        except Exception as e:
            msg = "Exception: \n %r" % e
            self.show_text.setText(msg)

    def select_by_xpath(self):
        """
        通过xpath语句查找
        :return: None
        """
        xml_path = self.show_path_label.text()
        express = self.input.text()
        try:
            tree = etree.parse(xml_path)
            results = tree.xpath(express)
        except Exception as e:
            msg = "Exception: \n %r" % e
            self.show_text.setText(msg)
            return
        res_list = list()
        if len(results) > 0:
            for item in results:
                str_item = etree.tostring(item).decode('utf-8')
                res_list.append(str_item)

        self.show_text.setText('\n'.join(res_list))

    def xlst_transform_html(self):
        """
        XSLT to transform XML into HTML
        :return:
        """
        xml_path = self.show_path_label.text()
        xslt_path = self.show_path_label2.text()
        xslt_doc = etree.parse(xslt_path)
        xslt_transformer = etree.XSLT(xslt_doc)

        source_doc = etree.parse(xml_path)
        output_doc = xslt_transformer(source_doc)

        msg = str(output_doc)
        self.show_text.setText(msg)
        file_name = xslt_path.replace("xsl", "html")
        output_doc.write(file_name, pretty_print=True)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
