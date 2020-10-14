# -*- coding: utf-8 -*-
import datetime
import os,logging
import time
from flask.logging import default_handler
from application import app, db
from common.components.helper.DateHelper import DateHelper
from common.components.helper.FileHelper import FileHelper
from common.components.helper.ModelHelper import ModelHelper
from common.models.job.JobList import JobList
from common.services.CommonConstant import CommonConstant
from common.services.JobService import JobService
from jobs.tasks.BaseJob import BaseJob

'''
核心监控程序
python manage_job.py runjob -m monitor/core
'''
class JobTask( BaseJob ):
    def __init__(self):
        app.config['DEBUG'] = True
        logging_format = logging.Formatter(
            '%(levelname)s %(asctime)s %(filename)s:%(funcName)s L%(lineno)s %(message)s')
        default_handler.setFormatter(logging_format)

    def run(self, kwargs):
        pid_path = self.getPidPath( 'monitor_core.pid' )
        if self.checkPidExist(pid_path):
            app.logger.info("[monitor] core is running")
            return False

        pid = str( os.getpid() )
        if not self.setPidFile( pid_path,pid):
            err_msg = self.getErrMsg()
            app.logger.info("Cann't get a lock file，err msg : " + err_msg)
            return False

        params = self.getEnvFile()
        server_id = params['id']
        host = params['name']
        list = JobList.query.filter_by(server_id = server_id, status = CommonConstant.default_status_true,
                                       is_del = CommonConstant.default_status_false ).all()
        if not list:
            app.logger.info("%s没有Job需要监控" % (host))
            return True

        self.current_time = time.time() - 300
        for item in list:
            self.handleItem( ModelHelper.model2Dict( item ),host )

        app.logger.info("it's over~~")
        return True

    def handleItem(self, item ,host ):
        pid_file = self.getPidPath( 'job_%s.pid' % item['id'] )
        pid = 0
        if self.checkPidExist( pid_file ):
            # 文件存储的是python的进程id，找真真运行的需要使用关键词查找
            pid = self.findPidByKw( item['id'] )

        app.logger.info("%s : %s"%( pid_file ,pid ) )
        # 判断进程本身是否存在，但是由于删除pid在进程结束之后 会有延迟，所以需要临时增加删除功能
        run_flag = os.path.exists('/proc/%s' % pid ) if pid > 0 else False

        '''
            1=>该结束未结束 
            2=>该运行未运行 
            3=>执行命令异常 
            4=>Job平台标识正在运行，但是在机器上没有发现job进程 
            5=>Job平台标识没有运行，但是在机器上发现了job进程 
            6=>运行时间过短
        '''
        alert_content = ''
        if item['run_status'] == CommonConstant.default_status_true and run_flag:
            # 数据库中标记没有运行，但是在机器上发现了进程
            alert_content = "您的job(job_{0} {1})运行状态异常,可能原因:{2}"\
                .format(item['id'], item['name'], "Job平台标识没有运行，但是在机器%s上发现了job进程" % host )
            os.system( 'ls -al /proc/%s' % pid )
            os.system( 'ps -ef |grep tmp_job_%s' % item['id'] )
        elif item['run_status'] == CommonConstant.default_status_pos_2 and not run_flag:
            # 重新检查job的状态，避免运行时间较短的job误报警
            time.sleep(2)
            job_info = JobList.query.filter_by( id = item['id'] ).first()

            if job_info.run_status == CommonConstant.default_status_pos_2:
                alert_content = "您的job(job_{0} {1})运行状态异常[Job平台会自动修复],可能原因:{2}" \
                    .format(item['id'], item['name'], "Job平台标识正在运行，但是在机器%s上没有发现job进程" % host )
        elif item['run_status'] == CommonConstant.default_status_true and item['next_run_time'] < self.current_time:
            # 该运行未运行
            alert_content = "您的JOB(job_{0} {1})应该在{2}运行,但是现在还没有运行" \
                .format(item['id'], item['name'], DateHelper.getDateOnTimestamps(item['next_run_time'], '%Y-%m-%d %H:%M'))
        elif item['run_status'] == CommonConstant.default_status_pos_2 and item['job_type'] != CommonConstant.default_status_pos_2:
            # 常驻Job不判断时间
            # 对于固定运行时长，如果运行时间大于原计划时间的120%就报警；动态运行时长，超出上限就报警
            run_duration_time = int(time.time() - item['next_run_time'] )

            # 使用动态预估运行时间确定是否报警，加了15分钟的缓冲时间
            if run_duration_time > ( item['threshold_up'] + 15 ) * 60:  # 运行时长高于上限值，报警
                run_duration_min = round(run_duration_time / 60, 1)
                alert_content = "[运行超时]您的job(job_{0} {1})在{2}开始运行,预计时长{3}-{4}分钟,但是目前仍然在运行(运行了{5}分钟)"\
                    .format(item['id'], item['name'], DateHelper.getDateOnTimestamps(item['next_run_time'], '%Y-%m-%d %H:%M'),
                            item['threshold_down'], item['threshold_up'],run_duration_min )

        # 自动修复
        if 'Job平台标识正在运行' in alert_content and 'Job平台会自动修复' in alert_content:
            try:
                ##下一分钟
                # next_date = datetime.datetime.now() + datetime.timedelta(minutes=1)
                # next_date = next_date.replace(second=0)
                # next_run_time = int(time.mktime(next_date.timetuple()))
                # params = {
                #     "next_run_time": next_run_time,
                #     "run_status": CommonConstant.default_status_true,
                #     "status": CommonConstant.default_status_true
                # }
                # JobList.query.filter_by(id=item['id']).update(dict(params))
                # db.session.commit()
                app.logger.info("您的job(job_{0} {1}) 自动修复成功~~".format( item['id'], item['name'] ) )
            except:
                app.logger.info("您的job(job_{0} {1}) 自动修复失败，错误原因：{2}~~".format( item['id'], item['name'],self.getErrMsg() ) )

        ##存储到报警日志表
        if alert_content:
            app.logger.info(alert_content)
            JobService.saveAlertLog(item['id'],alert_content)
        return True