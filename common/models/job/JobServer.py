# coding: utf-8
from application import db

class JobServer(db.Model):
    __tablename__ = 'job_server'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50, 'utf8mb4_general_ci'), nullable=False, server_default=db.FetchedValue(), info='服务器名字')
    env = db.Column(db.String(100, 'utf8mb4_general_ci'), nullable=False, server_default=db.FetchedValue(), info='支持环境，逗号分割')
    note = db.Column(db.String(100, 'utf8mb4_general_ci'), nullable=False, server_default=db.FetchedValue(), info='备注')
    cpu_load = db.Column(db.Numeric(10, 2), nullable=False, server_default=db.FetchedValue(), info='cpu load')
    available_mem = db.Column(db.Numeric(10, 2), nullable=False, server_default=db.FetchedValue(), info='可用内存')
    total_mem = db.Column(db.Numeric(10, 2), nullable=False, server_default=db.FetchedValue(), info='总内存数量')
    weight = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue(), info='权重')
    status = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue(), info='状态 1：有效 0：无效')
    updated_time = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='最后一次更新时间')
    created_time = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='插入时间')

    def __init__(self, **items):
        for key in items:
            if hasattr(self, key):
                setattr(self, key, items[key])
        