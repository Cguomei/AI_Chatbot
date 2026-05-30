# 桌游战绩记录与排名系统 — 设计文档

**日期**: 2026-05-27  
**版本**: 1.0

---

## 1. 产品定位

一款专为阿瓦隆、狼人杀等阵营对抗类桌游设计的战绩记录与排名系统。网页形式，手机/电脑自适应，小组内成员可随时记录胜负、查看排名。

---

## 2. 技术架构

| 层级 | 技术选型 | 说明 |
|------|---------|------|
| 后端框架 | **FastAPI** | 性能好，自带 API 文档 |
| 前端 | **Jinja2 模板 + 响应式 CSS** | 服务端渲染，无需前端框架 |
| 数据库 | **SQLite** | 单文件，零配置，足够小组使用 |
| 空间模型 | **全局空间** | 初期一个空间，后续可扩展多小组 |
| 管理员 | **Session 认证** | 管理员账号密码登录 |

### 项目结构

```
game/
├── main.py              # FastAPI 入口
├── requirements.txt     # 依赖
├── database.py          # SQLite 连接与初始化
├── models.py            # 数据模型
├── routers/
│   ├── pages.py         # 页面路由（Jinja2 渲染）
│   ├── api_matches.py   # 对局 API
│   ├── api_games.py     # 游戏管理 API
│   ├── api_players.py   # 玩家管理 API
│   └── auth.py          # 管理员登录
├── templates/           # Jinja2 模板
│   ├── base.html        # 基础布局（导航、响应式）
│   ├── index.html       # 首页排行榜
│   ├── record.html      # 记录对局
│   ├── player.html      # 个人战绩详情
│   ├── admin.html       # 管理后台
│   ├── games.html       # 游戏管理
│   └── login.html       # 管理员登录
├── static/
│   └── style.css        # 响应式样式
└── db/
    └── game.db          # SQLite 数据库文件
```

---

## 3. 数据模型

### players（玩家表）
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER PK | 自增主键 |
| name | TEXT NOT NULL | 昵称，唯一 |
| avatar | TEXT | 头像 emoji，默认 🎮 |
| created_at | TIMESTAMP | 创建时间 |

### games（游戏表）
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER PK | 自增主键 |
| name | TEXT NOT NULL | 游戏名称 |
| good_win_score | INTEGER | 好人赢得分（默认 +5） |
| evil_win_score | INTEGER | 坏人赢得分（默认 +8） |
| lose_penalty | INTEGER | 输方扣分（默认 -3，0 表示不扣） |
| created_at | TIMESTAMP | 创建时间 |

### matches（对局表）
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER PK | 自增主键 |
| game_id | INTEGER FK | 关联游戏 |
| winner | TEXT | 'good' 或 'evil' |
| played_at | TIMESTAMP | 对局时间 |
| created_by | TEXT | 记录者（可选） |

### match_players（对局参与表）
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER PK | 自增主键 |
| match_id | INTEGER FK | 关联对局 |
| player_id | INTEGER FK | 关联玩家 |
| team | TEXT | 'good' 或 'evil' |
| score_change | INTEGER | 本局得分变化 |

### admins（管理员表）
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER PK | 自增主键 |
| username | TEXT UNIQUE | 用户名 |
| password_hash | TEXT | 密码哈希 |

---

## 4. 核心功能流程

### 4.1 记录对局（三步流程）

```
第1步：选择游戏（下拉菜单，显示当前计分规则）
    ↓
第2步：选玩家 → 分配阵营（点击切换好人/坏人，至少 2 人）
    ↓
第3步：选择获胜阵营 → 自动计算每人得分 → 确认保存
```

**计分规则**：
- 获胜阵营玩家：好人 +good_win_score / 坏人 +evil_win_score
- 失败阵营玩家：-lose_penalty（如果配置了扣分）
- 得分实时预览，确认后写入 match_players

### 4.2 排名计算

- **总积分** = SUM(所有 match_players.score_change)
- **胜率** = 获胜局数 / 总局数
- **按游戏筛选**：只统计该游戏下的对局
- **阵营统计**：分别在好人/坏人阵营的次数、胜率、平均分

### 4.3 管理后台

- **游戏管理**：新建/编辑游戏计分规则
- **玩家管理**：添加/删除玩家
- **对局管理**：查看历史对局列表，可删除错误记录
- 以上操作均需管理员登录

---

## 5. 页面路由

| 路径 | 页面 | 权限 |
|------|------|------|
| `/` | 首页排行榜 | 公开 |
| `/record` | 记录对局 | 公开 |
| `/player/{id}` | 个人战绩详情 | 公开 |
| `/admin` | 管理后台主页 | 管理员 |
| `/admin/games` | 游戏管理 | 管理员 |
| `/admin/login` | 管理员登录 | 公开 |

### 6. API 端点

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/rankings` | 获取排行榜（支持 ?game_id 筛选） |
| POST | `/api/matches` | 创建对局 |
| DELETE | `/api/matches/{id}` | 删除对局（管理员） |
| GET/POST | `/api/players` | 玩家列表 / 创建玩家 |
| GET | `/api/players/{id}` | 玩家详情与统计 |
| GET/POST/PUT | `/api/games` | 游戏 CRUD |
| POST | `/api/auth/login` | 管理员登录 |
| POST | `/api/auth/logout` | 管理员登出 |

---

## 7. UI 设计

- **首页**：顶部统计卡片 + 排行榜表格 + 游戏筛选下拉
- **记录对局**：三步卡片式流程，适合手机操作
- **管理后台**：分 Tab 管理游戏、玩家、对局
- **个人详情**：积分 + 阵营胜率分开展示
- **响应式**：CSS 媒体查询适配手机/平板/电脑
- **管理员入口**：页面底部小字链接，不打扰普通用户

---

## 8. 待定/后续扩展

- [ ] 多小组独立空间
- [ ] 对局详细结算页（谁好谁坏一目了然）
- [ ] 历史趋势图表
- [ ] 数据导出功能

---

## 9. 初始数据

系统首次启动时自动创建管理员账号 `admin` / `admin123`，并预置游戏「阿瓦隆」（好人+5 / 坏人+8 / 输-3）和「狼人杀」（好人+4 / 坏人+7 / 输-2）。
