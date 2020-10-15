# -*- coding: utf-8 -*-
from flask import Blueprint,request
from application import db
from common.components.helper.ModelHelper import ModelHelper
from common.components.helper.UtilHelper import UtilHelper
from common.components.helper.ValidateHelper import ValidateHelper
from common.models.job.JobCategory import JobCategory
from common.services.CommonConstant import CommonConstant
from common.services.RBACService import RBACService

route_home_job_cate = Blueprint('home_cate_page', __name__)

@route_home_job_cate.route("/")
@route_home_job_cate.route("/index")
def cate_index():
    req = request.values
    kw = req.get("kw","").strip()
    page = int(req.get("p", 1))

    query = JobCategory.query
    if kw:
        query = query.filter( JobCategory.name.ilike( '%{}%'.format(kw) ) )

    page_params = {
        "total": query.count(),
        "page_size": CommonConstant.PAGE_SIZE,
        "page": page,
        "display": CommonConstant.PAGE_DISPLAY
    }

    pages = UtilHelper.iPagination(page_params)
    offset = (page - 1) * CommonConstant.PAGE_SIZE
    limit = CommonConstant.PAGE_SIZE * page
    list = query.order_by( JobCategory.id.desc() )[offset:limit]
    

    sc = {
        'kw': kw
    }

    set_flag = RBACService.checkPageRelatePrivilege("set")
    ops_flag = RBACService.checkPageRelatePrivilege("ops")

    return UtilHelper.renderView("home/job/cate/index.html",{
        "list": list,
        "pages":pages,
        "sc":sc ,
        "set_flag" : set_flag,
        "ops_flag" : ops_flag
    })


@route_home_job_cate.route("/set",methods=[ "POST","GET" ])
def cate_set():
    if UtilHelper.isGet() :
        req = request.values
        id = int( req['id'] ) if ( 'id' in req and req['id'] )else 0
        info = None
        if id > 0:
            info = JobCategory.query.filter_by( id=id ).first()


        return UtilHelper.renderPopView( "home/job/cate/set.html",{
            "info":info
        }  )

    req = request.values
    id = int(req['id']) if ('id' in req and req['id']) else 0
    name = req.get("name","").strip()

    if not ValidateHelper.validLength( name,1,30 ):
        return UtilHelper.renderErrJSON("请输入符合规范的名称~~")


    info = JobCategory.query.filter_by(id=id).first()

    if info:
        model_server = info
    else:
        model_server = JobCategory()

    model_server.name = name
    db.session.add( model_server )
    db.session.commit()
    return UtilHelper.renderSucJSON()


@route_home_job_cate.route("/ops",methods=[ "POST" ])
def cate_ops():
    req = request.values
    id = int(req['id']) if ('id' in req and req['id']) else 0
    act = req.get("act","").strip()
    allow_act = [ 'del','recovery' ]
    if not id:
        return UtilHelper.renderErrJSON( CommonConstant.SYSTEM_DEFAULT_ERROR )

    if act not in allow_act:
        return UtilHelper.renderErrJSON(CommonConstant.SYSTEM_DEFAULT_ERROR)

    info = JobCategory.query.filter_by(id=id).first()
    if not info:
        return UtilHelper.renderErrJSON( "指定数据不存在" )

    if act == "del":
        info.status = CommonConstant.default_status_false
    elif act == "recovery":
        info.status = CommonConstant.default_status_true

    db.session.add( info )
    db.session.commit()
    return UtilHelper.renderSucJSON()

