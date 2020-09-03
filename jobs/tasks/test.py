# -*- coding: utf-8 -*-

from common.services.notice.NewsService import NewsService


class JobTask():
    def __init__(self):
        pass

    def run(self, params):
        news_params = {
            "uid" : 1,
            "title" : "定制化 Flask 框架 V2.0",
            "content" : "新功能更多~~"
        }

        NewsService.addNews( news_params )