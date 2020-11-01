
# -*- coding: utf-8 -*-
import logging,os
from flask.logging import default_handler

from common.models.job.JobKillQueue import JobKillQueue
from common.services.CommonConstant import CommonConstant
from jobs.tasks.BaseJob import BaseJob
from application import app

'''
强制停止Job
python /data/www/python3/python3_jobs/manage_job.py runjob -m kill
'''
class JobTask( BaseJob ):
    def __init__(self):
        ## 设置Job使用debug模式
        app.config['DEBUG'] = True
        logging_format = logging.Formatter(
            '%(levelname)s %(asctime)s %(filename)s:%(funcName)s L%(lineno)s %(message)s')
        default_handler.setFormatter(logging_format)

    def run(self, params):
        pid_path = self.getPidPath('kill.pid')
        if self.checkPidExist(pid_path):
            app.logger.info("[core] dispatch is running")
            return False

        pid = str(os.getpid())
        if not self.setPidFile(pid_path, pid):
            err_msg = self.getErrMsg()
            app.logger.info("Cann't get a lock file，err msg : " + err_msg)
            return False

        params = self.getEnvFile()
        server_id = params['id']
        host = params['name']

        kill_list = JobKillQueue.query.filter_by( server_id = server_id ,status =  CommonConstant.default_status_neg_2)\
            .order_by( JobKillQueue.id.asc() ).limit(10).all()

        if not kill_list:
            app.logger.info("没有Job需要kill~~")
            return True

        ##找到Job 杀死job
        for t in kill_list :
            ##根据关键词找到的父id
            tmp_ppid = self.findPidByKw( t.job_id )
            app.logger.info( tmp_ppid )

        return True        
        