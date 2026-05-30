"""
综合测试脚本：稳定性 / 性能 / 数据完整性
使用方法: python test_comprehensive.py [--quick]
  --quick  只跑基础功能测试（不生成大量数据）
"""
import sys
import time
import random
import os
import shutil
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.stdout.reconfigure(encoding='utf-8')

# ========== 环境准备 ==========
DB_PATH = os.path.join(os.path.dirname(__file__), "db", "game.db")
DB_BACKUP = os.path.join(os.path.dirname(__file__), "db", "game_backup.db")

# 备份原数据库
if os.path.exists(DB_PATH):
    shutil.copy(DB_PATH, DB_BACKUP)
    print("[SETUP] 已备份原数据库")

if os.path.exists(DB_PATH):
    os.remove(DB_PATH)
    print("[SETUP] 已删除旧数据库")

import database
database.init_db()
print("[SETUP] 数据库初始化完成")

from fastapi.testclient import TestClient
from main import app

# TestClient 自动维护 cookie jar，登录后所有请求自动带 session
client = TestClient(app)

passed = 0
failed = 0
warnings = 0

def check(name, condition, detail=""):
    global passed, failed
    if condition:
        passed += 1
        print(f"  [PASS] {name}")
    else:
        failed += 1
        print(f"  [FAIL] {name}  {detail}")

def warn(msg):
    global warnings
    warnings += 1
    print(f"  [WARN] {msg}")

def timing(name, func, *args, **kwargs):
    start = time.perf_counter()
    result = func(*args, **kwargs)
    elapsed = time.perf_counter() - start
    return result, elapsed


# ========== 管理员登录 ==========
print("\n" + "=" * 60)
print("  管理员登录")
print("=" * 60)

r, t = timing("管理员登录", lambda: client.post("/api/auth/login",
    data={"username": "admin", "password": "admin123"}))
check("管理员登录成功", r.status_code in (200, 302), f"返回{r.status_code}")
check("登录耗时 < 0.1s", t < 0.1, f"{t:.4f}s")

r2 = client.get("/admin")
check("登录后可访问管理后台", r2.status_code == 200, f"返回{r2.status_code}")


# ============================================================
# 第1部分：基础功能测试
# ============================================================
print("\n" + "=" * 60)
print("  第1部分：基础功能测试")
print("=" * 60)

# 1.1 页面
for page in ["/", "/record"]:
    r, t = timing(f"访问 {page}", lambda p=page: client.get(p))
    check(f"页面 {page} 返回200", r.status_code == 200, str(r.status_code))

# 1.2 创建玩家
player_ids = []
for i in range(20):
    r = client.post("/api/players", json={"name": f"测试玩家{i+1:02d}"})
    if r.status_code == 200:
        pid = r.json().get("id")
        if pid:
            player_ids.append(pid)
check("创建20名玩家", len(player_ids) == 20, f"实际创建{len(player_ids)}名")

# 1.3 创建游戏
r = client.post("/api/games", json={
    "name": "测试游戏A", "good_count": 4, "evil_count": 2, "elo_enabled": False
})
check("创建游戏A", r.status_code == 200, f"返回{r.status_code}")
game_a_id = r.json().get("id") if r.status_code == 200 else None

r = client.post("/api/games", json={
    "name": "测试游戏B(ELO)", "good_count": 5, "evil_count": 3, "elo_enabled": True
})
check("创建ELO游戏B", r.status_code == 200, f"返回{r.status_code}")
game_b_id = r.json().get("id") if r.status_code == 200 else None

# 1.4 创建角色
role_ids = []
if game_a_id:
    for name, team in [("战士", "good"), ("法师", "good"), ("牧师", "good"),
                        ("盗贼", "evil"), ("刺客", "evil")]:
        r = client.post("/api/roles", json={"game_id": game_a_id, "name": name, "team": team})
        check(f"创建角色 {name}", r.status_code == 200, f"返回{r.status_code}")
        if r.status_code == 200:
            rid = r.json().get("id")
            if rid:
                role_ids.append(rid)
check("创建5个角色", len(role_ids) == 5, f"实际{len(role_ids)}个")

# 1.5 创建赛季
season_ids = []
for sname in ["S1-春季赛", "S2-夏季赛", "S3-秋季赛"]:
    r = client.post("/api/seasons", json={"name": sname})
    check(f"创建赛季 {sname}", r.status_code == 200, f"返回{r.status_code}")
    if r.status_code == 200:
        sid = r.json().get("id")
        if sid:
            season_ids.append(sid)
check("创建3个赛季", len(season_ids) == 3, f"实际{len(season_ids)}个")

# 激活S2
r = client.put(f"/api/seasons/{season_ids[1]}/activate")
check("激活赛季S2", r.status_code == 200, str(r.status_code))

# 1.6 创建自定义成就
r = client.post("/api/achievements", json={
    "name": "测试成就-百场", "icon": "[A]", "description": "测试用",
    "condition_type": "total_matches", "condition_value": 100,
    "game_id": None, "role_id": None
})
check("创建全局成就", r.status_code == 200, f"返回{r.status_code}")

if game_a_id:
    r = client.post("/api/achievements", json={
        "name": "游戏专属成就", "icon": "[G]",
        "condition_type": "game_matches", "condition_value": 5,
        "game_id": game_a_id, "role_id": None
    })
    check("创建游戏专属成就", r.status_code == 200, f"返回{r.status_code}")

if role_ids:
    r = client.post("/api/achievements", json={
        "name": "角色专属成就", "icon": "[R]",
        "condition_type": "role_matches", "condition_value": 3,
        "game_id": None, "role_id": role_ids[0]
    })
    check("创建角色专属成就", r.status_code == 200, f"返回{r.status_code}")


# ============================================================
# 第2部分：对局 & ELO & 成就测试
# ============================================================
print("\n" + "=" * 60)
print("  第2部分：对局 & ELO & 成就测试")
print("=" * 60)

match_ids = []
elo_before = {}

if game_b_id:
    for pid in player_ids[:10]:
        r = client.get(f"/player/{pid}")
        if r.status_code == 200:
            elo_before[pid] = r.json().get("elo_rating", 1000)

# 10场对局
for i in range(10):
    if not game_a_id:
        break
    good_pids = player_ids[i*3 % len(player_ids) : (i*3+3) % len(player_ids)+1]
    evil_pids = player_ids[(i*3+4) % len(player_ids) : (i*3+7) % len(player_ids)+1]
    if len(good_pids) < 2 or len(evil_pids) < 2:
        good_pids = player_ids[:3]
        evil_pids = player_ids[3:6]

    participants = [
        {"player_id": pid, "team": "good", "score_change": random.randint(0, 5)}
        for pid in good_pids
    ] + [
        {"player_id": pid, "team": "evil", "score_change": random.randint(0, 5)}
        for pid in evil_pids
    ]
    r = client.post("/api/matches", json={
        "game_id": game_a_id, "winner": "good" if i % 2 == 0 else "evil",
        "season_id": season_ids[i % 3], "participants": participants
    })
    if r.status_code == 200:
        mid = r.json().get("id")
        if mid:
            match_ids.append(mid)
check("创建10场对局", len(match_ids) >= 8, f"实际创建{len(match_ids)}场")

# ELO对局
elo_match_ids = []
if game_b_id:
    for i in range(5):
        good_players = random.sample(player_ids[:10], 3)
        evil_players = random.sample(player_ids[:10], 3)
        participants = [
            {"player_id": pid, "team": "good", "score_change": 0} for pid in good_players
        ] + [
            {"player_id": pid, "team": "evil", "score_change": 0} for pid in evil_players
        ]
        r = client.post("/api/matches", json={
            "game_id": game_b_id,
            "winner": "good" if i % 2 == 0 else "evil",
            "participants": participants
        })
        if r.status_code == 200:
            mid = r.json().get("id")
            if mid:
                elo_match_ids.append(mid)
    check("创建5场ELO对局", len(elo_match_ids) >= 4, f"实际{len(elo_match_ids)}场")

    elo_changed = 0
    for pid in player_ids[:5]:
        r = client.get(f"/player/{pid}")
        if r.status_code == 200:
            new_elo = r.json().get("elo_rating", 0)
            if abs(new_elo - elo_before.get(pid, 1000)) > 0.01:
                elo_changed += 1
    check("有ELO变化", elo_changed > 0, f"{elo_changed}名玩家ELO变化")

# 删除对局
if match_ids:
    r = client.delete(f"/api/matches/{match_ids[0]}")
    check("删除对局(ELO回滚)", r.status_code == 200, f"返回{r.status_code}")
    match_ids.pop(0)

# 成就触发
ach_earned = 0
for pid in player_ids[:5]:
    r = client.get(f"/player/{pid}")
    if r.status_code == 200:
        data = r.json()
        if len(data.get("achievements", [])) > 0:
            ach_earned += 1
check("有玩家获得成就", ach_earned > 0, f"{ach_earned}名")


# ============================================================
# 第3部分：操作加分测试
# ============================================================
print("\n" + "=" * 60)
print("  第3部分：操作加分测试")
print("=" * 60)

if game_a_id:
    r = client.post("/api/actions", json={"game_id": game_a_id, "name": "关键操作", "points": 3})
    check("创建操作类型", r.status_code == 200, f"返回{r.status_code}")
    action_id = r.json().get("id") if r.status_code == 200 else None

    if action_id and len(player_ids) >= 4:
        participants = [
            {"player_id": player_ids[0], "team": "good", "score_change": 1,
             "actions": [{"action_id": action_id, "count": 2}]},
            {"player_id": player_ids[1], "team": "good", "score_change": 2},
            {"player_id": player_ids[2], "team": "evil", "score_change": 3},
            {"player_id": player_ids[3], "team": "evil", "score_change": 1},
        ]
        r = client.post("/api/matches", json={
            "game_id": game_a_id, "winner": "good", "participants": participants
        })
        check("创建带操作加分的对局", r.status_code == 200, f"返回{r.status_code}")

        if r.status_code == 200:
            mid = r.json().get("id")
            r2 = client.get(f"/api/matches/{mid}")
            if r2.status_code == 200:
                detail = r2.json()
                has_actions = any(
                    pp.get("action_breakdown")
                    for pp in detail.get("participants", [])
                )
                check("对局详情含操作加分拆分", has_actions, "未找到")


# ============================================================
# 第4部分：全部 API 端点
# ============================================================
print("\n" + "=" * 60)
print("  第4部分：完整 API 端点覆盖")
print("=" * 60)

endpoints = [
    "/api/players", "/api/games", "/api/matches/history",
    "/api/settings", "/api/export/rankings", "/api/export/matches",
    "/api/balance/suggest",
]
if game_a_id:
    endpoints += [f"/api/games/{game_a_id}/rules", f"/api/games/{game_a_id}/actions"]
if season_ids:
    endpoints.append(f"/api/matches/history?season_id={season_ids[0]}")
if player_ids:
    endpoints.append(f"/api/export/player/{player_ids[0]}")
if match_ids:
    endpoints.append(f"/api/report/{match_ids[0]}")

for url in endpoints:
    r, t = timing(f"GET {url}", lambda u=url: client.get(u))
    check(f"{url}", r.status_code in (200, 204), f"返回{r.status_code}")


# ============================================================
# 第5部分：边界 & 异常
# ============================================================
print("\n" + "=" * 60)
print("  第5部分：边界 & 异常测试")
print("=" * 60)

# 空对局
r = client.post("/api/matches", json={"game_id": 99999, "winner": "good", "participants": []})
check("空参与者应422", r.status_code == 422, f"返回{r.status_code}")

# 不存在游戏
r = client.post("/api/matches", json={
    "game_id": 99999, "winner": "good",
    "participants": [{"player_id": player_ids[0] if player_ids else 1, "team": "good", "score_change": 1}]
})
check("不存在游戏应404", r.status_code in (404, 422), f"返回{r.status_code}")

# 不存在玩家
r = client.get("/player/99999")
check("不存在玩家页", r.status_code in (200, 404), f"返回{r.status_code}")

# 重复名
r = client.post("/api/players", json={"name": "测试玩家01"})
check("重复玩家名", r.status_code in (200, 400, 409), f"返回{r.status_code}")

# 删除不存在对局
r = client.delete("/api/matches/99999")
check("删除不存在对局", r.status_code in (200, 404), f"返回{r.status_code}")

# 开关
r = client.put("/api/settings", json={"enable_balance": "false"})
check("关闭平衡建议", r.status_code == 200, f"返回{r.status_code}")
r = client.put("/api/settings", json={"enable_achievements": "false"})
check("关闭成就", r.status_code == 200, f"返回{r.status_code}")
r = client.put("/api/settings", json={"enable_balance": "true", "enable_achievements": "true"})
check("恢复设置", r.status_code == 200, f"返回{r.status_code}")

# 赛季
if season_ids:
    r = client.put(f"/api/seasons/{season_ids[2]}/activate")
    check("激活S3", r.status_code == 200, f"返回{r.status_code}")
    r = client.put(f"/api/seasons/{season_ids[1]}/end")
    check("结束S2", r.status_code == 200, f"返回{r.status_code}")

# 删除成就
r = client.post("/api/achievements", json={
    "name": "临时", "icon": "[X]", "condition_type": "total_matches",
    "condition_value": 99999, "game_id": None, "role_id": None
})
if r.status_code == 200:
    tmp_id = r.json().get("id")
    if tmp_id:
        r2 = client.delete(f"/api/achievements/{tmp_id}")
        check("删除成就", r2.status_code == 200, f"返回{r2.status_code}")


# ============================================================
# 第6部分：性能测试
# ============================================================
QUICK_MODE = "--quick" in sys.argv

if QUICK_MODE:
    print("\n" + "=" * 60)
    print("  第6部分：性能测试 (跳过，--quick 模式)")
    print("=" * 60)
else:
    print("\n" + "=" * 60)
    print("  第6部分：性能测试（压力数据）")
    print("=" * 60)

    BULK_PLAYERS = 200
    BULK_MATCHES = 500

    # 6.1 批量玩家
    print(f"\n  [6.1] 批量创建 {BULK_PLAYERS} 名玩家...")
    t0 = time.perf_counter()
    bulk_player_ids = []

    def create_player(name):
        r = client.post("/api/players", json={"name": name})
        return r.json().get("id") if r.status_code == 200 else None

    names = [f"批量玩家{i+1:04d}" for i in range(BULK_PLAYERS)]
    with ThreadPoolExecutor(max_workers=20) as ex:
        futures = [ex.submit(create_player, name) for name in names]
        for f in as_completed(futures):
            pid = f.result()
            if pid:
                bulk_player_ids.append(pid)

    t1 = time.perf_counter() - t0
    check(f"批量创建{BULK_PLAYERS}玩家", len(bulk_player_ids) >= BULK_PLAYERS * 0.95,
          f"成功{len(bulk_player_ids)}/{BULK_PLAYERS}，{t1:.2f}s")
    if t1 > 0:
        print(f"      -> 吞吐: {len(bulk_player_ids)/t1:.0f} req/s")

    # 6.2 批量对局
    print(f"\n  [6.2] 批量创建 {BULK_MATCHES} 场对局...")
    t0 = time.perf_counter()
    bulk_match_ids = []
    all_players = player_ids + bulk_player_ids

    def create_match(idx):
        if not game_a_id or len(all_players) < 6:
            return None
        sel = random.sample(all_players, min(8, len(all_players)))
        half = len(sel) // 2
        participants = [
            {"player_id": pid, "team": "good" if j < half else "evil",
             "score_change": random.randint(0, 5)}
            for j, pid in enumerate(sel)
        ]
        r = client.post("/api/matches", json={
            "game_id": game_a_id,
            "winner": "good" if idx % 3 != 0 else "evil",
            "season_id": season_ids[idx % 3] if season_ids else None,
            "participants": participants
        })
        return r.json().get("id") if r.status_code == 200 else None

    with ThreadPoolExecutor(max_workers=10) as ex:
        futures = [ex.submit(create_match, i) for i in range(BULK_MATCHES)]
        for f in as_completed(futures):
            mid = f.result()
            if mid:
                bulk_match_ids.append(mid)

    t1 = time.perf_counter() - t0
    check(f"批量创建{BULK_MATCHES}场对局", len(bulk_match_ids) >= BULK_MATCHES * 0.9,
          f"成功{len(bulk_match_ids)}/{BULK_MATCHES}，{t1:.2f}s")
    if t1 > 0:
        print(f"      -> 吞吐: {len(bulk_match_ids)/t1*60:.0f} 场/分钟")

    # 6.3 排行榜性能
    print(f"\n  [6.3] 排行榜查询性能...")
    r, t = timing("全量排行榜", lambda: client.get("/"))
    check("全量排行榜 < 1.5s", t < 1.5, f"{t:.3f}s, {len(r.text)}字节")

    for sid in season_ids:
        r, t = timing(f"排行榜(赛季{sid})", lambda s=sid: client.get(f"/?season_id={s}"))
        check(f"按赛季 < 0.5s", t < 0.5, f"{t:.3f}s")

    if game_a_id:
        r, t = timing("排行榜(游戏A)", lambda: client.get(f"/?game_id={game_a_id}"))
        check("按游戏 < 0.5s", t < 0.5, f"{t:.3f}s")

    # 6.4 玩家详情
    if bulk_player_ids:
        pid = random.choice(bulk_player_ids)
        r, t = timing("玩家详情", lambda: client.get(f"/player/{pid}"))
        check("玩家详情 < 1s", t < 1.0, f"{t:.3f}s")

        r2, t2 = timing("玩家CSV导出", lambda: client.get(f"/api/export/player/{pid}"))
        check("CSV导出 < 2s", t2 < 2.0, f"{t2:.3f}s")

    # 6.5 导出性能
    r, t = timing("导出排行榜CSV", lambda: client.get("/api/export/rankings"))
    check("排行榜CSV < 2s", t < 2.0, f"{t:.3f}s, {len(r.text)}字节")

    r, t = timing("导出对局CSV", lambda: client.get("/api/export/matches"))
    check("对局CSV < 3s", t < 3.0, f"{t:.3f}s, {len(r.text)}字节")

    # 6.6 平衡建议
    if game_b_id:
        r, t = timing("ELO平衡建议", lambda: client.get(
            f"/api/balance/suggest?game_id={game_b_id}&player_count=8"))
        check("平衡建议 < 2s", t < 2.0, f"{t:.3f}s")

    # 6.7 管理后台加载
    r, t = timing("管理后台", lambda: client.get("/admin"))
    check("管理后台 < 2s", t < 2.0, f"{t:.3f}s")

    # 6.8 成就检查
    if bulk_player_ids:
        conn = database.get_db()
        import main as main_module
        _, t = timing("成就检查(单玩家)", lambda: main_module.check_achievements(conn, bulk_player_ids[0]))
        conn.close()
        check("成就检查 < 0.5s", t < 0.5, f"{t:.3f}s")


# ============================================================
# 第7部分：数据一致性
# ============================================================
print("\n" + "=" * 60)
print("  第7部分：数据一致性验证")
print("=" * 60)

conn = database.get_db()
cursor = conn.cursor()

# 空对局
cursor.execute("SELECT id FROM matches")
all_db = [r[0] for r in cursor.fetchall()]
empty = sum(1 for mid in all_db
            if cursor.execute("SELECT COUNT(*) FROM match_players WHERE match_id=?", (mid,)).fetchone()[0] == 0)
check("无空对局(无参与者)", empty == 0, f"发现{empty}个")

# 外键
cursor.execute("""SELECT mp.id FROM match_players mp
    LEFT JOIN players p ON mp.player_id = p.id WHERE p.id IS NULL""")
check("无孤儿参与者", len(cursor.fetchall()) == 0)

cursor.execute("""SELECT m.id FROM matches m
    LEFT JOIN games g ON m.game_id = g.id WHERE g.id IS NULL""")
check("无孤儿对局", len(cursor.fetchall()) == 0)

# 重复成就
cursor.execute("""SELECT player_id, achievement_id, COUNT(*)
    FROM player_achievements GROUP BY player_id, achievement_id HAVING COUNT(*) > 1""")
check("无重复成就", len(cursor.fetchall()) == 0)

# 赛季统计
print("\n  各赛季数据:")
for sid in season_ids:
    cursor.execute("SELECT COUNT(*) FROM matches WHERE season_id=?", (sid,))
    mc = cursor.fetchone()[0]
    cursor.execute("""SELECT COUNT(*) FROM match_players mp
        JOIN matches m ON mp.match_id=m.id WHERE m.season_id=?""", (sid,))
    pc = cursor.fetchone()[0]
    print(f"    赛季{sid}: {mc}场, {pc}人次")

conn.close()


# ============================================================
# 第8部分：并发安全
# ============================================================
print("\n" + "=" * 60)
print("  第8部分：并发安全测试")
print("=" * 60)

if not QUICK_MODE and game_a_id and len(player_ids) >= 6:
    print("  [8.1] 30并发创建对局...")
    errors = []

    def concurrent_create(i):
        try:
            p = random.sample(player_ids, min(6, len(player_ids)))
            half = len(p) // 2
            participants = [
                {"player_id": pid, "team": "good" if j < half else "evil",
                 "score_change": random.randint(0, 3)}
                for j, pid in enumerate(p)
            ]
            r = client.post("/api/matches", json={
                "game_id": game_a_id,
                "winner": random.choice(["good", "evil"]),
                "participants": participants
            })
            if r.status_code != 200:
                errors.append(f"req{i}:{r.status_code}")
        except Exception as e:
            errors.append(f"req{i}:{e}")

    threads = []
    for i in range(30):
        t = threading.Thread(target=concurrent_create, args=(i,))
        threads.append(t)
        t.start()
    for t in threads:
        t.join()

    check("30并发无崩溃", len(errors) <= 2,
          f"{len(errors)}错误: {errors[:3]}")

    conn = database.get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM matches")
    total_after = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(DISTINCT match_id) FROM match_players")
    mp_after = cursor.fetchone()[0]
    conn.close()
    check("并发后数据一致", abs(total_after - mp_after) <= 3,
          f"对局{total_after}场,参与{mp_after}条")


# ============================================================
# 第9部分：数据库完整性
# ============================================================
print("\n" + "=" * 60)
print("  第9部分：数据库文件完整性")
print("=" * 60)

db_size = os.path.getsize(DB_PATH)
check("数据库文件存在", db_size > 0, f"{db_size/1024/1024:.2f} MB")

conn = database.get_db()
cursor = conn.cursor()
cursor.execute("PRAGMA integrity_check")
integrity = cursor.fetchone()[0]
check(f"完整性检查: {integrity}", integrity == "ok", integrity)

cursor.execute("PRAGMA foreign_keys")
check("外键约束已启用", cursor.fetchone()[0] == 1)

# 表统计
tables = ["players", "games", "matches", "match_players", "seasons",
          "achievements", "player_achievements", "roles", "settings",
          "game_actions", "match_player_actions"]
print("\n  数据库表统计:")
for tbl in tables:
    try:
        cursor.execute(f"SELECT COUNT(*) FROM {tbl}")
        print(f"    {tbl:30s} {cursor.fetchone()[0]:6d} 行")
    except:
        print(f"    {tbl:30s} [不存在]")

conn.close()


# ============================================================
# 最终总结
# ============================================================
print("\n" + "=" * 60)
print("  测试总结")
print("=" * 60)
total = passed + failed
rate = (passed / total * 100) if total > 0 else 0
print(f"  通过: {passed}/{total} ({rate:.0f}%)")
print(f"  失败: {failed}/{total}")
print(f"  警告: {warnings}")

# 恢复数据库
if os.path.exists(DB_BACKUP):
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
    shutil.copy(DB_BACKUP, DB_PATH)
    os.remove(DB_BACKUP)
    print("\n  [CLEANUP] 已恢复原数据库")

if failed > 0:
    print("\n  *** 存在失败项 ***")
    sys.exit(1)
else:
    print("\n  全部测试通过!")
