# -*- coding: utf-8 -*-
import  datetime,time,math
from flask import Blueprint,request,redirect
from sqlalchemy import or_,and_
from application import db
from common.components.helper.DateHelper import DateHelper
from common.components.helper.ModelHelper import ModelHelper
from common.components.helper.UtilHelper import UtilHelper
from common.components.helper.ValidateHelper import ValidateHelper
from common.models.job.JobCategory import JobCategory
from common.models.job.JobKillQueue import JobKillQueue
from common.models.job.JobList import JobList
from common.models.job.JobRunLog import JobRunLog
from common.models.job.JobServer import JobServer
from common.models.rbac.User import User
from common.services.CommonConstant import CommonConstant
from common.services.CurrentUserService import CurrentUserService
from common.services.GlobalUrlService import GlobalUrlService
from common.services.RBACService import RBACService

route_home_job = Blueprint('home_job_page', __name__)


job_status_map = {
    0 : "不需要",
    1 : "需要"
}

display_status_map = {
    0 : "展示",
    1 : "隐藏"
}

@route_home_job.route("/")
@route_home_job.route("/index")
def job_index():
    req = request.values
    cate_id = int( req.get("cate_id", CommonConstant.default_status_false) )
    owner_uid = int( req.get("owner_uid", CurrentUserService.getUid() ) )
    env_id = int( req.get("env_id", CommonConstant.default_status_false) )
    server_id = int( req.get("server_id", CommonConstant.default_status_false) )
    status = int( req.get("status", CommonConstant.default_status_neg_99 ) )
    display_status = int( req.get("display_status", CommonConstant.default_status_neg_99 ) )
    job_type = int( req.get("job_type", CommonConstant.default_status_neg_99 ) )

    kw = req.get("kw","").strip()
    page = int(req.get("p", 1))

    query = JobList.query

    if RBACService.checkDataPrivilege("all"):
        pass
    else:
        query = query.filter_by( owner_uid = CurrentUserService.getUid() )

    if cate_id:
        query = query.filter_by(cate_id=cate_id)

    if env_id:
        query = query.filter_by( env_id = env_id)

    if owner_uid:
        query = query.filter_by(owner_uid=owner_uid)

    if server_id:
        query = query.filter_by( server_id = server_id)

    if status > CommonConstant.default_status_neg_99:
        query = query.filter_by( status = status )

    if display_status > CommonConstant.default_status_neg_99:
        query = query.filter_by( is_del = display_status )

    if job_type > CommonConstant.default_status_neg_99:
        query = query.filter_by( job_type = job_type )

    if kw:
        if kw.isdigit():
            query = query.filter_by( id = int( kw ) )
        else:
            query = query.filter( or_( JobList.name.ilike( '%{}%'.format(kw) ) ,JobList.command.ilike( '%{}%'.format(kw) ) ))

    page_params = {
        "total": query.count(),
        "page_size": CommonConstant.PAGE_SIZE,
        "page": page,
        "display": CommonConstant.PAGE_DISPLAY
    }

    pages = UtilHelper.iPagination(page_params)
    offset = (page - 1) * CommonConstant.PAGE_SIZE
    limit = CommonConstant.PAGE_SIZE * page
    list = query.order_by( JobList.id.desc() )[offset:limit]
    data = []

    server_map = ModelHelper.getDictFilterField( JobServer )
    cate_map = ModelHelper.getDictFilterField( JobCategory )
    staff_map = ModelHelper.getDictFilterField( User )
    server_env_map = CommonConstant.server_env_map
    run_status_map = CommonConstant.run_status_map
    job_type_map = CommonConstant.job_type_map
    if list:
        for item in list:
            tmp_data = ModelHelper.model2Dict( item )
            tmp_server_info = ModelHelper.model2Dict( server_map.get( tmp_data['server_id']) )
            tmp_cate_info = ModelHelper.model2Dict( cate_map.get( tmp_data['cate_id']) )
            tmp_owner_staff_info = ModelHelper.model2Dict( staff_map.get( tmp_data['owner_uid']) )
            tmp_relate_staff_info = ModelHelper.model2Dict( staff_map.get( tmp_data['relate_uid']) )
            tmp_data['next_run_time'] = DateHelper.getDateOnTimestamps( tmp_data['next_run_time'] ,'%Y-%m-%d %H:%M' )
            tmp_data['env_name'] = server_env_map.get( tmp_data['env_id'] )
            tmp_data['run_status_desc'] = run_status_map.get( tmp_data['run_status'] )
            tmp_data['job_status_desc'] = job_status_map.get( tmp_data['status'] )
            tmp_data['server_name'] = tmp_server_info.get("name")
            tmp_data['cate_name'] = tmp_cate_info.get("name",'')
            tmp_data['owner_name'] = tmp_owner_staff_info.get("name",'')
            tmp_data['relate_name'] = tmp_relate_staff_info.get("name",'')
            tmp_data['run_interval_desc'] = DateHelper.formatBeautyTime( tmp_data['run_interval'] * 60 )
            data.append( tmp_data )
    sc = {
        'kw': kw,
        'cate_id' : cate_id,
        'owner_uid' : owner_uid,
        'env_id' : env_id,
        'server_id' : server_id,
        'status' : status,
        'display_status' : display_status,
        'job_type' : job_type,
    }

    set_flag = RBACService.checkPageRelatePrivilege("set")
    ops_flag = RBACService.checkPageRelatePrivilege("ops")
    return UtilHelper.renderView("home/job/index/index.html",{
        "list": data,
        "pages":pages,
        "job_status_map":job_status_map,
        "server_env_map":server_env_map,
        "server_map":server_map,
        "staff_map":staff_map,
        "cate_map":cate_map,
        "display_status_map":display_status_map,
        "job_type_map":job_type_map,
        "sc":sc ,
        "set_flag" : set_flag,
        "ops_flag" : ops_flag,
    })


@route_home_job.route("/info")
def job_info():
    req = request.values
    id = int(req['id']) if ('id' in req and req['id']) else 0
    info = JobList.query.filter_by(id=id).first()
    if not info:
        return redirect( GlobalUrlService.buildHomeUrl("/job/index/index") )

    info = ModelHelper.model2Dict(info)

    server_info = JobServer.query.filter_by(id = info['server_id']).first()
    cate_info = JobCategory.query.filter_by(id= info['cate_id'] ).first()
    server_env_map = CommonConstant.server_env_map
    run_status_map = CommonConstant.run_status_map

    info['next_run_time'] = DateHelper.getDateOnTimestamps(info['next_run_time'], '%Y-%m-%d %H:%M')
    info['env_name'] = server_env_map.get(info['env_id'])
    info['run_status_desc'] = run_status_map.get(info['run_status'])
    info['job_status_desc'] = job_status_map.get(info['status'])
    info['server_name'] = server_info.name
    info['cate_name'] = cate_info.name if cate_info else ''
    info['run_interval_desc'] = DateHelper.formatBeautyTime(info['run_interval'] * 60)

    user_map = ModelHelper.getDictFilterField( User,select_field = User.id,id_list = [ info['owner_uid'],info['relate_uid'] ]  )

    ##获取最近5天运行记录
    log_list = JobRunLog.query.filter_by( job_id = id ).order_by( JobRunLog.id.desc() )[0:5]
    log_data = []
    if log_list:
        for item in log_list:
            tmp_data = ModelHelper.model2Dict( item )
            tmp_data['status_desc'] =  CommonConstant.job_log_status_map[tmp_data['status']]
            tmp_data['duration'] = ""
            if DateHelper.getCurrentTime(date=tmp_data['end_time']) == CommonConstant.DEFAULT_DATETIME:
                tmp_data['end_time'] = "未知"
                tmp_data['duration'] =time.time() - time.mktime( tmp_data['start_time'].timetuple() )
            else:
                tmp_data['duration'] = (tmp_data['end_time'] - tmp_data['start_time']).seconds
            tmp_data['duration'] = DateHelper.formatBeautyTime(tmp_data['duration'])
            log_data.append(tmp_data)

    return UtilHelper.renderView("home/job/index/info.html", {
        "info": info,
        "log_list":log_data,
        "user_map": user_map,
    })


@route_home_job.route("/set",methods=[ "POST","GET" ])
def job_set():
    if UtilHelper.isGet() :
        req = request.values
        id = int(req['id']) if ('id' in req and req['id']) else 0
        act = req.get("act", "").strip()
        info = {
            'owner_uid': CurrentUserService.getUid()
        }
        if id > 0:
            info = JobList.query.filter_by(id=id).first()
            info = ModelHelper.model2Dict( info )
            info['next_run_time'] = DateHelper.getDateOnTimestamps(info['next_run_time'], '%Y-%m-%d %H:%M')

        if act == "copy":
            info['id'] = 0
            info['status'] = 0
            info['name'] = "【复制】" + info['name']

        server_list = JobServer.query.order_by( JobServer.id.desc() ).all()
        user_list = User.query.order_by( User.id.desc() ).all()
        cate_list = JobCategory.query.order_by(JobCategory.id.desc()).all()

        return UtilHelper.renderView("home/job/index/set.html",{
            "info" : info,
            "server_list" : server_list,
            "user_list" : user_list,
            "cate_list" : cate_list,
            "server_env_map": CommonConstant.server_env_map,
            "job_type_map": CommonConstant.job_type_map,
            "job_status_map": job_status_map,
        })

    req = request.values
    id = int(req['id']) if ('id' in req and req['id']) else 0
    cate_id = int(req.get("cate_id", "0").strip())
    name = req.get("name", "").strip()
    env_id = int(req.get("env_id", "0" ).strip())
    server_id = int(req.get("server_id", "0" ).strip())
    owner_uid = int(req.get("owner_uid", "0" ).strip())
    relate_uid = int(req.get("relate_uid", "0" ).strip())
    command = req.get("command","").strip()
    job_type = int(req.get("job_type", "0" ).strip())
    status = int(req.get("status", "0" ).strip())
    next_run_time = req.get("next_run_time","").strip()
    run_interval = int(req.get("run_interval", "0" ).strip())
    threshold_down = int(req.get("threshold_down", "0" ).strip())
    threshold_up = int(req.get("threshold_up", "0" ).strip())
    note = req.get("note", "" ).strip()

    if cate_id < 1 :
        return UtilHelper.renderErrJSON("请选择所属分类~~")

    if not ValidateHelper.validLength( name,1,15 ):
        return UtilHelper.renderErrJSON("请输入符合规范的名称~~")

    if env_id < 1:
        return UtilHelper.renderErrJSON("请选择运行环境~~")

    if server_id < 1:
        return UtilHelper.renderErrJSON("请选择运行服务器~~")

    if owner_uid < 1:
        return UtilHelper.renderErrJSON("请选择Job负责人~~")

    if relate_uid < 1:
        return UtilHelper.renderErrJSON("请选择Job相关人~~")

    if not ValidateHelper.validLength( command,5 ):
        return UtilHelper.renderErrJSON("请输入Job命令~~")

    if job_type < 1 :
        return UtilHelper.renderErrJSON("请选择Job类型~~")

    if not ValidateHelper.validDate(next_run_time,r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}$'):
        return UtilHelper.renderErrJSON("请选择调度时间~~")

    if job_type != CommonConstant.default_status_pos_2:
        if run_interval < 1 :
            return UtilHelper.renderErrJSON("请输入运行间隔~~")

        if threshold_down < 0 :
            return UtilHelper.renderErrJSON("请输入预估最短运行时长~~")

        if threshold_up < 1 :
            return UtilHelper.renderErrJSON("请输入预估最长运行时长~~")
    else:
        run_interval = threshold_down = threshold_up = 0


    info = JobList.query.filter_by(id=id).first()

    if info:
        model_job = info
        ##正在运行的Job不能编辑运行时间
        if info.run_status == CommonConstant.default_status_pos_2:
            if info.command != command:
                return UtilHelper.renderErrJSON("正在运行的Job不能修改运行命令~~")

            if info.job_type != job_type:
                return UtilHelper.renderErrJSON("正在运行的Job不能修改类型~~")

            if info.status != status:
                return UtilHelper.renderErrJSON("正在运行的Job不能修改调度状态~~")

            if info.next_run_time != DateHelper.getTimestamps( next_run_time + ":00" ) :
                return UtilHelper.renderErrJSON("正在运行的Job不能修改调度时间~~")

    else:
        model_job = JobList()

    ##只有需要调度的才需要判断时间
    if model_job.run_status != CommonConstant.default_status_pos_2 and status \
            and DateHelper.getTimestamps(next_run_time + ":00") < time.time():
        return UtilHelper.renderErrJSON("调度时间不能小于当前时间~~")

    model_job.name = name
    model_job.env_id = env_id
    model_job.server_id = server_id
    model_job.owner_uid = owner_uid
    model_job.relate_uid = relate_uid
    model_job.job_type = job_type
    model_job.cate_id = cate_id
    model_job.command = command
    model_job.next_run_time = DateHelper.getTimestamps( next_run_time + ":00" )
    model_job.run_interval = run_interval
    model_job.threshold_up = threshold_up
    model_job.threshold_down = threshold_down
    model_job.note = note
    model_job.status = status
    if status:
        model_job.run_status = CommonConstant.default_status_true

    db.session.add( model_job )
    db.session.commit()

    return UtilHelper.renderSucJSON({ "id":model_job.id })


@route_home_job.route("/ops",methods=[ "POST" ])
def job_ops():
    req = request.values
    id = int(req['id']) if ('id' in req and req['id']) else 0
    act = req.get("act","").strip()
    allow_act = [ 'del','recovery','system_not_run','system_run','run_next','kill' ]
    if not id:
        return UtilHelper.renderErrJSON( CommonConstant.SYSTEM_DEFAULT_ERROR + " -1" )

    if act not in allow_act:
        return UtilHelper.renderErrJSON(CommonConstant.SYSTEM_DEFAULT_ERROR + " -2")

    info = JobList.query.filter_by(id=id).first()
    if not info:
        return UtilHelper.renderErrJSON( "指定数据不存在" )

    ##在增加一个判断，除了负责人和相关人外，还有管理严，其他人不能操作
    allow_ops_uids = [ info.owner_uid,info.relate_uid ]
    if not CurrentUserService.isRoot() and CurrentUserService.getUid() not in allow_ops_uids:
        return UtilHelper.renderErrJSON("非Job负责人或者相关人禁止操作")

    if act == "kill" and info.run_status != CommonConstant.default_status_pos_2:
        return UtilHelper.renderErrJSON("强制杀死的job必须正在运行")

    if act != "kill" and info.run_status == CommonConstant.default_status_pos_2:
        return UtilHelper.renderErrJSON("正在运行的Job不能操作")

    if act == "del":
        info.is_del = CommonConstant.default_status_true
    elif act == "recovery":
        info.is_del = CommonConstant.default_status_false
    elif act == "system_not_run":
        info.status = CommonConstant.default_status_false
    elif act == "system_run":
        #如果可以调度了，是不是要把调度时间改成下一个周期
        info.status = CommonConstant.default_status_true
        info.run_status = CommonConstant.default_status_true
        if int( info.job_type) == CommonConstant.default_status_pos_2:  # 常驻Job，他停止之后下一分钟直接运行
            next_date = datetime.datetime.now() + datetime.timedelta(minutes=1)
            next_date = next_date.replace(second=0)
            tmp_next_time = int( time.mktime( next_date.timetuple() ) )
        else:
            tmp_next_time = info.next_run_time + int( math.ceil((time.time() - info.next_run_time) / (info.run_interval * 60)) * info.run_interval * 60)
        info.next_run_time = tmp_next_time
    elif act == "run_next":

        if not info.status :
            return UtilHelper.renderErrJSON("Job 未调度，无法立即调度")

        ##下一分钟
        next_date = datetime.datetime.now() + datetime.timedelta(minutes=1)
        next_date = next_date.replace(second=0)
        info.next_run_time = int( time.mktime( next_date.timetuple() ) )
        info.run_status = CommonConstant.default_status_true
    elif act == "kill":
        ##这里是杀死job的判断
        has_not_handle = JobKillQueue.query.filter_by( job_id = info.id,status = CommonConstant.default_status_neg_2 ).count()
        if has_not_handle:
            return UtilHelper.renderErrJSON("该Job还有未执行的杀死任务，请等上一个执行完毕之后在点击~~")

        model_kill = JobKillQueue()
        model_kill.job_id = info.id
        model_kill.server_id = info.server_id
        db.session.add( model_kill )

    db.session.add( info )
    db.session.commit()
    return UtilHelper.renderSucJSON()

