# -*- coding: utf-8 -*-
import time

from flask import Blueprint,request
from application import db
from common.components.helper.DateHelper import DateHelper
from common.components.helper.ModelHelper import ModelHelper
from common.components.helper.UtilHelper import UtilHelper
from common.models.job.JobAlertList import JobAlertList
from common.models.job.JobList import JobList
from common.models.job.JobRunLog import JobRunLog
from common.services.CommonConstant import CommonConstant

route_home_job_tools = Blueprint('home_job_tools_page', __name__)


@route_home_job_tools.route("/")
@route_home_job_tools.route("/index")
def tools_index():
    list = JobList.query.filter_by( run_status = CommonConstant.default_status_pos_2 ).order_by( JobList.id.desc() ).all()
    return UtilHelper.renderView("home/job/tools/index.html",{
        "list": list,
        "current":"index"
    })

@route_home_job_tools.route("/log")
def tools_log():
    status_map = CommonConstant.job_log_status_map

    req = request.values
    page = int(req.get("p", 1))
    date_from = req.get("date_from", DateHelper.getCurrentTime(fmt="%Y-%m-%d"))
    date_to = req.get("date_to", DateHelper.getCurrentTime(fmt="%Y-%m-%d"))
    status = int(req.get("status", CommonConstant.default_status_neg_99))
    job_id = int(req.get("job_id", CommonConstant.default_status_false) )

    query = JobRunLog.query.filter(JobRunLog.created_time.between(date_from, date_to + " 23:59:59"))

    if job_id:
        query = query.filter_by(job_id=job_id)

    if status > CommonConstant.default_status_neg_99:
        query = query.filter_by( status = status )

    page_params = {
        "total": query.count(),
        "page_size": CommonConstant.PAGE_SIZE,
        "page": page,
        "display": CommonConstant.PAGE_DISPLAY,
    }

    pages = UtilHelper.iPagination(page_params)
    offset = (page - 1) * CommonConstant.PAGE_SIZE
    limit = CommonConstant.PAGE_SIZE * page
    list = query.order_by(JobRunLog.id.desc())[offset:limit]
    data = []
    if list:
        job_ids = ModelHelper.getFieldList( list,"job_id" )
        job_map = ModelHelper.getDictFilterField( JobList , select_field = JobList.id, id_list = job_ids.sort() )
        for item in list:
            tmp_data = ModelHelper.model2Dict( item )
            tmp_job_info = ModelHelper.model2Dict( job_map.get(tmp_data['job_id']))
            tmp_data['status_desc'] = status_map[ tmp_data['status'] ]
            tmp_data['job_name'] = tmp_job_info['name']
            tmp_data['duration'] = ""
            if DateHelper.getCurrentTime( date = tmp_data['end_time'] ) == CommonConstant.DEFAULT_DATETIME:
                tmp_data['end_time'] = "未知"
                tmp_data['duration'] = time.time() - time.mktime( tmp_data['start_time'].timetuple() )
            else:
                tmp_data['duration'] = ( tmp_data['end_time'] - tmp_data['start_time'] ).seconds
            tmp_data['duration'] = DateHelper.formatBeautyTime( tmp_data['duration'])

            data.append(tmp_data)

    sc = {
        'date_from': date_from,
        'date_to': date_to,
        'status': status,
        'job_id': job_id
    }

    return UtilHelper.renderView("home/job/tools/log.html",{
        "list": data,
        "pages": pages,
        "sc": sc,
        "status_map": status_map,
        "current":"log"
    })


@route_home_job_tools.route("/alert")
def tools_alert():
    req = request.values
    page = int(req.get("p", 1))
    date_from = req.get("date_from", DateHelper.getCurrentTime(fmt="%Y-%m-%d"))
    date_to = req.get("date_to", DateHelper.getCurrentTime(fmt="%Y-%m-%d"))
    status = int(req.get("status", CommonConstant.default_status_neg_99))

    query = JobAlertList.query.filter(JobAlertList.created_time.between(date_from, date_to + " 23:59:59"))
    if status > CommonConstant.default_status_neg_99:
        query = query.filter_by( status = status )

    page_params = {
        "total": query.count(),
        "page_size": CommonConstant.PAGE_SIZE,
        "page": page,
        "display": CommonConstant.PAGE_DISPLAY,
    }

    pages = UtilHelper.iPagination(page_params)
    offset = (page - 1) * CommonConstant.PAGE_SIZE
    limit = CommonConstant.PAGE_SIZE * page
    list = query.order_by(JobAlertList.id.desc())[offset:limit]
    data = []
    if list:
        job_ids = ModelHelper.getFieldList( list,"job_id" )
        job_map = ModelHelper.getDictFilterField( JobList , select_field = JobList.id, id_list = job_ids.sort() )
        for item in list:
            tmp_data = ModelHelper.model2Dict( item )
            tmp_job_info = ModelHelper.model2Dict( job_map.get(tmp_data['job_id']))
            tmp_data['status_desc'] = CommonConstant.common_status_map4[ tmp_data['status'] ]
            tmp_data['job_name'] = tmp_job_info['name']

            data.append(tmp_data)

    sc = {
        'date_from': date_from,
        'date_to': date_to,
        'status': status
    }

    return UtilHelper.renderView("home/job/tools/alert.html",{
        "list": data,
        "pages": pages,
        "sc": sc,
        "status_map": CommonConstant.common_status_map4,
        "current":"alert"
    })


