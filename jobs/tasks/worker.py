# -*- coding: utf-8 -*-
import getpass,json,multiprocessing,os,re,logging
from flask.logging import default_handler
from application import app, db
from common.components.helper.DateHelper import DateHelper
from common.components.helper.FileHelper import FileHelper
from common.models.job.JobServer import JobServer
from jobs.tasks.BaseJob import BaseJob

'''
注册Job 注册基本信息到服务器
python manage_job.py runjob -m worker -a reg -p server_id
python manage_job.py runjob -m worker -a reg -jp '{"server_id":1}'
python manage_job.py runjob -m worker -a update 
'''

class JobTask( BaseJob ):
    def __init__(self):
        app.config['DEBUG'] = True
        logging_format = logging.Formatter('%(levelname)s %(asctime)s %(filename)s:%(funcName)s L%(lineno)s %(message)s')
        default_handler.setFormatter( logging_format )

    def run(self, kwargs ):
        pid_path = self.getPidPath('worker.pid')
        if self.checkPidExist(pid_path):
            app.logger.info("[core] worker is running")
            return False

        pid = str(os.getpid())
        if not self.setPidFile(pid_path, pid):
            err_msg = self.getErrMsg()
            app.logger.info("Cann't get a lock file，err msg : " + err_msg)
            return False


        act = kwargs['act']
        if act == "update":
            self.update()
        else:
            params = kwargs['param']
            if len( params) < 1:
                app.logger.info("[reg] 需要服务器id参数 ")
                return True
            self.reg( params[0] )
        app.logger.info("it's over~~")
        return True

    def reg(self,server_id = 0):
        app.logger.info( "[reg] start" )
        if not self.regEnvFile( server_id,"reg" ):
            return False
        self.regCrontab()
        app.logger.info("[reg] end")
        return True

    def update(self):
        app.logger.info("start")
        params = self.getEnvFile()
        server_id = params['id']
        if not self.regEnvFile( server_id ):
            return False

        ##更新服务器负载信息
        total_mem, available_mem = self.getMem()
        params = {
            "cpu_load" : self.cpuLoad(),
            "total_mem" : total_mem,
            "available_mem" : available_mem,
        }
        JobServer.query.filter_by(id=server_id).update( dict(params) )
        db.session.commit()

        app.logger.info("end")
        return True


    '''
    注册环境文件到对应目录中
    '''
    def regEnvFile(self,server_id = 1,act = "update" ):
        info = JobServer.query.filter_by(id=server_id).first()
        if not info:
            app.logger.info("[reg] id:{0} 没有取到服务器信息".format(server_id))
            return False

        if act == "reg":
            app.logger.info("服务器信息如下\nid：{0}\n名称：{1}\n备注：{2}".format(info.id, info.name, info.note))
            custom_input = input("确定服务器新是否正确[y/N]:")
            if custom_input.lower() != "y":
                app.logger.info( "退出注册服务器新" )
                return False

        params = {
            "id": info.id,
            "name": info.name,
            "updated_time": DateHelper.getCurrentTime()
        }
        self.setEnvFile( json.dumps(params) )
        return True

    def regCrontab(self):
        logs_dir = FileHelper.getLogPath("/logs")
        FileHelper.makeSuredirs(logs_dir)

        manage_file = app.root_path + "/manage_job.py"
        kw = "Jobs Core Task"
        crontab = '''####{0}<<<####
MAILTO=""
##调度Job
* * * * * {{ . ~/.bash_jobs && python {1} runjob -m dispatch ;}} > /dev/null 2>&1
##更新服务器环境文件
* * * * * {{ . ~/.bash_jobs && python {1} runjob -m worker -a update  ;}} >> {2}/cron.worker.`date +\%Y_\%m_\%d`.log  2>&1
##监控Job
* * * * * {{ . ~/.bash_jobs && python {1} runjob -m monitor/core  ;}} >> {2}/monitor_core.`date +\%Y_\%m_\%d`.log  2>&1
* * * * * {{ . ~/.bash_jobs && python {1} runjob -m monitor/system  ;}} >> {2}/monitor_system.`date +\%Y_\%m_\%d`.log  2>&1
####{0}>>>####\n'''.format( kw,manage_file ,logs_dir)

        '''
        先将crontab 备份
        '''
        user = getpass.getuser()
        fpath = '/tmp/' + user + '.cron'
        os.system('crontab -l > ' + fpath)

        orig_content = FileHelper.getContent( fpath )

        reg_rule = re.compile('####{0}<<<####[\s\S]*####{0}>>>####'.format( kw) )
        new_content = reg_rule.sub('', orig_content)
        new_content +=  crontab
        FileHelper.saveContent(fpath,new_content)
        print( "Crontab Notice:\n%s\n------------\nchanged to:\n%s" % (orig_content, new_content) )

        custom_input = input("是否确定要替换Crontab内容[y/N]:")
        if custom_input.lower() == "y":
            os.system('crontab ' + fpath)
            print( "Saved Success" )
        else:
            print( "Cancel" )

    def getMem(self):
        total_mem = 0.00
        available_mem = 0.00
        try:
            import psutil
            div_gb_factor = (1024.0 ** 3)
            pc_mem = psutil.virtual_memory()
            total_mem = '%.2f' % (float(pc_mem.total / div_gb_factor))
            available_mem = '%.2f' % (float(pc_mem.available / div_gb_factor))
        except Exception as e:
                pass

        return (str(total_mem), str(available_mem))

    def cpuLoad(self):
        l = open("/proc/loadavg").read().split()[0]
        c = multiprocessing.cpu_count()
        cpu_load = '%.2f' % ( float(l) / c)
        return str(cpu_load)
