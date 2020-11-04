
# -*- coding: utf-8 -*-
import logging,os,subprocess,re
from flask.logging import default_handler

from common.models.job.JobKillQueue import JobKillQueue
from common.models.job.JobList import JobList
from common.services.CommonConstant import CommonConstant
from jobs.tasks.BaseJob import BaseJob
from application import app,db

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
            tmp_ret = self.kill_process_with_children( t.job_id )
            t.status = CommonConstant.default_status_true if tmp_ret else CommonConstant.default_status_false
            db.session.add( t )
            db.session.commit()

        return True
    '''
    杀死job的父进程 和子进程，我们只杀死子进程，父进程就会死掉
    '''
    def kill_process_with_children(self,job_id):
        info = JobList.query.filter_by(id=job_id).first()
        if not info:
            app.logger.info("job_id:%s 没有查询到新" %(job_id) )
            return True

        ##如果填写了杀死命令，那么就用杀死命令执行
        if info.command_kill:
            app.logger.info( "job_id:%s 配置了杀死命令：%s" %( job_id, info.command_kill) )
            try:
                status = subprocess.check_call("kill -9 %s" % info.command_kill, shell=True)
                if status != 0:
                    app.logger.info("job_id:%s 命令：%s 未能通过job平台正常退出，异常退出，退出状态为%d" % (job_id, info.command_kill, status))
            except Exception as e:
                app.logger.info("job_id:%s kill 命令：%s  失败，可能已经退出" % (job_id, info.command_kill ) )
            return True
        ##根据关键词找到的父id
        ppid = self.findPidByKw( job_id )

        if not os.path.isdir("/proc/%s/" % ppid ):
            app.logger.info("job_id:%s 父进程/proc/%s/不存在，进程已经退出,不再查询其子进程" % (job_id,ppid) )
            return True

        cmd = "ps -A -o ppid,pid,cmd | grep -v grep  |grep %s" % ppid
        app.logger.info( cmd )
        status, output = subprocess.getstatusoutput( cmd )
        if len( output ) < 1:
            return True

        output_arr = output.split('\n')
        child_pid = 0
        for tmp_p in output_arr:
            app.logger.info(tmp_p)
            if info.command not in tmp_p:
                app.logger.info("job_id:%s 没找到运行命令" % job_id)
                continue

            tmp_process_arr = re.split("\s+",tmp_p.strip() )
            app.logger.info( tmp_process_arr )
            if str(tmp_process_arr[0]) != str(ppid):
                continue

            child_pid = int( tmp_process_arr[1])


        app.logger.info( "job_id:%s 子进程id：%s"% (job_id,child_pid ) )
        if child_pid < 1:
            app.logger.info("job_id:%s 未找到运行的子进程" % job_id )
            return False

        if not os.path.isdir("/proc/%s/" % child_pid ):
            app.logger.info("job_id:%s 子进程/proc/%s/不存在，进程已经退出,不再查询其子进程" % (job_id, child_pid) )
            return False
        try:
            status = subprocess.check_call("kill -9 %s" % child_pid, shell=True)
            if status != 0:
                app.logger.info("job_id:%s 进程%s未能通过job平台正常退出，异常退出，退出状态为%d" % (job_id, child_pid,status ))
        except Exception as e:
            app.logger.info("job_id:%s kill 进程%s失败，可能已经退出" % (job_id, child_pid) )
        return True
        