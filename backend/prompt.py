"""
AI 财务分析 Prompt 模块
将结构化消费数据注入专业理财 Prompt，生成 Markdown 格式的财务诊断报告。
"""


def build_financial_prompt(user_data: dict) -> str:
    """
    根据用户月度账单聚合数据，构建发送给大模型的 Prompt。

    参数
    ----
    user_data : dict
        {
            "year_month": 202605,
            "total_income": 3500.00,
            "total_expense": 2100.00,
            "balance": 1400.00,
            "budget": 3000.00,
            "budget_remaining": 900.00,
            "income_breakdown": [
                {"category": "生活费", "amount": 2500.00, "percent": 71.4},
                {"category": "兼职收入", "amount": 1000.00, "percent": 28.6}
            ],
            "expense_breakdown": [
                {"category": "餐饮", "amount": 800.00, "percent": 38.1},
                {"category": "交通", "amount": 400.00, "percent": 19.0},
                ...
            ],
            "daily_trend": [
                {"date": "2026-05-01", "income": 0, "expense": 45.00},
                ...
            ],
            "top_expenses": [
                {"date": "2026-05-04", "category": "购物", "amount": 2499.00, "remark": "购买平板电脑"},
                ...
            ]
        }
    """

    month_label = _format_month(user_data["year_month"])

    prompt = f"""你是一位持有 CFA 证书的专业理财顾问，拥有 10 年个人财务管理经验，同时精通行为经济学与消费心理学。请根据以下用户的{month_label}财务数据，生成一份专业、详尽的月度财务诊断报告。

在分析时，请运用以下经济学与心理学理论框架：
1. **恩格尔定律与恩格尔系数**：食品支出占总消费支出的比重。根据联合国标准，恩格尔系数 40%-50% 为小康水平，30%-40% 为相对富裕。对于学生群体，餐饮占比 40%-60% 完全正常，不应简单判定为"过高"。
2. **50/30/20 法则**：国际通行的个人预算框架——50% 用于必需开支（含餐饮、住房、交通），30% 用于非必需消费，20% 用于储蓄。
3. **心理账户理论**（Mental Accounting）：人们会为不同来源的钱设立不同的"心理账户"，如生活费 vs 兼职收入，导致消费决策差异。
4. **锚定效应**（Anchoring）：人们在消费决策中会受到初始参考值的影响，如"原价 100 现价 60"会让人产生捡便宜的错觉。
5. **损失厌恶**（Loss Aversion）：人们对损失的痛苦感约是同等收益快乐感的 2 倍，这影响储蓄和消费决策。
6. **当下偏误**（Present Bias）：人们倾向于高估即时满足的价值，低估长期储蓄的重要性。

## 用户财务数据概览

### 月度总览
- **总收入**：{user_data['total_income']:.2f} 元
- **总支出**：{user_data['total_expense']:.2f} 元
- **月度结余**：{user_data['balance']:.2f} 元
- **预算金额**：{user_data['budget']:.2f} 元
- **预算剩余**：{user_data['budget_remaining']:.2f} 元
- **预算使用率**：{_budget_percent(user_data):.1f}%

### 收入构成
{_format_breakdown(user_data['income_breakdown'])}

### 支出构成
{_format_breakdown(user_data['expense_breakdown'])}

### 每日收支趋势
{_format_daily_trend(user_data.get('daily_trend', []))}

### 大额消费记录（单笔 > 100 元）
{_format_top_expenses(user_data.get('top_expenses', []))}

---

## 报告要求

请严格按照以下结构生成 Markdown 格式报告，使用"##"作为一级标题，"###"作为二级标题：

## 一、{month_label}财务总览
用 2-3 句话概括本月整体财务状况，包括总收入、总支出、结余率，并用箭头（↑/↓）标注与预算的对比。

## 二、消费结构分析
### 2.1 支出分类占比
分析各项支出占比，重点关注非必需消费（购物、娱乐）的占比。餐饮作为日常必需开支，占比 40%-60% 属于正常范围，不应简单地判定为"过高"。只有当餐饮绝对金额远超当地物价水平，或餐饮占比超过 70% 挤占其他必要开支时，才需提醒。

### 2.2 收入来源分析
分析收入来源的多样性和稳定性，评估是否需要拓展收入渠道。

### 2.3 大额消费合理性评估
逐一分析大额消费的必要性和合理性，给出建议。

## 三、消费行为诊断
### 3.1 不理性消费提醒
如果存在高频小额消费（如每日咖啡、奶茶）、冲动消费等模式，请明确指出并量化。结合"当下偏误"（Present Bias）和"锚定效应"分析这些消费行为背后的心理机制。

### 3.2 预算执行情况
分析预算使用率是否健康（建议 60%-85%），给出预算调整建议。运用"心理账户理论"分析用户对不同收入来源（如生活费 vs 兼职收入）的消费态度是否存在差异。

### 3.3 消费趋势分析
根据每日收支趋势，分析是否存在月末透支、月初冲动消费等问题。

### 3.4 行为经济学洞察
运用"损失厌恶"和"沉没成本"等理论，分析用户是否存在以下非理性消费行为：
- 因为"已经花了钱"而继续消费（如自助餐吃到撑）
- 因为"打折"而购买不需要的东西
- 对小额消费不在意但对大额消费过度谨慎的心理账户偏差
- 结合恩格尔系数，评估用户的消费结构是否健康

## 四、理财建议与下月规划
### 4.1 短期优化建议
给出 3-5 条具体的、可执行的省钱建议，每条建议包含预估节省金额。

### 4.2 下月预算分配建议
根据本月消费模式，给出下月各分类的预算分配建议（使用表格）。

### 4.3 长期理财目标与行为矫正
结合用户学生/职场新人身份，给出 1-2 条长期理财建议（如储蓄目标、投资启蒙等）。针对分析中发现的行为经济学偏差，给出具体的心理矫正策略（如设置自动储蓄对抗"当下偏误"、建立 24 小时消费冷静期对抗"锚定效应"、合并"心理账户"统一管理收支等）。

## 五、财务健康评分
给出一个 0-100 的财务健康评分，并简要说明评分理由。

---

**重要注意事项**：
1. 使用中国大陆的消费习惯和物价水平作为参考标准。
2. 语气亲切专业，像朋友一样给出建议，但数据必须严谨。
3. 金额全部以人民币（元）为单位。
4. 如果某项数据为空或无记录，请如实说明，不要编造。
5. 报告末尾加上免责声明："> ⚠️ 以上建议由 AI 生成，仅供参考，不构成专业财务建议。"
6. 直接输出 Markdown 内容，不要包含"```markdown"代码块包裹。
7. **排版格式要求**：
   - 段落之间最多空一行，不要连续空多行。
   - 各章节标题与正文之间不空行，保持紧凑。
   - 列表项之间不空行，紧凑排列。
   - 表格前不空行，表头分隔行必须使用 `|:---|:---|` 格式。
   - 总体风格：信息密度高，排版紧凑，适合屏幕阅读。
8. **关于餐饮占比的正确认知**：餐饮（一日三餐）本身就是人们日常开支的最大头，这是完全正常的。
   - 恩格尔系数（食品支出占比）在 40%-60% 对学生群体完全正常，根据联合国标准属于小康水平。
   - 只有当餐饮绝对金额远超当地物价水平，或餐饮占比超过 70% 挤占其他必要开支时，才需关注。
   - 分析时应重点关注：非必需消费（购物、娱乐等）的占比是否合理，而非一味批评餐饮占比高。
   - 如果餐饮占比高但其他消费控制得当、整体结余良好，应给予肯定而非批评。
9. **运用 50/30/20 法则**：将用户收入按 50% 必需 / 30% 非必需 / 20% 储蓄的框架进行对比分析，但不机械套用，需结合学生身份的实际特点灵活调整。
10. **行为经济学理论应用**：在分析消费行为时，主动运用心理账户、锚定效应、损失厌恶、当下偏误等理论解释用户的消费模式，让分析更具深度和说服力。"""

    return prompt


def _format_month(year_month: int) -> str:
    """将 202605 格式化为 2026年5月"""
    text = str(year_month)
    year = text[:4]
    month = str(int(text[4:6]))
    return f"{year}年{month}月"


def _format_breakdown(items: list) -> str:
    """格式化收支明细"""
    if not items:
        return "暂无数据"
    lines = []
    for item in items:
        lines.append(f"- {item['category']}：{item['amount']:.2f} 元（占比 {item['percent']:.1f}%）")
    return "\n".join(lines)


def _format_daily_trend(trend: list) -> str:
    """格式化每日趋势摘要"""
    if not trend:
        return "暂无数据"
    # 只展示关键信息：最高支出日、最高收入日
    max_expense_day = max(trend, key=lambda x: x.get("expense", 0))
    max_income_day = max(trend, key=lambda x: x.get("income", 0))

    total_days = len(trend)
    days_with_expense = sum(1 for d in trend if d.get("expense", 0) > 0)
    days_with_income = sum(1 for d in trend if d.get("income", 0) > 0)

    lines = [
        f"- 共 {total_days} 天，{days_with_expense} 天有支出记录，{days_with_income} 天有收入记录",
    ]
    if max_expense_day.get("expense", 0) > 0:
        lines.append(f"- 单日最高支出：{max_expense_day['date']}（{max_expense_day['expense']:.2f} 元）")
    if max_income_day.get("income", 0) > 0:
        lines.append(f"- 单日最高收入：{max_income_day['date']}（{max_income_day['income']:.2f} 元）")
    return "\n".join(lines)


def _format_top_expenses(expenses: list) -> str:
    """格式化大额消费"""
    if not expenses:
        return "本月无超过 100 元的大额消费记录"
    lines = []
    for item in expenses:
        remark = f"（{item['remark']}）" if item.get('remark') else ""
        lines.append(f"- {item['date']} | {item['category']} | {item['amount']:.2f} 元 {remark}")
    return "\n".join(lines)


def _budget_percent(user_data: dict) -> float:
    """计算预算使用率"""
    if user_data.get("budget", 0) > 0:
        return (user_data["total_expense"] / user_data["budget"]) * 100
    return 0.0


def build_yearly_prompt(user_data: dict) -> str:
    """
    构建年度财务分析 Prompt。

    参数
    ----
    user_data : dict
        {
            "year": 2026,
            "year_total_income": 42000.00,
            "year_total_expense": 28000.00,
            "year_balance": 14000.00,
            "monthly_summary": [
                {
                    "month": "2026-01",
                    "income": 3500, "expense": 2100, "balance": 1400,
                    "budget": 3000, "budget_usage": 70.0,
                    "top_expense_cat": "餐饮", "top_expense_amount": 800
                },
                ...
            ],
            "category_annual": [
                {"category": "餐饮", "total": 9600, "avg_monthly": 800, "percent": 34.3},
                ...
            ],
            "top_expenses": [...],
            "monthly_balance_trend": [1400, -200, 800, ...]  # 每月结余
        }
    """

    year = user_data["year"]

    # 月度摘要表格
    monthly_rows = []
    for m in user_data.get("monthly_summary", []):
        month_short = m["month"][5:7] + "月"  # "2026-01" -> "01月"
        budget_usage_str = f"{m['budget_usage']:.0f}%"
        flag = "⚠️ 超支" if m["budget_usage"] > 100 else ("✅" if m["budget_usage"] < 80 else "⚡")
        monthly_rows.append(
            f"| {month_short} | {m['income']:.0f} | {m['expense']:.0f} | {m['balance']:.0f} | "
            f"{m['budget']:.0f} | {budget_usage_str} {flag} |"
        )

    # 分类年度汇总
    cat_lines = []
    for c in user_data.get("category_annual", []):
        cat_lines.append(f"- {c['category']}：{c['total']:.0f} 元（月均 {c['avg_monthly']:.0f} 元，占比 {c['percent']:.1f}%）")

    # 大额消费
    top_expenses_str = _format_top_expenses(user_data.get("top_expenses", []))

    # 月度结余趋势
    balance_trend = user_data.get("monthly_balance_trend", [])
    balance_desc = "、".join([f"{v:.0f}" for v in balance_trend])

    prompt = f"""你是一位持有 CFA 证书的专业理财顾问，拥有 10 年个人财务管理经验，同时精通行为经济学与消费心理学。请根据以下用户{year}年全年财务数据，生成一份专业的年度财务分析报告。

在分析时，请运用以下经济学与心理学理论框架：
1. **恩格尔定律与恩格尔系数**：食品支出占总消费支出的比重。根据联合国标准，恩格尔系数 40%-50% 为小康水平，30%-40% 为相对富裕。对于学生群体，餐饮占比 40%-60% 完全正常，不应简单判定为"过高"。
2. **50/30/20 法则**：国际通行的个人预算框架——50% 用于必需开支（含餐饮、住房、交通），30% 用于非必需消费，20% 用于储蓄。
3. **心理账户理论**（Mental Accounting）：人们会为不同来源的钱设立不同的"心理账户"，如生活费 vs 兼职收入，导致消费决策差异。
4. **锚定效应**（Anchoring）：人们在消费决策中会受到初始参考值的影响，如"原价 100 现价 60"会让人产生捡便宜的错觉。
5. **损失厌恶**（Loss Aversion）：人们对损失的痛苦感约是同等收益快乐感的 2 倍，这影响储蓄和消费决策。
6. **当下偏误**（Present Bias）：人们倾向于高估即时满足的价值，低估长期储蓄的重要性。

## 用户{year}年财务数据概览

### 年度总览
- **年度总收入**：{user_data['year_total_income']:.2f} 元
- **年度总支出**：{user_data['year_total_expense']:.2f} 元
- **年度结余**：{user_data['year_balance']:.2f} 元
- **结余率**：{(user_data['year_balance'] / user_data['year_total_income'] * 100) if user_data['year_total_income'] > 0 else 0:.1f}%
- **最高支出月**：{user_data.get('peak_month', '无')}

### 月度收支明细

| 月份 | 收入 | 支出 | 结余 | 预算 | 预算使用率 |
|------|------|------|------|------|-----------|
{chr(10).join(monthly_rows)}

### 月度结余走势
{balance_desc}

### 年度分类支出汇总
{chr(10).join(cat_lines) if cat_lines else '暂无数据'}

### 年度大额消费记录（单笔 > 200 元）
{top_expenses_str}

---

## 报告要求

请严格按照以下结构生成 Markdown 格式报告，使用"##"作为一级标题，"###"作为二级标题：

## 一、{year}年财务总览
用 3-4 句话概括全年财务表现，包括年度总收入、总支出、结余率，分析整体趋势（同比变化等）。

## 二、月度趋势分析
### 2.1 收支波动分析
分析各月收入、支出的波动规律（如开学季支出增加、寒暑假收入变化、春节红包等），找出支出最高和最低的月份。

### 2.2 预算执行情况
评估全年预算执行情况，统计超支月份数量，分析超支原因。

### 2.3 结余趋势
分析月度结余变化趋势，是否呈现"前松后紧"或"稳定储蓄"等模式。

## 三、消费结构深度分析
### 3.1 年度分类支出占比
分析全年各分类支出占比，与大学生平均水平（餐饮42%、数码学习19%、娱乐社交17%、服饰美妆12%）对比。注意：餐饮占比在 40%-60% 属于正常范围，不应被判定为消费结构问题。重点分析非必需消费（购物、娱乐）的占比是否合理。结合恩格尔系数评估用户的生活水平。

### 3.2 消费习惯变迁
对比年初和年末的消费结构变化，分析消费习惯是否有所改善或恶化。运用"当下偏误"和"锚定效应"理论解释消费模式的变化。

### 3.3 大额消费回顾
总结全年大额消费，分析哪些是必要投资（如学习设备），哪些是冲动消费。运用"心理账户理论"分析大额消费决策背后的心理动机。

### 3.4 行为经济学年度洞察
从行为经济学视角，总结用户全年是否存在以下消费心理偏差：
- 心理账户偏差：是否对"生活费"和"兼职收入"区别对待？
- 当下偏误：是否过度倾向于即时消费而牺牲了长期储蓄？
- 锚定效应：是否因促销、打折而产生非理性消费？
- 损失厌恶：是否因害怕"亏了"而持有不必要的消费或放弃更好的选择？

## 四、年度理财建议
### 4.1 下年度预算规划
根据全年消费模式，给出下一年的月度预算分配建议（使用表格）。

### 4.2 储蓄目标建议
基于结余率，给出合理的年度储蓄目标和实现路径。

### 4.3 投资启蒙与行为矫正建议
结合用户学生/职场新人身份，给出 1-2 条入门级理财/投资建议（如货币基金、指数基金定投等）。同时，针对发现的行为经济学偏差，给出具体的心理矫正策略（如设置自动储蓄克服"当下偏误"、建立消费冷静期对抗"锚定效应"等）。

## 五、年度财务健康评分
给出一个 0-100 的年度财务健康评分，与月度评分对比，分析进步或退步。

---

**重要注意事项**：
1. 使用中国大陆的消费习惯和物价水平作为参考标准。
2. 语气亲切专业，像朋友一样给出建议，但数据必须严谨。
3. 金额全部以人民币（元）为单位。
4. 如果某项数据为空或无记录，请如实说明，不要编造。
5. 报告末尾加上免责声明："> ⚠️ 以上建议由 AI 生成，仅供参考，不构成专业财务建议。"
6. 直接输出 Markdown 内容，不要包含"```markdown"代码块包裹。
7. **排版格式要求**：
   - 段落之间最多空一行，不要连续空多行。
   - 各章节标题与正文之间不空行，保持紧凑。
   - 列表项之间不空行，紧凑排列。
   - 表格前不空行，表头分隔行必须使用 `|:---|:---|` 格式。
   - 总体风格：信息密度高，排版紧凑，适合屏幕阅读。
8. **关于餐饮占比的正确认知**：餐饮（一日三餐）本身就是人们日常开支的最大头，这是完全正常的。
   - 恩格尔系数（食品支出占比）在 40%-60% 对学生群体完全正常，根据联合国标准属于小康水平。
   - 只有当餐饮绝对金额远超当地物价水平，或餐饮占比超过 70% 挤占其他必要开支时，才需关注。
   - 分析时应重点关注：非必需消费（购物、娱乐等）的占比是否合理，而非一味批评餐饮占比高。
   - 如果餐饮占比高但其他消费控制得当、整体结余良好，应给予肯定而非批评。
9. **运用 50/30/20 法则**：将用户收入按 50% 必需 / 30% 非必需 / 20% 储蓄的框架进行对比分析，但不机械套用，需结合学生身份的实际特点灵活调整。
10. **行为经济学理论应用**：在分析消费行为时，主动运用心理账户、锚定效应、损失厌恶、当下偏误等理论解释用户的消费模式，让分析更具深度和说服力。"""

    return prompt