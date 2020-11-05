# -*- coding: utf-8 -*-
from flask import Blueprint,request

from common.components.helper.DateHelper import DateHelper
from common.components.helper.ModelHelper import ModelHelper
from common.components.helper.UtilHelper import UtilHelper
from common.models.applogs.AppAccessLog import AppAccessLog
from common.models.applogs.AppErrLog import AppErrLog
from common.models.job.JobKillQueue import JobKillQueue
from common.models.job.JobList import JobList
from common.services.CommonConstant import CommonConstant

route_home_log = Blueprint('home_log_page', __name__)

@route_home_log.route("/access")
def log_access():
    req = request.values
    page = int( req.get("p",1) )
    date_from = req.get("date_from",DateHelper.getCurrentTime(  fmt = "%Y-%m-%d" ))
    date_to = req.get("date_to",DateHelper.getCurrentTime(  fmt = "%Y-%m-%d" ))
    query = AppAccessLog.query.filter( AppAccessLog.created_time.between( date_from,date_to + " 23:59:59" ) )

    page_params = {
        "total": query.count(),
        "page_size": CommonConstant.PAGE_SIZE,
        "page": page,
        "display": CommonConstant.PAGE_DISPLAY,
    }

    pages = UtilHelper.iPagination(page_params)
    offset = (page - 1) * CommonConstant.PAGE_SIZE
    limit = CommonConstant.PAGE_SIZE * page
    list = query.order_by( AppAccessLog.id.desc())[offset:limit]

    sc = {
        'date_from': date_from,
        'date_to': date_to
    }
    return UtilHelper.renderView( "home/log/access.html",{"list": list,"pages":pages,"sc":sc }  )

@route_home_log.route("/error")
def log_error():
    req = request.values
    page = int(req.get("p", 1))
    date_from = req.get("date_from", DateHelper.getCurrentTime(fmt="%Y-%m-%d"))
    date_to = req.get("date_to", DateHelper.getCurrentTime(fmt="%Y-%m-%d"))
    query = AppErrLog.query.filter(AppErrLog.created_time.between(date_from, date_to + " 23:59:59" ))

    page_params = {
        "total": query.count(),
        "page_size": CommonConstant.PAGE_SIZE,
        "page": page,
        "display": CommonConstant.PAGE_DISPLAY,
    }

    pages = UtilHelper.iPagination(page_params)
    offset = (page - 1) * CommonConstant.PAGE_SIZE
    limit = CommonConstant.PAGE_SIZE * page
    list = query.order_by(AppErrLog.id.desc())[offset:limit]

    sc = {
        'date_from': date_from,
        'date_to': date_to
    }
    return UtilHelper.renderView("home/log/error.html", {"list": list, "pages": pages, "sc": sc})


@route_home_log.route("/kill")
def log_kill():

    req = request.values
    page = int(req.get("p", 1))
    date_from = req.get("date_from", DateHelper.getCurrentTime(fmt="%Y-%m-%d"))
    date_to = req.get("date_to", DateHelper.getCurrentTime(fmt="%Y-%m-%d"))
    status = int(req.get("status", CommonConstant.default_status_neg_99))
    query = JobKillQueue.query.filter(JobKillQueue.created_time.between(date_from, date_to + " 23:59:59"))

    if status > CommonConstant.default_status_neg_99:
        query = query.filter_by(status=status)

    page_params = {
        "total": query.count(),
        "page_size": CommonConstant.PAGE_SIZE,
        "page": page,
        "display": CommonConstant.PAGE_DISPLAY,
    }

    pages = UtilHelper.iPagination(page_params)
    offset = (page - 1) * CommonConstant.PAGE_SIZE
    limit = CommonConstant.PAGE_SIZE * page
    list = query.order_by(JobKillQueue.id.desc())[offset:limit]
    data = []
    if list:
        job_ids = ModelHelper.getFieldList(list, "job_id")
        job_map = ModelHelper.getDictFilterField(JobList, select_field= JobList.id, id_list = job_ids.sort() )
        for item in list:
            tmp_data = ModelHelper.model2Dict(item)
            tmp_job_info = ModelHelper.model2Dict(job_map.get(tmp_data['job_id']))
            tmp_data['status_desc'] = CommonConstant.common_status_map4[tmp_data['status']]
            tmp_data['job_name'] = tmp_job_info['name']

            data.append(tmp_data)

    sc = {
        'date_from': date_from,
        'date_to': date_to,
        'status': status
    }
    return UtilHelper.renderView("home/log/kill.html", {
        "list": data,
        "pages": pages,
        "sc": sc,
        "status_map": CommonConstant.common_status_map4,
    })


