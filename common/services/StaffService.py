# -*- coding: utf-8 -*-
import re
from common.services.BaseService import BaseService
from common.services.CommonConstant import CommonConstant
from common.models.rbac.User import ( User )



class StaffService( BaseService):
    @staticmethod
    def getRootStaffList():
        return User.query.filter_by( status = CommonConstant.default_status_true,is_root = CommonConstant.default_status_true ).all()






