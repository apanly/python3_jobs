# -*- coding: utf-8 -*-
import logging

import requests

from application import app, db
from flask.logging import default_handler

from common.components.helper.ModelHelper import ModelHelper
from common.models.job.JobAlertList import JobAlertList
from common.models.job.JobList import JobList
from common.services.CommonConstant import CommonConstant
from common.services.SysConfigService import SysConfigService
from common.services.notice.NewsService import NewsService
from jobs.tasks.BaseJob import BaseJob

'''
python manage_job.py runjob -m notice/queue
'''

class JobTask( BaseJob ):
    def __init__(self):
        app.config['DEBUG'] = True
        app.config['SQLALCHEMY_ECHO'] = True
        logging_format = logging.Formatter(
            '%(levelname)s %(asctime)s %(filename)s:%(funcName)s L%(lineno)s %(message)s')
        default_handler.setFormatter(logging_format)

    def run(self, params):
        list = JobAlertList.query.filter_by(status=CommonConstant.default_status_neg_2)\
            .order_by( JobAlertList.id.asc() ).limit(10).all()

        if not list:
            app.logger.info("没有报警异常数据需要处理")
            return True

        job_ids = ModelHelper.getFieldList(list, "job_id")
        job_map = ModelHelper.getDictFilterField(JobList, select_field=JobList.id, id_list=job_ids.sort())

        done_ids = []
        alert_content = [
            "Job异常报警"
        ]
        for item in list:
            tmp_data = ModelHelper.model2Dict( item )
            tmp_job_info = ModelHelper.model2Dict(job_map.get(tmp_data['job_id']))
            self.handleItem( tmp_data,tmp_job_info)

            tmp_msg = "Job Id : {0},名称：{1},报警内容：{2}".format( tmp_job_info['id'],tmp_job_info['name'],tmp_data['content'] )
            if 'Job平台标识没有运行' not in tmp_msg:
                alert_content.append( tmp_msg )
            done_ids.append( tmp_data['id'] )

        if done_ids:
            '''
            synchronize_session用于query在进行delete or update操作时，对session的同步策略。
            False - 不对session进行同步，直接进行delete or update操作
            '''
            JobAlertList.query.filter( JobAlertList.id.in_( done_ids ) )\
                .update( dict( status =  CommonConstant.default_status_true  ) ,synchronize_session=False )
            db.session.commit()


        if len( alert_content ) > 1:
            alert_content = "\r\n".join( alert_content )
            self.dingdingAlert( alert_content )
            self.wechatworkAlert( alert_content )

        return self.exitOK()

    def dingdingAlert(self,content):
        try:
            url = SysConfigService.getConfigByName( CommonConstant.config_dingding )
            if not url:
                return False

            headers = {
                'Content-Type':'application/json'
            }
            data = {
                "msgtype": "text",
                "text" : {
                    "content" : content
                }
            }
            r = requests.post(url, headers=headers, json=data)
            if r.status_code != 200:
                return None
            r_json = r.json()
            if r_json.get('errcode') != CommonConstant.default_status_false:
                app.logger.info("钉钉报警失败-1：" + str(r.text))

        except Exception as e:
            app.logger.info( "钉钉报警失败-2：" + str( e ) )

        return True

    def wechatworkAlert(self,content):
        try:
            url = SysConfigService.getConfigByName( CommonConstant.config_workwechat )
            app.logger.info( url )
            if not url:
                return False

            headers = {
                'Content-Type':'application/json'
            }
            data = {
                "msgtype": "text",
                "text" : {
                    "content" : content
                }
            }
            r = requests.post( url,headers = headers ,json = data)
            if r.status_code != 200:
                return None
            r_json = r.json()
            if r_json.get('errcode') != CommonConstant.default_status_false:
                app.logger.info("企业微信报警失败-1：" + str(r.text) )

        except Exception as e:
            app.logger.info( "企业微信报警失败-2：" + str( e ) )

        return True

    def handleItem(self,data,job_info ):
        ##站内信
        news_params = {
            "uid": job_info['owner_uid'],
            "title": "job_%s异常报警"%( data['job_id'] ),
            "content": data['content']
        }
        NewsService.addNews(news_params)
        if job_info['owner_uid'] != job_info['relate_uid']:
            news_params['uid'] = job_info['relate_uid']
            NewsService.addNews(news_params)

        return True





