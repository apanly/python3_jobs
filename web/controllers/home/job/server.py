# -*- coding: utf-8 -*-
from flask import Blueprint,request
from application import db
from common.components.helper.ModelHelper import ModelHelper
from common.components.helper.UtilHelper import UtilHelper
from common.components.helper.ValidateHelper import ValidateHelper
from common.models.job.JobServer import JobServer
from common.services.CommonConstant import CommonConstant
from common.services.RBACService import RBACService

route_home_job_server = Blueprint('home_server_page', __name__)

@route_home_job_server.route("/")
@route_home_job_server.route("/index")
def server_index():
    req = request.values
    kw = req.get("kw","").strip()
    page = int(req.get("p", 1))

    query = JobServer.query
    if kw:
        query = query.filter( JobServer.name.ilike( '%{}%'.format(kw) ) )

    page_params = {
        "total": query.count(),
        "page_size": CommonConstant.PAGE_SIZE,
        "page": page,
        "display": CommonConstant.PAGE_DISPLAY
    }

    pages = UtilHelper.iPagination(page_params)
    offset = (page - 1) * CommonConstant.PAGE_SIZE
    limit = CommonConstant.PAGE_SIZE * page
    list = query.order_by( JobServer.id.desc() )[offset:limit]

    data = []
    server_env_map = CommonConstant.server_env_map
    if list :
        for item in list:
            tmp_data = ModelHelper.model2Dict( item )
            tmp_env_ids = (item.env).strip( CommonConstant.special_strike ).split( CommonConstant.special_strike  )
            tmp_env_list = []
            for _env_id in tmp_env_ids:
                if int( _env_id ) not in server_env_map.keys():
                    continue
                tmp_env_list.append( server_env_map.get( int( _env_id ) ) )

            tmp_data['env'] = ",".join( tmp_env_list )
            data.append( tmp_data )

    sc = {
        'kw': kw
    }

    set_flag = RBACService.checkPageRelatePrivilege("set")
    ops_flag = RBACService.checkPageRelatePrivilege("ops")

    return UtilHelper.renderView("home/job/server/index.html",{
        "list": data,
        "pages":pages,
        "server_env_map":CommonConstant.server_env_map,
        "sc":sc ,
        "set_flag" : set_flag,
        "ops_flag" : ops_flag
    })


@route_home_job_server.route("/set",methods=[ "POST","GET" ])
def server_set():
    if UtilHelper.isGet() :
        req = request.values
        id = int( req['id'] ) if ( 'id' in req and req['id'] )else 0
        info = None
        env_list = []
        if id > 0:
            info = JobServer.query.filter_by( id=id ).first()
            env_list = (info.env).strip( CommonConstant.special_strike ).split( CommonConstant.special_strike  )



        weight_list = []
        weight_list.extend(range(1, 10))

        return UtilHelper.renderPopView( "home/job/server/set.html",{
            "info":info,
            "server_env_map":CommonConstant.server_env_map,
            "weight_list":weight_list,
            "env_list":env_list,
        }  )

    req = request.values
    id = int(req['id']) if ('id' in req and req['id']) else 0
    name = req.get("name","").strip()
    env = request.form.getlist("env[]")
    note = req.get("note","").strip()
    weight = int(req.get("weight", "1").strip())


    if not ValidateHelper.validLength( name,1,30 ):
        return UtilHelper.renderErrJSON("请输入符合规范的名称~~")

    if len( env ) < 1 :
        return UtilHelper.renderErrJSON("请选择支持环境~~")

    info = JobServer.query.filter_by(id=id).first()

    if info:
        model_server = info
    else:
        model_server = JobServer()

    model_server.name = name
    model_server.env = "{0}{1}{0}".format( CommonConstant.special_strike ,( CommonConstant.special_strike ).join( env ),CommonConstant.special_strike )
    model_server.note = note
    model_server.weight = weight
    db.session.add( model_server )
    db.session.commit()
    return UtilHelper.renderSucJSON()


@route_home_job_server.route("/ops",methods=[ "POST" ])
def server_ops():
    req = request.values
    id = int(req['id']) if ('id' in req and req['id']) else 0
    act = req.get("act","").strip()
    allow_act = [ 'del','recovery' ]
    if not id:
        return UtilHelper.renderErrJSON( CommonConstant.SYSTEM_DEFAULT_ERROR )

    if act not in allow_act:
        return UtilHelper.renderErrJSON(CommonConstant.SYSTEM_DEFAULT_ERROR)

    info = JobServer.query.filter_by(id=id).first()
    if not info:
        return UtilHelper.renderErrJSON( "指定数据不存在" )

    if act == "del":
        info.status = CommonConstant.default_status_false
    elif act == "recovery":
        info.status = CommonConstant.default_status_true

    db.session.add( info )
    db.session.commit()
    return UtilHelper.renderSucJSON()

