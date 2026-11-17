
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

# ---------------------------------------
# 1. 페이지 기본 설정
# ---------------------------------------

st.set_page_config(
    page_title="가계부채와 생활비 부담 분석",
    page_icon="📊",
    layout="wide"
)

# ---------------------------------------
# 2. 디자인
# ---------------------------------------

st.markdown("""
<style>
.stApp {
    background-color: #F5F7FA;
}
h1, h2, h3 {
    color: #17324D;
}
[data-testid="stMetric"] {
    background: white;
    padding: 18px;
    border-radius: 12px;
    border: 1px solid #E4EAF0;
}
.block-container {
    padding-top: 2rem;
}
</style>
""", unsafe_allow_html=True)

# ---------------------------------------
# 3. 데이터 불러오기
# ---------------------------------------

@st.cache_data
def load_data():
    candidates = [
        Path("data/household_debt_income_2024_verified.csv"),
        Path("household_debt_income_2024_verified.csv"),
    ]

    for path in candidates:
        if path.exists():
            return pd.read_csv(path, encoding="utf-8-sig")

    return None


df = load_data()

# ---------------------------------------
# 4. 제목
# ---------------------------------------

st.title("🇰🇷 가계부채와 생활비 부담 분석")

st.markdown("""
### 대한민국 17개 시도의 지역별 재정 부담 비교

가구부채와 가구소득을 바탕으로 지역별 경제적 차이를 분석합니다.
""")

st.caption(
    "데이터 출처: 국가데이터처 · 2024년 가계금융복지조사"
)

st.divider()

if df is None:
    st.error(
        "데이터 파일을 찾을 수 없습니다. "
        "data 폴더에 CSV 파일을 넣어주세요."
    )
    st.stop()

# ---------------------------------------
# 5. 데이터 전처리
# ---------------------------------------

debt_col = "household_debt_2024_03_만원"
income_col = "household_income_2023_만원"

required = ["region", debt_col, income_col]

if not all(col in df.columns for col in required):
    st.error("CSV의 열 이름이 예상한 형식과 다릅니다.")
    st.write("현재 CSV 열:", list(df.columns))
    st.stop()

df[debt_col] = pd.to_numeric(df[debt_col], errors="coerce")
df[income_col] = pd.to_numeric(df[income_col], errors="coerce")

df = df.dropna(subset=required).copy()

df["approx_DTI_percent"] = (
    df[debt_col] / df[income_col] * 100
)

# ---------------------------------------
# 6. 핵심 통계
# ---------------------------------------

st.subheader("📌 핵심 통계")

col1, col2, col3 = st.columns(3)

col1.metric(
    "분석 지역 수",
    f"{df['region'].nunique()}개"
)

col2.metric(
    "평균 가구부채",
    f"{df[debt_col].mean():,.0f}만원"
)

col3.metric(
    "평균 근사 DTI",
    f"{df['approx_DTI_percent'].mean():.1f}%"
)

st.divider()

# ---------------------------------------
# 7. 지역 선택
# ---------------------------------------

st.sidebar.title("📊 분석 설정")

regions = st.sidebar.multiselect(
    "분석할 지역 선택",
    options=sorted(df["region"].unique()),
    default=sorted(df["region"].unique())
)

if not regions:
    st.warning("최소 한 개의 지역을 선택해주세요.")
    st.stop()

selected = df[df["region"].isin(regions)].copy()

# ---------------------------------------
# 8. 가구부채 그래프
# ---------------------------------------

st.subheader("1. 시도별 가구당 평균 부채")

debt_data = selected.sort_values(
    debt_col, ascending=True
)

fig_debt = px.bar(
    debt_data,
    x=debt_col,
    y="region",
    orientation="h",
    text=debt_col,
    color=debt_col,
    color_continuous_scale="Blues",
    labels={
        debt_col: "평균 부채 (만원)",
        "region": "지역"
    }
)

fig_debt.update_layout(
    height=550,
    template="plotly_white",
    coloraxis_showscale=False,
    yaxis_title=""
)

st.plotly_chart(fig_debt, use_container_width=True)

st.caption(
    "기준: 2024년 3월 31일 · 단위: 만원"
)

st.divider()

# ---------------------------------------
# 9. 가구소득 그래프
# ---------------------------------------

st.subheader("2. 시도별 가구당 연평균 소득")

income_data = selected.sort_values(
    income_col, ascending=True
)

fig_income = px.bar(
    income_data,
    x=income_col,
    y="region",
    orientation="h",
    text=income_col,
    color=income_col,
    color_continuous_scale="Teal",
    labels={
        income_col: "연평균 소득 (만원)",
        "region": "지역"
    }
)

fig_income.update_layout(
    height=550,
    template="plotly_white",
    coloraxis_showscale=False,
    yaxis_title=""
)

st.plotly_chart(fig_income, use_container_width=True)

st.caption(
    "기준: 2023년 연간 소득 · 단위: 만원"
)

st.divider()

# ---------------------------------------
# 10. 소득과 부채의 관계
# ---------------------------------------

st.subheader("3. 가구소득과 가구부채의 관계")

fig_scatter = px.scatter(
    selected,
    x=income_col,
    y=debt_col,
    text="region",
    size="approx_DTI_percent",
    color="approx_DTI_percent",
    color_continuous_scale="RdBu_r",
    hover_name="region",
    labels={
        income_col: "연평균 소득 (만원)",
        debt_col: "평균 부채 (만원)",
        "approx_DTI_percent": "근사 DTI (%)"
    }
)

fig_scatter.update_traces(
    textposition="top center"
)

fig_scatter.update_layout(
    height=600,
    template="plotly_white"
)

st.plotly_chart(fig_scatter, use_container_width=True)

st.caption(
    "각 점은 하나의 시도를 의미합니다. "
    "점의 크기는 근사 DTI를 나타냅니다."
)

st.divider()

# ---------------------------------------
# 11. 지역별 근사 DTI
# ---------------------------------------

st.subheader("4. 지역별 근사 DTI 비교")

dti_data = selected.sort_values(
    "approx_DTI_percent",
    ascending=False
)

fig_dti = px.bar(
    dti_data,
    x="region",
    y="approx_DTI_percent",
    color="approx_DTI_percent",
    color_continuous_scale="Oranges",
    text_auto=".1f",
    labels={
        "region": "지역",
        "approx_DTI_percent": "근사 DTI (%)"
    }
)

fig_dti.update_layout(
    height=450,
    template="plotly_white",
    coloraxis_showscale=False
)

st.plotly_chart(fig_dti, use_container_width=True)

# ---------------------------------------
# 12. 이미지 갤러리
# ---------------------------------------

st.divider()
st.subheader("🖼️ 연구 자료 및 그래프 이미지")

image_files = [
    ("01_regional_household_debt.png", "지역별 가구부채"),
    ("02_regional_household_income.png", "지역별 가구소득"),
    ("03_debt_income_relationship.png", "소득과 부채의 관계"),
]

image_dir = Path("images")

for filename, caption in image_files:
    image_path = image_dir / filename

    if image_path.exists():
        st.image(
            str(image_path),
            caption=caption,
            use_container_width=True
        )

# ---------------------------------------
# 13. 데이터 표
# ---------------------------------------

st.divider()
st.subheader("📋 지역별 원자료 및 계산 결과")

display_data = selected[
    ["region", debt_col, income_col, "approx_DTI_percent"]
].copy()

display_data.columns = [
    "지역",
    "가구당 평균 부채 (만원)",
    "가구당 연평균 소득 (만원)",
    "근사 DTI (%)"
]

st.dataframe(
    display_data,
    use_container_width=True,
    hide_index=True
)

# ---------------------------------------
# 14. 데이터 다운로드
# ---------------------------------------

csv = display_data.to_csv(
    index=False
).encode("utf-8-sig")

st.download_button(
    label="📥 분석 데이터 다운로드",
    data=csv,
    file_name="regional_finance_analysis.csv",
    mime="text/csv"
)

# ---------------------------------------
# 15. 주의사항
# ---------------------------------------

st.divider()

st.subheader("⚠️ 분석 시 유의사항")

st.markdown("""
- 가구부채는 2024년 3월 31일 기준입니다.
- 가구소득은 2023년 연간 기준입니다.
- 근사 DTI는 지역별 평균 부채를 평균 연간 소득으로 나눈 분석용 지표입니다.
- 개인별 공식 DTI 또는 DSR과 동일하지 않습니다.
- 지역별 상관관계가 인과관계를 의미하지는 않습니다.
- 본 분석은 2024년 단면자료를 활용합니다.
""")

st.caption(
    "Korea Household Finance Research Project · 2026"
)
