# -*- coding: utf-8 -*-

import scrapy
from urllib import parse
import re
import urllib
import pymongo
from ciDu.items import CiduItem
from scrapy_splash import SplashRequest

class FenleiSpider(scrapy.Spider):
    name = 'fenlei'
    #allowed_domains = ['sss']
    start_urls = ['http://www.dictall.com/zt/G/w1.htm']
    headers = {
        # 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        # 'Accept-Encoding': 'gzip, deflate',
        # 'Accept-Language': 'zh-CN,zh;q=0.9',
        # 'Cache-Control': 'max-age=0',
        # 'Connection': 'keep-alive',
        # 'Cookie': 'Hm_lvt_e5b30bce62dbc9513272317426f633fb=1548749366,1548898328; JSESSIONID=226748F34D257C74DFCB5CC05AB92548; Hm_lpvt_e5b30bce62dbc9513272317426f633fb=1548922555',
        # 'Host': 'www.dictall.com',
        # 'If-Modified-Since': 'Mon, 01 Oct 2018 08:13:19 GMT',
        # 'If-None-Match': 'W/"13811-1538381599000"',
        # 'Referer': 'http://www.dictall.com/zt',
        # 'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36'
    }
    def start_requests(self):
        yield SplashRequest(url=self.start_urls[0], headers=self.headers,  callback=self.parse, args={'wait': 1, 'tag': 0})

    def parse(self, response):
        linksPre = re.findall('"(/zt/\w/w1.htm?)', response.text)
        links = []
        for link in linksPre:
            links.append(urllib.parse.urljoin(self.start_urls[0], link))
        for link in links:
            yield SplashRequest(url=link,  headers=self.headers,  callback=self.parsePlus, args={'wait': 1, 'tag': 0})

    def parsePlus(self, response):
        linksPre = re.findall('(/zt/.{0,4}?/.{0,4}?/w1.htm?)', response.text)
        links = []
        for link in linksPre:
            links.append(urllib.parse.urljoin(self.start_urls[0], link))
        for link in links:
            yield SplashRequest(url=link, headers=self.headers, callback=self.parsePP, args={'wait': 3, 'tag': 0})

    def parsePP(self, response):
        linksPre = re.findall('(/zt/.{0,4}?/.{0,4}?/.{0,4}?/w1.htm?)', response.text)
        links = []
        if linksPre != []:#有的可能没有下一级，抽出来是空的
            for link in linksPre:
                links.append(urllib.parse.urljoin(self.start_urls[0], link))
            for link in links:
                yield SplashRequest(url=link, headers=self.headers, callback=self.getPagenum, args={'wait': 3,  'tag': 0})
        else:
            yield SplashRequest(url=response.url, headers=self.headers, callback=self.getPagenum, args={'wait': 3, 'tag': 0}, dont_filter=True)

    def getPagenum(self, response):
        pageNumpre = re.findall('w(\d+).htm" title="尾页"', response.text)
        if pageNumpre == []:
            pageNum = 1
        else:
            pageNum = int(pageNumpre[0])
        for i in range(pageNum):
            url = response.url.replace('1.htm', str(i+1) + '.htm')
            host = '127.0.0.1'
            port = 27017
            client = pymongo.MongoClient(host=host, port=port)
            dbName = 'ciDuurl'
            collectionName = 'url'
            mgd = client[dbName]
            col = mgd[collectionName]
            inner = col.find()
            urls = []
            for x in inner:
                urls.append(x['url'])
            if url not in urls:
                yield SplashRequest(url=url, headers=self.headers, callback=self.parsePPPP, args={'wait': 5, 'tag': 0, 'crawled': 'crawled'}, dont_filter=True)

    def parsePPPP(self, response):
        item = CiduItem()
        list = response.xpath('//div[@id="catelist"]//a')
        item['分类'] = response.xpath('string(//div[@id="curCate"])').extract_first().split('->')[2:]
        item['中文词'] = list.xpath('./text()').extract_first().split('\xa0')[1].split('：')[0]
        item['英文翻译'] = list.xpath('./text()').extract_first().split('\xa0')[1].split('：')[1]
        item['名词解释链接'] = urllib.parse.urljoin(self.start_urls[0], list.xpath('./@href').extract_first())
        yield item
