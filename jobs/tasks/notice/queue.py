# -*- coding: utf-8 -*-
import logging
from application import app, db
from flask.logging import default_handler

from common.components.helper.ModelHelper import ModelHelper
from common.models.job.JobAlertList import JobAlertList
from common.models.job.JobList import JobList
from common.services.CommonConstant import CommonConstant
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
        for item in list:
            tmp_data = ModelHelper.model2Dict( item )
            tmp_job_info = ModelHelper.model2Dict(job_map.get(tmp_data['job_id']))
            self.handleItem( tmp_data,tmp_job_info)

            done_ids.append( tmp_data['id'] )

        if done_ids:
            '''
            synchronize_session用于query在进行delete or update操作时，对session的同步策略。
            False - 不对session进行同步，直接进行delete or update操作
            '''
            JobAlertList.query.filter( JobAlertList.id.in_( done_ids ) )\
                .update( dict( status =  CommonConstant.default_status_true  ) ,synchronize_session=False )
            db.session.commit()


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


