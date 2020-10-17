# -*- coding: utf-8 -*-
from common.models.config.Sysconfig import Sysconfig
from common.services.BaseService import BaseService


class SysConfigService( BaseService):
    @staticmethod
    def getConfigByName( name = ''):
        ret = ''
        if not name:
            return ret

        info = Sysconfig.query.filter_by( k_field = name ).first()
        if info and info.status and info.k_val:
            ret = info.k_val
        return ret