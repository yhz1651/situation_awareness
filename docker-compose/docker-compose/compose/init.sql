

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

create DATABASE  IF NOT EXISTS hyperspectral;
use hyperspectral;


DROP TABLE IF EXISTS `x_dict`;
CREATE TABLE `x_dict`  (
  `id` bigint(20) UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键',
  `code` varchar(40) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL COMMENT '标识',
  `label` varchar(50) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL COMMENT '标签',
  `value` varchar(150) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL COMMENT '值',
  `active` bit(1) NOT NULL DEFAULT b'1' COMMENT '启用',
  `editable` bit(1) NOT NULL DEFAULT b'1' COMMENT '可编辑',
  `gmt_create` datetime NOT NULL COMMENT '创建时间',
  `gmt_modified` datetime NOT NULL COMMENT '修改时间',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `UK_X_DICT_CODE_LABEL`(`code`, `label`) USING BTREE,
  UNIQUE INDEX `UK_X_DICT_CODE_VALUE`(`code`, `value`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8 COLLATE = utf8_general_ci COMMENT = '字典表' ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of x_dict
-- ----------------------------

-- ----------------------------
-- Table structure for x_menu
-- ----------------------------
DROP TABLE IF EXISTS `x_menu`;
CREATE TABLE `x_menu`  (
  `id` bigint(20) UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键',
  `pid` bigint(20) NOT NULL DEFAULT 0 COMMENT '父ID',
  `name` varchar(20) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL COMMENT '名称',
  `type` tinyint(1) NOT NULL COMMENT '类型（0：目录；1：页面；2：按钮）',
  `sort` int(11) NOT NULL DEFAULT 0 COMMENT '排序值',
  `component` varchar(200) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL COMMENT '组件名称',
  `description` varchar(200) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL COMMENT '描述',
  `icon` varchar(200) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL COMMENT '图标',
  `perms` varchar(200) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL COMMENT '权限标识',
  `url` varchar(200) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL COMMENT '请求地址',
  `active` bit(1) NOT NULL DEFAULT b'1' COMMENT '启用',
  `gmt_create` datetime NOT NULL COMMENT '创建时间',
  `gmt_modified` datetime NOT NULL COMMENT '修改时间',
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 19 CHARACTER SET = utf8 COLLATE = utf8_general_ci COMMENT = '菜单表' ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of x_menu
-- ----------------------------
INSERT INTO `x_menu` VALUES (1, 0, '基础信息管理', 0, 0, 'Layout', '基础信息管理', 'list', NULL, '/base', b'1', '2019-12-22 01:04:57', '2019-12-29 04:21:24');
INSERT INTO `x_menu` VALUES (2, 1, '用户管理', 1, 0, 'User', '用户管理', '', 'sys:user', '/user', b'1', '2019-12-22 01:05:36', '2020-01-01 12:52:57');
INSERT INTO `x_menu` VALUES (3, 2, '增加', 2, 0, NULL, '用户管理-增加', NULL, 'sys:user:add', NULL, b'1', '2019-12-26 05:09:05', '2020-01-01 12:53:02');
INSERT INTO `x_menu` VALUES (4, 2, '删除', 2, 2, NULL, '用户管理-删除', NULL, 'sys:user:delete', NULL, b'1', '2019-12-26 05:09:08', '2019-12-26 05:09:10');
INSERT INTO `x_menu` VALUES (5, 2, '修改', 2, 0, NULL, '用户管理-修改', NULL, 'sys:user:update', NULL, b'1', '2019-12-26 05:09:14', '2019-12-26 05:09:15');
INSERT INTO `x_menu` VALUES (6, 1, '角色管理', 1, 1, 'Role', '角色管理', '', 'sys:role', '/role', b'1', '2019-12-26 05:09:12', '2019-12-29 05:07:13');
INSERT INTO `x_menu` VALUES (7, 6, '增加', 2, 0, NULL, '角色管理-增加', NULL, 'sys:role:add', NULL, b'1', '2019-12-26 05:09:19', '2019-12-28 07:26:08');
INSERT INTO `x_menu` VALUES (8, 6, '删除', 2, 0, NULL, '角色管理-删除', NULL, 'sys:role:delete', NULL, b'1', '2019-12-26 05:09:20', '2019-12-26 05:09:22');
INSERT INTO `x_menu` VALUES (9, 6, '修改', 2, 0, NULL, '角色管理-修改', NULL, 'sys:role:update', NULL, b'1', '2019-12-26 05:09:25', '2020-01-11 16:55:32');
INSERT INTO `x_menu` VALUES (10, 6, '修改权限', 2, 0, NULL, '角色管理-修改权限', NULL, 'sys:role:perms', NULL, b'1', '2019-12-26 05:09:25', '2019-12-26 05:09:25');
INSERT INTO `x_menu` VALUES (11, 1, '节点管理', 1, 2, 'Menu', '菜单管理', '', 'sys:menu', '/menu', b'1', '2019-12-26 05:09:31', '2019-12-29 05:09:30');
INSERT INTO `x_menu` VALUES (12, 11, '增加', 2, 0, NULL, '菜单管理-增加', NULL, 'sys:menu:add', NULL, b'1', '2019-12-26 05:09:28', '2019-12-26 05:09:29');
INSERT INTO `x_menu` VALUES (13, 11, '删除', 2, 0, NULL, '菜单管理-删除', NULL, 'sys:menu:delete', NULL, b'1', '2019-12-26 05:09:34', '2019-12-26 05:09:36');
INSERT INTO `x_menu` VALUES (14, 11, '修改', 2, 0, NULL, '菜单管理-修改', NULL, 'sys:menu:update', NULL, b'1', '2019-12-26 05:09:37', '2019-12-26 05:09:39');
INSERT INTO `x_menu` VALUES (15, 1, '字典管理', 1, 0, 'Dict', '', '', 'sys:dict', '/dict', b'1', '2020-01-01 08:40:01', '2020-01-01 09:06:03');
INSERT INTO `x_menu` VALUES (16, 15, '增加', 2, 0, '', '字典管理-增加', '', 'sys:dict:add', '', b'1', '2020-01-01 08:41:23', '2020-01-01 08:41:23');
INSERT INTO `x_menu` VALUES (17, 15, '删除', 2, 0, '', '字典管理-删除', '', 'sys:dict:delete', '', b'1', '2020-01-01 08:41:45', '2020-01-01 08:41:45');
INSERT INTO `x_menu` VALUES (18, 15, '修改', 2, 0, '', '字典管理-修改', '', 'sys:dict:update', '', b'1', '2020-01-01 08:42:03', '2020-01-01 08:42:03');

-- ----------------------------
-- Table structure for x_role
-- ----------------------------
DROP TABLE IF EXISTS `x_role`;
CREATE TABLE `x_role`  (
  `id` bigint(20) UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键',
  `name` varchar(20) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL COMMENT '名称',
  `role` varchar(200) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL COMMENT '角色标识',
  `description` varchar(200) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL COMMENT '描述',
  `active` bit(1) NOT NULL DEFAULT b'1' COMMENT '启用',
  `gmt_create` datetime NOT NULL COMMENT '创建时间',
  `gmt_modified` datetime NOT NULL COMMENT '修改时间',
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 2 CHARACTER SET = utf8 COLLATE = utf8_general_ci COMMENT = '角色表' ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of x_role
-- ----------------------------
INSERT INTO `x_role` VALUES (1, 'admin', 'admin', '管理员', b'1', '2020-01-20 23:22:13', '2020-01-20 23:22:17');

-- ----------------------------
-- Table structure for x_role_menu
-- ----------------------------
DROP TABLE IF EXISTS `x_role_menu`;
CREATE TABLE `x_role_menu`  (
  `role_id` bigint(20) UNSIGNED NOT NULL COMMENT '角色ID',
  `menu_id` bigint(20) UNSIGNED NOT NULL COMMENT '菜单ID',
  INDEX `FK_X_ROLE_MENU_ROLE_ID`(`role_id`) USING BTREE,
  INDEX `FK_X_ROLE_MENU_MENU_ID`(`menu_id`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8 COLLATE = utf8_general_ci COMMENT = '角色菜单关联表' ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of x_role_menu
-- ----------------------------
INSERT INTO `x_role_menu` VALUES (1, 1);
INSERT INTO `x_role_menu` VALUES (1, 2);
INSERT INTO `x_role_menu` VALUES (1, 3);
INSERT INTO `x_role_menu` VALUES (1, 4);
INSERT INTO `x_role_menu` VALUES (1, 5);
INSERT INTO `x_role_menu` VALUES (1, 6);
INSERT INTO `x_role_menu` VALUES (1, 7);
INSERT INTO `x_role_menu` VALUES (1, 8);
INSERT INTO `x_role_menu` VALUES (1, 9);
INSERT INTO `x_role_menu` VALUES (1, 10);
INSERT INTO `x_role_menu` VALUES (1, 11);
INSERT INTO `x_role_menu` VALUES (1, 12);
INSERT INTO `x_role_menu` VALUES (1, 13);
INSERT INTO `x_role_menu` VALUES (1, 14);
INSERT INTO `x_role_menu` VALUES (1, 15);
INSERT INTO `x_role_menu` VALUES (1, 16);
INSERT INTO `x_role_menu` VALUES (1, 17);
INSERT INTO `x_role_menu` VALUES (1, 18);

-- ----------------------------
-- Table structure for x_situation
-- ----------------------------
DROP TABLE IF EXISTS `x_situation`;
CREATE TABLE `x_situation`  (
  `id` int(10) UNSIGNED NOT NULL AUTO_INCREMENT COMMENT 'id',
  `name` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL COMMENT '态势名称',
  `belong` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL COMMENT '态势归属',
  `description` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL COMMENT '态势描述',
  `file_address` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL COMMENT '态势文件地址',
  `classify_img` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL COMMENT '分类图地址',
  `temperature_img` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL COMMENT '温度图地址',
  `fire_img` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL COMMENT '火点异常图',
  `smoke_img` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL COMMENT '烟异常图',
  `target_img` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL COMMENT '目标识别图',
  `create_time` datetime NULL DEFAULT NULL COMMENT '创建时间',
  `update_time` datetime NULL DEFAULT NULL COMMENT '更新时间',
  `create_user` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL COMMENT '创建用户',
  `update_user` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL COMMENT '更新用户',
  `create_user_id` int(11) NULL DEFAULT NULL COMMENT '创建用户id',
  `deleted` int(11) NOT NULL DEFAULT 0 COMMENT '是否删除',
  `simulation_status` int(11) NULL DEFAULT 0 COMMENT '模拟数据状态(0未模拟1模拟中)',
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 31 CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of x_situation
-- ----------------------------
INSERT INTO `x_situation` VALUES (1, 'Frances Shaw', 'Zjv7AqwHJ1', '8XXgmQ4TaW', '639 The Pavilion, Lammas Field, Driftway', 'LSat7ZLxd8', '0fV5rWBx7H', 'XIBgSkx7X6', 'gCG86mMO2x', 'wJOCr2D7RP', '2017-11-17 14:41:44', '2007-09-17 17:22:32', 'admin', 'admin', 1, 0, 0);
INSERT INTO `x_situation` VALUES (2, 'Sugawara Shino', 'bsfFzymdpR', 'T5mnq2XMVr', '1-7-16 Omido, Higashiosaka', 'TPEev60Hg0', 'dGyiG68jtK', 'qylUdtxvzs', 'EiYXcsFs11', 'l0btbz5thp', '2008-02-04 19:47:35', '2001-03-05 06:10:48', 'admin', 'admin', 1, 0, 0);
INSERT INTO `x_situation` VALUES (3, 'Sherry Roberts', 'TonJcmfiwF', 'MSOOy7zQ9H', '2-3-10 Yoyogi, Shibuya-ku', 'j8bZguLAiG', 'JCrwgP44r4', 'BWnR2v69fU', 'bggHGXPlim', '5b82qzuU1H', '2007-03-29 01:01:06', '2022-05-23 03:06:44', 'admin', 'admin', 1, 0, 0);
INSERT INTO `x_situation` VALUES (4, 'Lam On Na', 'U2wJlhLdG2', 'uq1p1h2VWf', '988 Hinckley Rd', 'qxXjzDDknP', '2e6dtWqPvq', 'bvZveKmGbZ', 'EUPClDHQi3', 'pkUKolNhjK', '2004-10-27 00:08:32', '2018-07-26 18:48:51', 'admin', 'admin', 1, 0, 0);
INSERT INTO `x_situation` VALUES (5, 'Kinoshita Daisuke', '4PhSuvoAxR', 'i6NY9coUpo', '87 Ridgewood Road', 'zK06LT0diH', 'JLBUFT0vmc', 'miwobvsurX', 'H0hnA9DrI3', 'y5up5fRkIc', '2017-11-10 10:58:24', '2003-08-22 16:30:08', 'admin', 'admin', 1, 1, 0);
INSERT INTO `x_situation` VALUES (6, '我石广习之关', 'ea enim do commodo', '格近组并些立置计要级委即千组石。县参可片白写四要九低白内省六计参和。反你它青打展美更据目加快它求。', '江苏省那曲地区平罗县', 'http://dummyimage.com/400x400', 'http://dummyimage.com/400x400', 'http://dummyimage.com/400x400', 'http://dummyimage.com/400x400', 'http://dummyimage.com/400x400', NULL, NULL, NULL, NULL, NULL, 0, 0);
INSERT INTO `x_situation` VALUES (7, '我石广习之关id=7', 'ea enim do commodo', '格近组并些立置计要级委即千组石。县参可片白写四要九低白内省六计参和。反你它青打展美更据目加快它求。1', '江苏省那曲地区平罗县', 'http://dummyimage.com/400x400', 'http://dummyimage.com/400x400', 'http://dummyimage.com/400x400', 'http://dummyimage.com/400x400', 'http://dummyimage.com/400x400', NULL, '2024-07-01 14:15:43', NULL, 'admin', NULL, 0, 0);
INSERT INTO `x_situation` VALUES (8, '我石广习之关', 'ea enim do commodo', '格近组并些立置计要级委即千组石。县参可片白写四要九低白内省六计参和。反你它青打展美更据目加快它求。1', '江苏省那曲地区平罗县', 'http://dummyimage.com/400x400', 'http://dummyimage.com/400x400', 'http://dummyimage.com/400x400', 'http://dummyimage.com/400x400', 'http://dummyimage.com/400x400', NULL, NULL, NULL, NULL, NULL, 0, 0);
INSERT INTO `x_situation` VALUES (9, '我石广习之关333333', 'ea enim do commodo', '格近组并些立置计要级委即千组石。县参可片白写四要九低白内省六计参和。反你它青打展美更据目加快它求。1', '江苏省那曲地区平罗县', 'http://dummyimage.com/400x400', 'http://dummyimage.com/400x400', 'http://dummyimage.com/400x400', 'http://dummyimage.com/400x400', 'http://dummyimage.com/400x400', NULL, NULL, NULL, NULL, NULL, 0, 0);
INSERT INTO `x_situation` VALUES (10, '4444', 'ea enim do commodo', '格近组并些立置计要级委即千组石。县参可片白写四要九低白内省六计参和。反你它青打展美更据目加快它求。1', '江苏省那曲地区平罗县', 'http://dummyimage.com/400x400', 'http://dummyimage.com/400x400', 'http://dummyimage.com/400x400', 'http://dummyimage.com/400x400', 'http://dummyimage.com/400x400', NULL, NULL, NULL, NULL, NULL, 0, 0);
INSERT INTO `x_situation` VALUES (11, '4444', 'ea enim do commodo', '格近组并些立置计要级委即千组石。县参可片白写四要九低白内省六计参和。反你它青打展美更据目加快它求。1', '江苏省那曲地区平罗县', 'http://dummyimage.com/400x400', 'http://dummyimage.com/400x400', 'http://dummyimage.com/400x400', 'http://dummyimage.com/400x400', 'http://dummyimage.com/400x400', NULL, NULL, NULL, NULL, NULL, 0, 0);
INSERT INTO `x_situation` VALUES (12, '4444', 'ea enim do commodo', '格近组并些立置计要级委即千组石。县参可片白写四要九低白内省六计参和。反你它青打展美更据目加快它求。1', '江苏省那曲地区平罗县', 'http://dummyimage.com/400x400', 'http://dummyimage.com/400x400', 'http://dummyimage.com/400x400', 'http://dummyimage.com/400x400', 'http://dummyimage.com/400x400', NULL, NULL, NULL, NULL, NULL, 0, 0);
INSERT INTO `x_situation` VALUES (13, '4444', 'ea enim do commodo', '格近组并些立置计要级委即千组石。县参可片白写四要九低白内省六计参和。反你它青打展美更据目加快它求。1', '江苏省那曲地区平罗县', 'http://dummyimage.com/400x400', 'http://dummyimage.com/400x400', 'http://dummyimage.com/400x400', 'http://dummyimage.com/400x400', 'http://dummyimage.com/400x400', '2024-07-01 14:15:09', '2024-07-01 14:15:09', 'admin', 'admin', 1, 0, 0);
INSERT INTO `x_situation` VALUES (14, '哈哈哈', '88', '22222', '/temp/file/20240722/VrmlqVEDNAsOP_!!.json', NULL, NULL, NULL, NULL, NULL, '2024-07-22 10:12:19', '2024-07-22 10:12:19', 'admin', 'admin', 1, 0, 0);
INSERT INTO `x_situation` VALUES (15, 'new', '11', '111', '/temp/file/20240731/LrWmeagfsbPvl_!!.json', NULL, NULL, NULL, NULL, NULL, '2024-07-31 14:16:23', '2024-07-31 14:16:23', 'admin', 'admin', 1, 0, 0);
INSERT INTO `x_situation` VALUES (16, '9999', NULL, NULL, '/temp/file/20240801/VRWwFuwqAIGTf_!!.json', NULL, NULL, NULL, NULL, NULL, '2024-08-01 16:56:55', '2024-08-01 16:56:55', 'admin', 'admin', 1, 0, 0);
INSERT INTO `x_situation` VALUES (17, 'new1', '1', NULL, '/temp/file/20240801/VRwMFANSuliQq_!!.json', NULL, NULL, NULL, NULL, NULL, '2024-08-01 17:16:43', '2024-08-01 17:16:43', 'admin', 'admin', 1, 0, 0);
INSERT INTO `x_situation` VALUES (18, 'new2', NULL, NULL, '/temp/file/20240802/brwWPgPKacHCU_!!.json', NULL, NULL, NULL, NULL, NULL, '2024-08-02 10:16:52', '2024-08-02 10:16:52', 'admin', 'admin', 1, 0, 0);
INSERT INTO `x_situation` VALUES (19, 'new3', NULL, NULL, '/temp/file/20240805/VhMwidHwrlKEH_!!.json', NULL, NULL, NULL, NULL, NULL, '2024-08-05 13:54:33', '2024-08-05 13:54:33', 'admin', 'admin', 1, 0, 0);
INSERT INTO `x_situation` VALUES (20, 'new4', NULL, NULL, '/temp/file/20240814/lrcNQAnSQsEhp_!!.json', NULL, NULL, NULL, NULL, NULL, '2024-08-14 10:51:18', '2024-08-14 10:51:18', 'admin', 'admin', 1, 0, 0);
INSERT INTO `x_situation` VALUES (21, 'new5', NULL, NULL, '/temp/file/20240905/bHcFPlgnKgFio_!!.json', NULL, NULL, NULL, NULL, NULL, '2024-09-05 14:05:08', '2024-09-05 14:05:08', 'admin', 'admin', 1, 0, 0);
INSERT INTO `x_situation` VALUES (22, 'new6', NULL, NULL, '/temp/file/20240910/vHCFjDrOcdisG_!!.json', NULL, NULL, NULL, NULL, NULL, '2024-09-10 11:03:45', '2024-09-10 11:03:45', 'admin', 'admin', 1, 0, 0);
INSERT INTO `x_situation` VALUES (23, 'new6', NULL, NULL, '/temp/file/20240910/vHCFjDrOcdisG_!!.json', NULL, NULL, NULL, NULL, NULL, '2024-09-10 11:03:49', '2024-09-10 11:03:49', 'admin', 'admin', 1, 0, 0);
INSERT INTO `x_situation` VALUES (24, 'new6', NULL, NULL, '/temp/file/20240910/vHCFjDrOcdisG_!!.json', NULL, NULL, NULL, NULL, NULL, '2024-09-10 11:03:49', '2024-09-10 11:03:49', 'admin', 'admin', 1, 0, 0);
INSERT INTO `x_situation` VALUES (25, 'new6', NULL, NULL, '/temp/file/20240910/vHCFjDrOcdisG_!!.json', NULL, NULL, NULL, NULL, NULL, '2024-09-10 11:04:26', '2024-09-10 11:04:26', 'admin', 'admin', 1, 0, 0);
INSERT INTO `x_situation` VALUES (26, 'new6', NULL, NULL, '/temp/file/20240910/vHCFjDrOcdisG_!!.json', NULL, NULL, NULL, NULL, NULL, '2024-09-10 11:04:26', '2024-09-10 11:04:26', 'admin', 'admin', 1, 0, 0);
INSERT INTO `x_situation` VALUES (27, 'new6', NULL, NULL, '/temp/file/20240910/vHCFjDrOcdisG_!!.json', NULL, NULL, NULL, NULL, NULL, '2024-09-10 11:04:26', '2024-09-10 11:04:26', 'admin', 'admin', 1, 0, 0);
INSERT INTO `x_situation` VALUES (28, 'new6', NULL, NULL, '/temp/file/20240910/vHCFjDrOcdisG_!!.json', NULL, NULL, NULL, NULL, NULL, '2024-09-10 11:04:26', '2024-09-10 11:04:26', 'admin', 'admin', 1, 0, 0);
INSERT INTO `x_situation` VALUES (29, 'new6', NULL, NULL, '/temp/file/20240910/vHCFjDrOcdisG_!!.json', NULL, NULL, NULL, NULL, NULL, '2024-09-10 11:04:26', '2024-09-10 11:04:26', 'admin', 'admin', 1, 1, 0);
INSERT INTO `x_situation` VALUES (30, NULL, NULL, NULL, '/temp/file/20240910/BhWFjnRorVkfD_!!.json', NULL, NULL, NULL, NULL, NULL, '2024-09-10 11:04:32', '2024-09-10 11:04:32', 'admin', 'admin', 1, 1, 0);

-- ----------------------------
-- Table structure for x_user
-- ----------------------------
DROP TABLE IF EXISTS `x_user`;
CREATE TABLE `x_user`  (
  `id` bigint(20) UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键',
  `username` varchar(20) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL COMMENT '用户名',
  `password` varchar(32) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL COMMENT '密码',
  `phone` varchar(11) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL COMMENT '手机号',
  `real_name` varchar(20) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL COMMENT '真实姓名',
  `avatar` varchar(200) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL COMMENT '头像地址',
  `salty` int(11) NOT NULL COMMENT '盐值',
  `active` bit(1) NOT NULL DEFAULT b'1' COMMENT '启用',
  `deleted` bit(1) NOT NULL DEFAULT b'0' COMMENT '已删除',
  `gmt_create` datetime NOT NULL COMMENT '创建时间',
  `gmt_modified` datetime NOT NULL COMMENT '修改时间',
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 2 CHARACTER SET = utf8 COLLATE = utf8_general_ci COMMENT = '用户表' ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of x_user
-- ----------------------------
INSERT INTO `x_user` VALUES (1, 'admin', '81ab692038d219ecfd3939fb21e8e0e6', '18222222222', '开发者', '', 568959, b'1', b'0', '2020-01-10 18:01:34', '2020-01-10 18:01:36');

-- ----------------------------
-- Table structure for x_user_role
-- ----------------------------
DROP TABLE IF EXISTS `x_user_role`;
CREATE TABLE `x_user_role`  (
  `user_id` bigint(20) UNSIGNED NOT NULL COMMENT '用户ID',
  `role_id` bigint(20) UNSIGNED NOT NULL COMMENT '角色ID',
  INDEX `FK_X_USER_ROLE_ROLE_ID`(`role_id`) USING BTREE,
  INDEX `FK_X_USER_ROLE_USER_ID`(`user_id`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8 COLLATE = utf8_general_ci COMMENT = '用户角色关联表' ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of x_user_role
-- ----------------------------
INSERT INTO `x_user_role` VALUES (1, 1);

SET FOREIGN_KEY_CHECKS = 1;
