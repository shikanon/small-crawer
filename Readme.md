# Small Crawer
--------------

** This is a crawer micro frame, you can easy get data from web only set start url, Template and save path. It developed the ParserModel and grequests, you must install it.**



## Usage:


    import SmallCrawler
    import os
    import sys

    model_filename = u"/exmaple/house_template.xml"
    save_data_path = u"/exmaple/house_template.json"
    python_script = "/exmaple/house_python_script.py"
    url = "http://gz.fang.anjuke.com/loupan/s?p=2"
    ScriptPath = os.path.split( os.path.realpath( sys.argv[0] ) )[0]
    print(ScriptPath)
    model_filename = ScriptPath + model_filename
    save_data_path = ScriptPath + save_data_path
    python_script = ScriptPath + python_script
    
    crawler = SmallCrawler.small_crawler(url, save_data_path, model_filename, python_script)
    crawler.small_crawler()


Yes, it is easy if you use create the Template of ParserModel, the type of ParserModel you can see [shikanon/ParserModel](https://github.com/shikanon/ParserModel)