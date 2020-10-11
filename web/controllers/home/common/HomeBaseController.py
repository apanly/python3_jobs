# -*- coding: utf-8 -*-
from common.components.BaseWebController import BaseWebController
from flask import render_template,g

class HomeBaseController( BaseWebController ):
    def renderView(self,template, context = {}):
        if 'current_user' in g:
            context['current_user'] = g.current_user

        if 'menus' in g:
            context['menus'] = g.menus
        return render_template(template, **context)