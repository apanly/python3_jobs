### 数据库变更历史
#### 2020-10-14 郭威
```
CREATE TABLE `job_server` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT '' COMMENT '服务器名字',
  `env` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT '' COMMENT '支持环境，逗号分割',
  `note` varchar(100) COLLATE utf8mb4_general_ci NOT NULL DEFAULT '' COMMENT '备注',
  `cpu_load` decimal(10,2) NOT NULL DEFAULT '0.00' COMMENT 'cpu load',
  `available_mem` decimal(10,2) NOT NULL DEFAULT '0.00' COMMENT '可用内存',
  `total_mem` decimal(10,2) NOT NULL DEFAULT '0.00' COMMENT '总内存数量',
  `weight` tinyint NOT NULL DEFAULT '1' COMMENT '权重',
  `status` tinyint NOT NULL DEFAULT '1' COMMENT '状态 1：有效 0：无效',
  `updated_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '最后一次更新时间',
  `created_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '插入时间',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='job服务器';

CREATE TABLE `job_list` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT '' COMMENT 'Job的名字',
  `env_id` int NOT NULL DEFAULT '0' COMMENT '环境id',
  `server_id` int NOT NULL DEFAULT '0' COMMENT '服务器id',
  `owner_uid` int NOT NULL DEFAULT '0' COMMENT '负责人uid',
  `relate_uid` int NOT NULL DEFAULT '0' COMMENT '相关人uid',
  `job_type` tinyint NOT NULL DEFAULT '0' COMMENT '类型 1：周期性 2：常驻 3：一次性',
  `command` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '命令',
  `next_run_time` int NOT NULL DEFAULT '0' COMMENT 'Job下一次运行时间',
  `run_interval` int NOT NULL COMMENT '运行间隔（每隔多久运行一次）单位分钟',
  `threshold_up` int NOT NULL DEFAULT '0' COMMENT 'job运行时长上限,单位秒',
  `threshold_down` int NOT NULL DEFAULT '0' COMMENT 'job运行时长下限,单位秒',
  `note` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT '' COMMENT 'Job描述',
  `max_mem` decimal(10,2) NOT NULL DEFAULT '0.00' COMMENT '使用的最大内存',
  `run_status` tinyint NOT NULL DEFAULT '0' COMMENT '运行状态：1 等待调度时间到来 2  运行中  0：不调度',
  `status` tinyint NOT NULL DEFAULT '0' COMMENT '是否需要调度 1：需要 0：不需要',
  `is_del` tinyint NOT NULL DEFAULT '0' COMMENT '删除否，1：删除 0：未删除',
  `updated_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '最后一次更新时间',
  `created_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '插入时间',
  PRIMARY KEY (`id`),
  KEY `idx_name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='Job列表';

CREATE TABLE `job_run_log` (
  `id` int NOT NULL AUTO_INCREMENT,
  `job_id` int NOT NULL COMMENT 'job的id',
  `server_id` int NOT NULL DEFAULT '0' COMMENT '服务器id',
  `server_name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT '' COMMENT '运行在哪台机器',
  `start_time` datetime NOT NULL DEFAULT '1970-01-01 00:00:00' COMMENT 'job开始运行时间',
  `end_time` datetime NOT NULL DEFAULT '1970-01-01 00:00:00' COMMENT 'job结束运行时间',
  `max_mem` decimal(10,2) NOT NULL DEFAULT '0.00' COMMENT '使用的最大内存',
  `status` tinyint NOT NULL DEFAULT '-1' COMMENT '运行状态 -1：运行中 1：成功 0：失败',
  `updated_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '最后一次更新时间',
  `created_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '插入时间',
  PRIMARY KEY (`id`),
  KEY `idx_created_time` (`created_time`),
  KEY `idx_job_id_created_time` (`job_id`,`created_time`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='job服务器';

CREATE TABLE `job_alert_list` (
  `id` int NOT NULL AUTO_INCREMENT,
  `job_id` int NOT NULL COMMENT 'job的id',
  `content` varchar(500) COLLATE utf8mb4_general_ci NOT NULL DEFAULT '' COMMENT '报警内容',
  `status` tinyint NOT NULL DEFAULT '-2' COMMENT '运行状态 -2：待处理 1：成功 0：失败',
  `updated_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '最后一次更新时间',
  `created_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '插入时间',
  PRIMARY KEY (`id`),
  KEY `idx_status` (`status`),
  KEY `idx_created_time` (`created_time`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='job报警列表';


CREATE TABLE `job_category` (
  `id` int unsigned NOT NULL AUTO_INCREMENT,
  `name` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT '' COMMENT '名称',
  `status` tinyint NOT NULL DEFAULT '1' COMMENT '状态 1：有效 0：无效',
  `updated_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '最后一次更新时间',
  `created_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '插入时间',
  PRIMARY KEY (`id`),
  KEY `idx_name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='job类型';

ALTER TABLE `job_list` ADD `cate_id` INT  NOT NULL  DEFAULT '0'  COMMENT '分类id'  AFTER `job_type`;

```

#### 2020-10-17 郭威
```
CREATE TABLE `sysconfig` (
  `id` int unsigned NOT NULL AUTO_INCREMENT,
  `name` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT '' COMMENT '配置描述',
  `tip` varchar(100) COLLATE utf8mb4_general_ci NOT NULL DEFAULT '',
  `k_field` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT '' COMMENT '配置名称key',
  `k_val` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT '' COMMENT '配置对应的值',
  `status` tinyint(1) NOT NULL DEFAULT '0' COMMENT '状态 1：有效 0：无效',
  `updated_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '最后一次更新时间',
  `created_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '插入时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `idx_k_field` (`k_field`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='系统配置';

INSERT INTO `sysconfig` (`id`, `name`, `tip`, `k_field`, `k_val`, `status`, `updated_time`, `created_time`)
VALUES
	(1, '钉钉', '请输入钉钉机器人的webhook地址', 'dingding', '', 0, '2020-10-17 12:46:22', '2020-10-17 11:51:02'),
	(2, '企业微信', '请输入企业机器人的webhook地址', 'wechat_work', '', 0, '2020-10-17 12:45:38', '2020-10-17 11:51:28');


```

#### 2020-11-01 郭威
```
CREATE TABLE `job_kill_queue` (
  `id` int NOT NULL AUTO_INCREMENT,
  `job_id` int NOT NULL DEFAULT '0' COMMENT 'job的id',
  `server_id` int NOT NULL DEFAULT '0' COMMENT '服务器id',
  `status` tinyint NOT NULL DEFAULT '-2' COMMENT '运行状态 -2：处理中 1：成功 0：失败',
  `updated_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '最后一次更新时间',
  `created_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '插入时间',
  PRIMARY KEY (`id`),
  KEY `idx_status` (`status`),
  KEY `idx_server_id` (`server_id`),
  KEY `idx_job_id` (`job_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='杀死job队列';
```

#### 2020-11-04 郭威
```
ALTER TABLE `job_list` ADD `command_kill` VARCHAR(255)  NOT NULL  DEFAULT ''  COMMENT '强制停止job的杀死命令'  AFTER `command`;
ALTER TABLE `job_list` ADD `job_level` TINYINT  NOT NULL  DEFAULT '1'  COMMENT '级别 1：一般 2：重要 3：紧急'  AFTER `job_type`;
```