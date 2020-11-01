# -*- coding: utf-8 -*-
import json
import os,sys,traceback,atexit
from signal import signal, SIGTERM

from application import app
from common.components.helper.FileHelper import FileHelper

'''
基础Job类
'''
class BaseJob():

    #获取pid 目录路径
    def getLogPidDir(self):
        log_pid_dir = FileHelper.getLogPath("/pids")
        FileHelper.makeSuredirs(log_pid_dir)
        return log_pid_dir

    #获取log目录路径
    def getLogDir(self):
        return FileHelper.getLogPath("/logs")

    # 获取pid文件路径
    def getPidPath(self,file_name = ''):
        pid_path = self.getLogPidDir() + "/" + file_name
        return pid_path

    # 获取log文件路径
    def getLogPath(self,file_name = ''):
        file_path = self.getLogDir() + "/" + file_name
        return file_path

    # 检查pid文件路径是否存在
    def checkPidExist(self,file_name = ''):
        return os.path.isfile( file_name )


    #新建pid文件，并存储进程
    def setPidFile(self,pid_path = '',pid = '0'):
        try:
            signal(SIGTERM, lambda signum, stack_frame: exit(1))
            #只有正常结束 或者 调用sys.exit 才会执行 atexit注册的行数
            atexit.register(lambda: self.atexit_removepid(pid_path) )
            fd = os.open( pid_path, os.O_CREAT | os.O_EXCL | os.O_RDWR)
            os.write(fd, str.encode(  pid  ) )
            os.close(fd)
        except :
            return False

        return True

    def coverPidFile(self, pid_path = '',pid = '0' ):
        try:
            FileHelper.saveContent(pid_path, str( pid ) )
        except:
            return False

        return True



    #获取服务器的环境文件内容
    def getEnvFile(self,file = "host"):
        path = FileHelper.getLogPath( "/" + file )
        params = FileHelper.getContent(path)
        params = json.loads(params)
        return params

    # 设置服务器的环境文件 内容
    def setEnvFile(self,content,file = "host"):
        path = FileHelper.getLogPath( "/" + file )
        FileHelper.saveContent(path, content )
        return True

    # 删除文件
    def atexit_removepid(self, pid_file):
        try:
            os.remove(pid_file)
        except:
            pass

    # 获取错误内容
    def getErrMsg(self):
        exc_type, exc_value, exc_obj = sys.exc_info()
        err_msg = "exception_type: \t%s,\nexception_value: \t%s,\nexception_object: \t%s,\n" % (
            exc_type, exc_value, traceback.format_exc())
        return err_msg

    def findPidByKw(self,job_id):
        pid = 0
        try:
            import subprocess
            cmd = "ps aux| grep 'tmp_job_%s='|grep -v grep " % job_id
            out = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
            kw_list = out.stdout.read().splitlines()
            if len(kw_list) >= 1:
                for i in kw_list:
                    pid = i.split()[1]
                    pid = str(pid, encoding="utf-8")
                    pid = int(pid)
                    break
        except Exception as error:
            print( self.getErrMsg() )
        return pid

    def exitOK(self):
        return 0

    def exitFail(self,exit_code = 1):
        return exit_code