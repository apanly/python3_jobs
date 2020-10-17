# -*- coding: utf-8 -*-
from flask import Blueprint,request
from application import db
from common.components.helper.ModelHelper import ModelHelper
from common.components.helper.UtilHelper import UtilHelper
from common.components.helper.ValidateHelper import ValidateHelper
from common.models.config.Sysconfig import Sysconfig
from common.services.CommonConstant import CommonConstant
from common.services.RBACService import RBACService

route_home_config_index = Blueprint('home_config_index_page', __name__)

@route_home_config_index.route("/")
@route_home_config_index.route("/index")
def config_index():
    req = request.values
    kw = req.get("kw","").strip()
    page = int(req.get("p", 1))

    query = Sysconfig.query
    if kw:
        query = query.filter( Sysconfig.name.ilike( '%{}%'.format(kw) ) )

    page_params = {
        "total": query.count(),
        "page_size": CommonConstant.PAGE_SIZE,
        "page": page,
        "display": CommonConstant.PAGE_DISPLAY
    }

    pages = UtilHelper.iPagination(page_params)
    offset = (page - 1) * CommonConstant.PAGE_SIZE
    limit = CommonConstant.PAGE_SIZE * page
    list = query.order_by( Sysconfig.id.desc() )[offset:limit]
    

    sc = {
        'kw': kw
    }

    set_flag = RBACService.checkPageRelatePrivilege("set")
    ops_flag = RBACService.checkPageRelatePrivilege("ops")

    return UtilHelper.renderView("home/config/index.html",{
        "list": list,
        "pages":pages,
        "sc":sc ,
        "set_flag" : set_flag,
        "ops_flag" : ops_flag
    })


@route_home_config_index.route("/set",methods=[ "POST","GET" ])
def config_set():
    if UtilHelper.isGet() :
        req = request.values
        id = int( req['id'] ) if ( 'id' in req and req['id'] )else 0
        info = None
        if id > 0:
            info = Sysconfig.query.filter_by( id=id ).first()


        return UtilHelper.renderPopView( "home/config/set.html",{
            "info":info
        })

    req = request.values
    id = int(req['id']) if ('id' in req and req['id']) else 0
    k_val = req.get("k_val","").strip()

    if not ValidateHelper.validLength( k_val,1 ):
        return UtilHelper.renderErrJSON("请输入符合规范的值~~")


    info = Sysconfig.query.filter_by(id=id).first()

    if info:
        model_config = info
    else:
        model_config = Sysconfig()

    model_config.k_val = k_val
    db.session.add( model_config )
    db.session.commit()
    return UtilHelper.renderSucJSON()


@route_home_config_index.route("/ops",methods=[ "POST" ])
def config_ops():
    req = request.values
    id = int(req['id']) if ('id' in req and req['id']) else 0
    act = req.get("act","").strip()
    allow_act = [ 'del','recovery' ]
    if not id:
        return UtilHelper.renderErrJSON( CommonConstant.SYSTEM_DEFAULT_ERROR )

    if act not in allow_act:
        return UtilHelper.renderErrJSON(CommonConstant.SYSTEM_DEFAULT_ERROR)

    info = Sysconfig.query.filter_by(id=id).first()
    if not info:
        return UtilHelper.renderErrJSON( "指定数据不存在" )

    if act == "del":
        info.status = CommonConstant.default_status_false
    elif act == "recovery":
        info.status = CommonConstant.default_status_true

    db.session.add( info )
    db.session.commit()
    return UtilHelper.renderSucJSON()

