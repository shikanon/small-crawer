#!/usr/bin/env python3
# coding:utf8
# __author__ = "shikanon <shikanon@live.com>"
#__version__ = "0.2.2"

import logging
import re
from abc import ABCMeta, abstractmethod
from bs4 import BeautifulSoup
from lxml import etree
from lxml.html import html5parser, tostring, fromstring
from hashlib import md5
from urllib.parse import urlsplit, urljoin
from multiprocessing.dummy import Pool
from pyquery import PyQuery


class Parser(metaclass=ABCMeta):
    '''
    Input: to input a parsed file content to the Parser class,
    and use parse function to get the result.
    '''

    def __init__(self):
        self.parsed_files = None
        self.result = {}

    def load_parsed_files(self, parsed_files, python_script=None):
        '''
        加载xml模板数据和python脚本数据
        '''
        self.python_script = python_script
        if self.parsed_files is None:
            self.parsed_files = [parsed_files]
        elif isinstance(parsed_files, list):
            self.parsed_files = self.parsed_files + parsed_files
        else:
            self.parsed_files.append(parsed_files)

    @abstractmethod
    def XMLTemplateTest(self, url, content):
        pass

    def TemplateTest(self, response):
        '''
        XML模板文件测试,
        return example:
        {XML1-MD5: True, XML2-MD5: False, ...}
        其关键字XML1为xml文件的MD5值(UTF8)
        '''
        return self.XMLTemplateTest(response.url, response.content)

    @abstractmethod
    def parsering(self, url, content):
        pass

    def parse(self, response):
        '''
        the parse function used to parse the response though parsed file.
        Return a dict include parsed-data and outlink,
        parsed data is a key/value pair,
        oulink is a urls collection include url and metadata.
        return example:
        {
          "parsed-data":
             {key2 :[value1,...],key2:[value2,...],...},
          "outlink":
            {
               url_1:{"inlink":current-url,"update-interval":1, ...},
               url_2:{"inlink":current-url,"update-interval":1, ...},
               ...
            }
        }
        '''
        return self.parsering(response.url, response.text)


class XMLParser(Parser):

    def parsering(self, url, content):
        # 初始化
        # 返回值可能为空{}，也可以只有一个如{"parsered":{key2 :[value1,...],key2:[value2,...],...}}
        self.url = url
        self.content = content

        if self.parsed_files is None:
            raise AttributeError(
                "please use load_parsed_files function load parsed_file")
        for parsed_file in self.parsed_files:
            pattern_data, outlink = self.parser_model(parsed_file)
            if pattern_data:
                self.result["parsed-data"] = pattern_data
            if outlink:
                self.result["outlink"] = outlink
        return self.result

    def XMLTemplateTest(self, url, content):
        '''
        XML模板文件测试,
        return example:
        {XML1-MD5: True, XML2-MD5: False, ...}
        其关键字XML1为xml文件的MD5值(UTF8)
        '''
        # 初始化
        self.url = url
        self.content = content
        if self.parsed_files is None:
            raise AttributeError(
                "please use load_parsed_files function load parsed_file")
        test_result = {}
        pattern_data, outlink = None, None
        for parsed_file in self.parsed_files:
            try:
                pattern_data, outlink = self.parser_model(parsed_file)
            finally:
                if pattern_data is None or outlink is None:
                    test_result[
                        md5(parsed_file.encode("utf8")).hexdigest()] = False
                else:
                    test_result[
                        md5(parsed_file.encode("utf8")).hexdigest()] = True
        return test_result

    def xpath_parser(self, expression, content):
        '''
        xpath解析方法
        '''
        try:
            html = etree.parse(response, etree.HTMLParser())
        except:
            html = fromstring(content)
        try:
            express_result = html.xpath(expression)
        except:
            logging.error(u"xml解析文件存在错误!xpath表达式存在错误.")
            raise AttributeError("xml_file is Error! xpath parser is incorroct,\
             please input valid xpath parser.")
        return express_result

    def css_parser(self, expression, content):
        '''css解析方法
        Return:为一个标签数组'''
        try:
            html = etree.parse(content, etree.HTMLParser())
        except:
            html = fromstring(content)
        query_tree = PyQuery(html)
        return query_tree(expression)

    def str_parser(self, str_value, expression_method):
        '''
        对xpath解析后的字符串进行后续解析
        '''
        # 字符串切片
        if expression_method["str-range"]:
            str_start, str_end = ("", "")
            if "start" in expression_method["str-range"].attrs.keys():
                str_start = expression_method["str-range"].attrs["start"]
            if "end" in expression_method["str-range"].attrs.keys():
                str_end = expression_method["str-range"].attrs["end"]
            str_value = self.str_slice_parser(str_value, str_start, str_end)
        # 正则法解析
        if expression_method["regular-match"] is not None:
            str_value = self.regular_parser(
                expression_method["regular-match"].string, str_value)
        if expression_method["script-name"] is not None:
            if self.python_script is None:
                logging.warn("Python脚本未加载,请传入Python脚本函数.")
            else:
                str_value = self.python_function_parser(
                    self.python_script, str_value, expression_method["script-name"].string)
        # 自定义python代码进行解析
        if expression_method["script"] is not None:
            if "def user_parser_function" not in expression_method["script"].string:
                logging.warn("Python脚本函数名称错误,没有用指定函数名.")
                raise SyntaxError("Python script exit SyntaxError!")
            str_value = self.python_function_parser(
                expression_method["script"].string, str_value)
        return str_value

    def str_slice_parser(self, str_content, start, end):
        '''
        字符串切片解析方法
        '''
        str_pattern = "%s(.*)%s" % (start, end)
        str_value = re.findall(str_pattern, str_content)
        if len(str_value):
            return str_value[0]
        else:
            return str_content

    def regular_parser(self, expression, str_content):
        '''
        字符串正则表达式解析
        '''
        if not expression:
            return str_content
        else:
            try:
                str_value = re.findall(expression, str_content)
                if len(str_value):
                    return str_value[0]
                else:
                    return None
            except:
                logging.warn(u"xml解析文件存在错误!正则表达式存在语法错误.")
                raise AttributeError(
                    "xml_file is Error! Regular Parser Syntax is error.")

    def python_function_parser(self, expression, str_content, function_name=None):
        '''
        字符串python自定义函数解析
        '''
        if not expression:
            return str_content
        try:
            exec(expression)
            if function_name is not None:
                exec("self.script_str_content = %s('''%s''')" %
                     (function_name, str_content))
                str_content = self.script_str_content
                del self.script_str_content
            elif "def user_parser_function" in expression:
                exec(
                    "self.script_str_content = user_parser_function('''%s''')" % str_content)
                str_content = self.script_str_content
                del self.script_str_content
            elif "def user_normalize_function" in expression:
                exec(
                    "self.script_str_content = user_normalize_function('''%s''')" % str_content)
                str_content = self.script_str_content
                del self.script_str_content
            elif "def " in expression:
                function_name = re.findall("def (.*?)\(", expression)[0]
                exec("self.script_str_content = %s('''%s''')" %(function_name, str_content))
                str_content = self.script_str_content
                del self.script_str_content
            return str_content
        except:
            logging.warn(u"xml解析文件存在错误!用户自定义script解析函数存在错误.")
            raise SyntaxError(
                "xml_file is Error! User Python script exit SyntaxError!")

    def set_defaut_value(self, attrs, default_attrs):
        '''
        将属性设置默认值
        '''
        for attrs_name in default_attrs:
            if attrs_name not in attrs.keys():
                attrs[attrs_name] = default_attrs[attrs_name]
        return attrs

    def url_normalize(self, url):
        return urlsplit(url).geturl().lower()

    def url_match(self, website):
        '''
        URL匹配判断,匹配返回True,不匹配返回False
        '''
        # 通过domain和host判断
        is_match = False
        try:
            if website.attrs["domain"] in self.url:
                is_match = True
        except KeyError:
            if website.attrs["host"] in self.url:
                is_match = True
        if not is_match:
            return is_match
        # 再通过url-pattern判断
        if not website.findAll("url-pattern"):
            return is_match
        for url_pattern in website.findAll("url-pattern"):
            if url_pattern.text:
                if self.regular_parser(url_pattern.text, self.url):
                    is_match = True
                    continue
                else:
                    is_match = False
        return is_match

    def express_function(self, content, expression_method):
        '''
        根据expression_method方法进行循环解析
        '''
        if expression_method["xpath-expression"] is not None:
            values = self.xpath_parser(
                expression_method["xpath-expression"].string, content)
        elif expression_method["css-expression"] is not None:
            values = self.css_parser(
                expression_method["css-expression"].string, content)
        elif "text-extraction" in expression_method:
            if expression_method["text-extraction"]:
                pass
            else:
                values = content
        else:
            values = content
        if isinstance(values, list):
            result_values = []
            for value in values:
                if expression_method["used-zone"] == "field":
                    if isinstance(value, list):
                        value = "".join(v.text_content() for v in value)
                    elif expression_method["keep-tag"] == "true":
                        value = tostring(value, encoding="utf8").decode("utf8")
                    elif "text_content" in dir(value):
                        value = value.text_content()
                    elif "text" in dir(value):
                        value = value.text
                elif expression_method["used-zone"] == "outlink":
                    #由lxml生成的类
                    if "items" in dir(value):
                        value = [
                            value for key, value in value.items() if key == "href"]
                        if value:
                            value = value[0]
                        else:
                            value = None
                    else:
                        value = None
                if value is None:
                    continue
                result_values.append(
                    self.str_parser(value, expression_method)
                )

        elif values is None:
            return []
        else:
            result_values = [self.str_parser(values, expression_method)]
        return result_values

    def get_field(self, field):
        '''
        解析field，返回得到一个key-values字典
        '''
        default_attrs = {"name": None, "data-type": "string", "multi-value": "false",
                         "occur": "optional", "description": ""}
        field_attrs = field.attrs

        if "name" not in field_attrs:
            logging.warn(u"xml解析文件存在错误!其中一个field的name字段缺少属性值.")
            raise NameError(
                "xml_file is Error! there is a field lack of essential property: name")
        # 添加默认值
        self.set_defaut_value(field_attrs, default_attrs)
        # 调用解析方法得到values
        values = []
        xpaths = field.findAll("parse")
        for xpath in xpaths:
            express = {}
            express["used-zone"] = "field"
            #是否保留html标签
            if "keep-tag" in field_attrs:
                express["keep-tag"] = field_attrs["keep-tag"]
            else:
                express["keep-tag"] = "false"
            #xpath 或 css 都可以
            express["xpath-expression"] = xpath.find("xpath-expression")
            express["css-expression"] = xpath.find("css-expression")
            express["text-extraction"] = xpath.find("text-extraction")
            express["str-range"] = xpath.find("str-range")
            express["regular-match"] = xpath.find("regular-match")
            express["script-name"] = xpath.find("script-name")
            express["script"] = xpath.find("script")
            values = self.express_function(self.content, express)
            if len(values) != 0:
                if values[0]:
                    break
        # 类型转换
        try:
            if field_attrs["data-type"] != "string":
                read_values = []
                for value in values:
                    exec("read_values.append(%s(%s))" % (field_attrs["data-type"], value))
                values = read_values
        except:
            logging.warn(u"xml解析文件存在错误!其中一个field的data-type存在类型错误.")
            raise AttributeError(
                "xml_file is Error! the filed's data-type exit a error when express.")
        # 检测occur是否为mandatory，判断是否抛出错误
        values = [value for value in values if value]
        if len(values) == 0:
            if field_attrs["occur"] == "mandatory":
                logging.warn(u" 警告：%s(%s)为必须值，但未能抓取到." %
                             (field_attrs["name"], field_attrs["description"]))
                #raise AttributeError("the field of %s(%s) is mandatory, but it can not be fetched." % (
                #    field_attrs["name"], field_attrs["description"]))
        #检测是否为多值
        if field_attrs["multi-value"] == "false":
            try:
                values = values[0]
            except:
                values = None

        return field_attrs["name"], values

    def get_outlink(self, outlink):
        '''
        解析field，返回得到一个key-values字典
        '''
        default_attrs = {"trace": "true", "normalize": "none",
                         "occur": "optional", "update-interval": "-1"}
        outlink_attrs = outlink.attrs
        # 添加默认值
        self.set_defaut_value(outlink_attrs, default_attrs)
        xpaths = outlink.findAll("parse")
        urls = []
        # 解析URL
        for xpath in xpaths:
            express = {}
            express["used-zone"] = "outlink"
            #xpath 或 css 都可以
            express["xpath-expression"] = xpath.find("xpath-expression")
            express["css-expression"] = xpath.find("css-expression")
            express["str-range"] = xpath.find("str-range")
            express["regular-match"] = xpath.find("regular-match")
            express["script-name"] = xpath.find("script-name")
            express["script"] = xpath.find("script")
            urls = self.express_function(self.content, express)
            if len(urls) != 0:
                if urls[0]:
                    break
        if not urls:
            return None, None
        # url-host检测
        urls = [urljoin(self.url, url) for url in urls if url]
        # 检测occur是否为mandatory，判断是否抛出错误
        if len(urls) == 0:
            if outlink_attrs["occur"] == "mandatory":
                logging.warn(u" 警告：未能解析出URL！")
                raise AttributeError(
                    "outlink exit error, it can not be parsed.")
        # url规范化处理
        if outlink_attrs["normalize"] == "default":
            urls = [self.url_normalize(url) for url in urls]
        elif outlink_attrs["normalize"] == "user-function":
            if "def user_normalize_function" not in self.python_script:
                logging.warn("Python脚本函数名称错误,没有用指定函数名.")
                raise SyntaxError("Python script exit SyntaxError!")
            urls = [self.python_function_parser(
                self.python_script, url) for url in urls]
        return urls, outlink_attrs

    def thread_pool_dealing(self, function, keywork, pools=None):
        '''开启线程模式'''
        if pools is None:
            pools = Pool(2)
        result_list = pools.map(function, keywork)
        return dict(result_list)

    def parser_model(self, xml):
        '''
        解析模块，将xml-pattern文件解析成配置文件
        '''
        try:
            soup = BeautifulSoup(xml, "xml")
        except Exception:
            logging.error(u"xml文件载入错误!")
            raise IOError(
                "xml_file is Error! it can't convert to xml tree.")

        websites = soup.findAll("website")
        # 解析
        fields_result = {}
        outlinks_result = {}
        for website in websites:
            # URL匹配,不匹配则跳过
            if not self.url_match(website):
                continue
            # 数据解析
            data_object = website.find("data-object")
            if data_object:
                fields = data_object.findAll("field")
                #fields_result.update(self.thread_pool_dealing(self.get_field, fields))
                for field in fields:
                    field_name, field_value = self.get_field(field)
                    fields_result[field_name] = field_value
            # 链接解析
            outlink = website.find("outlinks")
            if outlink:
                entities = outlink.findAll("entity")
                #outlinks_result.update(self.thread_pool_dealing(self.get_outlink, entities))
                for entity in entities:
                    urls, outlink_metadata = self.get_outlink(entity)
                    if not urls:
                        continue
                    for url in urls:
                        outlinks_result[url] = outlink_metadata
        return fields_result, outlinks_result


class Url2ReExpress(object):

    def __init__(self):
        self.urls = set()

    def add_url(self, url):
        self.urls.add(urlsplit(url))

    def compare(self):
        similar = []
        different = []
        if self.urls:
            if len(set(url.path for url in self.urls)) == 1:
                similar.append(url.scheme+url.netloc+url.path)
            else:
                pass
        return similar, different

    def toReExpress(self, content):
        result = []
        for c in content:
            if c in [".","?","*"]:
                result.append("\\"+c)
            else:
                result.append(c)
        return "".join(result)
