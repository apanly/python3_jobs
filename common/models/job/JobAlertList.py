# coding: utf-8
from application import db

class JobAlertList(db.Model):
    __tablename__ = 'job_alert_list'
    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer, nullable=False, info='job的id')
    content = db.Column(db.String(500, 'utf8mb4_general_ci'), nullable=False, server_default=db.FetchedValue(), info='报警内容')
    status = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue(), info='运行状态 -2：待处理 1：成功 0：失败')
    updated_time = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='最后一次更新时间')
    created_time = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='插入时间')

    def __init__(self, **items):
        for key in items:
            if hasattr(self, key):
                setattr(self, key, items[key])
        