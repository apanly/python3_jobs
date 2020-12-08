### jobs 业务表初始化
```
CREATE TABLE `job_server` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(50) NOT NULL DEFAULT '' COMMENT '服务器名字',
  `env` varchar(100) NOT NULL DEFAULT '' COMMENT '支持环境，逗号分割',
  `note` varchar(100) NOT NULL DEFAULT '' COMMENT '备注',
  `cpu_load` decimal(10,2) NOT NULL DEFAULT '0.00' COMMENT 'cpu load',
  `available_mem` decimal(10,2) NOT NULL DEFAULT '0.00' COMMENT '可用内存',
  `total_mem` decimal(10,2) NOT NULL DEFAULT '0.00' COMMENT '总内存数量',
  `weight` tinyint(4) NOT NULL DEFAULT '1' COMMENT '权重',
  `status` tinyint(4) NOT NULL DEFAULT '1' COMMENT '状态 1：有效 0：无效',
  `updated_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '最后一次更新时间',
  `created_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '插入时间',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='job服务器';

CREATE TABLE `job_category` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `name` varchar(20) NOT NULL DEFAULT '' COMMENT '名称',
  `status` tinyint(4) NOT NULL DEFAULT '1' COMMENT '状态 1：有效 0：无效',
  `updated_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '最后一次更新时间',
  `created_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '插入时间',
  PRIMARY KEY (`id`),
  KEY `idx_name` (`name`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='job类型';

CREATE TABLE `job_list` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(50) NOT NULL DEFAULT '' COMMENT 'Job的名字',
  `env_id` int(11) NOT NULL DEFAULT '0' COMMENT '环境id',
  `server_id` int(11) NOT NULL DEFAULT '0' COMMENT '服务器id',
  `owner_uid` int(11) NOT NULL DEFAULT '0' COMMENT '负责人uid',
  `relate_uid` int(11) NOT NULL DEFAULT '0' COMMENT '相关人uid',
  `job_type` tinyint(4) NOT NULL DEFAULT '0' COMMENT '类型 1：周期性 2：常驻 3：一次性',
  `job_level` tinyint(4) NOT NULL DEFAULT '1' COMMENT '级别 1：一般 2：重要 3：紧急',
  `cate_id` int(11) NOT NULL DEFAULT '0' COMMENT '分类id',
  `command` varchar(255) NOT NULL DEFAULT '' COMMENT '运行命令',
  `command_kill` varchar(255) NOT NULL DEFAULT '' COMMENT '强制停止job的杀死命令',
  `next_run_time` int(11) NOT NULL DEFAULT '0' COMMENT 'Job下一次运行时间',
  `run_interval` int(11) NOT NULL COMMENT '运行间隔（每隔多久运行一次）单位分钟',
  `threshold_up` int(11) NOT NULL DEFAULT '0' COMMENT 'job运行时长上限,单位秒',
  `threshold_down` int(11) NOT NULL DEFAULT '0' COMMENT 'job运行时长下限,单位秒',
  `note` varchar(500) NOT NULL DEFAULT '' COMMENT 'Job描述',
  `max_mem` decimal(10,2) NOT NULL DEFAULT '0.00' COMMENT '使用的最大内存',
  `run_status` tinyint(4) NOT NULL DEFAULT '0' COMMENT '运行状态：1 等待调度时间到来 2  运行中  0：不调度',
  `status` tinyint(4) NOT NULL DEFAULT '0' COMMENT '是否需要调度 1：需要 0：不需要',
  `is_del` tinyint(4) NOT NULL DEFAULT '0' COMMENT '删除否，1：删除 0：未删除',
  `updated_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '最后一次更新时间',
  `created_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '插入时间',
  PRIMARY KEY (`id`),
  KEY `idx_name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='Job列表';

CREATE TABLE `job_run_log` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `job_id` int(11) NOT NULL DEFAULT '0' COMMENT 'job的id',
  `server_id` int(11) NOT NULL DEFAULT '0' COMMENT '服务器id',
  `server_name` varchar(100) NOT NULL DEFAULT '' COMMENT '运行在哪台机器',
  `start_time` datetime NOT NULL DEFAULT '1970-01-01 00:00:00' COMMENT 'job开始运行时间',
  `end_time` datetime NOT NULL DEFAULT '1970-01-01 00:00:00' COMMENT 'job结束运行时间',
  `max_mem` decimal(10,2) NOT NULL DEFAULT '0.00' COMMENT '使用的最大内存',
  `status` tinyint(4) NOT NULL DEFAULT '-1' COMMENT '运行状态 -1：运行中 1：成功 0：失败',
  `updated_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '最后一次更新时间',
  `created_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '插入时间',
  PRIMARY KEY (`id`),
  KEY `idx_created_time` (`created_time`),
  KEY `idx_job_id_created_time` (`job_id`,`created_time`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='job运行日志';

CREATE TABLE `job_kill_queue` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `job_id` int(11) NOT NULL DEFAULT '0' COMMENT 'job的id',
  `server_id` int(11) NOT NULL DEFAULT '0' COMMENT '服务器id',
  `status` tinyint(4) NOT NULL DEFAULT '-2' COMMENT '运行状态 -2：处理中 1：成功 0：失败',
  `updated_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '最后一次更新时间',
  `created_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '插入时间',
  PRIMARY KEY (`id`),
  KEY `idx_status` (`status`),
  KEY `idx_server_id` (`server_id`),
  KEY `idx_job_id` (`job_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci  COMMENT='杀死job队列';


CREATE TABLE `sysconfig` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `name` varchar(20) NOT NULL DEFAULT '' COMMENT '配置描述',
  `tip` varchar(100) NOT NULL DEFAULT '',
  `k_field` varchar(20) NOT NULL DEFAULT '' COMMENT '配置名称key',
  `k_val` varchar(500) NOT NULL DEFAULT '' COMMENT '配置对应的值',
  `status` tinyint(1) NOT NULL DEFAULT '0' COMMENT '状态 1：有效 0：无效',
  `updated_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '最后一次更新时间',
  `created_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '插入时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `idx_k_field` (`k_field`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='系统配置';


### 数据初始化
INSERT INTO `sysconfig` (`id`, `name`, `tip`, `k_field`, `k_val`, `status`, `updated_time`, `created_time`)
VALUES
	(1, '钉钉', '请输入钉钉机器人的webhook地址', 'dingding', '', 0, '2020-10-17 12:46:22', '2020-10-17 11:51:02'),
	(2, '企业微信', '请输入企业机器人的webhook地址', 'wechat_work', '', 0, '2020-10-17 13:34:19', '2020-10-17 11:51:28');

```