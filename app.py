# app.py
import pandas as pd
import streamlit as st
import plotly.express as px
from ratios import FinancialInputs, compute_ratios
import os
import pandas as pd


simplified_views = {
    "Current Ratio": {
        "ar": "👥 تبسيط: هذه النسبة توضح إذا كانت الشركة تملك ما يكفي من الأصول المتداولة (النقدية + المدينون + المخزون) لسداد التزاماتها القصيرة (الدائنون + القروض قصيرة الأجل). كلما ارتفعت كان الوضع أفضل.",
        "en": "👥 Simple view: Measures if current assets (cash + receivables + inventory) are enough to cover short-term liabilities (payables + short-term loans). The higher, the safer."
    },
    "Quick Ratio": {
        "ar": "👥 تبسيط: مثل نسبة التداول لكن تستبعد المخزون (لأنه قد يستغرق وقتًا للتحويل لنقد). تقيس قدرة الشركة على الوفاء بالتزاماتها باستخدام النقدية والذمم المدينة فقط.",
        "en": "👥 Simple view: Like Current Ratio but excludes inventory (as it may take time to convert). Focuses on cash and receivables to cover short-term obligations."
    },
    "Cash Ratio": {
        "ar": "👥 تبسيط: أدق مقياس للسيولة، يقارن النقد والنقد المعادل (Cash & Cash Equivalents) فقط مع الخصوم المتداولة. إذا كان منخفض جدًا فهذا يشير إلى مخاطر في السداد الفوري.",
        "en": "👥 Simple view: Strict liquidity test, compares only cash and cash equivalents with current liabilities. Very low ratio may indicate immediate liquidity risk."
    },
    "Debt Ratio": {
        "ar": "👥 تبسيط: يقيس نسبة الأصول الممولة بالديون (القروض قصيرة وطويلة الأجل) مقارنة بإجمالي الأصول. إذا زادت عن 60% فهذا قد يشكل عبء مالي على الشركة.",
        "en": "👥 Simple view: Shows how much of assets are financed by debt (short & long-term loans). Above 60% can be financially risky."
    },
    "Debt to Equity Ratio (D/E)": {
        "ar": "👥 تبسيط: يقيس اعتماد الشركة على الديون (Loans) مقارنة بحقوق الملاك (Equity). ارتفاعه يعني مخاطر أكبر على الاستقرار المالي.",
        "en": "👥 Simple view: Measures reliance on debt vs equity. Higher ratio means higher financial risk."
    },
    "Interest Coverage": {
        "ar": "👥 تبسيط: يوضح إذا كانت أرباح التشغيل (Operating Profit) تكفي لتغطية مصروفات الفوائد (Interest Expense). إذا كان أقل من 1 فالشركة في خطر كبير.",
        "en": "👥 Simple view: Tells if operating profits are enough to cover interest expenses. Below 1 means financial distress."
    },
    "Gross Profit Margin": {
        "ar": "👥 تبسيط: يقيس الربح الإجمالي (الإيرادات - تكلفة المبيعات) مقارنة بالمبيعات. ارتفاعه يعني كفاءة في التسعير أو الإنتاج.",
        "en": "👥 Simple view: Gross profit (revenue - cost of goods sold) compared to sales. Higher margin = better pricing or efficiency."
    },
    "Operating Margin": {
        "ar": "👥 تبسيط: يقيس نسبة الربح بعد خصم المصاريف التشغيلية (الإيجارات + الرواتب + المصاريف الإدارية). يعطي فكرة عن كفاءة الإدارة.",
        "en": "👥 Simple view: Profit after operating expenses (rent + salaries + admin expenses). Reflects management efficiency."
    },
    "Net Profit Margin": {
        "ar": "👥 تبسيط: النسبة النهائية للربح بعد جميع المصاريف (التشغيلية + التمويلية + الضريبة). توضح كم يبقى من كل 1 ريال مبيعات كربح صافٍ.",
        "en": "👥 Simple view: Final profit after all expenses (operating + financing + taxes). Shows how much remains from each $1 of sales."
    },
    "Return on Assets (ROA)": {
        "ar": "👥 تبسيط: هل الأصول (المباني + المعدات + النقدية) تحقق عائد جيد؟ كلما ارتفعت النسبة زادت كفاءة استغلال الأصول.",
        "en": "👥 Simple view: Are assets (buildings + equipment + cash) generating good return? Higher means more efficient use of assets."
    },
    "Return on Equity (ROE)": {
        "ar": "👥 تبسيط: يقيس العائد الذي يحصل عليه الملاك (Equity Holders) على استثماراتهم. ارتفاعه مؤشر إيجابي للمستثمرين.",
        "en": "👥 Simple view: Measures return shareholders get on their equity investment. Higher is better for investors."
    },
    "Cash Conversion Ratio": {
        "ar": "👥 تبسيط: يقارن بين الأرباح المحاسبية (Net Income) والتدفق النقدي من التشغيل (Operating Cash Flow). إذا كان منخفض فقد يعني أن الأرباح ليست نقدية فعلًا.",
        "en": "👥 Simple view: Compares net income vs operating cash flow. Low ratio may mean profits are not turning into actual cash."
    },
    "Basic Earnings Power Ratio": {
        "ar": "👥 تبسيط: يقيس قدرة الأصول (المباني + المعدات) على توليد أرباح تشغيلية قبل الفوائد والضرائب. يعطي صورة عن قوة النشاط الأساسي.",
        "en": "👥 Simple view: Measures assets’ ability (buildings + equipment) to generate operating profit before interest and tax."
    },
    "Inventory Turnover Ratio": {
        "ar": "👥 تبسيط: يوضح كم مرة يتم بيع وتجديد المخزون خلال السنة. كلما ارتفع يعني أن البضاعة تتحرك بسرعة.",
        "en": "👥 Simple view: Shows how many times inventory is sold and replaced in a year. Higher = faster sales cycle."
    },
    "Accounts Receivable Turnover": {
        "ar": "👥 تبسيط: يقيس سرعة تحصيل المدينين (العملاء). ارتفاعه يعني أن الشركة تجمع أموالها بسرعة.",
        "en": "👥 Simple view: Measures how fast receivables (customers) are collected. Higher = faster collection."
    },
    "Fixed Assets Turnover Ratio": {
        "ar": "👥 تبسيط: يقيس كفاءة الأصول الثابتة (المصانع + المعدات) في توليد المبيعات.",
        "en": "👥 Simple view: Efficiency of fixed assets (plants + equipment) in generating sales."
    },
    "Earnings per Share (EPS) Ratio": {
        "ar": "👥 تبسيط: نصيب كل سهم من صافي الربح. يساعد المستثمرين في تقييم العائد من امتلاك سهم واحد.",
        "en": "👥 Simple view: Portion of net income allocated to each share. Useful for investors to assess return per share."
    },
    "Payout Ratio": {
        "ar": "👥 تبسيط: يوضح نسبة الأرباح الموزعة نقدًا على المساهمين من صافي الربح. كلما ارتفعت زاد رضا المساهمين، لكن يقل التمويل المتاح للنمو.",
        "en": "👥 Simple view: Shows portion of net income paid as dividends. Higher = happier shareholders but less reinvestment."
    }
}



# 📌 تحسينات مقترحة لكل نسبة
improvements = {
    "Current Ratio": {
        "ar": "زيادة الأصول المتداولة (النقدية + المدينون + المخزون) أو خفض الخصوم قصيرة الأجل (الدائنون + القروض قصيرة الأجل).",
        "en": "Increase current assets (cash + receivables + inventory) or reduce short-term liabilities (payables + short-term loans)."
    },
    "Quick Ratio": {
        "ar": "زيادة النقدية أو الذمم المدينة لتغطية الخصوم الفورية، مع تقليل الاعتماد على المخزون.",
        "en": "Improve cash or receivables to cover immediate liabilities, reduce reliance on inventory."
    },
    "Cash Ratio": {
        "ar": "الحفاظ على احتياطي نقدي كافٍ (Cash Reserves) لتغطية الالتزامات السريعة.",
        "en": "Maintain sufficient cash reserves to meet urgent obligations."
    },
    "Debt Ratio": {
        "ar": "تقليل الاعتماد على الديون (Loans) وزيادة التمويل الذاتي (Equity Financing).",
        "en": "Reduce reliance on debt (loans) and increase equity financing."
    },
    "Debt to Equity Ratio (D/E)": {
        "ar": "خفض الديون أو زيادة حقوق الملكية لتحقيق توازن أفضل بين الالتزامات والملاك.",
        "en": "Lower debt or raise equity for a healthier balance."
    },
    "Interest Coverage": {
        "ar": "زيادة الأرباح التشغيلية (Operating Profit) أو خفض مصروف الفوائد (Interest Expense).",
        "en": "Boost operating profits or reduce interest expenses."
    },
    "Gross Profit Margin": {
        "ar": "تحسين المبيعات (Revenue) أو خفض تكلفة المبيعات (COGS).",
        "en": "Enhance sales (revenue) or reduce cost of goods sold (COGS)."
    },
    "Operating Margin": {
        "ar": "تقليل المصاريف التشغيلية (الإيجارات + الرواتب + الإدارية) أو زيادة كفاءة التشغيل.",
        "en": "Reduce operating expenses (rent + salaries + admin) or improve operational efficiency."
    },
    "Net Profit Margin": {
        "ar": "زيادة الإيرادات أو التحكم في جميع المصروفات (التشغيلية + التمويلية + الضرائب).",
        "en": "Increase revenues or control all expenses (operating + financing + taxes)."
    },
    "Return on Assets (ROA)": {
        "ar": "زيادة الأرباح أو تحسين استغلال الأصول (المباني + المعدات + النقدية).",
        "en": "Increase profits or utilize assets (buildings + equipment + cash) more effectively."
    },
    "Return on Equity (ROE)": {
        "ar": "زيادة العائد للملاك عن طريق تحسين الربحية ورفع كفاءة إدارة الموارد.",
        "en": "Increase shareholder return by improving profitability and resource efficiency."
    },
    "Cash Conversion Ratio": {
        "ar": "تحسين التدفقات النقدية عبر تحصيل أسرع (Receivables Collection) وإدارة نفقات أفضل.",
        "en": "Improve cash flow through faster receivables collection and better expense management."
    },
        "Basic Earnings Power Ratio": {
        "ar": "زيادة كفاءة استخدام الأصول الثابتة (المصانع + المعدات) لرفع الأرباح التشغيلية.",
        "en": "Improve utilization of fixed assets (plants + equipment) to increase operating profit."
    },
    "Inventory Turnover Ratio": {
        "ar": "تحسين إدارة المخزون وتقليل البضاعة الراكدة لزيادة سرعة الدوران.",
        "en": "Enhance inventory management, reduce obsolete stock to increase turnover speed."
    },
    "Accounts Receivable Turnover": {
        "ar": "تسريع تحصيل العملاء وتقليل فترات الائتمان لتحسين التدفقات النقدية.",
        "en": "Speed up customer collections, shorten credit terms to improve cash flow."
    },
    "Fixed Assets Turnover Ratio": {
        "ar": "زيادة المبيعات أو تحسين استغلال الأصول الثابتة لرفع كفاءة الدوران.",
        "en": "Increase sales or use fixed assets more efficiently to boost turnover."
    },
    "Earnings per Share (EPS) Ratio": {
        "ar": "زيادة صافي الربح أو إعادة شراء الأسهم لرفع نصيب السهم من الأرباح.",
        "en": "Increase net income or repurchase shares to raise EPS."
    },
    "Payout Ratio": {
        "ar": "تحقيق توازن بين توزيع أرباح مناسبة للمساهمين والاحتفاظ بأرباح كافية للنمو.",
        "en": "Balance between distributing dividends and retaining earnings for growth."
    }
}

# 🎨 تنسيقات CSS شاملة + Cairo Font
st.markdown("""
    <style>
    /* الخطوط */
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@500&display=swap');

    html, body, [class*="css"] {
        font-family: 'Cairo', sans-serif !important;
        background-color: #ffffff !important;  /* خلفية فاتحة دائمًا */
    }

    /* نصوص عربية */
    .arabic {
        direction: rtl !important;
        text-align: right !important;
        font-family: 'Cairo', 'Tajawal', sans-serif;
        font-size: 16px;
        color: #212529 !important;  /* أسود */
    }

    /* نصوص إنجليزية */
    .english {
        direction: ltr;
        text-align: left;
        font-family: 'Cairo', sans-serif;
        font-size: 15px;
        color: #212529 !important;  /* أسود */
    }

    /* 📌 صندوق الشرح */
    .explanation-box {
        background: #FFCDD2 !important;   /* أحمر فاتح */
        color: #B71C1C !important;        /* أحمر غامق */
        padding: 12px;
        border-radius: 8px;
        margin: 6px 0;
        box-shadow: inset 0px 1px 3px rgba(0,0,0,0.1);
    }

    /* 📐 المعادلات */
    .equation-ar, .equation-en {
        background: #BBDEFB !important;   /* أزرق فاتح */
        color: #0D47A1 !important;        /* أزرق داكن */
        padding: 12px;
        border-radius: 8px;
        font-weight: 600;
        margin: 6px 0;
        direction: rtl !important;
        text-align: right !important;
    }

    /* 🧾 التحليل */
    .analysis-box {
        background: #C8E6C9 !important;   /* أخضر فاتح */
        color: #1B5E20 !important;        /* أخضر غامق */
        padding: 12px;
        border-radius: 8px;
        margin: 6px 0;
        font-weight: 600;
    }

    /* 👥 التبسيط */
    .simplified-box {
        background: #FFE0B2 !important;   /* برتقالي فاتح */
        color: #E65100 !important;        /* برتقالي غامق */
        padding: 12px;
        border-radius: 8px;
        margin: 6px 0;
    }

    /* 🚀 التحسين */
    .improvement-box {
        display: block;
        width: 100% !important;
        box-sizing: border-box;
        padding: 20px;
        margin: 15px 0;
        border-radius: 10px;
        
        background: linear-gradient(90deg, #FFECB3, #FFE082) !important;  /* أصفر برتقالي جذاب */
        border: 2px solid #F57C00 !important;
        color: #212121 !important;   /* أسود */
        font-weight: 700;
        font-size: 16px;
        text-align: center;
        font-family: 'Cairo', 'Tajawal', sans-serif !important;
    }

    .improvement-box p { margin: 5px 0; }
 
    .improvement-ar {
        direction: rtl !important;
        text-align: right !important;
        font-family: 'Cairo', 'Tajawal', sans-serif !important;
    }
    
    .improvement-en {
        direction: ltr !important;
        text-align: left !important;
        font-family: 'Cairo', sans-serif !important;
    }
    </style>
""", unsafe_allow_html=True)






st.set_page_config(page_title="📊 منصة تحليل النسب المالية", layout="wide")



st.title("📊  تحليل النسب المالية | Financial Ratios Platform")

st.sidebar.header("⚙️ الفلاتر")

# 🟢 تحميل البيانات

file_path = "financial_data.xlsx"  # 👈 اسم ملفك اللي بالمجلد الرئيسي

if os.path.exists(file_path):
    df = pd.read_excel(file_path)
else:
    st.error("⚠️ ملف البيانات financial_data.xlsx غير موجود، يرجى رفعه أو إضافته للمجلد.")
    st.stop()

# عرض البيانات
st.subheader("📋 البيانات المالية")
st.dataframe(df)

# 🟢 فلتر السنوات
years = df["year"].unique().tolist()
selected_years = st.sidebar.multiselect("اختر السنوات للتحليل", years, default=years)

# 🟢 أيقونات لكل مجموعة نسب
icons = {
    "نسب الأصول": "🏦",
    "نسب الخصوم": "💳",
    "نسب المبيعات": "🛒",
    "نسب الربحية": "📈",
}
tab1, tab2 = st.tabs(["🔎 نتائج التحليل", "📊 مقارنة السنوات"])

with tab1:
        
    if selected_years:
        st.subheader("🔎 نتائج التحليل")

        for year in selected_years:
            st.markdown(f"## 📅 السنة: {year}")
            row = df[df["year"] == year].iloc[0]

            # تجهيز المدخلات
            fi = FinancialInputs(
                sales=row["Revenue"],
                cogs=row["Cost of goods sold"],
                opex=row.get("Total Operating expenses", 0),
                interest_expense=row.get("Financial charges", 0),
                tax_expense=row.get("Zakat", 0),
                net_income=row["Profit/(Loss) for the period"],
                current_assets=row["Current assets"],
                inventory=row["Inventory"],
                cash=row["Cash and Bank balances"],
                accounts_receivable=row["Trade Receivable"],
                accounts_payable=row["Current liabilities"],  
                current_liabilities=row["Current liabilities"],
                total_assets=row["Total assets"],
                total_liabilities=row["Total liabilities"],
                equity=row["Owners' equity"],
                cfo=row.get("Cash flow", 0),
            )

            results = compute_ratios(fi)

            # 📊 عرض النتائج
            for group in ["نسب الأصول", "نسب الخصوم", "نسب المبيعات", "نسب الربحية"]:
                st.markdown(f"### {icons.get(group, '')} {group}")
                group_items = [r for r in results if r["group"] == group]

                for r in group_items:
                    value_display = r["value"] if r["value"] is not None else "—"

                    # 🟢 expander مع العنوان في المنتصف بخط Cairo
                    with st.expander(
                        f"{r['name']} | {r['name_en']} — {value_display}",  # 👈 بدون span هنا
                        expanded=False
                    ):

                        # ✅ العنوان المنسق يظهر دائمًا (مطوي أو مفتوح)
                        st.markdown(
                            f"""
                            <div style="text-align:center; font-family:'Cairo', sans-serif;
                                        font-size:26px; font-weight:800; color:#2C3E50;">
                                {r['name']} | {r['name_en']} —
                                <span style="color:#8E44AD;">{value_display}</span>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )


                        col1, col2 = st.columns(2)

                        # 🟦 العمود الأيمن (AR)
                        with col2:
                            st.markdown(
                                f"<div class='explanation-box arabic'><b>📌 الشرح:</b> {r['explain']}</div>",
                                unsafe_allow_html=True
                            )
                            st.markdown(
                                f"<div class='equation-ar'>📐 {r['equation']}</div>",
                                unsafe_allow_html=True
                            )
                            st.markdown(
                                f"<div class='analysis-box arabic'><b>🧾 التحليل:</b> {r['analysis']}</div>",
                                unsafe_allow_html=True
                            )
                            if r["name_en"] in simplified_views:
                                st.markdown(
                                    f"<div class='simplified-box arabic'>{simplified_views[r['name_en']]['ar']}</div>",
                                    unsafe_allow_html=True
                                )
                        
                        # 🟨 العمود الأيسر (EN)
                        with col1:
                            st.markdown(
                                f"<div class='explanation-box english'><b>📌 Explanation:</b> {r['explain_en']}</div>",
                                unsafe_allow_html=True
                            )
                            st.markdown(
                                f"<div class='equation-en'>📐 {r['equation_en']}</div>",
                                unsafe_allow_html=True
                            )
                            st.markdown(
                                f"<div class='analysis-box english'><b>🧾 Analysis:</b> {r['analysis_en']}</div>",
                                unsafe_allow_html=True
                            )
                            if r["name_en"] in simplified_views:
                                st.markdown(
                                    f"<div class='simplified-box english'>{simplified_views[r['name_en']]['en']}</div>",
                                    unsafe_allow_html=True
                                )



                        # ✅ صندوق التحسينات
                        if r["name_en"] in improvements:
                            st.markdown(
                                f"""
                                <div class="improvement-box">
                                    <p class="improvement-ar">📌 <b>تحسين (AR):</b> {improvements[r['name_en']]['ar']}</p>
                                    <p class="improvement-en">📌 <b>Improvement (EN):</b> {improvements[r['name_en']]['en']}</p>
                                </div>
                                """,
                                unsafe_allow_html=True
                            )


            # 📈 رسم بياني باستخدام plotly
            chart_df = pd.DataFrame([{
                "Year": year,
                "Ratio (AR)": r["name"],
                "Ratio (EN)": r["name_en"],
                "Value": r["value"]
            } for r in results if r["value"] is not None])

            if not chart_df.empty:
                fig = px.bar(
                    chart_df,
                    x="Ratio (EN)",
                    y="Value",
                    color="Ratio (EN)",
                    title=f"📊 نسب السنة {year}",
                    text="Value",
                )
                fig.update_traces(texttemplate='%{text:.2f}', textposition='outside')
                fig.update_layout(
                    xaxis=dict(title="Ratio"),
                    yaxis=dict(title="Value"),
                    plot_bgcolor="#1C2833" if st.get_option("theme.base") == "dark" else "#f8f9f9",
                    paper_bgcolor="#17202A" if st.get_option("theme.base") == "dark" else "#ffffff",
                    font=dict(family="Cairo, sans-serif", size=14, color="#FDFEFE" if st.get_option("theme.base") == "dark" else "#2C3E50"),
                )
                st.plotly_chart(fig, use_container_width=True)



##################################################################################################
with tab2:
    st.subheader("📊 مقارنة السنوات المالية")
    comparison_data = []

    for year in selected_years:
        row = df[df["year"] == year].iloc[0]
        fi = FinancialInputs(
            sales=row["Revenue"],
            cogs=row["Cost of goods sold"],
            opex=row.get("Total Operating expenses", 0),
            interest_expense=row.get("Financial charges", 0),
            tax_expense=row.get("Zakat", 0),
            net_income=row["Profit/(Loss) for the period"],
            current_assets=row["Current assets"],
            inventory=row["Inventory"],
            cash=row["Cash and Bank balances"],
            accounts_receivable=row["Trade Receivable"],
            accounts_payable=row["Current liabilities"],  
            current_liabilities=row["Current liabilities"],
            total_assets=row["Total assets"],
            total_liabilities=row["Total liabilities"],
            equity=row["Owners' equity"],
            cfo=row.get("Cash flow", 0),
        )
        results = compute_ratios(fi)
        for r in results:
            # 🛠 نحول القيم لأرقام (حتى لو فيها % أو نصوص)
            val = None
            if r["value"] not in [None, "—"]:
                try:
                    val = float(str(r["value"]).replace("%", "").replace(",", ""))
                    if "%" in str(r["value"]):
                        val = val / 100  # نرجعها لنسبة عشرية
                except:
                    val = None

            comparison_data.append({
                "Year": year,
                "Ratio (AR)": r["name"],
                "Ratio (EN)": r["name_en"],
                "Value": val,
                "Analysis": r["analysis"],
                "Analysis_EN": r["analysis_en"]
            })

    comp_df = pd.DataFrame(comparison_data)

    if not comp_df.empty:
        for ratio in comp_df["Ratio (EN)"].unique():
            ratio_df = comp_df[comp_df["Ratio (EN)"] == ratio].dropna(subset=["Value"]).sort_values("Year")

            if ratio_df.empty:
                st.warning(f"⚠️ لا توجد بيانات كافية لمقارنة {ratio}")
                continue

            # ✅ العنوان آمن لأن فيه بيانات
            st.markdown(f"### {ratio_df.iloc[0]['Ratio (AR)']} | {ratio}")

            if len(ratio_df) < 2:
                st.warning(f"⚠️ لا توجد بيانات كافية لعرض الاتجاه في {ratio}")
                continue

            fig = px.line(
                ratio_df,
                x="Year",
                y="Value",
                markers=True,
                title=f"{ratio} Trend"
            )
            fig.update_traces(text=ratio_df["Value"].round(2), textposition="top center")
            st.plotly_chart(fig, use_container_width=True)

            # 🔼 تحليل التغير
            v1, v2 = ratio_df.iloc[0]["Value"], ratio_df.iloc[-1]["Value"]
            diff = v2 - v1
            direction = "✅ تحسنت" if diff > 0 else "❌ انخفضت"

            # ✅ شرح إضافي + تحسينات
            improvement_text_ar = improvements.get(ratio, {}).get("ar", "—")
            improvement_text_en = improvements.get(ratio, {}).get("en", "—")

            st.markdown(
                f"""
                <div class="improvement-box">
                    <p><b>{ratio}</b> {direction} بمقدار {diff:.2f}</p>
                    <p>📝 التحليل (AR): {ratio_df.iloc[-1]['Analysis']}</p>
                    <p>📝 Analysis (EN): {ratio_df.iloc[-1]['Analysis_EN']}</p>
                    <hr>
                    <p>ℹ️ <b>شرح إضافي:</b> التغير من {v1:.2f} في {ratio_df.iloc[0]['Year']} 
                    إلى {v2:.2f} في {ratio_df.iloc[-1]['Year']}.</p>
                    <p style="direction:rtl; text-align:right;">📌 <b>تحسين مقترح (AR):</b> {improvement_text_ar}</p>
                    <p>📌 <b>Suggested Improvement (EN):</b> {improvement_text_en}</p>
                </div>
                """,
                unsafe_allow_html=True
            )


    else:
        st.warning("⚠️ لا توجد بيانات كافية للمقارنة")





















