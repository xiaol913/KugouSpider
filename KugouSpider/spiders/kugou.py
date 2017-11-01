# -*- coding: utf-8 -*-
import re
import json

import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from scrapy.xlib.pydispatch import dispatcher
from scrapy import signals
from scrapy.loader import ItemLoader

from selenium import webdriver

from KugouSpider.items import KugouspiderItem


class KugouSpider(CrawlSpider):

    def __init__(self):
        chrome_opt = webdriver.ChromeOptions()
        prefs = {"profile.managed_default_content_settings.images": 2}
        chrome_opt.add_experimental_option("prefs", prefs)

        self.browser = webdriver.Chrome(executable_path="chromedriver.exe", chrome_options=chrome_opt)
        super(KugouSpider, self).__init__()
        dispatcher.connect(self.spider_closed, signals.spider_closed)

    def spider_closed(self, spider):
        # 当爬虫退出的时候关闭chrome
        self.browser.quit()

    name = 'kugou'
    allowed_domains = ['www.kugou.com']
    start_urls = ['http://www.kugou.com/']

    rules = (
        Rule(LinkExtractor(allow=("yy/singer/index",)), follow=True),
        Rule(LinkExtractor(allow=r"yy/singer/home/\d+.html", ), callback='parse_album', follow=True),
        Rule(LinkExtractor(allow=r"yy/album/single/\d+.html",), callback='parse_list', follow=True),
    )

    def parse_album(self, response):
        all_urls = response.css("#album_container a::attr(href)").extract()
        for url in all_urls:
            yield scrapy.Request(url, callback=self.parse_list)

    def parse_list(self, response):
        all_song_hash = response.css(".songList a::attr(data)").extract()
        for song_hash in all_song_hash:
            match_obj = re.match("(\w{32})\|.*", song_hash)
            if match_obj:
                song_hx = match_obj.group(1)
                url = "http://www.kugou.com/yy/index.php?r=play/getdata&hash={0}".format(song_hx)
                yield scrapy.Request(url, callback=self.parse_song)

    def parse_song(self, response):
        # 处理歌曲api返回的json
        song_json = json.loads(response.text)
        item_loader = ItemLoader(item=KugouspiderItem(), response=response)
        item_loader.add_value("song_hash", song_json["data"]["hash"])
        item_loader.add_value("timelength", song_json["data"]["timelength"])
        item_loader.add_value("album_name", song_json["data"]["album_name"])
        item_loader.add_value("video_id", song_json["data"]["video_id"])
        item_loader.add_value("author_name", song_json["data"]["author_name"])
        item_loader.add_value("song_name", song_json["data"]["song_name"])
        item_loader.add_value("lyrics", song_json["data"]["lyrics"])
        item_loader.add_value("author_id", song_json["data"]["author_id"])
        item_loader.add_value("bitrate", song_json["data"]["bitrate"])

        song_item = item_loader.load_item()

        yield song_item

