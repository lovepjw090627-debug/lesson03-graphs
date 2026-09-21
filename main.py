import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

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

st.plotly_chart(fig1, use_container_width=True, key="fig1_movie_daily_line")

# 이 그래프로 알 수 있는 것: 아래 문장을 원하는 내용으로 바꿔서 쓰세요.
st.info("💡 **이 그래프로 알 수 있는 것:** (여기에 이 그래프에서 읽을 수 있는 한 문장을 적어주세요)")

st.divider()

# ══════════════════════════════════════════════
# 섹션 2. 기간 내 일관객 합계 상위 5편 비교
# ══════════════════════════════════════════════
st.header("2. 일관객 합계 상위 5편의 날짜별 관객수")

# 영화별로 전체 기간의 일관객을 다 더해서, 합계가 큰 순서로 5편을 뽑습니다.
top5_names = (
    df.groupby("영화명")["일관객"].sum().sort_values(ascending=False).head(5).index
)

top5_df = df[df["영화명"].isin(top5_names)].sort_values("날짜")

fig2 = px.line(
    top5_df,
    x="날짜",
    y="일관객",
    color="영화명",  # 영화마다 다른 색으로 구분합니다.
    markers=True,
    title="일관객 합계 상위 5편의 날짜별 관객수 변화",
    labels={"날짜": "날짜", "일관객": "일일 관객수(명)", "영화명": "영화"},
)

fig2.update_traces(
    hovertemplate="날짜: %{x|%Y-%m-%d}<br>관객수: %{y:,}명<extra>%{fullData.name}</extra>"
)
fig2.update_layout(hovermode="x unified")
fig2.update_xaxes(tickformat="%Y-%m-%d")

# 범례는 기본적으로 클릭하면 해당 영화 선을 껐다 켰다 할 수 있어요.
st.plotly_chart(fig2, use_container_width=True, key="fig2_top5_lines")

st.info("💡 **이 그래프로 알 수 있는 것:** (여기에 이 그래프에서 읽을 수 있는 한 문장을 적어주세요)")

st.divider()

# ══════════════════════════════════════════════
# 섹션 3. 날짜별 10위권 전체 관객수 합계
# ══════════════════════════════════════════════
st.header("3. 날짜별 10위권 전체 관객수 합계")

# 날짜별로 그날 10위권에 든 영화들의 일관객을 모두 더합니다.
daily_total = df.groupby("날짜")["일관객"].sum().reset_index(name="합계")

fig3 = go.Figure()

# 영역 그래프(면적 채우기 선 그래프)를 직접 그립니다.
fig3.add_trace(go.Scatter(
    x=daily_total["날짜"],
    y=daily_total["합계"],
    mode="lines",
    fill="tozeroy",  # 선 아래를 색으로 채워서 영역 그래프처럼 보이게 합니다.
    line=dict(color="#4C78A8"),
    name="일별 합계",
    hovertemplate="날짜: %{x|%Y-%m-%d}<br>합계: %{y:,}명<extra></extra>",
))

# 합계가 가장 컸던 3일을 찾아서 그래프 위에 점과 날짜 글자로 표시합니다.
top3_days = daily_total.sort_values("합계", ascending=False).head(3)

fig3.add_trace(go.Scatter(
    x=top3_days["날짜"],
    y=top3_days["합계"],
    mode="markers+text",
    marker=dict(size=11, color="red"),
    text=top3_days["날짜"].dt.strftime("%Y-%m-%d"),
    textposition="top center",
    textfont=dict(color="red", size=13),
    name="합계 상위 3일",
    hovertemplate="날짜: %{x|%Y-%m-%d}<br>합계: %{y:,}명<extra>상위 3일</extra>",
))

fig3.update_layout(
    title="날짜별 10위권 전체 관객수 합계",
    xaxis_title="날짜",
    yaxis_title="그날 10위권 전체 관객수(명)",
)
fig3.update_xaxes(tickformat="%Y-%m-%d")

st.plotly_chart(fig3, use_container_width=True, key="fig3_daily_total_area")

st.info("💡 **이 그래프로 알 수 있는 것:** (여기에 이 그래프에서 읽을 수 있는 한 문장을 적어주세요)")

st.divider()

# ══════════════════════════════════════════════
# 섹션 4. 일관객 합계 TOP 10 영화
# ══════════════════════════════════════════════
st.header("4. 일관객 합계 TOP 10 영화")

# 영화별로 이 기간의 일관객을 모두 더하고, 10위권에 든 날수(행 개수)도 함께 셉니다.
movie_summary = (
    df.groupby("영화명")
    .agg(합계=("일관객", "sum"), 상위권일수=("날짜", "count"))
    .reset_index()
)

top10_movies = movie_summary.sort_values("합계", ascending=False).head(10)

# 가로 막대그래프는 데이터 순서대로 아래에서 위로 쌓이기 때문에,
# 관객이 많은 영화가 맨 위에 오도록 오름차순(작은 값이 먼저)으로 다시 정렬합니다.
top10_movies = top10_movies.sort_values("합계", ascending=True)

fig4 = go.Figure()

fig4.add_trace(go.Bar(
    x=top10_movies["합계"],
    y=top10_movies["영화명"],
    orientation="h",
    marker=dict(color="#4C78A8"),
    customdata=top10_movies["상위권일수"],
    hovertemplate=(
        "영화: %{y}<br>"
        "합계 관객수: %{x:,}명<br>"
        "10위권에 든 날수: %{customdata}일"
        "<extra></extra>"
    ),
))

fig4.update_layout(
    title="일관객 합계 TOP 10 영화",
    xaxis_title="합계 관객수(명)",
    yaxis_title="",
)

st.plotly_chart(fig4, use_container_width=True, key="fig4_top10_bar")

st.info("💡 **이 그래프로 알 수 있는 것:** (여기에 이 그래프에서 읽을 수 있는 한 문장을 적어주세요)")

st.divider()

# ══════════════════════════════════════════════
# 섹션 5. 월 × 요일별 일관객 합계 히트맵
# ══════════════════════════════════════════════
st.header("5. 월 × 요일별 일관객 합계")

# 날짜에서 월(1~12)과 요일을 뽑아냅니다.
df["월"] = df["날짜"].dt.month
df["요일번호"] = df["날짜"].dt.weekday  # 0=월요일 ... 6=일요일

weekday_names = ["월", "화", "수", "목", "금", "토", "일"]

# 월 × 요일 조합별로 일관객을 다 더합니다.
# pivot_table을 쓰면 데이터가 없는 조합은 자동으로 0으로 채워줍니다.
heatmap_data = df.pivot_table(
    index="요일번호",
    columns="월",
    values="일관객",
    aggfunc="sum",
    fill_value=0,
)

# 요일은 월요일(0)부터 일요일(6) 순서로, 월은 1월부터 12월 순서로 정렬합니다.
heatmap_data = heatmap_data.reindex(index=range(7), columns=range(1, 13), fill_value=0)

fig5 = go.Figure(data=go.Heatmap(
    z=heatmap_data.values,
    x=[f"{m}월" for m in heatmap_data.columns],
    y=weekday_names,
    colorscale="Blues",  # 값이 클수록(관객이 많을수록) 색이 진해집니다.
    hovertemplate="%{x} %{y}요일<br>합계 관객수: %{z:,}명<extra></extra>",
    colorbar=dict(title="관객수(명)"),
))

fig5.update_layout(
    title="월 × 요일별 일관객 합계",
    xaxis_title="월",
    yaxis_title="요일",
)
# y축 기본 방향은 아래에서 위로 쌓이므로, 뒤집어서 월요일이 맨 위,
# 일요일이 맨 아래로 오는 자연스러운 순서로 보이게 합니다.
fig5.update_yaxes(autorange="reversed")

st.plotly_chart(fig5, use_container_width=True, key="fig5_month_weekday_heatmap")

st.info("💡 **이 그래프로 알 수 있는 것:** (여기에 이 그래프에서 읽을 수 있는 한 문장을 적어주세요)")

st.divider()

# ══════════════════════════════════════════════
# 섹션 6. (다음 '시간' 관련 그래프는 여기에 추가하세요)
# ══════════════════════════════════════════════
# 예시:
# st.header("6. ...")
# fig6 = px.bar(...)
# st.plotly_chart(fig6, use_container_width=True)
# st.info("💡 **이 그래프로 알 수 있는 것:** ...")
# st.divider()
