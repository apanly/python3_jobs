# coding: utf-8
from application import db

class JobList(db.Model):
    __tablename__ = 'job_list'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50, 'utf8mb4_general_ci'), nullable=False, index=True, server_default=db.FetchedValue(), info='Job的名字')
    env_id = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue(), info='环境id')
    server_id = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue(), info='服务器id')
    owner_uid = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue(), info='负责人uid')
    relate_uid = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue(), info='相关人uid')
    job_type = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue(), info='类型 1：周期性 2：常驻 3：一次性')
    job_level = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue(), info='级别 1：一般 2：重要 3：紧急')
    cate_id = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue(), info='分类id')
    command = db.Column(db.String(255, 'utf8mb4_general_ci'), nullable=False, server_default=db.FetchedValue(), info='运行命令')
    command_kill = db.Column(db.String(255, 'utf8mb4_general_ci'), nullable=False, server_default=db.FetchedValue(), info='强制停止job的杀死命令')
    next_run_time = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue(), info='Job下一次运行时间')
    run_interval = db.Column(db.Integer, nullable=False, info='运行间隔（每隔多久运行一次）单位分钟')
    threshold_up = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue(), info='job运行时长上限,单位秒')
    threshold_down = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue(), info='job运行时长下限,单位秒')
    note = db.Column(db.String(500, 'utf8mb4_general_ci'), nullable=False, server_default=db.FetchedValue(), info='Job描述')
    max_mem = db.Column(db.Numeric(10, 2), nullable=False, server_default=db.FetchedValue(), info='使用的最大内存')
    run_status = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue(), info='运行状态：1 等待调度时间到来 2  运行中  0：不调度')
    status = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue(), info='是否需要调度 1：需要 0：不需要')
    is_del = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue(), info='删除否，1：删除 0：未删除')
    updated_time = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='最后一次更新时间')
    created_time = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), info='插入时间')

    def __init__(self, **items):
        for key in items:
            if hasattr(self, key):
                setattr(self, key, items[key])
        