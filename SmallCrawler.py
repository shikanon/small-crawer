#!/usr/bin/env python3
# coding:utf8
# __author__ = "shikanon <shikanon@live.com>"
#__version__ = "0.0.1"

import requests
import grequests
import time
import ParserModel
import logging
import json
import os
import sys

class small_crawler(object):
    '''
    There is a small crawler, you can only set the start_url, Template and save path you can crawl data.
    '''
    def __init__(self, start_url, save_path, model_filename, python_express_script=None):
        '''初始化
        sart_url: the frist crawler's start point,
        save_path: the saved path of crawled data
        model_filename: the path of a xml template parser model of webpage,
        '''
        if type(start_url) in [list, tuple]:
            self.start_urls = start_url
        else:
            self.start_urls = [start_url]
        self.save_data_path = save_path
        #load Template from ParserModel
        self.parser = ParserModel.XMLParser()
        with open(model_filename, "r", encoding="utf8") as f:
            xml_file = f.read()
        if python_express_script is None:
            python_express = None
        else:
            with open(python_express_script, "r") as f:
                python_express = f.read()
        self.parser.load_parsed_files(xml_file, python_script=python_express)

    def get_header(self):
        headers = {'Connection':'Keep-Alive',
           'Accept':'text/html,*/*',
           'User-Agent':'Mozilla/6.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/29.0.1547.66 Safari/537.36',
           'Referer':'http://epub.cnki.net/kns/brief/result.aspx?dbprefix=scdb&action=scdbsearch&db_opt=SCDB'}
        return headers

    def exception_url_handler(self, request, exception):
        logging.warn(str(request.url) + "\t"*3 + "is failed!")

    def parse_from_request(self, request):
        urls = []
        self.parser.parsering(request.url, request.text)
        if "outlink" in self.parser.result.keys():
            urls = list(self.parser.result["outlink"].keys())
        if "parsed-data" in self.parser.result.keys():
            data = self.parser.result["parsed-data"]
        else:
            data = None
        result = {"url": request.url, "data": data}
        with open(self.save_data_path, "a", encoding="utf8") as f:
            print(result, file=f)
        return urls

    def small_crawler(self, headers=None, cookies=None):
        '''There is a small spider class, you only few lines can creat a crawler'''
        urls = self.start_urls
        finish_url = set()
        if headers is None:
            headers = self.get_header()
        while True:
            rs = (grequests.get(url, headers=headers, timeout=1)for url in urls)
            response_list = grequests.imap(rs, exception_handler=self.exception_url_handler)
            for r in response_list:
                if r is None:
                    continue
                t1 = time.clock()
                urls = urls + self.parse_from_request(r)
                finish_url.add(r.url)
                print("爬虫时间：%f"%(time.clock()-t1))
            urls = [url for url in urls if url not in finish_url]
            print("next!")
            if len(urls) == 0:
                break

if __name__ == "__main__":
    model_filename = u"/exmaple/house_template.xml"
    save_data_path = u"/exmaple/house_template.json"
    python_script = "/exmaple/house_python_script.py"
    url = "http://gz.fang.anjuke.com/loupan/s?p=2"
    ScriptPath = os.path.split( os.path.realpath( sys.argv[0] ) )[0]
    print(ScriptPath)
    model_filename = ScriptPath + model_filename
    save_data_path = ScriptPath + save_data_path
    python_script = ScriptPath + python_script
    crawler = small_crawler(url, save_data_path, model_filename, python_script)
    crawler.small_crawler()
