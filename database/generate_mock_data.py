#!/usr/bin/env python3
"""
模拟数据生成脚本
生成 5 个用户画像 × 12 个月（2025-07 ~ 2026-06）的逼真账单数据。

用户画像（基于 2025 大学生消费调查报告真实数据）：
  - lsy:       实习打工族，月入 3500，咖啡依赖，实习打车多
  - zhangsan:  数码游戏男孩，月入 3500，游戏充值 + 数码外设
  - lisi:      高收入实习白领，月入 6500，社交娱乐丰富
  - xiaomei:   时尚美妆女孩，月入 3500，美妆护肤 + 下午茶
  - xiaowang:  节俭学霸，月入 1600，食堂为主，极少娱乐

运行：python3 generate_mock_data.py > mock_data.sql
"""

import random
import hashlib
from datetime import date, timedelta

random.seed(42)  # 固定随机种子，保证可复现

# ---------- 密码哈希 (bcrypt 模拟) ----------
PASSWORD_HASH = "$2b$12$eUmPE/DBdMK1v4FHDvuwh.ltCGA2d1j20slhlaC9dCcj2WHXjiIOi"

# ---------- 基础分类 ----------
CATEGORIES = [
    (1, "餐饮", "expense"),
    (2, "购物", "expense"),
    (3, "娱乐", "expense"),
    (4, "交通", "expense"),
    (5, "学习", "expense"),
    (6, "工资", "income"),
    (7, "奖学金", "income"),
    (8, "生活费", "income"),
    (9, "兼职收入", "income"),
]

# ---------- 时间范围 ----------
START_DATE = date(2025, 7, 1)
END_DATE = date(2026, 6, 30)
MONTHS = [(2025, m) for m in range(7, 13)] + [(2026, m) for m in range(1, 7)]


def ym(y, m):
    """year_month 格式 YYYYMM"""
    return y * 100 + m


def days_in_month(y, m):
    if m == 12:
        return (date(y + 1, 1, 1) - date(y, m, 1)).days
    return (date(y, m + 1, 1) - date(y, m, 1)).days


def rand_date(y, m, day=None):
    """生成某月某日，day 为 None 则随机"""
    max_d = days_in_month(y, m)
    d = day if day is not None else random.randint(1, max_d)
    return date(y, m, d)


def pick(choices, weights):
    """带权重的随机选择"""
    r = random.random()
    acc = 0
    for c, w in zip(choices, weights):
        acc += w
        if r <= acc:
            return c
    return choices[-1]


# ============================================================
# 用户画像定义
# ============================================================

class Persona:
    def __init__(self, user_id, username, nickname, description, budget, incomes, daily_meals, monthly_specials, weekly_patterns):
        self.user_id = user_id
        self.username = username
        self.nickname = nickname
        self.description = description
        self.budget = budget          # 每月预算
        self.incomes = incomes        # [(日偏移, 金额, 备注, category_id)]
        self.daily_meals = daily_meals  # {"早餐": (min, max), "午餐": (min, max), "晚餐": (min, max)}
        self.monthly_specials = monthly_specials  # 每月特殊消费 [(category_id, min, max, 概率, 备注模板)]
        self.weekly_patterns = weekly_patterns  # [(category_id, min, max, 每周次数, 备注)]


PERSONAS = [
    Persona(
        user_id=1, username="lsy", nickname="实习打工族",
        description="大三学生，每周3天实习，靠家教补贴生活费，爱喝咖啡",
        budget=3000,
        incomes=[
            (8, 2500, "父母生活费", 8),
            (20, 1000, "家教兼职工资", 9),
        ],
        daily_meals={"早餐": (5, 10), "午餐": (12, 20), "晚餐": (15, 30)},
        monthly_specials=[
            (2, 50, 200, 0.6, "淘宝买衣服"),       # 购物
            (3, 25, 80, 0.4, "电影票/聚餐"),        # 娱乐
            (5, 30, 120, 0.3, "买书/学习资料"),      # 学习
        ],
        weekly_patterns=[
            (1, 9, 15, 3, "瑞幸咖啡"),               # 咖啡 3x/周
            (4, 35, 60, 2, "打车去实习"),             # 交通 2x/周
        ],
    ),
    Persona(
        user_id=2, username="zhangsan", nickname="数码游戏男孩",
        description="大二计算机系，沉迷电竞和数码产品，接设计私单赚零花钱",
        budget=2500,
        incomes=[
            (10, 2500, "父母生活费", 8),
            (20, 1000, "兼职设计稿酬", 9),
        ],
        daily_meals={"早餐": (5, 10), "午餐": (12, 22), "晚餐": (15, 28)},
        monthly_specials=[
            (2, 50, 300, 0.5, "买外设/键帽"),        # 购物
            (3, 128, 648, 0.5, "游戏充值/皮肤"),      # 娱乐
            (5, 20, 80, 0.3, "买教材/网课"),          # 学习
            (2, 800, 3000, 0.08, "购买数码产品"),      # 大额数码（偶尔）
        ],
        weekly_patterns=[
            (1, 9, 15, 2, "瑞幸咖啡"),               # 咖啡 2x/周
            (4, 15, 40, 1, "打车/地铁"),              # 交通 1x/周
        ],
    ),
    Persona(
        user_id=3, username="lisi", nickname="高收入实习白领",
        description="研二，大厂实习，收入高，社交活跃，周末剧本杀爱好者",
        budget=4000,
        incomes=[
            (8, 6000, "实习工资", 6),
            (18, 500, "校内勤工助学", 9),
        ],
        daily_meals={"早餐": (8, 15), "午餐": (20, 35), "晚餐": (20, 40)},
        monthly_specials=[
            (2, 100, 500, 0.7, "买衣服/鞋子"),        # 购物
            (3, 200, 400, 0.6, "周末剧本杀"),          # 娱乐
            (3, 80, 200, 0.5, "朋友聚餐"),             # 娱乐
            (5, 50, 200, 0.3, "买专业书"),             # 学习
        ],
        weekly_patterns=[
            (1, 12, 18, 5, "瑞幸/Manner咖啡"),       # 咖啡 每天
            (4, 40, 80, 2, "打车上下班"),              # 交通 2x/周
        ],
    ),
    Persona(
        user_id=4, username="xiaomei", nickname="时尚美妆女孩",
        description="大二艺术系，兼职模特，小红书重度用户，注重形象管理",
        budget=3000,
        incomes=[
            (5, 2000, "父母生活费", 8),
            (15, 1500, "兼职模特薪酬", 9),
        ],
        daily_meals={"早餐": (8, 12), "午餐": (15, 25), "晚餐": (18, 35)},
        monthly_specials=[
            (2, 200, 500, 0.8, "护肤品/化妆品"),       # 购物
            (2, 100, 400, 0.7, "买衣服"),             # 购物
            (3, 30, 80, 0.5, "看电影"),               # 娱乐
            (3, 80, 200, 0.4, "闺蜜聚餐"),             # 娱乐
            (2, 80, 250, 0.5, "美甲/美发"),            # 购物
        ],
        weekly_patterns=[
            (1, 15, 22, 3, "喜茶/霸王茶姬"),         # 奶茶 3x/周
            (1, 25, 60, 2, "下午茶甜品"),             # 下午茶 2x/周
            (4, 15, 35, 2, "打车/地铁"),              # 交通 2x/周
        ],
    ),
    Persona(
        user_id=5, username="xiaowang", nickname="节俭学霸",
        description="大四考研党，家庭经济一般，靠奖学金和助学金，坚持记账，极少娱乐",
        budget=1500,
        incomes=[
            (3, 1200, "父母生活费", 8),
            (15, 400, "奖学金/助学金", 7),
        ],
        daily_meals={"早餐": (3, 6), "午餐": (8, 14), "晚餐": (10, 16)},
        monthly_specials=[
            (5, 30, 120, 0.6, "买考研资料/网课"),      # 学习
            (2, 20, 80, 0.3, "买日用品/衣服"),         # 购物
            (3, 15, 40, 0.2, "偶尔看电影"),            # 娱乐
        ],
        weekly_patterns=[
            (4, 2, 6, 3, "公交/地铁"),                # 交通 3x/周
        ],
    ),
]


def generate_records():
    """生成所有账单记录，返回 [(record_id, amount, date, remark, user_id, category_id)]"""
    records = []
    rid = 10000

    for p in PERSONAS:
        for (y, m) in MONTHS:
            ndays = days_in_month(y, m)
            month_str = f"{y}-{m:02d}"

            # ---- 收入 ----
            for day_offset, amount, remark, cat_id in p.incomes:
                # 随机微调 +-5%
                adj = amount * random.uniform(0.95, 1.05)
                d = min(day_offset, ndays)
                records.append((rid, round(adj, 2), rand_date(y, m, d), remark, p.user_id, cat_id))
                rid += 1

            # ---- 每日三餐 ----
            for day in range(1, ndays + 1):
                for meal, (lo, hi) in p.daily_meals.items():
                    amt = round(random.uniform(lo, hi), 2)
                    # 随机波动：偶尔贵一点或便宜一点
                    if random.random() < 0.15:
                        amt = round(amt * random.uniform(0.6, 1.5), 2)
                    records.append((rid, amt, date(y, m, day), f"{month_str} {meal}", p.user_id, 1))
                    rid += 1

            # ---- 每周模式 ----
            for cat_id, lo, hi, freq, remark in p.weekly_patterns:
                weeks = ndays // 7
                for _ in range(weeks * freq):
                    amt = round(random.uniform(lo, hi), 2)
                    d = random.randint(1, ndays)
                    records.append((rid, amt, date(y, m, d), remark, p.user_id, cat_id))
                    rid += 1

            # ---- 每月特殊消费 ----
            for cat_id, lo, hi, prob, remark_template in p.monthly_specials:
                if random.random() < prob:
                    amt = round(random.uniform(lo, hi), 2)
                    d = random.randint(1, ndays)
                    records.append((rid, amt, date(y, m, d), remark_template, p.user_id, cat_id))
                    rid += 1

    return records


def generate_sql(records):
    """生成 SQL 文件"""
    lines = []
    lines.append("-- =========================================")
    lines.append("-- Smart Ledger Mock 数据脚本（自动生成）")
    lines.append("-- 5 用户画像 × 12 个月（2025-07 ~ 2026-06）")
    lines.append("-- 基于 2025 大学生消费调查报告真实数据")
    lines.append("-- =========================================")
    lines.append("")
    lines.append("SET FOREIGN_KEY_CHECKS = 0;")
    lines.append("TRUNCATE TABLE `bill_record`;")
    lines.append("TRUNCATE TABLE `ai_report`;")
    lines.append("TRUNCATE TABLE `monthly_budget`;")
    lines.append("TRUNCATE TABLE `user`;")
    lines.append("TRUNCATE TABLE `category`;")
    lines.append("SET FOREIGN_KEY_CHECKS = 1;")
    lines.append("")

    # 用户
    lines.append("-- 用户")
    for p in PERSONAS:
        lines.append(f"INSERT INTO `user` (`user_id`, `username`, `register_time`, `password`) VALUES")
        lines.append(f"({p.user_id}, '{p.username}', '2025-01-01 10:00:00', '{PASSWORD_HASH}');")
    lines.append("")

    # 分类
    lines.append("-- 分类")
    for cat_id, name, typ in CATEGORIES:
        lines.append(f"INSERT INTO `category` (`category_id`, `category_name`, `type`) VALUES")
        lines.append(f"({cat_id}, '{name}', '{typ}');")
    lines.append("")

    # 预算
    lines.append("-- 月度预算")
    for p in PERSONAS:
        for (y, m) in MONTHS:
            lines.append(f"INSERT INTO `monthly_budget` (`user_id`, `year_month`, `amount`) VALUES")
            lines.append(f"({p.user_id}, {ym(y,m)}, {p.budget:.2f});")
    lines.append("")

    # 账单记录（分批插入，每批 500 条）
    lines.append("-- 账单记录")
    batch_size = 500
    for i in range(0, len(records), batch_size):
        batch = records[i:i + batch_size]
        lines.append("INSERT INTO `bill_record` (`record_id`, `amount`, `date`, `remark`, `user_id`, `category_id`) VALUES")
        vals = []
        for rid, amt, dt, remark, uid, cid in batch:
            remark_escaped = remark.replace("'", "''") if remark else ""
            vals.append(f"({rid}, {amt:.2f}, '{dt}', '{remark_escaped}', {uid}, {cid})")
        lines.append(",\n".join(vals) + ";")
        lines.append("")

    lines.append("COMMIT;")
    return "\n".join(lines)


# ============================================================
# 打印用户画像统计
# ============================================================
def print_stats(records):
    """打印每个用户、每个月的收支统计"""
    from collections import defaultdict

    # 按用户+月份聚合
    user_month = defaultdict(lambda: {"income": 0.0, "expense": 0.0, "by_cat": defaultdict(float)})
    for rid, amt, dt, remark, uid, cid in records:
        key = (uid, dt.year * 100 + dt.month)
        cat_info = next((c for c in CATEGORIES if c[0] == cid), None)
        if cat_info:
            typ = cat_info[2]
            if typ == "income":
                user_month[key]["income"] += amt
            else:
                user_month[key]["expense"] += amt
            user_month[key]["by_cat"][cat_info[1]] += amt

    print("=" * 80)
    print("用户画像统计（月度均值）")
    print("=" * 80)
    for p in PERSONAS:
        uid = p.user_id
        totals = {"income": 0.0, "expense": 0.0, "by_cat": defaultdict(float)}
        count = 0
        for (u, ym_key), data in user_month.items():
            if u == uid:
                totals["income"] += data["income"]
                totals["expense"] += data["expense"]
                for c, v in data["by_cat"].items():
                    totals["by_cat"][c] += v
                count += 1
        if count == 0:
            continue
        n = count
        avg_income = totals["income"] / n
        avg_expense = totals["expense"] / n
        print(f"\n[{p.nickname}] {p.username} - {p.description}")
        print(f"  月均收入: ¥{avg_income:.0f}    月均支出: ¥{avg_expense:.0f}    结余: ¥{avg_income - avg_expense:.0f}")
        for c, v in sorted(totals["by_cat"].items(), key=lambda x: x[1], reverse=True):
            print(f"    {c}: ¥{v/n:.0f}/月 ({v/totals['expense']*100:.1f}%)" if c in ["餐饮","购物","娱乐","交通","学习"] else f"    {c}: ¥{v/n:.0f}/月")


if __name__ == "__main__":
    records = generate_records()
    print(f"共生成 {len(records)} 条账单记录")
    print_stats(records)

    sql = generate_sql(records)
    with open("/Users/zyl/finance-management-system/database/mock_data.sql", "w", encoding="utf-8") as f:
        f.write(sql)
    print(f"\nSQL 文件已写入 mock_data.sql ({len(sql)} 字符)")