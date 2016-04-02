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
        self.save_url_path = "".join(save_path.split(".")[:-1]) + ".urls"
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

    def load_url(self):
        if os.path.exists(self.save_url_path):
            with open(self.save_url_path, "r") as f:
                url_dict = json.load(f)
            return url_dict["undo_urls"], url_dict["finish_urls"]
        else:
            return list(),list()

    def save_url(self, undo_urls, finish_urls):
        with open(self.save_url_path, "w") as f:
            json.dump({"undo_urls":list(undo_urls), "finish_urls":list(finish_urls)}, f)

    def parse_from_request(self, request):
        '''paser the requests from Template and save the data'''
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
        with open(self.save_data_path, "a", encoding="utf8") as f:
            print(result["url"], file=f)
        return urls

    def small_crawler(self, headers=None, cookies=None):
        '''There is a small spider class, you only few lines can creat a crawler'''
        
        undo_urls, finish_urls = self.load_url()
        urls = set(undo_urls + self.start_urls)
        finish_urls = set(finish_urls)
        if headers is None:
            headers = self.get_header()
        t0 = time.clock()
        try:
            while True:
                rs = (grequests.get(url, headers=headers, timeout=2)for url in urls)
                response_list = grequests.imap(rs, exception_handler=self.exception_url_handler)
                for r in response_list:
                    if r is None:
                        continue
                    t1 = time.clock()
                    urls = urls|set(self.parse_from_request(r))
                    print(r.url)
                    finish_urls.add(r.url)
                urls = urls - finish_urls
                print("预计平均每分钟 %f 个页面"%(60*len(finish_urls)/(time.clock()-t0)))
                print("next!")
                if len(urls) == 0:
                    break
        finally:
            self.save_url(urls, finish_urls)

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
