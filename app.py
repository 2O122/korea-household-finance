
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

# ==========================================
# 1. PAGE CONFIGURATION
# ==========================================

st.set_page_config(
    page_title="Korea Finance Lab",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# 2. DESIGN SYSTEM
# ==========================================

st.markdown("""
<style>

@import url(
'https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap'
);

.stApp {
    background: #F3F6FA;
    font-family: 'Inter', sans-serif;
    color: #20334A;
}

.block-container {
    max-width: 1450px;
    padding-top: 2rem;
    padding-bottom: 4rem;
}

[data-testid="stHeader"] {
    background: rgba(243,246,250,0.95);
}

h1, h2, h3 {
    color: #142D49 !important;
    font-weight: 750 !important;
}

p, label {
    color: #53677D;
}

[data-testid="stSidebar"] {
    background: #10243A;
}

[data-testid="stSidebar"] * {
    color: #EAF2F9 !important;
}

[data-testid="stSidebar"] [data-baseweb="select"] * {
    color: #20334A !important;
}

[data-testid="stMetric"] {
    background: white;
    border: 1px solid #E2EAF2;
    border-radius: 14px;
    padding: 20px;
    box-shadow: 0 3px 12px rgba(20,45,73,0.04);
}

[data-testid="stMetricLabel"] {
    color: #647B91 !important;
}

[data-testid="stMetricValue"] {
    color: #1769AA !important;
    font-weight: 800;
}

div[data-testid="stPlotlyChart"] {
    background: white;
    padding: 12px;
    border: 1px solid #E2EAF2;
    border-radius: 15px;
}

section[data-testid="stSidebar"] {
    border-right: 1px solid #263F58;
}

hr {
    border-color: #DFE7EF;
}

.hero {
    background: linear-gradient(115deg, #10243A, #19466D);
    padding: 42px;
    border-radius: 20px;
    margin-bottom: 28px;
}

.hero-label {
    color: #A8C9E5;
    font-size: 12px;
    font-weight: 700;
    letter-spacing: 2px;
}

.hero-title {
    color: #FFFFFF;
    font-size: 35px;
    font-weight: 800;
    margin-top: 15px;
    line-height: 1.4;
}

.hero-subtitle {
    color: #D0DFEC;
    font-size: 15px;
    margin-top: 12px;
    line-height: 1.8;
}

.section-label {
    color: #68829C;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 1.5px;
    margin-bottom: 5px;
}

.small-note {
    background: #EAF1F8;
    border-left: 4px solid #327CB5;
    border-radius: 7px;
    padding: 14px;
    color: #405B75;
    font-size: 13px;
}

</style>
""", unsafe_allow_html=True)

# ==========================================
# 3. LOAD DATA
# ==========================================

@st.cache_data
def load_data():

    paths = [
        Path("data/household_debt_income_2024_verified.csv"),
        Path("household_debt_income_2024_verified.csv")
    ]

    for path in paths:
        if path.exists():
            return pd.read_csv(path, encoding="utf-8-sig")

    return None


df = load_data()

if df is None:
    st.error(
        "CSV 파일을 찾을 수 없습니다. "
        "data 폴더에 CSV 파일을 업로드해주세요."
    )
    st.stop()

# ==========================================
# 4. DATA VALIDATION
# ==========================================

debt_col = "household_debt_2024_03_만원"
income_col = "household_income_2023_만원"

required = ["region", debt_col, income_col]

if not all(c in df.columns for c in required):
    st.error("CSV 열 이름을 확인해주세요.")
    st.write(list(df.columns))
    st.stop()

df[debt_col] = pd.to_numeric(
    df[debt_col], errors="coerce"
)

df[income_col] = pd.to_numeric(
    df[income_col], errors="coerce"
)

df = df.dropna(subset=required).copy()

df = df[
    (df[income_col] > 0) &
    (df[debt_col] >= 0)
].copy()

df["approx_DTI_percent"] = (
    df[debt_col] / df[income_col] * 100
)

if df.empty:
    st.error("분석할 수 있는 데이터가 없습니다.")
    st.stop()

# ==========================================
# 5. SIDEBAR
# ==========================================

st.sidebar.markdown("""
<div style="padding:15px 0 25px 0;">
    <div style="font-size:12px;letter-spacing:2px;
    color:#8CB7DC;font-weight:700;">
        KOREA FINANCE LAB
    </div>
    <div style="font-size:23px;font-weight:800;
    color:white;margin-top:8px;">
        DATA CENTER
    </div>
    <div style="font-size:12px;color:#B7C9D9;">
        Regional Economic Research
    </div>
</div>
""", unsafe_allow_html=True)

st.sidebar.divider()

page = st.sidebar.radio(
    "NAVIGATION",
    [
        "Overview",
        "Debt Analysis",
        "Income Analysis",
        "Regional Comparison",
        "Data & Sources"
    ]
)

st.sidebar.divider()

st.sidebar.markdown("### 지역 선택")

regions = st.sidebar.multiselect(
    "분석 대상 시도",
    sorted(df["region"].unique()),
    default=sorted(df["region"].unique())
)

if not regions:
    st.warning("최소 한 개의 지역을 선택해주세요.")
    st.stop()

selected = df[df["region"].isin(regions)].copy()

st.sidebar.caption(
    "Source: 2024 Household Finance Survey"
)

# ==========================================
# 6. HERO
# ==========================================

st.markdown("""
<div class="hero">
    <div class="hero-label">
        SOUTH KOREA · ECONOMIC RESEARCH
    </div>
    <div class="hero-title">
        가계부채와 생활비 부담 분석
    </div>
    <div class="hero-subtitle">
        대한민국 17개 시도의 재정 부담과 지역별 경제적 차이를
        데이터 기반으로 분석합니다.
        <br>
        Household Debt & Cost of Living Analysis
    </div>
</div>
""", unsafe_allow_html=True)

# ==========================================
# 7. CHART THEME
# ==========================================

def style_chart(fig, height=450):

    fig.update_layout(
        template="plotly_white",
        height=height,
        font=dict(
            family="Arial",
            color="#30465D",
            size=12
        ),
        paper_bgcolor="white",
        plot_bgcolor="white",
        margin=dict(l=25, r=25, t=45, b=30),
        legend_title_text=""
    )

    fig.update_xaxes(
        showgrid=True,
        gridcolor="#EAF0F5"
    )

    fig.update_yaxes(
        showgrid=False
    )

    return fig


# ==========================================
# 8. OVERVIEW
# ==========================================

if page == "Overview":

    st.markdown(
        '<div class="section-label">01 / OVERVIEW</div>',
        unsafe_allow_html=True
    )

    st.header("Regional Financial Overview")

    st.write(
        "17개 시도의 가구부채와 소득 구조를 요약합니다."
    )

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "분석 지역",
        f"{selected['region'].nunique()}개"
    )

    c2.metric(
        "평균 가구부채",
        f"{selected[debt_col].mean():,.0f}만원"
    )

    c3.metric(
        "평균 가구소득",
        f"{selected[income_col].mean():,.0f}만원"
    )

    c4.metric(
        "평균 근사 DTI",
        f"{selected['approx_DTI_percent'].mean():.1f}%"
    )

    st.divider()

    left, right = st.columns(2)

    with left:

        st.subheader("지역별 가구부채")

        d = selected.sort_values(
            debt_col, ascending=True
        )

        fig = px.bar(
            d,
            x=debt_col,
            y="region",
            orientation="h",
            color=debt_col,
            color_continuous_scale="Blues",
            labels={
                debt_col: "평균 부채 (만원)",
                "region": "지역"
            }
        )

        fig = style_chart(fig, 500)

        st.plotly_chart(
            fig, use_container_width=True
        )

    with right:

        st.subheader("지역별 가구소득")

        d = selected.sort_values(
            income_col, ascending=True
        )

        fig = px.bar(
            d,
            x=income_col,
            y="region",
            orientation="h",
            color=income_col,
            color_continuous_scale="Teal",
            labels={
                income_col: "연평균 소득 (만원)",
                "region": "지역"
            }
        )

        fig = style_chart(fig, 500)

        st.plotly_chart(
            fig, use_container_width=True
        )

    st.subheader("가구소득과 가구부채의 관계")

    fig = px.scatter(
        selected,
        x=income_col,
        y=debt_col,
        text="region",
        size="approx_DTI_percent",
        color="approx_DTI_percent",
        color_continuous_scale="Blues",
        labels={
            income_col: "연평균 소득 (만원)",
            debt_col: "평균 부채 (만원)",
            "approx_DTI_percent": "근사 DTI (%)"
        }
    )

    fig.update_traces(
        textposition="top center"
    )

    fig = style_chart(fig, 520)

    st.plotly_chart(
        fig, use_container_width=True
    )


# ==========================================
# 9. DEBT ANALYSIS
# ==========================================

elif page == "Debt Analysis":

    st.markdown(
        '<div class="section-label">02 / DEBT</div>',
        unsafe_allow_html=True
    )

    st.header("Household Debt Analysis")

    st.write(
        "2024년 3월 31일 기준 시도별 가구당 평균 부채"
    )

    d = selected.sort_values(
        debt_col, ascending=False
    )

    fig = px.bar(
        d,
        x="region",
        y=debt_col,
        color=debt_col,
        text_auto=",.0f",
        color_continuous_scale="Blues",
        labels={
            "region": "지역",
            debt_col: "평균 부채 (만원)"
        }
    )

    fig = style_chart(fig, 550)

    st.plotly_chart(
        fig, use_container_width=True
    )

    st.subheader("부채 데이터")

    st.dataframe(
        d[["region", debt_col]],
        use_container_width=True,
        hide_index=True
    )


# ==========================================
# 10. INCOME ANALYSIS
# ==========================================

elif page == "Income Analysis":

    st.markdown(
        '<div class="section-label">03 / INCOME</div>',
        unsafe_allow_html=True
    )

    st.header("Household Income Analysis")

    st.write(
        "2023년 기준 시도별 가구당 연평균 소득"
    )

    d = selected.sort_values(
        income_col, ascending=False
    )

    fig = px.bar(
        d,
        x="region",
        y=income_col,
        color=income_col,
        text_auto=",.0f",
        color_continuous_scale="Teal",
        labels={
            "region": "지역",
            income_col: "연평균 소득 (만원)"
        }
    )

    fig = style_chart(fig, 550)

    st.plotly_chart(
        fig, use_container_width=True
    )

    st.subheader("Income vs Debt")

    fig = px.scatter(
        selected,
        x=income_col,
        y=debt_col,
        text="region",
        color="approx_DTI_percent",
        color_continuous_scale="Blues",
        labels={
            income_col: "연평균 소득 (만원)",
            debt_col: "평균 부채 (만원)"
        }
    )

    fig.update_traces(
        textposition="top center"
    )

    fig = style_chart(fig, 500)

    st.plotly_chart(
        fig, use_container_width=True
    )


# ==========================================
# 11. REGIONAL COMPARISON
# ==========================================

elif page == "Regional Comparison":

    st.markdown(
        '<div class="section-label">04 / COMPARISON</div>',
        unsafe_allow_html=True
    )

    st.header("Regional Financial Comparison")

    st.write(
        "지역별 평균 부채와 연평균 소득을 비교합니다."
    )

    d = selected.sort_values(
        "approx_DTI_percent",
        ascending=False
    )

    fig = px.bar(
        d,
        x="region",
        y="approx_DTI_percent",
        color="approx_DTI_percent",
        text_auto=".1f",
        color_continuous_scale="Oranges",
        labels={
            "region": "지역",
            "approx_DTI_percent": "근사 DTI (%)"
        }
    )

    fig = style_chart(fig, 480)

    st.plotly_chart(
        fig, use_container_width=True
    )

    st.subheader("지역별 지표 비교")

    st.dataframe(
        d[
            [
                "region",
                debt_col,
                income_col,
                "approx_DTI_percent"
            ]
        ],
        use_container_width=True,
        hide_index=True
    )


# ==========================================
# 12. DATA & SOURCES
# ==========================================

elif page == "Data & Sources":

    st.markdown(
        '<div class="section-label">05 / DATA</div>',
        unsafe_allow_html=True
    )

    st.header("Data & Research Sources")

    st.write(
        "본 프로젝트에서 활용한 원자료와 파생 지표를 확인합니다."
    )

    st.subheader("Original Dataset")

    st.dataframe(
        selected,
        use_container_width=True,
        hide_index=True
    )

    st.subheader("Data Sources")

    st.markdown("""
    - 국가데이터처
    - 2024년 가계금융복지조사
    - 표 5-2: 시도별 가구부채
    - 표 5-3: 시도별 가구소득
    - KOSIS 국가통계포털
    """)

    st.subheader("Calculation Method")

    st.latex(
        r"DTI_{approx} = "
        r"\frac{Average\ Household\ Debt}"
        r"{Average\ Annual\ Household\ Income}"
        r"\times 100"
    )

    st.markdown("""
    <div class="small-note">
    주의: 본 지표는 지역별 평균값을 이용한 분석용 근사 비율이며,
    개인별 공식 DTI 또는 DSR이 아닙니다.
    부채와 소득의 기준 기간도 서로 다릅니다.
    </div>
    """, unsafe_allow_html=True)

    csv = selected.to_csv(
        index=False
    ).encode("utf-8-sig")

    st.download_button(
        "데이터 CSV 다운로드",
        data=csv,
        file_name="regional_finance_data.csv",
        mime="text/csv"
    )


# ==========================================
# 13. IMAGE GALLERY
# ==========================================

st.divider()

st.markdown(
    '<div class="section-label">RESEARCH VISUALS</div>',
    unsafe_allow_html=True
)

st.header("Research Gallery")

images = [
    (
        "01_regional_household_debt.png",
        "Regional Household Debt"
    ),
    (
        "02_regional_household_income.png",
        "Regional Household Income"
    ),
    (
        "03_debt_income_relationship.png",
        "Debt & Income Relationship"
    )
]

cols = st.columns(3)

for col, (filename, caption) in zip(cols, images):

    candidates = [
        Path("images") / filename,
        Path(filename)
    ]

    image_path = next(
        (p for p in candidates if p.exists()),
        None
    )

    with col:

        if image_path:
            st.image(
                str(image_path),
                caption=caption,
                use_container_width=True
            )
        else:
            st.caption(
                f"이미지 준비 중: {caption}"
            )


# ==========================================
# 14. FOOTER
# ==========================================

st.divider()

st.markdown("""
<div style="
    text-align:center;
    padding:20px;
    color:#71869A;
    font-size:12px;
">
    KOREA FINANCE LAB · HOUSEHOLD FINANCE RESEARCH
    <br><br>
    Data-based Regional Economic Analysis · 2026
</div>
""", unsafe_allow_html=True)
