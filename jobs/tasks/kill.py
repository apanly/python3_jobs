
# -*- coding: utf-8 -*-
import logging,os,subprocess
from flask.logging import default_handler

from common.models.job.JobKillQueue import JobKillQueue
from common.models.job.JobList import JobList
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
            self.kill_process_with_children( t.job_id )


        return True
    '''
    杀死job的父进程 和子进程，我们只杀死子进程，父进程就会死掉
    '''
    def kill_process_with_children(self,job_id):
        info = JobList.query.filter_by(id=job_id).first()
        if not info:
            app.logger.info("job_id:%s 没有查询到新" %(job_id) )
            return True
        ##根据关键词找到的父id
        ppid = self.findPidByKw( job_id )

        if not os.path.isdir("/proc/%s/" % ppid ):
            app.logger.info("父进程/proc/%s/不存在，进程已经退出,不再查询其子进程" % ppid )
            return True

        cmd = "ps -A -o ppid,pid,cmd | grep -v grep  |grep %s" % ppid
        app.logger.info( cmd )
        status, output = subprocess.getstatusoutput( cmd )
        if len( output ) < 1:
            return True

        output_arr = output.split('\n')
        child_pid = 0
        for tmp_p in output_arr:
            if info.command not in tmp_p:
                continue

            tmp_process_arr = tmp_p.split(" ")
            if str(tmp_process_arr[0]) != str(ppid):
                continue

            app.logger.info( tmp_p )

        app.logger.info( "子进程id：%s"% child_pid )

        return True
        