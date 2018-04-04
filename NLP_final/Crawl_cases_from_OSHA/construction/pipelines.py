# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import json
import csv
import os
from .spiders.temp import keywords


class ConstructionPipeline(object):
    def __init__(self):
        # save the extract context into txt file
        place =os.getcwd() + '\\' + keywords + ".txt"
        self.f = open(place, "w")

    def process_item(self, item, spider):
        # content = json.dumps(dict(item), ensure_ascii = False) + ",\n"
        # self.f.write(content.encode("utf-8"))  # 写入json
        self.f.write(item['info'] + "\n")
        return item

    def close_spider(self, spider):
        self.f.close()
