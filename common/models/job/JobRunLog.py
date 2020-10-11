# coding: utf-8
from application import db

class JobRunLog(db.Model):
    __tablename__ = 'job_run_log'
    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer, nullable=False, info='job的id')
    server_id = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue(), info='服务器id')
    server_name = db.Column(db.String(100, 'utf8mb4_general_ci'), nullable=False, server_default=db.FetchedValue(), info='运行在哪台机器')
    start_time = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='job开始运行时间')
    end_time = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='job结束运行时间')
    max_mem = db.Column(db.Numeric(10, 2), nullable=False, server_default=db.FetchedValue(), info='使用的最大内存')
    status = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue(), info='运转状态 -1：运行中 0：成功 1：失败')
    updated_time = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='最后一次更新时间')
    created_time = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='插入时间')

    def __init__(self, **items):
        for key in items:
            if hasattr(self, key):
                setattr(self, key, items[key])
        