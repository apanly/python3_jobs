# -*- coding: utf-8 -*-
import os,logging,subprocess
from flask.logging import default_handler
from application import app, db
from common.components.helper.ModelHelper import ModelHelper
from common.services.StaffService import StaffService
from common.services.notice.NewsService import NewsService
from jobs.tasks.BaseJob import BaseJob

'''
系统本身的一些监控
python manage_job.py runjob -m monitor/system
'''
class JobTask( BaseJob ):
    def __init__(self):
        app.config['DEBUG'] = True
        logging_format = logging.Formatter(
            '%(levelname)s %(asctime)s %(filename)s:%(funcName)s L%(lineno)s %(message)s')
        default_handler.setFormatter(logging_format)

    def run(self, kwargs):
        pid_path = self.getPidPath( 'monitor_system.pid' )
        if self.checkPidExist(pid_path):
            app.logger.info("[monitor] system is running")
            return False

        pid = str( os.getpid() )
        if not self.setPidFile( pid_path,pid):
            err_msg = self.getErrMsg()
            app.logger.info("Cann't get a lock file，err msg : " + err_msg)
            return False

        params = self.getEnvFile()
        server_id = params['id']
        host = params['name']
        ## 判断是否有僵尸进程

        cmd = "ps -A -o stat,ppid,pid,cmd | grep -v grep  |grep -e '^[Zz]'"
        status,output = subprocess.getstatusoutput( cmd )
        if len( output ) < 1:
            return True

        output_arr = output.split( '\n' )
        if len( output_arr ) > 3:#多余3个僵尸进程
            staff_list = StaffService.getRootStaffList()
            staff_ids = ModelHelper.getFieldList( staff_list,"id")
            for tmp_staff_id in staff_ids:
                news_params = {
                    "uid": tmp_staff_id,
                    "title": "僵尸进程：" + host,
                    "content": "<br/>".join( output_arr )
                }
                NewsService.addNews(news_params)
        return True
