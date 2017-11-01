# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html
import hashlib

import scrapy


def get_md5(url):
    if isinstance(url, str):
        url = url.encode("utf-8")
    m = hashlib.md5()
    m.update(url)
    return m.hexdigest()


class KugouspiderItem(scrapy.Item):
    song_hash = scrapy.Field()
    timelength = scrapy.Field()
    album_name = scrapy.Field()
    video_id = scrapy.Field()
    author_name = scrapy.Field()
    song_name = scrapy.Field()
    lyrics = scrapy.Field()
    author_id = scrapy.Field()
    bitrate = scrapy.Field()

    def get_insert_sql(self):
        insert_sql = """
                    insert into kugou_song(song_hash, timelength, album_name, video_id, 
                    author_name, song_name, lyrics, author_id, bitrate) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)        
                """
        params = (
            self["song_hash"],
            self["timelength"],
            self["album_name"],
            self["video_id"],
            self["author_name"],
            self["song_name"],
            self["lyrics"],
            self["author_id"],
            self["bitrate"],
        )
        return insert_sql, params

