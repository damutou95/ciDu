# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymongo

class CiduPipeline(object):

    def __init__(self):
        host = '127.0.0.1'
        port = 27017
        dbName = 'ciDu'
        collectionName = 'fenlei'
        client = pymongo.MongoClient(host=host, port=port)
        mgd = client[dbName]
        self.post = mgd[collectionName]

    def process_item(self, item, spider):
        data = dict(item)
        self.post.insert(data)
        return item
