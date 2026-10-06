from pathlib import Path

import pandas as pd
import streamlit as st

st.set_page_config(page_title="Streamlit 요소 체험실", page_icon="🧪", layout="wide")


@st.cache_data
def load_gdp_data():
    """CSV의 연도별 GDP 열을 표와 차트에 쓰기 쉬운 형태로 바꿉니다."""
    data_path = Path(__file__).parent / "data" / "gdp_data.csv"
    raw_data = pd.read_csv(data_path)
    year_columns = [column for column in raw_data.columns if column.isdigit()]
    data = raw_data.melt(
        id_vars=["Country Name", "Country Code"],
        value_vars=year_columns,
        var_name="연도",
        value_name="GDP (US$)",
    )
    data["연도"] = data["연도"].astype(int)
    data["GDP (US$)"] = pd.to_numeric(data["GDP (US$)"], errors="coerce")
    return data.dropna(subset=["GDP (US$)"])


gdp_data = load_gdp_data()

st.title("Streamlit 요소 체험실")
st.write(
    "Streamlit은 Python 코드만으로 웹 앱을 만드는 도구예요. "
    "아래 탭을 눌러 다양한 요소를 직접 바꿔 보세요."
)
st.caption("예제 데이터: World Bank 국가별 GDP · 데이터가 바뀌면 페이지가 자동으로 다시 실행됩니다.")

form_tab, data_tab, layout_tab = st.tabs(["1. 입력과 버튼", "2. 표와 차트", "3. 상태와 레이아웃"])

with form_tab:
    st.header("입력 요소")
    st.write("텍스트, 숫자, 선택 입력을 사용해 간단한 프로필을 만들어 봅니다.")

    with st.form("profile_form"):
        name = st.text_input("이름", placeholder="예: 민지")
        left, right = st.columns(2)
        with left:
            age = st.number_input("나이", min_value=1, max_value=120, value=20, step=1)
            topic = st.selectbox("관심 주제", ["데이터", "시각화", "웹 앱"])
        with right:
            experience = st.select_slider(
                "Streamlit 경험", options=["처음이에요", "조금 써 봤어요", "익숙해요"]
            )
            wants_email = st.checkbox("새 예제 소식 받기")
        submitted = st.form_submit_button("입력 결과 확인", type="primary")

    st.caption("폼 안의 입력은 제출 버튼을 눌렀을 때 한 번에 전달됩니다.")
    if submitted:
        display_name = name.strip() or "방문자"
        st.success(f"{display_name}님, 반가워요! {age}세 · 관심 주제: {topic}")
        st.write(f"Streamlit 경험: **{experience}** · 새 소식: **{'받기' if wants_email else '받지 않기'}**")

    st.subheader("버튼")
    st.write("버튼을 누르면 클릭한 순간에만 아래 메시지가 나타납니다.")
    if st.button("버튼 눌러 보기"):
        st.toast("버튼 클릭을 확인했어요!", icon="✅")
        st.success("버튼 입력이 앱에 전달됐어요.")

with data_tab:
    st.header("데이터 표와 차트")
    st.write("국가와 기간을 고르면 아래 표와 그래프가 함께 바뀝니다.")

    countries = sorted(gdp_data["Country Name"].unique())
    preferred = ["Germany", "France", "Japan", "Brazil", "United Kingdom"]
    defaults = [country for country in preferred if country in countries]
    if not defaults:
        defaults = countries[:3]

    selected_countries = st.multiselect(
        "비교할 국가 (여러 개 선택 가능)", countries, default=defaults
    )
    min_year = int(gdp_data["연도"].min())
    max_year = int(gdp_data["연도"].max())
    year_range = st.slider(
        "조회할 연도 범위",
        min_value=min_year,
        max_value=max_year,
        value=(max(min_year, 2000), max_year),
        step=1,
    )
    chart_type = st.radio("차트 종류", ["선", "영역", "막대"], horizontal=True)

    filtered = gdp_data[
        gdp_data["Country Name"].isin(selected_countries)
        & gdp_data["연도"].between(year_range[0], year_range[1])
    ].copy()
    filtered["GDP (십억 US$)"] = filtered["GDP (US$)"] / 1_000_000_000
    chart_data = filtered[["연도", "Country Name", "GDP (십억 US$)"]]

    st.subheader("차트")
    if filtered.empty:
        st.info("국가를 하나 이상 선택하면 차트가 표시됩니다.")
    elif chart_type == "선":
        st.line_chart(chart_data, x="연도", y="GDP (십억 US$)", color="Country Name")
    elif chart_type == "영역":
        st.area_chart(chart_data, x="연도", y="GDP (십억 US$)", color="Country Name")
    else:
        st.bar_chart(chart_data, x="연도", y="GDP (십억 US$)", color="Country Name")

    st.subheader("데이터 표")
    st.caption("GDP 값은 십억 미국 달러 단위입니다. 열 제목을 눌러 정렬할 수 있어요.")
    st.dataframe(
        chart_data.sort_values(["Country Name", "연도"]),
        hide_index=True,
        width="stretch",
    )
    st.download_button(
        "표를 CSV로 다운로드",
        data=chart_data.to_csv(index=False).encode("utf-8-sig"),
        file_name="gdp_sample.csv",
        mime="text/csv",
        disabled=filtered.empty,
    )

with layout_tab:
    st.header("상태 표시와 레이아웃")
    st.write("메시지, 진행 막대, 지표, 펼침 영역으로 정보를 나누어 보여줄 수 있어요.")

    progress_value = st.slider("진행률", min_value=0, max_value=100, value=65, format="%d%%")
    st.progress(progress_value, text=f"작업 진행률: {progress_value}%")

    show_messages = st.checkbox("상태 메시지 모두 보기", value=True)
    if show_messages:
        st.success("성공: 작업을 마쳤습니다.")
        st.info("안내: 이곳에 추가 정보를 표시할 수 있습니다.")
        st.warning("주의: 데이터에 빈 값이 있을 수 있습니다.")

    st.subheader("열과 지표")
    first_column, second_column, third_column = st.columns(3)
    first_column.metric("전체 국가·지역", f"{gdp_data['Country Name'].nunique():,}개")
    second_column.metric("데이터 시작 연도", f"{int(gdp_data['연도'].min())}년")
    third_column.metric("데이터 마지막 연도", f"{int(gdp_data['연도'].max())}년")

    with st.expander("이 요소들은 언제 쓰나요?"):
        st.markdown(
            "- **상태 메시지**: 성공, 안내, 주의처럼 결과의 성격을 구분합니다.\n"
            "- **진행 막대**: 파일 처리나 오래 걸리는 작업의 진행 상황을 보여줍니다.\n"
            "- **열과 지표**: 숫자 요약을 나란히 배치해 빠르게 비교합니다.\n"
            "- **펼침 영역**: 필요할 때만 추가 설명을 열어 화면을 간결하게 유지합니다."
        )
