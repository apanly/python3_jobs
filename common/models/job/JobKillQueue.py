# coding: utf-8
from application import db

class JobKillQueue(db.Model):
    __tablename__ = 'job_kill_queue'
    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer, nullable=False, index=True, server_default=db.FetchedValue(), info='job的id')
    server_id = db.Column(db.Integer, nullable=False, index=True, server_default=db.FetchedValue(), info='服务器id')
    status = db.Column(db.Integer, nullable=False, index=True, server_default=db.FetchedValue(), info='运行状态 -1：处理中 1：成功 0：失败')
    updated_time = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='最后一次更新时间')
    created_time = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='插入时间')

    def __init__(self, **items):
        for key in items:
            if hasattr(self, key):
                setattr(self, key, items[key])
        