# -*- coding: utf-8 -*-
from common.services.BaseService import BaseService


class CommonConstant(BaseService):
    '''
    这里存放常量，就是不随着环境变的参数
    '''

    # 分页显示最多页数
    PAGE_DISPLAY = 10

    # 分页显示每页大小
    PAGE_SIZE = 30

    ##默认json系统错误
    SYSTEM_DEFAULT_ERROR = "系统繁忙，请稍后再试~~"

    DEFAULT_DATE = "1970-01-01"
    DEFAULT_DATETIME = "1970-01-01 00:00:00"

    ## 如果使用cookie登录，可以用这个作为cookie的name，即学即码
    AUTH_COOKIE_NAME = "learn_master"

    special_char = "@@@"
    special_strike = "-"

    default_status_false = 0
    default_status_true = 1
    default_status_neg_99 = -99
    default_status_neg_1 = -1
    default_status_neg_2 = -2
    default_status_pos_2 = 2
    default_status_pos_3 = 3

    common_status_map = {
        1 : "正常",
        0 : "已删除"
    }

    common_status_map2 = {
        1: "可用",
        0: "禁用"
    }

    common_status_map3 = {
        1: "已读",
        0: "未读"
    }

    common_status_map4 = {
        1: "处理成功",
        0: "处理失败",
        -2 : "待处理"
    }

    link_type_map = {
        2: {
            "title": "系统",
            "class": "warning"
        },
        3: {
            "title": "工具",
            "class": "warning"
        },
        4: {
            "title": "媒体",
            "class": "primary"
        },
        5: {
            "title": "平台",
            "class": "success"
        },
        1: {
            "title": "其他",
            "class": "info"
        }
    }


    server_env_map = {
        1: "python",
        2: "php72"
    }

    job_type_map = {
        1: "周期性",
        2: "常驻",
        3: "一次性"
    }

    run_status_map = {
        1: "等待下次运行",
        2: "运行中",
        0: "不调度"
    }

    job_log_status_map = {
        -1: "运行中",
        0: "运行失败",
        1: "运行成功"
    }

