# coding: utf-8
from application import db

class Sysconfig(db.Model):
    __tablename__ = 'sysconfig'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20, 'utf8mb4_general_ci'), nullable=False, server_default=db.FetchedValue(), info='配置描述')
    tip = db.Column(db.String(100, 'utf8mb4_general_ci'), nullable=False, server_default=db.FetchedValue())
    k_field = db.Column(db.String(20, 'utf8mb4_general_ci'), nullable=False, server_default=db.FetchedValue(), info='配置名称key')
    k_val = db.Column(db.String(500, 'utf8mb4_general_ci'), nullable=False, server_default=db.FetchedValue(), info='配置对应的值')
    status = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue(), info='状态 1：有效 0：无效')
    updated_time = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='最后一次更新时间')
    created_time = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='插入时间')

    def __init__(self, **items):
        for key in items:
            if hasattr(self, key):
                setattr(self, key, items[key])
        