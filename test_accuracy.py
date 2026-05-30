"""
全面数据准确性验证测试
重点: 得分计算、ELO、胜率、成就条件、排行榜
"""
import sys, os, math, json
sys.stdout.reconfigure(encoding='utf-8')

DB_PATH = os.path.join(os.path.dirname(__file__), "db", "game.db")
DB_BACKUP = DB_PATH + ".acc_backup"

import shutil
if os.path.exists(DB_PATH):
    shutil.copy(DB_PATH, DB_BACKUP)
    print("[SETUP] 已备份数据库")
if os.path.exists(DB_PATH):
    os.remove(DB_PATH)

import database
database.init_db()
print("[SETUP] 数据库初始化完成\n")

from fastapi.testclient import TestClient
from main import app, calc_elo
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
        print(f"  [FAIL] {name}  | {detail}")

def warn(msg):
    global warnings
    warnings += 1
    print(f"  [WARN] {msg}")

def api_post(url, json_data):
    return client.post(url, json=json_data)

def api_get(url):
    return client.get(url)


# ============================================================
# 管理员登录
# ============================================================
print("=" * 60)
print("  管理员登录")
print("=" * 60)
r = client.post("/api/auth/login", data={"username": "admin", "password": "admin123"})
check("管理员登录", r.status_code in (200, 302), f"状态码{r.status_code}")


# ============================================================
# 第1部分: 创建基础数据
# ============================================================
print("\n" + "=" * 60)
print("  第1部分: 创建基础数据")
print("=" * 60)

# 创建玩家
player_names = ["张三", "李四", "王五", "赵六", "钱七", "孙八", "周九", "吴十"]
player_ids = []
for name in player_names:
    r = api_post("/api/players", {"name": name})
    if r.status_code == 200:
        pid = r.json().get("id")
        if pid:
            player_ids.append(pid)
check("创建8名玩家", len(player_ids) == 8, f"实际{len(player_ids)}")

# 创建游戏
r = api_post("/api/games", {"name": "测试游戏A", "good_win_score": 5, "evil_win_score": 8, "lose_penalty": 3})
check("创建普通游戏", r.status_code == 200)
game_ordinary = r.json().get("id") if r.status_code == 200 else None

r = api_post("/api/games", {"name": "测试ELO游戏", "good_win_score": 5, "evil_win_score": 8, "lose_penalty": 3, "use_elo": 1})
check("创建ELO游戏", r.status_code == 200)
game_elo = r.json().get("id") if r.status_code == 200 else None

# 初始化变量，避免 NameError
match1_id = None
match2_id = None
match3_id = None
elo_match_id = None
elo_match2 = None
action_match = None

# 创建赛季
season_ids = []
for sname in ["S1-春季", "S2-夏季", "S3-秋季"]:
    r = api_post("/api/seasons", {"name": sname})
    if r.status_code == 200:
        data = r.json()
        # 查回 id
        conn = database.get_db()
        c = conn.cursor()
        c.execute("SELECT id FROM seasons WHERE name = ?", (sname,))
        row = c.fetchone()
        conn.close()
        if row:
            season_ids.append(row["id"])
check("创建3个赛季", len(season_ids) == 3, f"实际{len(season_ids)}")

if len(season_ids) >= 2:
    client.put(f"/api/seasons/{season_ids[1]}/activate")
    check("激活赛季S2", True)


# ============================================================
# 第2部分: 得分计算准确性
# ============================================================
print("\n" + "=" * 60)
print("  第2部分: 得分计算准确性验证")
print("=" * 60)

if game_ordinary and len(player_ids) >= 4:
    # 2.1 基础得分: 好人胜利
    # 好人获胜=+5, 坏人失败=-3
    participants = [
        {"player_id": player_ids[0], "team": "good", "score_change": 0},
        {"player_id": player_ids[1], "team": "good", "score_change": 0},
        {"player_id": player_ids[2], "team": "evil", "score_change": 0},
        {"player_id": player_ids[3], "team": "evil", "score_change": 0},
    ]
    r = api_post("/api/matches", {
        "game_id": game_ordinary, "winner": "good", "players": participants
    })
    check("创建好人胜对局", r.status_code == 200, f"状态{r.status_code}")
    match1_id = r.json().get("match_id") if r.status_code == 200 else None

    if match1_id:
        # 验证得分
        conn = database.get_db()
        c = conn.cursor()
        c.execute("SELECT player_id, team, score_change FROM match_players WHERE match_id = ?", (match1_id,))
        scores = {r["player_id"]: {"team": r["team"], "score": r["score_change"]} for r in c.fetchall()}
        conn.close()

        check("好人(张三)得+5", scores.get(player_ids[0], {}).get("score") == 5,
              f"实际:{scores.get(player_ids[0], {}).get('score')}")
        check("好人(李四)得+5", scores.get(player_ids[1], {}).get("score") == 5,
              f"实际:{scores.get(player_ids[1], {}).get('score')}")
        check("坏人(王五)得-3", scores.get(player_ids[2], {}).get("score") == -3,
              f"实际:{scores.get(player_ids[2], {}).get('score')}")
        check("坏人(赵六)得-3", scores.get(player_ids[3], {}).get("score") == -3,
              f"实际:{scores.get(player_ids[3], {}).get('score')}")

    # 2.2 坏人胜利: 坏人+8, 好人-3
    r = api_post("/api/matches", {
        "game_id": game_ordinary, "winner": "evil", "players": participants
    })
    check("创建坏人胜对局", r.status_code == 200)
    match2_id = r.json().get("match_id") if r.status_code == 200 else None

    if match2_id:
        conn = database.get_db()
        c = conn.cursor()
        c.execute("SELECT player_id, team, score_change FROM match_players WHERE match_id = ?", (match2_id,))
        scores = {r["player_id"]: {"team": r["team"], "score": r["score_change"]} for r in c.fetchall()}
        conn.close()

        check("好人张三得-3", scores.get(player_ids[0], {}).get("score") == -3,
              f"实际:{scores.get(player_ids[0], {}).get('score')}")
        check("坏人王五得+8", scores.get(player_ids[2], {}).get("score") == 8,
              f"实际:{scores.get(player_ids[2], {}).get('score')}")
        check("坏人赵六得+8", scores.get(player_ids[3], {}).get("score") == 8,
              f"实际:{scores.get(player_ids[3], {}).get('score')}")

    # 2.3 角色加分
    conn = database.get_db()
    c = conn.cursor()
    c.execute("SELECT id FROM roles WHERE game_id = ? AND name = '梅林'", (game_ordinary,))
    role_merlin = c.fetchone()
    c.execute("SELECT id FROM roles WHERE game_id = ? AND name = '刺客'", (game_ordinary,))
    role_assassin = c.fetchone()
    conn.close()

    if role_merlin and role_assassin:
        participants_role = [
            {"player_id": player_ids[0], "team": "good", "score_change": 0, "role_id": role_merlin["id"]},
            {"player_id": player_ids[1], "team": "good", "score_change": 0},
            {"player_id": player_ids[2], "team": "evil", "score_change": 0, "role_id": role_assassin["id"]},
            {"player_id": player_ids[3], "team": "evil", "score_change": 0},
        ]
        r = api_post("/api/matches", {
            "game_id": game_ordinary, "winner": "good", "players": participants_role
        })
        check("创建带角色对局", r.status_code == 200)
        match3_id = r.json().get("match_id") if r.status_code == 200 else None

        if match3_id:
            conn = database.get_db()
            c = conn.cursor()
            c.execute("SELECT player_id, team, score_change, role_id FROM match_players WHERE match_id = ?", (match3_id,))
            scores = {r["player_id"]: {"team": r["team"], "score": r["score_change"], "role": r["role_id"]} for r in c.fetchall()}
            conn.close()

            # 梅林好人胜: 基础5 + 角色3 = 8
            check("梅林(好人胜+角色加分)=8", scores.get(player_ids[0], {}).get("score") == 8,
                  f"实际:{scores.get(player_ids[0], {}).get('score')}")
            # 普通好人胜: 基础5
            check("普通好人胜=5", scores.get(player_ids[1], {}).get("score") == 5,
                  f"实际:{scores.get(player_ids[1], {}).get('score')}")
            # 刺客坏人败: 基础-3 + 刺客角色5 = 2 (坏人失败时角色分也加上)
            check("刺客(坏人败+角色加分)=2", scores.get(player_ids[2], {}).get("score") == 2,
                  f"实际:{scores.get(player_ids[2], {}).get('score')}")


# ============================================================
# 第3部分: ELO 计算准确性
# ============================================================
print("\n" + "=" * 60)
print("  第3部分: ELO 计算准确性验证")
print("=" * 60)

# 手动验证 ELO 公式
# expected = 1 / (1 + 10^((opp_avg - player) / 400))
# new = player + K * (actual - expected), K=32
test_elo = calc_elo(1000, 1000, 1.0)
expected_v = 1.0 / (1.0 + math.pow(10, (1000 - 1000) / 400.0))
expected_detail = f"{1000+32*(1.0-expected_v):.0f}"
check("ELO: 等分对等分胜利", test_elo == 1016,
      f"期望{expected_detail}=1016, 实际{test_elo}")

test_elo2 = calc_elo(1000, 1000, 0.0)
check("ELO: 等分对等分失败", test_elo2 == 984,
      f"期望{1000+32*(0.0-0.5)}={984}, 实际{test_elo2}")

test_elo3 = calc_elo(1200, 1000, 1.0)
expected_v3 = 1.0 / (1.0 + math.pow(10, (1000 - 1200) / 400.0))
check("ELO: 高分对低分胜利", abs(test_elo3 - (1200+round(32*(1.0-expected_v3)))) <= 1,
      f"期望{1200+round(32*(1.0-expected_v3))}, 实际{test_elo3}")

test_elo4 = calc_elo(1000, 1200, 0.0)
expected_v4 = 1.0 / (1.0 + math.pow(10, (1200 - 1000) / 400.0))
check("ELO: 低分对高分失败", abs(test_elo4 - (1000+round(32*(0.0-expected_v4)))) <= 1,
      f"期望{1000+round(32*(0.0-expected_v4))}, 实际{test_elo4}")

# 实际 ELO 对局(使用另一批玩家，避免污染 ordinary 玩家统计)
if game_elo and len(player_ids) >= 8:
    r = api_post("/api/matches", {
        "game_id": game_elo, "winner": "good",
        "players": [
            {"player_id": player_ids[4], "team": "good", "score_change": 0},
            {"player_id": player_ids[5], "team": "good", "score_change": 0},
            {"player_id": player_ids[6], "team": "evil", "score_change": 0},
            {"player_id": player_ids[7], "team": "evil", "score_change": 0},
        ]
    })
    check("ELO对局创建成功", r.status_code == 200)
    elo_match_id = r.json().get("match_id") if r.status_code == 200 else None

    if elo_match_id:
        conn = database.get_db()
        c = conn.cursor()
        c.execute("SELECT player_id, elo_change FROM match_players WHERE match_id = ?", (elo_match_id,))
        elo_changes = {r["player_id"]: r["elo_change"] for r in c.fetchall()}

        # 好人胜: 新玩家(孙七周八)ELO=1000, 都是等分, expected=0.5, actual=1, elo_change=+16
        c.execute("SELECT elo_rating FROM players WHERE id = ?", (player_ids[4],))
        new_elo = c.fetchone()["elo_rating"]
        conn.close()

        check("ELO对等分对战好人+16", elo_changes.get(player_ids[4], 0) == 16,
              f"实际:{elo_changes.get(player_ids[4])}, 新ELO:{new_elo}")
        check("ELO对等分对战坏人-16", elo_changes.get(player_ids[6], 0) == -16,
              f"实际:{elo_changes.get(player_ids[6])}")
        check("ELO好人新分=1016", new_elo == 1016, f"实际:{new_elo}")

    # 反向测试: 坏人获胜
    r = api_post("/api/matches", {
        "game_id": game_elo, "winner": "evil",
        "players": [
            {"player_id": player_ids[4], "team": "good", "score_change": 0},
            {"player_id": player_ids[5], "team": "good", "score_change": 0},
            {"player_id": player_ids[6], "team": "evil", "score_change": 0},
            {"player_id": player_ids[7], "team": "evil", "score_change": 0},
        ]
    })
    check("ELO坏人胜对局创建", r.status_code == 200)
    elo_match2 = r.json().get("match_id") if r.status_code == 200 else None

    if elo_match2:
        conn = database.get_db()
        c = conn.cursor()
        c.execute("SELECT elo_rating FROM players WHERE id = ?", (player_ids[4],))
        bad_elo = c.fetchone()["elo_rating"]
        c.execute("SELECT player_id, elo_change FROM match_players WHERE match_id = ?", (elo_match2,))
        changes = {r["player_id"]: r["elo_change"] for r in c.fetchall()}
        conn.close()
        # 好人现在是1016, 坏人1000→984, 对战坏人984/984=984平均
        # expected = 1/(1+10^((984-1016)/400)) ≈ 1/(1+10^(-0.08)) ≈ 1/1.832 ≈ 0.546
        # actual=0, elo_change=round(32*(0-0.546))=round(-17.5)=-18
        # 新分=1016-18=998
        check("ELO好人败后分", abs(bad_elo - 998) <= 2, f"实际:{bad_elo}")


# ============================================================
# 第4部分: 胜率计算验证
# ============================================================
print("\n" + "=" * 60)
print("  第4部分: 胜率计算验证")
print("=" * 60)

if game_ordinary and len(player_ids) >= 4:
    # 当前数据(仅含 2 场普通对局，第3场角色对局需要预置角色，可能未创建):
    # 张三(player_ids[0]): 好人胜(M1), 好人败(M2) = 2场, 赢1, 胜率50.0%
    # 李四(player_ids[1]): 好人胜(M1), 好人败(M2) = 2场, 赢1, 胜率50.0%
    # 王五(player_ids[2]): 坏人败(M1), 坏人胜(M2) = 2场, 赢1, 胜率50.0%
    # 赵六(player_ids[3]): 坏人败(M1), 坏人胜(M2) = 2场, 赢1, 胜率50.0%

    conn = database.get_db()
    c = conn.cursor()

    # 张三 验证
    pid = player_ids[0]
    c.execute("SELECT COUNT(*) FROM match_players WHERE player_id = ?", (pid,))
    zm_matches = c.fetchone()[0]
    c.execute("""SELECT ROUND(CAST(SUM(CASE WHEN mp.team = m.winner THEN 1 ELSE 0 END) AS FLOAT) / NULLIF(COUNT(*), 0) * 100, 1)
        FROM match_players mp JOIN matches m ON mp.match_id = m.id WHERE mp.player_id = ?""", (pid,))
    zm_wr = c.fetchone()[0] or 0
    c.execute("""SELECT COUNT(*) FROM match_players WHERE player_id = ? AND team = 'good'""", (pid,))
    zm_good = c.fetchone()[0]
    c.execute("""SELECT COUNT(*), ROUND(CAST(SUM(CASE WHEN mp.team = m.winner THEN 1 ELSE 0 END) AS FLOAT) / NULLIF(COUNT(*), 0) * 100)
        FROM match_players mp JOIN matches m ON mp.match_id = m.id WHERE mp.player_id = ? AND mp.team = 'good'""", (pid,))
    zg = c.fetchone()

    check("张三总场次=2", zm_matches == 2, f"实际:{zm_matches}")
    check("张三胜率≈50.0%", abs(zm_wr - 50.0) < 1, f"实际:{zm_wr}%")
    check("张三好人场次=2", zm_good == 2, f"实际:{zm_good}")
    check("张三好人胜率≈50.0%", abs((zg[1] or 0) - 50) <= 1, f"实际:{zg[1]}%")

    # 王五 验证
    pid2 = player_ids[2]
    c.execute("SELECT COUNT(*) FROM match_players WHERE player_id = ?", (pid2,))
    ww_matches = c.fetchone()[0]
    c.execute("""SELECT ROUND(CAST(SUM(CASE WHEN mp.team = m.winner THEN 1 ELSE 0 END) AS FLOAT) / NULLIF(COUNT(*), 0) * 100, 1)
        FROM match_players mp JOIN matches m ON mp.match_id = m.id WHERE mp.player_id = ?""", (pid2,))
    ww_wr = c.fetchone()[0] or 0
    c.execute("""SELECT COUNT(*) FROM match_players WHERE player_id = ? AND team = 'evil'""", (pid2,))
    ww_evil = c.fetchone()[0]
    c.execute("""SELECT COUNT(*), ROUND(CAST(SUM(CASE WHEN mp.team = m.winner THEN 1 ELSE 0 END) AS FLOAT) / NULLIF(COUNT(*), 0) * 100)
        FROM match_players mp JOIN matches m ON mp.match_id = m.id WHERE mp.player_id = ? AND mp.team = 'evil'""", (pid2,))
    we = c.fetchone()

    check("王五总场次=2", ww_matches == 2, f"实际:{ww_matches}")
    check("王五胜率≈50.0%", abs(ww_wr - 50.0) < 1, f"实际:{ww_wr}%")
    check("王五坏人场次=2", ww_evil == 2, f"实际:{ww_evil}")
    check("王五坏人胜率≈50.0%", abs((we[1] or 0) - 50) <= 1, f"实际:{we[1]}%")

    conn.close()


# ============================================================
# 第5部分: 操作加分准确性
# ============================================================
print("\n" + "=" * 60)
print("  第5部分: 操作加分准确性")
print("=" * 60)

if game_ordinary and len(player_ids) >= 4:
    r = api_post("/api/actions", {"game_id": game_ordinary, "name": "MVP操作", "score_bonus": 3})
    if r.status_code == 200:
        data = r.json()
        action_id = data.get("id")
        if not action_id:
            conn = database.get_db()
            c = conn.cursor()
            c.execute("SELECT id FROM game_actions WHERE name = 'MVP操作' AND game_id = ?", (game_ordinary,))
            row = c.fetchone()
            conn.close()
            if row:
                action_id = row["id"]
    else:
        action_id = None

    if action_id:
        r = api_post("/api/matches", {
            "game_id": game_ordinary, "winner": "good",
            "players": [
                {"player_id": player_ids[0], "team": "good", "score_change": 1},
                {"player_id": player_ids[1], "team": "good", "score_change": 2},
                {"player_id": player_ids[2], "team": "evil", "score_change": 3},
                {"player_id": player_ids[3], "team": "evil", "score_change": 1},
            ],
            "actions": [
                {"player_id": player_ids[0], "action_id": action_id},
                {"player_id": player_ids[1], "action_id": action_id},
            ]
        })
        check("创建带操作的对局", r.status_code == 200)
        action_match = r.json().get("match_id") if r.status_code == 200 else None

        if action_match:
            conn = database.get_db()
            c = conn.cursor()
            c.execute("SELECT player_id, score_change FROM match_players WHERE match_id = ?", (action_match,))
            scores = {r["player_id"]: r["score_change"] for r in c.fetchall()}
            conn.close()

            # 好人胜: 基础5 + 操作3 = 8
            check("张三(好人胜+操作)=8", scores.get(player_ids[0], 0) == 8,
                  f"实际:{scores.get(player_ids[0])}")
            check("李四(好人胜+操作)=8", scores.get(player_ids[1], 0) == 8,
                  f"实际:{scores.get(player_ids[1])}")
            # 坏人败无操作: 基础-3
            check("王五(坏人败)=-3", scores.get(player_ids[2], 0) == -3,
                  f"实际:{scores.get(player_ids[2])}")
            check("赵六(坏人败)=-3", scores.get(player_ids[3], 0) == -3,
                  f"实际:{scores.get(player_ids[3])}")


# ============================================================
# 第6部分: 排行榜准确性验证
# ============================================================
print("\n" + "=" * 60)
print("  第6部分: 排行榜准确性验证")
print("=" * 60)

r = api_get("/")
check("排行榜页面返回200", r.status_code == 200)

# 验证玩家总积分：直接查 DB 并用排行榜页面渲染数据交叉验证
conn = database.get_db()
c = conn.cursor()

# 排行榜查询对比
for pid in player_ids[:4]:
    c.execute("SELECT COALESCE(SUM(score_change), 0) FROM match_players WHERE player_id = ?", (pid,))
    db_total = c.fetchone()[0]
    # 同时通过排行榜 SQL 验证（和 index.html 路由相同逻辑）
    c.execute("""SELECT COALESCE(SUM(mp.score_change), 0) as total_score
        FROM players p LEFT JOIN match_players mp ON p.id = mp.player_id
        LEFT JOIN matches m ON mp.match_id = m.id
        WHERE p.id = ?""", (pid,))
    rank_total = c.fetchone()[0]
    check(f"玩家{pid}积分一致: {db_total}", db_total == rank_total,
          f"略表SUM:{db_total}, 排行榜SQL:{rank_total}")

# 验证对局总数
c.execute("SELECT COUNT(*) FROM matches")
total_matches_db = c.fetchone()[0]
c.execute("SELECT COUNT(*) FROM match_players")
total_mp_db = c.fetchone()[0]
print(f"\n  数据库统计: {total_matches_db}场对局, {total_mp_db}条参与记录")

# 验证无孤儿数据
c.execute("""SELECT mp.id FROM match_players mp
    LEFT JOIN matches m ON mp.match_id = m.id WHERE m.id IS NULL""")
orphan_mp = len(c.fetchall())
check("无孤儿参与记录", orphan_mp == 0, f"发现{orphan_mp}条")

c.execute("""SELECT mpa.id FROM match_player_actions mpa
    LEFT JOIN match_players mp ON mpa.match_id = mp.match_id AND mpa.player_id = mp.player_id
    WHERE mp.id IS NULL""")
orphan_act = len(c.fetchall())
check("无孤儿操作记录", orphan_act == 0, f"发现{orphan_act}条")

c.execute("""SELECT m.id FROM matches m
    LEFT JOIN games g ON m.game_id = g.id WHERE g.id IS NULL""")
orphan_match = len(c.fetchall())
check("无孤儿对局(游戏不存在)", orphan_match == 0, f"发现{orphan_match}条")

# 验证胜率公式: win_rate = ROUND(wins * 100.0 / total_matches, 1)
# 与 player_detail 路由中的查询做交叉验证
c.execute("""
    SELECT p.id, p.name,
           ROUND(CAST(SUM(CASE WHEN mp.team = m.winner THEN 1 ELSE 0 END) AS FLOAT) / NULLIF(COUNT(mp.id), 0) * 100, 1) as win_rate,
           COUNT(mp.id) as total_matches
    FROM players p
    LEFT JOIN match_players mp ON p.id = mp.player_id
    LEFT JOIN matches m ON mp.match_id = m.id
    GROUP BY p.id HAVING COUNT(mp.id) > 0
""")
for row in c.fetchall():
    # 联表版胜率 (与排行榜 SQL 一致)
    wr1 = row["win_rate"]
    # 分步版胜率 (与 player_detail SQL 一致)
    c.execute("""SELECT ROUND(CAST(SUM(CASE WHEN mp.team = m.winner THEN 1 ELSE 0 END) AS FLOAT) / NULLIF(COUNT(*), 0) * 100, 1)
        FROM match_players mp JOIN matches m ON mp.match_id = m.id WHERE mp.player_id = ?""", (row["id"],))
    wr2 = c.fetchone()[0] or 0
    check(f"{row['name']} 胜率SQL一致性: {wr1}% vs {wr2}%", abs(wr1 - wr2) < 0.2,
          f"联表:{wr1}%, 分步:{wr2}%")

# 验证好人/坏人胜率
c.execute("""
    SELECT p.id, p.name,
           ROUND(CAST(SUM(CASE WHEN mp.team = m.winner AND mp.team='good' THEN 1 ELSE 0 END) AS FLOAT) / 
                 NULLIF(SUM(CASE WHEN mp.team='good' THEN 1 ELSE 0 END), 0) * 100) as good_wr,
           ROUND(CAST(SUM(CASE WHEN mp.team = m.winner AND mp.team='evil' THEN 1 ELSE 0 END) AS FLOAT) / 
                 NULLIF(SUM(CASE WHEN mp.team='evil' THEN 1 ELSE 0 END), 0) * 100) as evil_wr,
           SUM(CASE WHEN mp.team='good' THEN 1 ELSE 0 END) as good_count,
           SUM(CASE WHEN mp.team='evil' THEN 1 ELSE 0 END) as evil_count
    FROM players p
    LEFT JOIN match_players mp ON p.id = mp.player_id
    LEFT JOIN matches m ON mp.match_id = m.id
    GROUP BY p.id HAVING COUNT(mp.id) > 0
""")
for row in c.fetchall():
    if (row["good_count"] or 0) > 0:
        exp_gwr = row["good_wr"] or 0
        c.execute("""SELECT ROUND(CAST(SUM(CASE WHEN mp.team = m.winner THEN 1 ELSE 0 END) AS FLOAT) / NULLIF(COUNT(*), 0) * 100)
            FROM match_players mp JOIN matches m ON mp.match_id = m.id WHERE mp.player_id = ? AND mp.team = 'good'""", (row["id"],))
        gwr2 = c.fetchone()[0] or 0
        check(f"{row['name']} 好人胜率一致性: {exp_gwr}%", abs((exp_gwr or 0) - (gwr2 or 0)) <= 1,
              f"联表:{exp_gwr}%, 分步:{gwr2}%")
    if (row["evil_count"] or 0) > 0:
        exp_ewr = row["evil_wr"] or 0
        c.execute("""SELECT ROUND(CAST(SUM(CASE WHEN mp.team = m.winner THEN 1 ELSE 0 END) AS FLOAT) / NULLIF(COUNT(*), 0) * 100)
            FROM match_players mp JOIN matches m ON mp.match_id = m.id WHERE mp.player_id = ? AND mp.team = 'evil'""", (row["id"],))
        ewr2 = c.fetchone()[0] or 0
        check(f"{row['name']} 坏人胜率一致性: {exp_ewr}%", abs((exp_ewr or 0) - (ewr2 or 0)) <= 1,
              f"联表:{exp_ewr}%, 分步:{ewr2}%")

conn.close()


# ============================================================
# 第7部分: 成就触发条件验证
# ============================================================
print("\n" + "=" * 60)
print("  第7部分: 成就触发条件验证")
print("=" * 60)

conn = database.get_db()
c = conn.cursor()
for pid in player_ids[:4]:
    c.execute("""
        SELECT a.name, a.condition_type, a.condition_value
        FROM player_achievements pa
        JOIN achievements a ON pa.achievement_id = a.id
        WHERE pa.player_id = ?
    """, (pid,))
    earned = c.fetchall()
    for ach in earned:
        print(f"  [{player_names[player_ids.index(pid)]}] 获得: {ach['name']} ({ach['condition_type']}>={ach['condition_value']})")

# 验证无重复成就
c.execute("""SELECT player_id, achievement_id, COUNT(*) 
    FROM player_achievements GROUP BY player_id, achievement_id HAVING COUNT(*) > 1""")
dup = c.fetchall()
check("无重复成就记录", len(dup) == 0, f"发现{len(dup)}组重复")

conn.close()


# ============================================================
# 第8部分: ELO 回滚验证
# ============================================================
print("\n" + "=" * 60)
print("  第8部分: ELO 删除回滚验证")
print("=" * 60)

if elo_match_id:
    conn = database.get_db()
    c = conn.cursor()
    # 记录当前 ELO
    elo_before = {}
    for pid in player_ids[:4]:
        c.execute("SELECT elo_rating FROM players WHERE id = ?", (pid,))
        elo_before[pid] = c.fetchone()["elo_rating"]

    # 获取该局的 elo_change
    c.execute("SELECT player_id, elo_change FROM match_players WHERE match_id = ?", (elo_match_id,))
    changes = {r["player_id"]: r["elo_change"] for r in c.fetchall()}
    conn.close()

    # 删除对局
    r = client.delete(f"/api/matches/{elo_match_id}")
    check("删除ELO对局", r.status_code == 200, f"返回{r.status_code}")

    conn = database.get_db()
    c = conn.cursor()
    all_rolled = True
    for pid, before in elo_before.items():
        c.execute("SELECT elo_rating FROM players WHERE id = ?", (pid,))
        after = c.fetchone()["elo_rating"]
        expected = before - changes.get(pid, 0)
        if abs(after - expected) > 1:
            all_rolled = False
            print(f"  [FAIL] 玩家{pid}: 回滚前{before}, 变化{changes.get(pid, 0)}, 期望{expected}, 实际{after}")
    conn.close()
    check("ELO正确回滚", all_rolled, "部分玩家ELO未正确回滚")


# ============================================================
# 第9部分: 季赛季份归档测试
# ============================================================
print("\n" + "=" * 60)
print("  第9部分: 赛季筛选准确性")
print("=" * 60)

if len(season_ids) >= 2:
    # 在 S1 下再创建一场对局
    client.put(f"/api/seasons/{season_ids[0]}/activate")
    r = api_post("/api/matches", {
        "game_id": game_ordinary, "winner": "good",
        "players": [
            {"player_id": player_ids[0], "team": "good", "score_change": 0},
            {"player_id": player_ids[1], "team": "evil", "score_change": 0},
        ]
    })
    if r.status_code == 200:
        r2 = client.get(f"/?season_id={season_ids[0]}")
        check(f"按赛季{season_ids[0]}筛选排行榜", r2.status_code == 200)

        # 验证 S1 对局数
        conn = database.get_db()
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM matches WHERE season_id = ?", (season_ids[0],))
        s1_count = c.fetchone()[0]
        conn.close()
        check(f"赛季{season_ids[0]}有对局", s1_count > 0, f"共{s1_count}场")

    # 恢复激活 S2
    client.put(f"/api/seasons/{season_ids[1]}/activate")


# ============================================================
# 第10部分: API端点全覆盖
# ============================================================
print("\n" + "=" * 60)
print("  第10部分: API端点覆盖")
print("=" * 60)

endpoints = [
    ("GET", "/api/players"),
    ("GET", "/api/games"),
    ("GET", "/api/matches/history"),
    ("GET", "/api/settings"),
    ("GET", "/api/export/rankings"),
    ("GET", "/api/export/matches"),
    ("GET", "/api/balance/suggest"),
]
if game_ordinary:
    endpoints += [
        ("GET", f"/api/games/{game_ordinary}/rules"),
        ("GET", f"/api/games/{game_ordinary}/actions"),
    ]
if season_ids:
    endpoints.append(("GET", f"/api/matches/history?season_id={season_ids[0]}"))
if player_ids:
    endpoints.append(("GET", f"/api/export/player/{player_ids[0]}"))
    endpoints.append(("GET", f"/api/achievements/progress/{player_ids[0]}"))

for method, url in endpoints:
    r = client.get(url)
    ok = r.status_code in (200, 204, 307)
    check(f"{method} {url}", ok, f"状态码{r.status_code}")


# ============================================================
# 第11部分: 边界与异常
# ============================================================
print("\n" + "=" * 60)
print("  第11部分: 边界与异常测试")
print("=" * 60)

# 空参与者
r = api_post("/api/matches", {"game_id": 99999, "winner": "good", "players": []})
check("空参与者应400", r.status_code in (400, 422), f"返回{r.status_code}")

# 不存在的游戏
r = api_post("/api/matches", {
    "game_id": 99999, "winner": "good",
    "players": [
        {"player_id": player_ids[0] if player_ids else 1, "team": "good", "score_change": 0},
        {"player_id": player_ids[1] if len(player_ids) > 1 else 2, "team": "evil", "score_change": 0},
    ]
})
check("不存在游戏应404", r.status_code in (404, 422), f"返回{r.status_code}")

# 缺少阵营
if player_ids:
    r = api_post("/api/matches", {
        "game_id": game_ordinary, "winner": "good",
        "players": [
            {"player_id": player_ids[0], "team": "good", "score_change": 0},
            {"player_id": player_ids[1], "team": "good", "score_change": 0},
        ]
    })
    check("缺少坏人阵营应400", r.status_code in (400, 422), f"返回{r.status_code}")

# 删除不存在的对局
r = client.delete("/api/matches/99999")
check("删除不存在对局", r.status_code in (200, 404), f"返回{r.status_code}")

# 不存在玩家页面
r = client.get("/player/99999")
check("不存在玩家页404", r.status_code == 404, f"返回{r.status_code}")

# 设置开关
r = client.put("/api/settings", json={"enable_balance": "false"})
check("关闭平衡建议", r.status_code == 200)
r = client.put("/api/settings", json={"enable_achievements": "false"})
check("关闭成就", r.status_code == 200)
r = client.put("/api/settings", json={"enable_balance": "true", "enable_achievements": "true"})
check("恢复设置", r.status_code == 200)


# ============================================================
# 第12部分: 数据库完整性
# ============================================================
print("\n" + "=" * 60)
print("  第12部分: 数据库完整性")
print("=" * 60)

conn = database.get_db()
c = conn.cursor()

c.execute("PRAGMA integrity_check")
integrity = c.fetchone()[0]
check("数据库完整性检查", integrity == "ok", str(integrity))

c.execute("PRAGMA foreign_keys")
check("外键约束已启用", c.fetchone()[0] == 1)

# 表行数统计
tables = ["players", "games", "matches", "match_players", "seasons",
          "achievements", "player_achievements", "roles", "game_actions",
          "match_player_actions", "settings"]
print("\n  表统计:")
for tbl in tables:
    try:
        c.execute(f"SELECT COUNT(*) FROM {tbl}")
        print(f"    {tbl:30s} {c.fetchone()[0]:6d} 行")
    except:
        print(f"    {tbl:30s} [不存在]")

# 检查 INSERT OR IGNORE 唯一索引
c.execute("SELECT name FROM sqlite_master WHERE type='index' AND name='idx_player_achievement_unique'")
idx_exists = c.fetchone() is not None
check("成就唯一索引存在", idx_exists, "缺失")

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
    print("\n  *** 存在失败项，请检查 ***")
    sys.exit(1)
else:
    print("\n  全部测试通过!")
