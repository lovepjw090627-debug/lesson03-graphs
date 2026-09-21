import streamlit as st
import pandas as pd
import plotly.express as px

# ──────────────────────────────────────────────
# 기본 설정
# ──────────────────────────────────────────────
st.set_page_config(page_title="영화 데이터 그래프 도감 1 - 시간", page_icon="📈", layout="wide")

DATA_URL = "https://raw.githubusercontent.com/greatsong/modudata/main/data/kobis_daily.csv"


@st.cache_data(ttl=3600)  # 1시간 동안 같은 데이터를 다시 안 불러오고 기억해 둡니다.
def load_data():
    """
    KOBIS 일별 박스오피스 1년치(365일) 데이터를 불러옵니다.
    날짜 열(yyyymmdd 여덟 자리 숫자)을 진짜 날짜(datetime) 타입으로 바꿔서 반환합니다.
    """
    df = pd.read_csv(DATA_URL)

    # 날짜 열이 20250901 같은 숫자(또는 숫자 문자열)로 와 있어서
    # pandas가 날짜로 다룰 수 있는 datetime 타입으로 바꿔줍니다.
    df["날짜"] = pd.to_datetime(df["날짜"], format="%Y%m%d")

    return df


df = load_data()

st.title("📈 영화 데이터 그래프 도감 1 - 시간")
st.caption("KOBIS 일별 박스오피스 데이터로 그리는 '시간에 따른 변화' 그래프 모음집이에요.")

st.divider()

# ══════════════════════════════════════════════
# 섹션 1. 영화별 일별 관객수 추이
# ══════════════════════════════════════════════
st.header("1. 영화별 일별 관객수 추이")

# 드롭다운에 넣을 영화 목록(가나다 순으로 정렬)을 만듭니다.
movie_list = sorted(df["영화명"].unique())

selected_movie = st.selectbox("영화를 선택하세요", movie_list)

# 선택한 영화의 기록만 골라서, 날짜 순서대로 정렬합니다.
movie_df = df[df["영화명"] == selected_movie].sort_values("날짜")

fig1 = px.line(
    movie_df,
    x="날짜",
    y="일관객",
    markers=True,  # 각 지점에 점을 찍어서 어느 날짜인지 알아보기 쉽게 합니다.
    title=f"'{selected_movie}' 일별 관객수 변화",
    labels={"날짜": "날짜", "일관객": "일일 관객수(명)"},
)

# 마우스를 올리면(hover) 날짜와 관객수가 보이도록 설정합니다.
fig1.update_traces(
    hovertemplate="날짜: %{x|%Y-%m-%d}<br>관객수: %{y:,}명<extra></extra>"
)
fig1.update_layout(hovermode="x unified")

# x축을 항상 'YYYY-MM-DD' 형식의 날짜로 보여줍니다.
# (하루치 기록만 있는 영화를 고르면 날짜 범위가 0이 되어 Plotly가 자동으로
#  시:분:초 단위 눈금을 그리는 문제가 있어서, 그런 경우엔 눈금 범위를
#  하루 앞뒤로 살짝 넓혀서 날짜만 깔끔하게 보이도록 합니다.)
fig1.update_xaxes(tickformat="%Y-%m-%d")
if movie_df["날짜"].nunique() == 1:
    only_date = movie_df["날짜"].iloc[0]
    fig1.update_xaxes(range=[only_date - pd.Timedelta(days=1), only_date + pd.Timedelta(days=1)])

st.plotly_chart(fig1, use_container_width=True)

# 이 그래프로 알 수 있는 것: 아래 문장을 원하는 내용으로 바꿔서 쓰세요.
st.info("💡 **이 그래프로 알 수 있는 것:** (여기에 이 그래프에서 읽을 수 있는 한 문장을 적어주세요)")

st.divider()

# ══════════════════════════════════════════════
# 섹션 2. (다음 '시간' 관련 그래프는 여기에 추가하세요)
# ══════════════════════════════════════════════
# 예시:
# st.header("2. 요일별 평균 관객수")
# fig2 = px.bar(...)
# st.plotly_chart(fig2, use_container_width=True)
# st.info("💡 **이 그래프로 알 수 있는 것:** ...")
# st.divider()
