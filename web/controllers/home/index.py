# -*- coding: utf-8 -*-
from flask import Blueprint, request
from common.components.helper.DateHelper import DateHelper
from common.components.helper.UtilHelper import UtilHelper
from common.models.job.JobAlertList import JobAlertList
from common.models.job.JobList import JobList
from common.models.job.JobServer import JobServer
from common.models.notice.UserNews import UserNews
from common.services.CommonConstant import CommonConstant
from common.services.CurrentUserService import CurrentUserService

route_home_index = Blueprint('home_index_page', __name__)


@route_home_index.route("/")
@route_home_index.route("/index")
def home_index():
    date = DateHelper.getCurrentTime(fmt="%Y-%m-%d")
    job_count = JobList.query.filter_by(is_del=CommonConstant.default_status_false).count()
    server_count = JobServer.query.filter_by(status=CommonConstant.default_status_true).count()
    alert_count = JobAlertList.query.filter(JobAlertList.created_time.between(date, date + " 23:59:59")).count()
    return UtilHelper.renderView("home/index/index.html", {
        "job_count": job_count,
        "server_count": server_count,
        "alert_count": alert_count
    })


@route_home_index.route("/release")
def home_release():
    release_list = [
        {
            "title": "V1.1 上线",
            "date": "2020-10-14",
            "content": "增加Job分类管理，每个Job需要所属组<br/>增加钉钉和企业微信报警配置"
        },
        {
            "title": "V1.0 上线",
            "date": "2020-10-03",
            "content": "Job管理调度平台 正式上线<br/>服务器管理、Job管理、Job工具、异常监控"
        },
        {
            "title": "V0.1",
            "date": "2020-10-01",
            "content": "基础功能（员工管理、RBAC、日志管理、站内信、网址之家等）基于个人开源Python3 CMS，详细前往： 网址"
        }
    ]
    return UtilHelper.renderView("home/index/release.html",{
        "list" : release_list,
        "count" : len( release_list )
    })


@route_home_index.route("/news")
def home_news():
    query = UserNews.query.filter_by(uid=CurrentUserService.getUid(), status=CommonConstant.default_status_false)
    total = query.count()
    list = query.order_by(UserNews.id.desc()).all()
    data = []
    if list:
        for item in list:
            tmp_content = "<h5 class='text-danger'>标题：%s</h5><br/>%s<br/>时间：%s" % (
            item.title, item.content, item.created_time)
            tmp_data = {
                "id": item.id,
                "title": item.title,
                "content": tmp_content,
                "created_time": DateHelper.getFormatDate(DateHelper.str2Date(item.created_time), format="%m-%d %H:%M"),
            }
            data.append(tmp_data)
    content = UtilHelper.renderView("home/index/news.html", {"list": data, "total": total})
    return UtilHelper.renderSucJSON({"total": total, "content": content})
