# 任务计划 - 角色系统增强

## 目标
丰富角色系统：支持同一角色多人使用（如平民/忠臣/狼人），根据对局人数智能推荐角色配置。

## 阶段概览

| 阶段 | 内容 | 状态 |
|------|------|------|
| 1 | 数据库重构（is_unique + role_presets） | ✅ 完成 |
| 2 | 后端 API（获取角色预设、is_unique） | ✅ 完成 |
| 3 | 前端改造（duplicate角色不阻止、推荐面板） | ✅ 完成 |
| 4 | 验证测试 | ✅ 完成 |

---

## 阶段 1: 数据库重构 ✅

### 1.1 roles 表增加 is_unique 字段
- [x] 忠臣、村民、狼人、爪牙 等基础角色设置为非唯一 (is_unique=0)
- [x] 梅林、预言家等特殊角色保持唯一 (is_unique=1)

### 1.2 新增 role_presets 表
- [x] game_id, player_count, good_count, evil_count, config(JSON)
- [x] 预置阿瓦隆 5-10人配置
- [x] 预置狼人杀 8-12人配置

### 1.3 丰富角色库
- [x] 阿瓦隆: 增加湖中仙女、爪牙
- [x] 狼人杀: 增加白痴、骑士、混血儿、石像鬼、恶灵骑士、恶魔

---

## 阶段 2: 后端 API ✅
- [x] GET /api/games/{game_id}/role-presets?count=N
- [x] 角色 API 返回 is_unique 字段
- [x] 管理后台同步更新

## 阶段 3: 前端改造 ✅
- [x] assignRole 对非唯一角色不阻止重复
- [x] 人数>=5时显示"推荐角色"按钮
- [x] 推荐面板显示当前人数匹配的配置
- [x] "一键应用推荐"自动分配角色
- [x] 角色下拉菜单显示使用次数（×2）

## 阶段 4: 验证测试 ✅
- [x] 数据库结构验证通过
- [x] API 端点测试通过
- [x] 重复角色提交测试通过

---

## 遇到的错误
| 错误 | 解决方案 |
|------|---------|
| 无 | - |

## 修改文件
- database.py: roles 加 is_unique + role_presets 表 + 预设数据
- main.py: 新增 role-presets API + 角色查询含 is_unique
- templates/record.html: 重复角色支持 + 推荐面板 + 一键应用
