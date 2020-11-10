# -*- coding: utf-8 -*-
from common.components.helper.DateHelper import DateHelper
from common.models.job.JobAlertList import JobAlertList
from common.models.job.JobRunLog import JobRunLog
from common.services.BaseService import BaseService
from application import db,app

class JobService(BaseService):
    @staticmethod
    def addRunLog( params ):
        log_id = 0
        try:
            model = JobRunLog( **params )
            db.session.add(model)
            db.session.commit()
            log_id = model.id
        except Exception as e:
            app.logger.info( e )

        return log_id

    @staticmethod
    def updateRunLog( log_id = 0, max_mem = 0,status = 0):
        params = {
            "end_time":DateHelper.getCurrentTime(),
            "max_mem" : max_mem,
            "status":status
        }
        JobRunLog.query.filter_by(id=log_id).update( dict( params ) )
        db.session.commit()
        return True

    '''
    当一个 SQL 事务出错时，唯一能做的就是回滚该事务，否则该会话（好像是与数据库连接同生命期）将不再接受任何语句
    '''
    @staticmethod
    def saveAlertLog(job_id,content):
        try:
            if not content:
                return True

            model = JobAlertList()
            model.job_id = job_id
            model.content = content
            db.session.add(model)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return False

        return True
