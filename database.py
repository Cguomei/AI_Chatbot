import sqlite3
import os, sys

# 打包成 exe 后，数据库放在 exe 同目录下（可写），而非临时解压目录
if getattr(sys, 'frozen', False):
    _BASE_DIR = os.path.dirname(sys.executable)
else:
    _BASE_DIR = os.path.dirname(__file__)

DB_DIR = os.path.join(_BASE_DIR, "db")
DB_PATH = os.path.join(DB_DIR, "game.db")


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    os.makedirs(DB_DIR, exist_ok=True)
    conn = get_db()
    cursor = conn.cursor()

    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS players (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            avatar TEXT DEFAULT '🎮',
            elo_rating INTEGER DEFAULT 1000,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS games (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            good_win_score INTEGER DEFAULT 5,
            evil_win_score INTEGER DEFAULT 8,
            lose_penalty INTEGER DEFAULT 3,
            lose_mode TEXT DEFAULT 'keep_bonus',
            use_elo INTEGER DEFAULT 0,
            enable_roles INTEGER DEFAULT 1,
            enable_actions INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS roles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            game_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            team TEXT NOT NULL CHECK(team IN ('good', 'evil')),
            score_bonus INTEGER DEFAULT 0,
            is_unique INTEGER DEFAULT 1,
            FOREIGN KEY (game_id) REFERENCES games(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS role_presets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            game_id INTEGER NOT NULL,
            player_count INTEGER NOT NULL,
            good_count INTEGER NOT NULL,
            evil_count INTEGER NOT NULL,
            config TEXT NOT NULL,
            FOREIGN KEY (game_id) REFERENCES games(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS seasons (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            ended_at TIMESTAMP,
            is_active INTEGER DEFAULT 1
        );

        CREATE TABLE IF NOT EXISTS matches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            game_id INTEGER NOT NULL,
            winner TEXT NOT NULL CHECK(winner IN ('good', 'evil')),
            season_id INTEGER,
            played_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (game_id) REFERENCES games(id),
            FOREIGN KEY (season_id) REFERENCES seasons(id)
        );

        CREATE TABLE IF NOT EXISTS match_players (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            match_id INTEGER NOT NULL,
            player_id INTEGER NOT NULL,
            team TEXT NOT NULL CHECK(team IN ('good', 'evil')),
            role_id INTEGER,
            score_change INTEGER NOT NULL DEFAULT 0,
            elo_change INTEGER DEFAULT 0,
            FOREIGN KEY (match_id) REFERENCES matches(id) ON DELETE CASCADE,
            FOREIGN KEY (player_id) REFERENCES players(id),
            FOREIGN KEY (role_id) REFERENCES roles(id)
        );

        CREATE TABLE IF NOT EXISTS achievements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            icon TEXT DEFAULT '🏅',
            condition_type TEXT NOT NULL,
            condition_value INTEGER DEFAULT 1,
            is_preset INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS player_achievements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            player_id INTEGER NOT NULL,
            achievement_id INTEGER NOT NULL,
            earned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (player_id) REFERENCES players(id),
            FOREIGN KEY (achievement_id) REFERENCES achievements(id)
        );

        CREATE UNIQUE INDEX IF NOT EXISTS idx_player_achievement_unique
            ON player_achievements(player_id, achievement_id);

        CREATE TABLE IF NOT EXISTS admins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS game_presets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            game_id INTEGER NOT NULL,
            config TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (game_id) REFERENCES games(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS game_actions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            game_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            score_bonus INTEGER DEFAULT 0,
            is_preset INTEGER DEFAULT 0,
            FOREIGN KEY (game_id) REFERENCES games(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS match_player_actions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            match_id INTEGER NOT NULL,
            player_id INTEGER NOT NULL,
            action_id INTEGER NOT NULL,
            FOREIGN KEY (match_id) REFERENCES matches(id) ON DELETE CASCADE,
            FOREIGN KEY (player_id) REFERENCES players(id),
            FOREIGN KEY (action_id) REFERENCES game_actions(id)
        );
    """)

    # 数据库迁移：为旧数据库添加 lose_mode 列
    try:
        cursor.execute("ALTER TABLE games ADD COLUMN lose_mode TEXT DEFAULT 'keep_bonus'")
    except sqlite3.OperationalError:
        pass  # 列已存在

    # 预置管理员
    import hashlib
    cursor.execute("SELECT COUNT(*) FROM admins WHERE username = 'admin'")
    if cursor.fetchone()[0] == 0:
        pw = hashlib.sha256("admin123".encode()).hexdigest()
        cursor.execute("INSERT INTO admins (username, password_hash) VALUES (?, ?)", ("admin", pw))

    # 预置游戏
    preset_games = [
        ("阿瓦隆", 5, 8, 3, "keep_bonus", 0),
        ("狼人杀", 4, 7, 2, "keep_bonus", 0),
    ]
    for name, gs, es, lp, lm, ue in preset_games:
        cursor.execute("SELECT COUNT(*) FROM games WHERE name = ?", (name,))
        if cursor.fetchone()[0] == 0:
            cursor.execute(
                "INSERT INTO games (name, good_win_score, evil_win_score, lose_penalty, lose_mode, use_elo) VALUES (?, ?, ?, ?, ?, ?)",
                (name, gs, es, lp, lm, ue)
            )

    # 预置角色（根据游戏类型）
    cursor.execute("SELECT id, name FROM games")
    games_map = {r[1]: r[0] for r in cursor.fetchall()}

    preset_roles = {
        "阿瓦隆": [
            # (名称, 阵营, 加分, 是否唯一)
            ("梅林", "good", 3, 1), ("派西维尔", "good", 2, 1),
            ("忠臣", "good", 0, 0),        # 非唯一，允许多人
            ("湖中仙女", "good", 2, 1),
            ("莫甘娜", "evil", 3, 1), ("刺客", "evil", 5, 1),
            ("莫德雷德", "evil", 2, 1), ("奥伯伦", "evil", 1, 1),
            ("爪牙", "evil", 0, 0),          # 非唯一，充数坏人
        ],
        "狼人杀": [
            # (名称, 阵营, 加分, 是否唯一)
            ("预言家", "good", 2, 1), ("女巫", "good", 2, 1),
            ("猎人", "good", 2, 1), ("守卫", "good", 1, 1),
            ("白痴", "good", 1, 1), ("骑士", "good", 1, 1),
            ("村民", "good", 0, 0),        # 非唯一，允许多人
            ("混血儿", "good", 0, 1),
            ("狼人", "evil", 2, 0),        # 非唯一，允许多狼
            ("白狼王", "evil", 3, 1), ("狼美人", "evil", 2, 1),
            ("石像鬼", "evil", 2, 1), ("恶灵骑士", "evil", 2, 1),
            ("恶魔", "evil", 3, 1),
        ],
    }
    for game_name, roles in preset_roles.items():
        gid = games_map.get(game_name)
        if not gid:
            continue
        cursor.execute("SELECT COUNT(*) FROM roles WHERE game_id = ?", (gid,))
        if cursor.fetchone()[0] == 0:
            for rname, rteam, rbonus, runique in roles:
                cursor.execute(
                    "INSERT INTO roles (game_id, name, team, score_bonus, is_unique) VALUES (?, ?, ?, ?, ?)",
                    (gid, rname, rteam, rbonus, runique)
                )

    # 预置角色-人数配置推荐
    import json
    cursor.execute("SELECT COUNT(*) FROM role_presets")
    if cursor.fetchone()[0] == 0:
        # 阿瓦隆角色预设（按人数）
        avalon_presets = {
            5:  (3, 2, [("梅林",1),("派西维尔",1),("忠臣",1),("莫甘娜",1),("刺客",1)]),
            6:  (4, 2, [("梅林",1),("派西维尔",1),("忠臣",2),("莫甘娜",1),("刺客",1)]),
            7:  (4, 3, [("梅林",1),("派西维尔",1),("忠臣",2),("莫甘娜",1),("刺客",1),("莫德雷德",1)]),
            8:  (5, 3, [("梅林",1),("派西维尔",1),("忠臣",3),("莫甘娜",1),("刺客",1),("莫德雷德",1)]),
            9:  (6, 3, [("梅林",1),("派西维尔",1),("忠臣",4),("莫甘娜",1),("刺客",1),("莫德雷德",1)]),
            10: (6, 4, [("梅林",1),("派西维尔",1),("忠臣",4),("莫甘娜",1),("刺客",1),("莫德雷德",1),("奥伯伦",1)]),
        }
        for count, (gc, ec, config) in avalon_presets.items():
            cursor.execute(
                "INSERT INTO role_presets (game_id, player_count, good_count, evil_count, config) VALUES (?, ?, ?, ?, ?)",
                (games_map["阿瓦隆"], count, gc, ec, json.dumps(config, ensure_ascii=False))
            )

        # 狼人杀角色预设（按人数）- 标准预言家女巫猎人+
        # 8-10人：基础板，无守卫（小局加守卫好人太强）
        # 11-12人：预女猎守标准板
        # 13-14人：标准板+白痴/骑士+石像鬼（多1个神+功能狼）
        # 15-16人：大板，加白狼王/恶灵骑士等花板子
        werewolf_presets = {
            8:  (5, 3, [("预言家",1),("女巫",1),("猎人",1),("村民",2),("狼人",3)]),
            9:  (6, 3, [("预言家",1),("女巫",1),("猎人",1),("村民",3),("狼人",3)]),
            10: (7, 3, [("预言家",1),("女巫",1),("猎人",1),("守卫",1),("村民",3),("狼人",3)]),
            11: (7, 4, [("预言家",1),("女巫",1),("猎人",1),("守卫",1),("村民",3),("狼人",4)]),
            12: (8, 4, [("预言家",1),("女巫",1),("猎人",1),("守卫",1),("村民",4),("狼人",4)]),
            13: (9, 4, [("预言家",1),("女巫",1),("猎人",1),("守卫",1),("白痴",1),("村民",4),("狼人",3),("石像鬼",1)]),
            14: (10,4, [("预言家",1),("女巫",1),("猎人",1),("守卫",1),("白痴",1),("骑士",1),("村民",4),("狼人",3),("石像鬼",1)]),
            15: (10,5, [("预言家",1),("女巫",1),("猎人",1),("守卫",1),("白痴",1),("村民",5),("狼人",4),("白狼王",1)]),
            16: (11,5, [("预言家",1),("女巫",1),("猎人",1),("守卫",1),("白痴",1),("骑士",1),("村民",5),("狼人",4),("石像鬼",1)]),
        }
        for count, (gc, ec, config) in werewolf_presets.items():
            cursor.execute(
                "INSERT INTO role_presets (game_id, player_count, good_count, evil_count, config) VALUES (?, ?, ?, ?, ?)",
                (games_map["狼人杀"], count, gc, ec, json.dumps(config, ensure_ascii=False))
            )

    # 预置默认赛季
    cursor.execute("SELECT COUNT(*) FROM seasons")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO seasons (name, is_active) VALUES (?, 1)", ("默认赛季",))

    # 预置成就
    preset_achievements = [
        ("初出茅庐", "完成第1场对局", "🎮", "total_matches", 1, 1),
        ("百战老兵", "完成50场对局", "⚔️", "total_matches", 50, 1),
        ("百场战神", "完成100场对局", "👑", "total_matches", 100, 1),
        ("连胜达人", "连胜5场", "🔥", "consecutive_wins", 5, 1),
        ("不败传说", "连胜10场", "💎", "consecutive_wins", 10, 1),
        ("卧底之王", "扮演坏人胜率达到70%", "🕵️", "evil_win_rate", 70, 1),
        ("正义使者", "扮演好人胜率达到70%", "🛡️", "good_win_rate", 70, 1),
        ("积分破千", "ELO积分超过1200", "📈", "elo_rating", 1200, 1),
        ("大师段位", "ELO积分超过1400", "🏆", "elo_rating", 1400, 1),
    ]
    for name, desc, icon, ctype, cval, isp in preset_achievements:
        cursor.execute("SELECT COUNT(*) FROM achievements WHERE name = ?", (name,))
        if cursor.fetchone()[0] == 0:
            cursor.execute(
                "INSERT INTO achievements (name, description, icon, condition_type, condition_value, is_preset) VALUES (?, ?, ?, ?, ?, ?)",
                (name, desc, icon, ctype, cval, isp)
            )

    # 预置特殊事件/操作加分
    preset_actions = {
        "阿瓦隆": [
            ("刺杀梅林成功", 5), ("三连任务失败", 3),
        ],
        "狼人杀": [
            ("盲杀预言家", 4), ("首夜救人成功", 3), ("自刀骗药", 3), ("抗推好人", 2),
        ],
    }
    for game_name, actions in preset_actions.items():
        gid = games_map.get(game_name)
        if not gid:
            continue
        cursor.execute("SELECT COUNT(*) FROM game_actions WHERE game_id = ?", (gid,))
        if cursor.fetchone()[0] == 0:
            for aname, abonus in actions:
                cursor.execute(
                    "INSERT INTO game_actions (game_id, name, score_bonus, is_preset) VALUES (?, ?, ?, 1)",
                    (gid, aname, abonus)
                )

    # 迁移已有数据库：添加可能缺失的列
    try:
        cursor.execute("ALTER TABLE games ADD COLUMN enable_roles INTEGER DEFAULT 1")
    except:
        pass
    try:
        cursor.execute("ALTER TABLE games ADD COLUMN enable_actions INTEGER DEFAULT 1")
    except:
        pass
    try:
        cursor.execute("ALTER TABLE achievements ADD COLUMN game_id INTEGER REFERENCES games(id)")
    except:
        pass
    try:
        cursor.execute("ALTER TABLE achievements ADD COLUMN role_id INTEGER REFERENCES roles(id)")
    except:
        pass
    try:
        cursor.execute("ALTER TABLE matches ADD COLUMN notes TEXT DEFAULT ''")
    except:
        pass
    try:
        cursor.execute("ALTER TABLE roles ADD COLUMN is_unique INTEGER DEFAULT 1")
    except:
        pass
    # 为已有数据库添加成就唯一约束，防止重复
    try:
        cursor.execute("""
            CREATE UNIQUE INDEX IF NOT EXISTS idx_player_achievement_unique
                ON player_achievements(player_id, achievement_id)
        """)
    except:
        pass
    # 创建 role_presets 表（如果不存在）
    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS role_presets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                game_id INTEGER NOT NULL,
                player_count INTEGER NOT NULL,
                good_count INTEGER NOT NULL,
                evil_count INTEGER NOT NULL,
                config TEXT NOT NULL,
                FOREIGN KEY (game_id) REFERENCES games(id) ON DELETE CASCADE
            )
        """)
    except:
        pass
    # 对于已有的旧角色，标记非唯一角色
    try:
        cursor.execute("UPDATE roles SET is_unique = 0 WHERE name IN ('忠臣', '村民', '狼人', '爪牙') AND is_unique = 1")
    except:
        pass

    # 迁移：已有数据库补充狼人杀13-16人预设
    try:
        import json as _json
        ww_gid = games_map.get("狼人杀")
        if ww_gid:
            _extended_presets = {
                13: (9, 4, [("预言家",1),("女巫",1),("猎人",1),("守卫",1),("白痴",1),("村民",4),("狼人",3),("石像鬼",1)]),
                14: (10,4, [("预言家",1),("女巫",1),("猎人",1),("守卫",1),("白痴",1),("骑士",1),("村民",4),("狼人",3),("石像鬼",1)]),
                15: (10,5, [("预言家",1),("女巫",1),("猎人",1),("守卫",1),("白痴",1),("村民",5),("狼人",4),("白狼王",1)]),
                16: (11,5, [("预言家",1),("女巫",1),("猎人",1),("守卫",1),("白痴",1),("骑士",1),("村民",5),("狼人",4),("石像鬼",1)]),
            }
            for _count, (_gc, _ec, _config) in _extended_presets.items():
                cursor.execute(
                    "INSERT OR IGNORE INTO role_presets (game_id, player_count, good_count, evil_count, config) VALUES (?, ?, ?, ?, ?)",
                    (ww_gid, _count, _gc, _ec, _json.dumps(_config, ensure_ascii=False))
                )
    except:
        pass

    # 默认设置
    cursor.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('enable_achievements', '1')")
    cursor.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('enable_balance', '1')")
    cursor.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('enable_seasons', '1')")

    conn.commit()
    conn.close()
