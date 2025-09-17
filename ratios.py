# -*- coding: utf-8 -*-
# ratios.py
from dataclasses import dataclass
from typing import Optional, Dict, Any, List

@dataclass
class FinancialInputs:
    sales: float = 0.0
    cogs: float = 0.0
    opex: float = 0.0
    interest_expense: float = 0.0
    tax_expense: float = 0.0
    net_income: Optional[float] = None

    current_assets: float = 0.0
    inventory: float = 0.0
    cash: float = 0.0
    accounts_receivable: float = 0.0
    accounts_payable: float = 0.0
    current_liabilities: float = 0.0
    total_assets: float = 0.0
    total_liabilities: float = 0.0
    equity: float = 0.0

    prev_total_assets: Optional[float] = None
    prev_inventory: Optional[float] = None
    prev_accounts_receivable: Optional[float] = None
    prev_accounts_payable: Optional[float] = None

    cfo: float = 0.0


# ---------------- أدوات مساعدة ----------------
def safe_div(n, d) -> Optional[float]:
    try:
        if d is None or d == 0:
            return None
        return n / d
    except Exception:
        return None

def avg(curr: float, prev: Optional[float]) -> float:
    if prev is None or prev == 0:
        return curr
    return (curr + prev) / 2.0

def compute_derived(fi: FinancialInputs) -> Dict[str, float]:
    ebit = (fi.sales - fi.cogs - fi.opex)
    net_income = fi.net_income if fi.net_income is not None else (ebit - fi.interest_expense - fi.tax_expense)
    return {"ebit": ebit, "net_income": net_income}

# ---------------- تنسيق الأرقام ----------------
def fmt_number(x: Optional[float], is_percent: bool = False) -> str:
    """تهيئة الأرقام بفواصل الآلاف وعشريتين. إذا نسبة مئوية نضيف %"""
    if x is None:
        return "—"
    if is_percent:
        return f"{x*100:,.2f}%"
    return f"{x:,.2f}"

def format_equation(ar: str, en: str, numbers: str) -> Dict[str, str]:
    return {
        "ar": f"<span style='font-family:Cairo, Tajawal, sans-serif;'>📐 <b>المعادلة:</b> {ar}<br>🔢 <b>بالتعويض:</b> {numbers}</span>",
        "en": f"<span style='font-family:Cairo, sans-serif;'>📐 <b>Equation:</b> {en}<br>🔢 <b>Substitution:</b> {numbers}</span>"
    }

# ---------------- التفسيرات ----------------
def interpret_current_ratio(x): 
    if x is None: return ("لا يمكن تقييم النسبة.", "Not enough data.")
    if x < 1: return ("منخفضة (<1).", "Low (<1).")
    if 1 <= x <= 2: return ("ضمن النطاق (1–2).", "Acceptable (1–2).")
    return ("مرتفعة (>2).", "High (>2).")

def interpret_quick_ratio(x):
    if x is None: return ("لا يمكن تقييم النسبة.", "Not enough data.")
    if x < 0.8: return ("ضعيفة (<0.8).", "Weak (<0.8).")
    if 0.8 <= x < 1: return ("متوسطة (≈1).", "Moderate (≈1).")
    return ("جيدة (≥1).", "Good (≥1).")

def interpret_cash_ratio(x):
    if x is None: return ("لا يمكن تقييم النسبة.", "Not enough data.")
    if x < 0.2: return ("ضعيفة (<0.2).", "Weak (<0.2).")
    if 0.2 <= x < 0.5: return ("متوسطة (0.2–0.5).", "Moderate (0.2–0.5).")
    return ("مطمئنة (≥0.5).", "Comfortable (≥0.5).")

def interpret_debt_ratio(x):
    if x is None: return ("لا يمكن تقييم النسبة.", "Not enough data.")
    if x > 0.6: return ("مرتفعة (>60%).", "High (>60%).")
    if 0.4 <= x <= 0.6: return ("متوازنة (40–60%).", "Balanced (40–60%).")
    return ("منخفضة (<40%).", "Low (<40%).")

def interpret_dte(x):
    if x is None: return ("لا يمكن تقييم النسبة.", "Not enough data.")
    if x > 2: return ("مرتفعة (>2).", "High (>2).")
    if 1 <= x <= 2: return ("متوسطة (1–2).", "Moderate (1–2).")
    return ("منخفضة (<1).", "Low (<1).")

def interpret_margin(x, ar, en):
    if x is None: return ("لا يمكن تقييم النسبة.", "Not enough data.")
    pct = x * 100
    if pct < 5: return (f"{ar} ضعيف (<5%).", f"{en} Weak (<5%).")
    if 5 <= pct < 15: return (f"{ar} متوسط (5–15%).", f"{en} Moderate (5–15%).")
    return (f"{ar} جيد (≥15%).", f"{en} Good (≥15%).")


# ---------------- الحساب ----------------
def compute_ratios(fi: FinancialInputs) -> List[Dict[str, Any]]:
    d = compute_derived(fi)
    ebit, net_income = d["ebit"], d["net_income"]

    avg_assets = avg(fi.total_assets, fi.prev_total_assets)
    avg_inv = avg(fi.inventory, fi.prev_inventory)
    avg_ar = avg(fi.accounts_receivable, fi.prev_accounts_receivable)
    avg_ap = avg(fi.accounts_payable, fi.prev_accounts_payable)

    current_ratio = safe_div(fi.current_assets, fi.current_liabilities)
    quick_ratio = safe_div(fi.current_assets - fi.inventory, fi.current_liabilities)
    cash_ratio = safe_div(fi.cash, fi.current_liabilities)

    debt_ratio = safe_div(fi.total_liabilities, fi.total_assets)
    dte = safe_div(fi.total_liabilities, fi.equity)
    interest_cov = safe_div(ebit, fi.interest_expense)

    gross_margin = safe_div((fi.sales - fi.cogs), fi.sales)
    operating_margin = safe_div(ebit, fi.sales)
    net_margin = safe_div(net_income, fi.sales)

    roa = safe_div(net_income, avg_assets)
    roe = safe_div(net_income, fi.equity)
    cash_conv_ratio = safe_div(fi.cfo, net_income)

    results = []

    # --- الأصول ---
    eq = format_equation("الأصول المتداولة ÷ الخصوم المتداولة", "Current Assets ÷ Current Liabilities",
                         f"{fmt_number(fi.current_assets)} ÷ {fmt_number(fi.current_liabilities)}")
    ar, en = interpret_current_ratio(current_ratio)
    results.append({
        "group":"نسب الأصول","name":"نسبة التداول","name_en":"Current Ratio",
        "value": fmt_number(current_ratio),
        "equation":eq["ar"],"equation_en":eq["en"],
        "explain":"تقيس قدرة الشركة على سداد الالتزامات قصيرة الأجل.",
        "explain_en":"Measures ability to pay short-term obligations.",
        "analysis":ar,"analysis_en":en
    })

    eq = format_equation("(الأصول المتداولة − المخزون) ÷ الخصوم المتداولة",
                         "(Current Assets − Inventory) ÷ Current Liabilities",
                         f"({fmt_number(fi.current_assets)} − {fmt_number(fi.inventory)}) ÷ {fmt_number(fi.current_liabilities)}")
    ar, en = interpret_quick_ratio(quick_ratio)
    results.append({
        "group":"نسب الأصول","name":"النسبة السريعة","name_en":"Quick Ratio",
        "value": fmt_number(quick_ratio),
        "equation":eq["ar"],"equation_en":eq["en"],
        "explain":"تستبعد المخزون لقياس السيولة الفورية.",
        "explain_en":"Excludes inventory for immediate liquidity.",
        "analysis":ar,"analysis_en":en
    })

    eq = format_equation("النقدية ÷ الخصوم المتداولة","Cash ÷ Current Liabilities",
                         f"{fmt_number(fi.cash)} ÷ {fmt_number(fi.current_liabilities)}")
    ar, en = interpret_cash_ratio(cash_ratio)
    results.append({
        "group":"نسب الأصول","name":"النسبة النقدية","name_en":"Cash Ratio",
        "value": fmt_number(cash_ratio),
        "equation":eq["ar"],"equation_en":eq["en"],
        "explain":"يقيس تغطية الخصوم بالنقد.",
        "explain_en":"Covers liabilities with cash.",
        "analysis":ar,"analysis_en":en
    })

    # --- الخصوم ---
    eq = format_equation("إجمالي الخصوم ÷ إجمالي الأصول", "Total Liabilities ÷ Total Assets",
                         f"{fmt_number(fi.total_liabilities)} ÷ {fmt_number(fi.total_assets)}")
    ar, en = interpret_debt_ratio(debt_ratio)
    results.append({
        "group":"نسب الخصوم","name":"نسبة المديونية","name_en":"Debt Ratio",
        "value": fmt_number(debt_ratio, is_percent=True),
        "equation":eq["ar"],"equation_en":eq["en"],
        "explain":"نسبة تمويل الأصول بالديون.",
        "explain_en":"Assets financed by debt.",
        "analysis":ar,"analysis_en":en
    })

    # --- المبيعات ---
    eq = format_equation("(المبيعات − تكلفة المبيعات) ÷ المبيعات",
                         "(Sales − COGS) ÷ Sales",
                         f"({fmt_number(fi.sales)} − {fmt_number(fi.cogs)}) ÷ {fmt_number(fi.sales)}")
    ar, en = interpret_margin(gross_margin,"هامش إجمالي","Gross Margin")
    results.append({
        "group":"نسب المبيعات","name":"هامش الربح الإجمالي","name_en":"Gross Margin",
        "value": fmt_number(gross_margin, is_percent=True),
        "equation":eq["ar"],"equation_en":eq["en"],
        "explain":"ربحية النشاط الأساسي.","explain_en":"Core profitability.",
        "analysis":ar,"analysis_en":en
    })

    eq = format_equation("EBIT ÷ المبيعات","EBIT ÷ Sales",
                         f"{fmt_number(ebit)} ÷ {fmt_number(fi.sales)}")
    ar, en = interpret_margin(operating_margin,"هامش التشغيل","Operating Margin")
    results.append({
        "group":"نسب المبيعات","name":"هامش التشغيل","name_en":"Operating Margin",
        "value": fmt_number(operating_margin, is_percent=True),
        "equation":eq["ar"],"equation_en":eq["en"],
        "explain":"كفاءة النشاط.","explain_en":"Operating efficiency.",
        "analysis":ar,"analysis_en":en
    })

    # --- الربحية ---
    eq = format_equation("صافي الربح ÷ المبيعات","Net Income ÷ Sales",
                         f"{fmt_number(net_income)} ÷ {fmt_number(fi.sales)}")
    ar, en = interpret_margin(net_margin,"هامش صافي","Net Margin")
    results.append({
        "group":"نسب الربحية","name":"هامش صافي الربح","name_en":"Net Profit Margin",
        "value": fmt_number(net_margin, is_percent=True),
        "equation":eq["ar"],"equation_en":eq["en"],
        "explain":"نسبة الربح الصافي.","explain_en":"Net profit ratio.",
        "analysis":ar,"analysis_en":en
    })

    eq = format_equation("صافي الربح ÷ حقوق الملكية","Net Income ÷ Equity",
                         f"{fmt_number(net_income)} ÷ {fmt_number(fi.equity)}")
    results.append({
        "group":"نسب الربحية","name":"العائد على حقوق الملكية (ROE)","name_en":"Return on Equity (ROE)",
        "value": fmt_number(roe, is_percent=True),
        "equation":eq["ar"],"equation_en":eq["en"],
        "explain":"عائد الملاك.","explain_en":"Return on equity.",
        "analysis":"أعلى أفضل","analysis_en":"Higher is better"
    })

    # --- الربحية (تكملة) ---
    eq = format_equation("صافي الربح ÷ إجمالي الأصول","Net Income ÷ Total Assets",
                         f"{fmt_number(net_income)} ÷ {fmt_number(fi.total_assets)}")
    results.append({
        "group":"نسب الربحية","name":"العائد على الأصول (ROA)","name_en":"Return on Assets (ROA)",
        "value": fmt_number(roa, is_percent=True),
        "equation":eq["ar"],"equation_en":eq["en"],
        "explain":"يقيس كفاءة الأصول في توليد الأرباح.",
        "explain_en":"Efficiency of assets in generating profit.",
        "analysis":"أعلى أفضل","analysis_en":"Higher is better"
    })

    eq = format_equation("EBIT ÷ إجمالي الأصول","EBIT ÷ Total Assets",
                         f"{fmt_number(ebit)} ÷ {fmt_number(fi.total_assets)}")
    results.append({
        "group":"نسب الربحية","name":"مؤشر كفاءة الربح (BEP)","name_en":"Basic Earnings Power Ratio",
        "value": fmt_number(safe_div(ebit, fi.total_assets), is_percent=True),
        "equation":eq["ar"],"equation_en":eq["en"],
        "explain":"يبين قدرة الأصول على توليد أرباح تشغيلية بغض النظر عن الضرائب والفوائد.",
        "explain_en":"Ability of assets to generate EBIT regardless of tax/interest.",
        "analysis":"أعلى أفضل","analysis_en":"Higher is better"
    })

    # --- المديونية ---
    eq = format_equation("إجمالي الخصوم ÷ حقوق الملكية","Total Liabilities ÷ Equity",
                         f"{fmt_number(fi.total_liabilities)} ÷ {fmt_number(fi.equity)}")
    ar, en = interpret_dte(dte)
    results.append({
        "group":"نسب المديونية","name":"نسبة الدين إلى حقوق الملكية","name_en":"Debt to Equity Ratio (D/E)",
        "value": fmt_number(dte),
        "equation":eq["ar"],"equation_en":eq["en"],
        "explain":"يقيس اعتماد الشركة على الديون مقابل حقوق الملكية.",
        "explain_en":"Measures reliance on debt vs equity.",
        "analysis":ar,"analysis_en":en
    })

    eq = format_equation("EBIT ÷ مصروف الفوائد","EBIT ÷ Interest Expense",
                         f"{fmt_number(ebit)} ÷ {fmt_number(fi.interest_expense)}")
    results.append({
        "group":"نسب المديونية","name":"تغطية الفوائد","name_en":"Interest Coverage",
        "value": fmt_number(interest_cov),
        "equation":eq["ar"],"equation_en":eq["en"],
        "explain":"يبين قدرة الأرباح التشغيلية على تغطية مصروف الفوائد.",
        "explain_en":"Ability of EBIT to cover interest expense.",
        "analysis":">1 آمن، <1 خطر","analysis_en":">1 safe, <1 risky"
    })

    # --- الأصول ---
    eq = format_equation("تكلفة المبيعات ÷ متوسط المخزون","COGS ÷ Avg Inventory",
                         f"{fmt_number(fi.cogs)} ÷ {fmt_number(avg_inv)}")
    results.append({
        "group":"نسب الأصول","name":"دوران المخزون","name_en":"Inventory Turnover Ratio",
        "value": fmt_number(safe_div(fi.cogs, avg_inv)),
        "equation":eq["ar"],"equation_en":eq["en"],
        "explain":"عدد مرات بيع وتجديد المخزون خلال الفترة.",
        "explain_en":"Times inventory is sold and replaced.",
        "analysis":"أعلى أفضل","analysis_en":"Higher is better"
    })

    eq = format_equation("المبيعات ÷ متوسط الذمم المدينة","Sales ÷ Avg Accounts Receivable",
                         f"{fmt_number(fi.sales)} ÷ {fmt_number(avg_ar)}")
    results.append({
        "group":"نسب الأصول","name":"دوران الذمم المدينة","name_en":"Accounts Receivable Turnover",
        "value": fmt_number(safe_div(fi.sales, avg_ar)),
        "equation":eq["ar"],"equation_en":eq["en"],
        "explain":"عدد مرات تحصيل الذمم خلال الفترة.",
        "explain_en":"Times receivables collected during period.",
        "analysis":"أعلى أفضل","analysis_en":"Higher is better"
    })

    eq = format_equation("المبيعات ÷ الأصول الثابتة","Sales ÷ Fixed Assets",
                         f"{fmt_number(fi.sales)} ÷ {fmt_number(fi.total_assets - fi.current_assets)}")
    results.append({
        "group":"نسب الأصول","name":"دوران الأصول الثابتة","name_en":"Fixed Assets Turnover Ratio",
        "value": fmt_number(safe_div(fi.sales, fi.total_assets - fi.current_assets)),
        "equation":eq["ar"],"equation_en":eq["en"],
        "explain":"كفاءة الأصول الثابتة في توليد المبيعات.",
        "explain_en":"Efficiency of fixed assets in generating sales.",
        "analysis":"أعلى أفضل","analysis_en":"Higher is better"
    })

    # --- السوق ---
    eq = format_equation("صافي الربح ÷ عدد الأسهم","Net Income ÷ Shares Outstanding",
                         f"{fmt_number(net_income)} ÷ {fmt_number(1)}")
    results.append({
        "group":"نسب السوق","name":"ربحية السهم (EPS)","name_en":"Earnings per Share (EPS) Ratio",
        "value": fmt_number(safe_div(net_income, 1)),  # عدّل 1 → عدد الأسهم الفعلي إذا متاح
        "equation":eq["ar"],"equation_en":eq["en"],
        "explain":"يبين نصيب السهم الواحد من صافي الربح.",
        "explain_en":"Shows net income per share.",
        "analysis":"أعلى أفضل","analysis_en":"Higher is better"
    })

    eq = format_equation("الأرباح الموزعة ÷ صافي الربح","Dividends ÷ Net Income",
                         f"{fmt_number(fi.cfo)} ÷ {fmt_number(net_income)}")
    results.append({
        "group":"نسب السوق","name":"نسبة التوزيعات","name_en":"Payout Ratio",
        "value": fmt_number(safe_div(fi.cfo, net_income), is_percent=True),
        "equation":eq["ar"],"equation_en":eq["en"],
        "explain":"يبين نسبة صافي الربح التي توزع كأرباح نقدية.",
        "explain_en":"Portion of net income paid as dividends.",
        "analysis":"40-60% مناسب","analysis_en":"40-60% reasonable"
    })

    return results
