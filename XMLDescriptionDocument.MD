ParserModel
========

ParserModel is a tools for crawler extracting information from web though a specific XML documents. You can get a extracter only with a XML files with configuration. It's made by Python language, and it can easy to use as modular embedded in craweler framwork. 

********
## Usage
--------

** This is exmaple of ParserModel usage under the test file. **

Exmaple of Code:

    #!/usr/bin/env python3
    # coding:utf8
    import requests
    import time
    import ParserModel
    import json 

    url_search = "http://gz.fang.anjuke.com/loupan/s?p=1"   

    headers = {'Connection':'Keep-Alive',
               'Accept':'text/html,*/*',
               'User-Agent':'Mozilla/6.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/29.0.1547.66 Safari/537.36',
               'Referer':'http://epub.cnki.net/kns/brief/result.aspx?dbprefix=scdb&action=scdbsearch&db_opt=SCDB'}  

    r_search = requests.get(url_search, headers=headers)    

    #load xml files
    with open("house_template.xml","r",encoding="utf8") as f:
        xml_file = f.read() 

    parser = ParserModel.XMLParser()
    parser.load_parsed_files(xml_file)
    urls = [r_search.url]
    finish_url = [] 

    with open("result.json", "w" ,encoding="utf8") as f:
        result = {}
        result["data"] = []
        while True:
            url = urls.pop()
            if url in finish_url:
                continue
            r = requests.get(url, headers=headers)
            html_content = r.content.decode("utf8")
            with open("./parser_model_profile_test/"+url[-1], "w") as f:
                print(url)
                f.write(html_content)
            t1 = time.clock()
            parser.parsering(url, html_content)
            print("Time：%f"%(time.clock()-t1))

            if "outlink" in parser.result.keys():
                urls = list(set(urls + list(parser.result["outlink"].keys())))
            if "parsed-data" in parser.result.keys():
                #print(parser.result["parsed-data"])
                result["data"].append(parser.result["parsed-data"])
            finish_url.append(url)
            time.sleep(5)
            if len(urls) == 0:
                break
        f.write(json.dumps(result, ensure_ascii=False))


How to write correct XML files?
-------------------------------

XML file include three levels:

* Website is the topest, which describes the web page include url pattern, domain and host.
* data-object and outlink is the second level. It marking the names and types of extracting data, and update interval of url etc..
* xpath is the third level. It include some method of extracting data, like Xpath expression, string slice, regular expression and Python script.


Example of XML template:

    <?xml version="1.0" encoding="UTF-8"?>  

    <websites>  
    

        <website domain="" host="" paser-engine="parse">
            <!--  -->
            <url-pattern>url-pattern-1</url-pattern>
            <url-pattern>url-pattern-2</url-pattern>
            <url-pattern>url-pattern-3</url-pattern>
            <!-- indicate how to retrieve data from page -->
            <data-object>
                <!-- occur value must in {"mandatory", "optional"}, default is "optional" -->
                <!-- data-type value must in {"string", "int", "float", "boolean"}, default
                    is "string"-->
                <field name="title" data-type="string" multi-value="false" occur="mandatory"
                    description="new's title">
                    <!-- list of xpath-expression or css-expression -->
                    <parse>
                        <xpath-expression>parse xpath-expression</xpath-expression>
                        <!-- optional tags: start & end -->
                        <str-range start="" end="" />
                        <regular-match>abc</regular-match>
                        <script-name>function_name<script-name>
                    </parse>
                    <parse>
                        <css-expression>parse xpath-expression</css-expression>
                        <!-- optional tags: start & end -->
                        <str-range start="" end="" />
                        <script><![CDATA[
                        ]]>
                        </script>
                    </parse>
                </field>
                
                <field name="author" multi-value="false" occur="mandatory"
                    description="new's author">
                    <parse>
                        <xpath-expression>parse</xpath-expression>
                    </parse>
                </field>
                
                <field name="text" multi-value="false" occur="mandatory"
                    description="new's text">
                    <parse>
                        <xpath-expression>parse</xpath-expression>
                    </parse>
                </field>    

                <field name="publish_time" multi-value="false" description="new's time">
                    <!-- list of template -->
                    <parse>
                        <xpath-expression>parse</xpath-expression>
                        <!-- optional tags: start & end -->
                        <regular-match>abc</regular-match>
                    </parse>
                </field>
            </data-object>
            
            <!-- indicate how to retrieve outlink from page -->
            <outlinks>
                <!-- normalize value must in {"none", "default", "user-function"}, default
                    is "none"-->
                <entity occur="mandatory" trace="true" normalize="none" update-interval="-1">
                    <parse>
                        <xpath-expression>//DIV[@id='pageDivTop']/A</xpath-expression>
                        <regular-match>abc</regular-match>
                    </parse>
                    <parse>
                        <xpath-expression>//DIV[@id='pageDivTop']/A</xpath-expression>
                        <regular-match>abc</regular-match>
                    </parse>
                </entity>
                <entity>
                    <parse>
                        <xpath-expression>//DIV[@id='pageDivTop']/A</xpath-expression>
                        <regular-match>abc</regular-match>
                    </parse>
                </entity>
            </outlinks>
        </website>  
    

    </websites>



****************************

中文文档
========

ParserModel是一个网页解析模板库，通过编写一个简单的XML文件模板就可以实现对页面的解析，ParserModel是由Python语言写的，因此可以很容易的嵌入到Scrapy，PySpider等Python爬虫框架当中使用，当然也可以是你自己的爬虫框架。





## XML文件各类标签说明
--------------  
    

`<websites></websites>`
一个用户的所有模板文件存放，里面可以包含多个`<website ></website>`模板    

`<website></website>`
一个网页抓取模板，主要包含了domain、host和paser-engine属性。
其中domain表示域名模式，如:sina.com, hao123.com等，host则表示域名全称，例如www.sina.com, news.sina.com等，domain和host两者至少需要有一个要填写，否则抛出文件错误异常，当两者都写时默认domain有效。paser-engine表示用何种格式进行解析，默认为xpath。 

`<url-pattern>url-pattern-1</url-pattern>`
url-pattern表示网页链接匹配的模式，url-pattern 可以为多个值，表达式为正则表达式形式。  

`<data-object></data-object>`
定义如何从页面解析得到所需数据，可以包含多个`<field></field>`解析方法。  

`<field></field>`
各字段包含信息，包含name，data-type，multi-value，occur，description, keep-tag六个属性。
name为数据存储字段名，name值必须存在否则抛出文件错误异常。
data-type为数据存储类型，仅支持string，int，float三种类型，默认为string。
multi-value表示存储数据是否为多值，默认为false。
occur表示所抓取数据是否必须存在，支持mandatory，optional两种类型。mandatory表示所抓数据不能为空否则抛出异常，optional则表示解析数据可以为空。默认为optional。
description对数据的描述，用于报错时快速锁定。
keep-tag 表示解析出来是否保留html标签
`<field></field>`下可以包含多个xpath解析，以循环形式遍历每个`<xpath></xpath>`
解析，直到成功则直接跳出。   

`<parse></parse>`
parse解析，`<xpath-expression></xpath-expression>`内为xpath解析表示式，`<css-expression> </css-expression>`为css选择器解析表示式，空则表示对全文进行采集。对解析后的文字处理包括了三种可选方法，分别为str-range字符串切片方法，regular-match 表示用正则表达式匹配，script用户自定义函数。
`<text-extraction></text-extraction>`表示对正文进行抽取，只有在`<xpath-expression>`和`<css-expression>`均为空的情况下方能被使用。
`<str-range start="" end="" />`表示字符切片的开始字符和结束字符，如果start为空则表示从第一个开始，end为空表示到最后一个结束。
`<regular-match></regular-match>`表示对xpath抽取文字用正则表达式解析。如果为空，则不匹配。如果匹配结果有多个值，选择第一个值输出。
`<script-name><script-name>`表示一个python代码函数名称。
`<script></script>`可以写入用户自定义python代码进行解析。代码必须以一个函数方式传入，函数名称必须为user_parser_function，传入一个字符串str，并返回一个字符串类型，否则抛出一个xml文件异样错误。
如果三个都存在，解析顺序为`<str-range start="" end="" />`，`<regular-match></regular-match>`，`<script></script>`  

`<outlinks></outlinks>`
获取外链，内可包含多个`<entity></entity>`外链解析。   

`<entity></entity>`
外链解析，包含occur，trace，normalize，update-interval 四种属性。
occur表示所抓取数据是否必须存在，支持mandatory，optional两种类型。mandatory表示所抓数据不能为空否则抛出异常，optional则表示解析数据可以为空。默认为optional。
trace表示外链是否具有痕迹记录功能，true表示可记录痕迹，false表示不记录。默认为true。
normalize表示对外链是否进行规则化去重处理，包含none，default，user-function三种选择。none表示不对外链进行规则化去重处理，default表示使用默认方法对外链进行规则话去重处理，user-function表示自定义Python函数，函数必须命名为user_normalize_function，输入一个url，返回一个修正后的url值。默认为none。
update-interval表示外链更新间隔，单位为分钟，默认为-1，表示不更新。
`<entity></entity>`下可以包含多个xpath解析，以循环形式遍历每个`<parse></parse>`
解析，直到成功则直接跳出。



用法
------------------

下面用一个ParserModel的案例说明ParserModel的用法,下面做一个安居客的简单爬虫例子：

    #!/usr/bin/env python3
    # coding:utf8
    import requests
    import time
    import ParserModel
    import json 

    url_search = "http://gz.fang.anjuke.com/loupan/s?p=1"   

    headers = {'Connection':'Keep-Alive',
               'Accept':'text/html,*/*',
               'User-Agent':'Mozilla/6.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/29.0.1547.66 Safari/537.36',
               'Referer':'http://epub.cnki.net/kns/brief/result.aspx?dbprefix=scdb&action=scdbsearch&db_opt=SCDB'}  

    r_search = requests.get(url_search, headers=headers)    

    #load xml files
    with open("house_template.xml","r",encoding="utf8") as f:
        xml_file = f.read() 

    parser = ParserModel.XMLParser()
    parser.load_parsed_files(xml_file)
    urls = [r_search.url]
    finish_url = [] 

    with open("result.json", "w" ,encoding="utf8") as f:
        result = {}
        result["data"] = []
        while True:
            url = urls.pop()
            if url in finish_url:
                continue
            r = requests.get(url, headers=headers)
            html_content = r.content.decode("utf8")
            with open("./parser_model_profile_test/"+url[-1], "w") as f:
                print(url)
                f.write(html_content)
            t1 = time.clock()
            parser.parsering(url, html_content)
            print("Time：%f"%(time.clock()-t1))

            if "outlink" in parser.result.keys():
                urls = list(set(urls + list(parser.result["outlink"].keys())))
            if "parsed-data" in parser.result.keys():
                #print(parser.result["parsed-data"])
                result["data"].append(parser.result["parsed-data"])
            finish_url.append(url)
            time.sleep(5)
            if len(urls) == 0:
                break
        f.write(json.dumps(result, ensure_ascii=False))


我们可以看到，ParserModel只需要通过加载XML文件就可以自动帮助我们爬取所需要的内容并存储在一个字典当中，实际就是将语言代码的编写转换成了统一的XML文件的编写工作。
那么这种特定的XML文件模板要如何编写呢?



XML模板文件编写
------------------

本文的XML文件主要分为三个层次：

* 最上面的一层为 网页解析。这一层主要用来描述 能够被后面步骤解析的URL，过滤掉无效的URL。
* 第二层为 数据描述层。 这一层主要用于描述 数据的属性，比如名称、存储类型、是否能为空、URL的更新周期等。
* 第三层是 数据解析层。 这一层主要是对数据的解析，包括Xpath表达式、字符串切片、正则表达式、Python脚本等。


下面展示上面代码的XML文件模板：

    <?xml version="1.0" encoding="UTF-8"?>  

    <websites>  
        <website domain="gz.fang.anjuke.com" paser-engine="xpath">
            <!--  -->
            <url-pattern>http://gz.fang.anjuke.com/loupan/s\?p=.*</url-pattern>
            <!-- indicate how to retrieve data from page -->
            <!-- indicate how to retrieve outlink from page -->
            <outlinks>
                <entity occur="optional" trace="true" normalize="none" update-interval="-1">
                    <xpath>
                        <expression>.//*[@id='container']/div[2]/div[1]/div[4]/div/a</expression>
                    </xpath>
                </entity>
                <entity occur="optional" trace="true" normalize="none" update-interval="-1">
                    <xpath>
                        <expression>.//*[@id='container']/div[2]/div[1]/div[3]/div/div[1]/div[1]/h3/a</expression>
                    </xpath>
                </entity>
            </outlinks>
        </website>  
        <website domain="gz.fang.anjuke.com" paser-engine="xpath">
            <!--  -->
            <url-pattern>http://gz.fang.anjuke.com/loupan/\d+</url-pattern>
            <!-- indicate how to retrieve data from page -->
            <!-- indicate how to retrieve outlink from page -->
            <data-object>
                <!-- occur value must in {"mandatory", "optional"}, default is "optional" -->
                <!-- data-type value must in {"string", "int", "float", "boolean"}, default
                    is "string"-->
                <field name="楼盘名称" data-type="string" multi-value="true" occur="mandatory"
                    description="小区名称">
                    <!-- list of expression -->
                    <xpath>
                        <expression>.//*[@id='j-triggerlayer']</expression>
                    </xpath>
                </field>
                
                <field name="价格" multi-value="true" occur="optional"
                    description="价格,单位:元/m2">
                    <xpath>
                        <expression>.//*[@id='container']/div[1]/div[2]/div[1]/dl/dd[1]</expression>
                        <regular-match>(\d+)元</regular-match>
                    </xpath>
                </field>
                <field name="户型" multi-value="true" description="户型">
                    <!-- list of template -->
                    <xpath>
                        <expression>.//*[@id='container']/div[1]/div[2]/div[1]/dl/dd[3]/div/a</expression>
                    </xpath>
                </field>
                <field name="地址" multi-value="true" description="地址">
                    <!-- list of template -->
                    <xpath>
                        <expression>.//*[@id='container']/div[1]/div[2]/div[1]/dl/dd[4]/span</expression>
                    </xpath>
                </field>
                <field name="电话" multi-value="true" description="电话">
                    <!-- list of template -->
                    <xpath>
                        <expression>.//*[@id='j-triggerlayer-b']/div/p/strong[1]</expression>
                    </xpath>
                </field>
                <field name="开盘日期" multi-value="true" description="开盘日期">
                    <!-- list of template -->
                    <xpath>
                        <expression>.//*[@id='container']/div[1]/div[2]/div[4]/ul[1]/li[1]</expression>
                    </xpath>
                </field>
                <field name="交房日期" multi-value="true" description="交房日期">
                    <!-- list of template -->
                    <xpath>
                        <expression>.//*[@id='container']/div[1]/div[2]/div[4]/ul[2]/li[1]/span</expression>
                    </xpath>
                </field>
            </data-object>
        </website>
    </websites>

