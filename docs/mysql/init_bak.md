### 数据库变更历史

```
CREATE DATABASE `learn_master` DEFAULT COLLATE = `utf8mb4_general_ci`;
use learn_master;
CREATE TABLE `action` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT '权限ID',
  `level1_name` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT '' COMMENT '一级菜单名称',
  `level2_name` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT '' COMMENT '二级菜单名称',
  `name` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT '' COMMENT '权限名',
  `url` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT '' COMMENT '允许访问的链接,用特殊字符分割',
  `level1_weight` tinyint NOT NULL DEFAULT '0' COMMENT '一级菜单权重',
  `level2_weight` tinyint NOT NULL DEFAULT '0' COMMENT '二级菜单权重',
  `weight` tinyint NOT NULL DEFAULT '0' COMMENT '权重 越大排名越前面',
  `is_important` tinyint(1) NOT NULL DEFAULT '0' COMMENT '是否是重要权限',
  `status` tinyint NOT NULL DEFAULT '1' COMMENT '1 有效 0无效',
  `updated_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '最后一次更新时间',
  `created_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '插入时间',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='权限表';




CREATE TABLE `app_access_log` (
  `id` int NOT NULL AUTO_INCREMENT,
  `uid` int NOT NULL DEFAULT '0' COMMENT '用户表id',
  `uname` varchar(20) COLLATE utf8mb4_general_ci NOT NULL DEFAULT '' COMMENT '用户表姓名',
  `referer_url` varchar(1000) COLLATE utf8mb4_general_ci NOT NULL DEFAULT '' COMMENT '当前访问的refer',
  `target_url` varchar(1000) COLLATE utf8mb4_general_ci NOT NULL DEFAULT '' COMMENT '访问的url',
  `query_params` varchar(1000) COLLATE utf8mb4_general_ci NOT NULL DEFAULT '' COMMENT 'get和post参数',
  `ua` varchar(1000) COLLATE utf8mb4_general_ci NOT NULL DEFAULT '' COMMENT '访问ua',
  `ip` varchar(32) COLLATE utf8mb4_general_ci NOT NULL DEFAULT '' COMMENT '访问ip',
  `note` varchar(1000) COLLATE utf8mb4_general_ci NOT NULL DEFAULT '' COMMENT 'json格式备注字段',
  `created_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '插入日期',
  PRIMARY KEY (`id`),
  KEY `idx_created_time` (`created_time`),
  KEY `idx_uid` (`uid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='用户访问日志记录表';




CREATE TABLE `app_err_log` (
  `id` int unsigned NOT NULL AUTO_INCREMENT,
  `request_uri` varchar(255) COLLATE utf8mb4_general_ci NOT NULL DEFAULT '' COMMENT '请求uri',
  `referer` varchar(500) COLLATE utf8mb4_general_ci NOT NULL DEFAULT '' COMMENT '来源url',
  `content` varchar(3000) COLLATE utf8mb4_general_ci NOT NULL DEFAULT '' COMMENT '日志内容',
  `ip` varchar(100) COLLATE utf8mb4_general_ci NOT NULL DEFAULT '' COMMENT 'ip',
  `ua` varchar(1000) COLLATE utf8mb4_general_ci NOT NULL DEFAULT '' COMMENT 'ua信息',
  `created_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '插入时间',
  PRIMARY KEY (`id`),
  KEY `idx_created_time` (`created_time`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='app错误日表';




CREATE TABLE `link` (
  `id` int unsigned NOT NULL AUTO_INCREMENT,
  `type` tinyint NOT NULL DEFAULT '0' COMMENT '类型',
  `title` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT '' COMMENT '标题',
  `url` varchar(300) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT '' COMMENT '网址',
  `weight` int NOT NULL DEFAULT '1' COMMENT '权重 越大越排前',
  `status` tinyint(1) NOT NULL DEFAULT '1' COMMENT '状态： 1：有效  0：无效',
  `updated_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '最后一次更新时间',
  `created_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '插入时间',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='网址管理';





CREATE TABLE `role` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT '角色ID',
  `name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT '' COMMENT '角色名',
  `pid` int NOT NULL DEFAULT '0' COMMENT '父级id',
  `status` tinyint NOT NULL DEFAULT '1' COMMENT '1有效 0无效',
  `updated_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '最后一次更新时间',
  `created_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '插入时间',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='角色部门表';




CREATE TABLE `role_action` (
  `id` int NOT NULL AUTO_INCREMENT COMMENT '角色权限ID',
  `role_id` int NOT NULL DEFAULT '0' COMMENT '角色ID',
  `action_id` int NOT NULL DEFAULT '0' COMMENT '权限ID',
  `status` tinyint NOT NULL DEFAULT '1' COMMENT '1有效 0无效',
  `updated_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '最后一次更新时间',
  `created_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '插入时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_role_action_id` (`role_id`,`action_id`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='角色权限表';



CREATE TABLE `user` (
  `id` int unsigned NOT NULL AUTO_INCREMENT,
  `name` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT '' COMMENT '用户名',
  `email` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT '' COMMENT '邮箱地址也是登录用户名',
  `role_id` int NOT NULL DEFAULT '0' COMMENT '人员所属部门',
  `salt` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT '' COMMENT '随机码',
  `is_root` tinyint(1) NOT NULL DEFAULT '0' COMMENT '是否是管理员 1：是 0：不是',
  `status` tinyint(1) NOT NULL DEFAULT '1' COMMENT '状态 1：有效 0：无效',
  `updated_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '最后一次更新时间',
  `created_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '插入时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_email` (`email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='用户表';




CREATE TABLE `user_news` (
  `id` int unsigned NOT NULL AUTO_INCREMENT COMMENT '消息id',
  `uid` int unsigned NOT NULL DEFAULT '0' COMMENT '用户id',
  `title` varchar(255) COLLATE utf8mb4_general_ci NOT NULL DEFAULT '' COMMENT '标题',
  `content` varchar(1500) COLLATE utf8mb4_general_ci NOT NULL DEFAULT '' COMMENT '内容',
  `status` tinyint unsigned NOT NULL DEFAULT '0' COMMENT '状态 0：未读 1：已读',
  `updated_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '更新时间',
  `created_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci ROW_FORMAT=DYNAMIC COMMENT='用户站内消息表';





```

#### 初始化数据
```
INSERT INTO `user` (`id`, `name`, `email`, `role_id`, `salt`, `is_root`, `status`, `updated_time`, `created_time`)
VALUES
	(1, '即学即码工作室', 'apanly@163.com', 0, 'HRD60OnSkN4dpCDH', 1, 1, '2020-08-23 14:41:11', '2018-05-16 23:50:43');

INSERT INTO `link` (`id`, `type`, `title`, `url`, `weight`, `status`, `updated_time`, `created_time`)
VALUES
	(1, 4, '今日头条媒体后台', 'https://ad.oceanengine.com/', 1, 1, '2020-08-18 14:31:23', '2020-08-18 14:31:23'),
	(2, 4, '百度媒体后台', 'http://www2.baidu.com/', 1, 1, '2020-08-18 14:31:43', '2020-08-18 14:31:43'),
	(3, 5, '媒体开户平台', 'http://1.hsh.cn/', 1, 1, '2020-08-18 14:32:14', '2020-08-18 14:32:14'),
	(4, 5, '联展平台', 'http://hsh.cn/', 1, 1, '2020-08-18 14:32:32', '2020-08-18 14:32:32'),
	(5, 3, '图片压缩工具，想想不到的压缩比', 'https://tinypng.com/', 1, 1, '2020-08-18 14:32:51', '2020-08-18 14:32:51'),
	(6, 3, '查域名解析IP', 'https://ip138.com/', 1, 1, '2020-08-18 14:33:18', '2020-08-18 14:33:18'),
	(7, 2, '联展、代维、财务、风控、资产等系统，全公司都在用', 'http://www.corp.hsh568.cn', 1, 1, '2020-08-18 14:33:41', '2020-08-18 14:33:41'),
	(8, 3, 'Gitea：代码版本管理工具，记录您好几吨的代码咧', 'http://git.corp.hsh568.cn/', 88, 1, '2020-08-18 15:06:29', '2020-08-18 14:34:01');


```
