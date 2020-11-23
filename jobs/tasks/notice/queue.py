# -*- coding: utf-8 -*-
import logging

import requests

from application import app, db
from flask.logging import default_handler

from common.components.helper.ModelHelper import ModelHelper
from common.models.job.JobAlertList import JobAlertList
from common.models.job.JobCategory import JobCategory
from common.models.job.JobList import JobList
from common.models.rbac.User import User
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
            return self.exitOK()

        job_ids = ModelHelper.getFieldList(list, "job_id")
        job_map = ModelHelper.getDictFilterField(JobList, select_field=JobList.id, id_list= job_ids )

        staff_ids = []
        for _key,_item in job_map.items():
            staff_ids.append( _item.owner_uid )
            staff_ids.append( _item.relate_uid )

        staff_map = ModelHelper.getDictFilterField(User, select_field= User.id, id_list= staff_ids)
        done_ids = []
        alert_content = [
            "Job异常报警"
        ]

        cate_map = ModelHelper.getDictFilterField(JobCategory)
        for item in list:

            tmp_data = ModelHelper.model2Dict( item )
            tmp_job_info = ModelHelper.model2Dict(job_map.get(tmp_data['job_id']))

            #负责人和相关人用户信息
            tmp_job_owner_info =  ModelHelper.model2Dict( staff_map.get( tmp_job_info['owner_uid'] ) )
            tmp_job_relate_info =  ModelHelper.model2Dict( staff_map.get( tmp_job_info['relate_uid'] ) )

            #分类
            tmp_cate_info = ModelHelper.model2Dict( cate_map.get( tmp_job_info['cate_id'] ) )

            done_ids.append(tmp_data['id'])
            tmp_msg = "Job Id: {0},名称：[{1}]{2},负责人：{3},相关人：{4},重要级别：{5},类型：{6},报警内容：{7}"\
                .format( tmp_job_info['id'],tmp_cate_info['name'],tmp_job_info['name']
                         ,tmp_job_owner_info['name'],tmp_job_relate_info['name']
                         ,CommonConstant.job_level_map[ tmp_job_info['job_level'] ]
                         ,CommonConstant.job_type_map[ tmp_job_info['job_type'] ]
                         , tmp_data['content']
                         )

            if 'Job平台标识没有运行'  in tmp_msg or 'Job平台标识正在运行'  in tmp_msg:
                continue

            self.handleItem(tmp_data, tmp_job_info)
            alert_content.append(tmp_msg)


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





