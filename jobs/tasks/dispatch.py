# -*- coding: utf-8 -*-
import json
import os,time,atexit,sys,subprocess,math,logging
from flask.logging import default_handler
from application import app,db
from common.components.helper.DateHelper import DateHelper
from common.components.helper.UtilHelper import UtilHelper
from common.models.job.JobList import JobList
from common.services.CommonConstant import CommonConstant
from common.services.JobService import JobService
from jobs.tasks.BaseJob import BaseJob

'''
调度核心Job
python manage_job.py runjob -m dispatch
参考文章:Flask-Sqlalchemy与多线程、多进程
https://www.cnblogs.com/flowell/p/multiprocessing_flask_sqlalchemy.html
https://docs.sqlalchemy.org/en/13/core/pooling.html#pooling-multiprocessing
'''

class JobTask( BaseJob ):
    def __init__(self):
        app.config['DEBUG'] = True
        '''
        这里得考虑常驻Job，那么这个文件句柄就会被一直占用。如果日志按天设置，就会有老日志文件句柄被占
        所以这里的日志请需要使用logrotate进行切割就行了, 那就在/etc/logrotate.d/jobs配置
        '''
        log_path = self.getLogPath( "dispatch.log"% DateHelper.getCurrentTime( "%Y_%m_%d" ) )
        handler = logging.FileHandler( log_path , encoding='UTF-8')
        logging_format = logging.Formatter('%(levelname)s %(asctime)s %(filename)s:%(funcName)s L%(lineno)s %(message)s')
        handler.setFormatter(logging_format)
        app.logger.addHandler( handler )

        ##默认的还是继续输出
        default_handler.setFormatter(logging_format)

    def run(self, params):
        pid_path = self.getPidPath('dispatch.pid')
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
        list = JobList.query.filter_by( server_id = server_id,status = CommonConstant.default_status_true,
                                        run_status = CommonConstant.default_status_true,is_del = CommonConstant.default_status_false ).all()

        if not list:
            app.logger.info("没有数据需要调度~~")
            return True

        for t in list:

            ##调度时间是否到了，应该加入到SQL查询中查询
            if t.next_run_time >= time.time():
                app.logger.info( "job_id:%s，运行时间未到"%( t.id ) )
                continue

            # 启子进程中运行
            app.logger.info( "get a task: job_id:%s，运行时间：%s" % (t.id,DateHelper.getCurrentTime()) )
            '''
            子进程复制一份父进程内存给自己，两个进程之间的执行是相互独立的，其执行顺序可以是不确定的、随机的、不可预测的
            多进程（os.fork()）下，子进程会继承父进程的连接，所以会有问题.先销毁已有的engine，确保父进程没有数据库连接
            相关错误：Mysql server has gone away
            '''
            db.get_engine(app=app).dispose()

            pid = os.fork()
            if pid == 0: #子进程,这里是一个独立进程（在复制出来的那一刻 所有变量都会共享到子进程）,所以写代码 就要感觉在一个独立方法中
                #
                '''
                错误
                sqlalchemy.exc.InvalidRequestError: This session is in 'prepared' state; 
                no further SQL can be emitted within this transaction.
                '''
                db.session.remove()
                #db.session.close()
                job_id = t.id
                job_pid_file = self.getPidPath( 'job_%s.pid' % job_id )
                if self.checkPidExist(job_pid_file):
                    app.logger.info("job_id:%s is running on  %s" % (job_id, host))
                    return 0

                ## 建立具体job的pid 文件，防止重复运行
                tmp_pid = str(os.getpid())
                if not self.setPidFile(job_pid_file, tmp_pid):
                    app.logger.info("job_id:%s 不能建立pid，path：%s，msg：%s" % (job_id, job_pid_file, self.getErrMsg()))
                    return True

                app.logger.info("job_id:%s 建立pid，子进程pid：%s" % (job_id, tmp_pid))


                ## 更新job为运行中
                try:
                    tmp_affect_rows = JobList.query.filter_by( id = job_id,run_status = CommonConstant.default_status_true )\
                        .update( dict( run_status = CommonConstant.default_status_pos_2 ) )
                    db.session.commit()
                    if tmp_affect_rows < 1:
                        app.logger.info("job_id:%s不能得到lock，任务已经运行中" % job_id)
                        return False
                except:
                    app.logger.info( "job_id:%s不能得到锁状态，err：%s" % (job_id,str( sys.exc_info() ) ) )

                ##写入一条调度日志
                tmp_log_id = 0
                try:
                    tmp_log_params = {
                        "job_id":job_id,
                        "server_id":server_id,
                        "server_name":host,
                        "status": CommonConstant.default_status_neg_1,
                        "start_time":DateHelper.getCurrentTime()
                    }
                    tmp_log_id = JobService.addRunLog( tmp_log_params )
                except :
                    pass

                tmp_job_run_start_time = time.time()  # job开始运行的时间
                # t.command无法获取job内部输出的内容，我们需要按行读取或者按buffer读取的
                # status = os.system(t.command)>>8#status, output = commands.getstatusoutput(t.command)
                # 可以加 bufsize = -1 表示使用系统默认缓存
                # 命令前面加一下前缀，方便搜索关键词查找
                # 创建子进程后子进程不结束 https://bbs.csdn.net/topics/390596479?_=1515055076
                tmp_command = t.command
                tmp_command = "tmp_job_%s='%s' && %s"%( job_id,DateHelper.getCurrentTime(),tmp_command)
                #如果想要达到2>&1 可以设置为stdout=subprocess.PIPE,stderr=subprocess.STDOUT
                sp = subprocess.Popen(tmp_command, bufsize = -1, shell = True, close_fds=True, stdout=subprocess.PIPE,stderr=subprocess.STDOUT)

                tmp_run_job_pid = sp.pid
                '''
                    如果是包裹了一层runshell的需要找到进程的子进程pid，然后在查看内存
                    tmp_pid 是目前子进程的进程号
                    tmp_run_job_pid 是目前 subprocess启动的进程好
                    真真运行的进程号，需要通过关键词查询，所以在命令前面加了特别东西
                '''
                app.logger.info( "job_id:%s 启动Job脚本，pid：%s" % (job_id, tmp_run_job_pid))

                ##统计内存占用量
                tmp_max_job_used_mem = tmp_job_used_mem = UtilHelper.getUsedMemory( tmp_run_job_pid )
                app.logger.info("job_id:%s 日志start-------" %job_id )
                while True:
                    ##统计内存占用量
                    tmp_job_used_mem = UtilHelper.getUsedMemory( tmp_run_job_pid )
                    if tmp_job_used_mem > tmp_max_job_used_mem:
                        tmp_max_job_used_mem = tmp_job_used_mem

                    # 换一种读取缓冲区内容的方式
                    # sp.stdout.read(400)
                    # sp.stdout.readline()
                    tmp_line_output = sp.stdout.readline()
                    tmp_line_output = tmp_line_output.strip()
                    #返回的是bytes
                    tmp_line_output = str(tmp_line_output, encoding="utf8")
                    if not tmp_line_output:
                        app.logger.info( "job_id:%s output break" % (job_id) )
                        break
                    tmp_lines = tmp_line_output.split("\n")
                    for tmp_line in tmp_lines:
                        app.logger.info("job_id:%s %s" % (job_id, tmp_line) )

                app.logger.info("job_id:%s 日志end-------" % job_id)
                ##统计内存占用量
                tmp_job_used_mem = UtilHelper.getUsedMemory( tmp_run_job_pid )
                if tmp_job_used_mem > tmp_max_job_used_mem:
                    tmp_max_job_used_mem = tmp_job_used_mem

                app.logger.info("job_id:%s PID:%s, 使用内存（end） %s" % (job_id, tmp_run_job_pid, tmp_job_used_mem))
                app.logger.info("job_id:%s PID:%s, 最大使用内存 %s" % (job_id, tmp_run_job_pid, tmp_max_job_used_mem))
                app.logger.info("job_id:%s 更新消耗内存完毕" % (job_id))

                # 将标准输出关闭了
                sp.stdout.close()
                tmp_status = sp.wait()
                app.logger.info("job_id:%s status_code:%s，%s" % (t.id, str(tmp_status),tmp_command ))


                #和下面分开就是怕报警影响正常处理
                try:
                    #相关报警判断
                    self.alertStatusJudge(t, tmp_status)
                    self.alertRunTimeJudge(t, tmp_job_run_start_time)
                except:
                    app.logger.info( self.getErrMsg() )


                # 更新状态和下一次运行时间
                try:
                    ##提前将文件释放下，因为当服务器状态非常繁忙的时候，进程比较缓慢，会导致状态已经更新但是pid文件没有删除
                    self.atexit_removepid(job_pid_file)
                    ##更新对应日志的log
                    JobService.updateRunLog( tmp_log_id,tmp_max_job_used_mem,( tmp_status == 0 ) )
                    if t.job_type == CommonConstant.default_status_pos_3 :#一次性job
                        JobList.query.filter_by(id=job_id).update( dict( run_status = CommonConstant.default_status_false,status = CommonConstant.default_status_false) )
                        db.session.commit()
                    else:
                        tmp_next_time = t.next_run_time + int( math.ceil((time.time() - t.next_run_time) / (t.run_interval * 60)) * t.run_interval * 60)
                        JobList.query.filter_by(id=job_id).update( dict( run_status = CommonConstant.default_status_true ,next_run_time =  tmp_next_time ) )
                        db.session.commit()
                except:
                    app.logger.info( self.getErrMsg() )
                # 完成



                app.logger.info('job_id:%s 运行完成时间为：%s，子进程结束~~' % (job_id, DateHelper.getCurrentTime() ))
                return 0

            elif pid > 0:  # 父进程
                '''
                status是一个传出参数。
                waitpid的pid参数选择：
                < -1 回收指定进程组内的任意子进程
                = -1 回收任意子进程,等待所有的子进程终止
                = 0  回收和当前调用waitpid一个组的所有子进程
                > 0  回收指定ID的子进程
                '''
                app.logger.info("父进程 job_id:%s pid：%s" % (t.id, pid))
                #os.waitpid( pid , os.WNOHANG)
                os.waitpid(-1, os.WNOHANG)
                app.logger.info("job_id:%s 父进程结束~~" % t.id)
            else:
                app.logger.info("job_id:%s,不能建立调度器" % (t.id))

        app.logger.info("it's over~~")
        return True



    def alertStatusJudge(self,job_info,status):
        if status == CommonConstant.default_status_false:
            return True
        alert_content = "job_id:{0}({1}) 执行出错,返回错误码是{2}，错误原因是{3}".format(job_info.id, job_info.name, status,
                                                                         self.format_posixexitvalue(status))

        JobService.saveAlertLog( job_info.id, alert_content)
        return True


    def alertRunTimeJudge(self, job_info, job_run_start_time):
        #常驻Job不用判断时间
        if job_info.job_type == CommonConstant.default_status_pos_2:
            return True
        job_run_total_time = int( time.time() - job_run_start_time)
        job_id = job_info.id

        alert_temp = "[运行时间异常]您的job(job_{0} {1})在{2}开始运行,预计时长{3} - {4}分钟,但是运行了{5}分钟"
        alert_content = ""
        if job_run_total_time < (job_info.threshold_down * 60 - 10 * 60):  # 运行时长低于下限值，报警（阀值后面-10分钟）
            alert_content = alert_temp.format(job_id, job_info.name,
                                              DateHelper.getDateOnTimestamps(job_info.next_run_time,format="%Y-%m-%d %H:%M"),
                                              job_info.threshold_down, job_info.threshold_up,DateHelper.formatBeautyTime( job_run_total_time ) )
        elif job_run_total_time > ( job_info.threshold_up * 60 + 15 * 60 ):
            alert_content = alert_temp.format(job_id, job_info.name,
                                              DateHelper.getDateOnTimestamps(job_info.next_run_time,format="%Y-%m-%d %H:%M"),
                                              job_info.threshold_down, job_info.threshold_up,DateHelper.formatBeautyTime( job_run_total_time ) )

        if alert_content:
            JobService.saveAlertLog( job_id , alert_content)

        return True

    def format_posixexitvalue(self, exit_code ):
        if exit_code == 0:
            return "命令运行成功"
        elif exit_code == 2:
            return "参数不正确"
        elif exit_code > 0 and exit_code < 126:
            return "命令运行失败"
        elif exit_code == 126:
            return "命令无法运行"
        elif exit_code == 127:
            return "找不到指定命令"
        elif exit_code > 128:  # 128+signal
            return "强制退出"

