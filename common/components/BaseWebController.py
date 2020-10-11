# -*- coding: utf-8 -*-
from flask import render_template,jsonify,request

class BaseWebController:
    def isGet(self):
        return request.method == "GET"

    def isAjax( self ):
        '''
        request.is_xhr有bug ，因为Werkzeug版本问题
        需要Werkzeug==0.16.1，等后面官方修复了这个bug再用，自己学再判断算了
        '''
        if  hasattr(request,"is_xhr") and request.is_xhr:
            return True

        head_ajax = request.headers.get("X-Requested-With","")
        if head_ajax == "XMLHttpRequest":
            return True

        return False

    def renderJSON(self,msg = "操作成功~~",data = {},code = 200):
        resp = {'code': code, 'msg': msg, 'data': data}
        return jsonify(resp)

    def renderErrJSON(self,msg = "操作失败~~",data = {},code = -1):
        return self.renderJSON( msg = msg, data=data,code = code )


    def renderPopView(self,template, context = {}):
        content =  render_template(template, **context)
        return self.renderJSON( data = { "content":content } )

    def renderView(self,template, context = {}):
        return render_template(template, **context)

    def getCookie(self):
        pass

    def removeCookie(self):
        pass