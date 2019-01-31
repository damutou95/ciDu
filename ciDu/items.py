# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class CiduItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    分类 = scrapy.Field()
    中文词 = scrapy.Field()
    英文翻译 = scrapy.Field()
    名词解释链接 = scrapy.Field()
    pass
