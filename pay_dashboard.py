import pandas as pd
import streamlit as st
from datetime import datetime, timedelta
from PIL import Image
import matplotlib.pyplot as plt
import altair as alt
import plotly.express as px

plt.rcParams['font.family'] ='Malgun Gothic'
plt.rcParams['axes.unicode_minus'] =False

st.set_page_config(page_title="카드사용내역", page_icon="🧊",layout="wide")

image = Image.open('C:/Users/MZC01-KEXIN/Desktop/streamlit/kakaopay_analysis/kakao_img.png')
st.sidebar.image(image)

st.title("Users Payment Analysis Dashboard")
st.sidebar.title('파일 업로드')
uploaded_file = st.sidebar.file_uploader("Choose a file")
if uploaded_file is not None:
    df = pd.read_csv(uploaded_file,encoding='utf-8')
##데이터 전처리
    df.loc[df['거래구분']=='[+] 송금취소','거래구분']="[+] 부족분충전"
    df.loc[df['거래구분']=='[+] 충전','거래구분']="[+] 부족분충전"
    df.loc[df['거래구분']=='[-] 내계좌로_내보내기','거래구분']="[-] 송금"
    df['yyyymmdd']=[i[:10] for i in df['거래일시']]
    df['yyyymm']=[i[:7] for i in df['거래일시']]
    df['yyyy']=[i[:4] for i in df['거래일시']]
    df['pay_type']=''
    for i in range(len(df)):
        if df.loc[i,'거래구분']=='[-] 송금':
            df.loc[i,'pay_type']='송금'
        elif '교통카드' in df.loc[i,'계좌 정보 / 결제 정보']:
            df.loc[i,'pay_type']='교통'
        elif '(' in df.loc[i,'계좌 정보 / 결제 정보'] and ')' in df.loc[i,'계좌 정보 / 결제 정보']:
            df.loc[i,'pay_type']='오픈라인'
        else:
            df.loc[i,'pay_type']='온라인'

    with st.expander('Filter'):
        add_selectbox = st.selectbox('분석기준', ('연도별','월별','일별'))

    if add_selectbox == '연도별':
        add_selectbox1 = st.selectbox('YEAR', tuple(df['yyyy'].drop_duplicates().tolist()))
        st.subheader('사용내역 Summary')
        df_pay_year = df.groupby(['yyyy','거래구분'])[['거래금액']].agg(['sum','count']).reset_index()
        df_pay_year.columns=['거래연도','거래구분','거래금액','거래횟수']
        df_pay_year_select = df_pay_year[df_pay_year['거래연도']==add_selectbox1].reset_index(drop=True)
        df_pay_year_select_2022 = df_pay_year[df_pay_year['거래연도']==str(int(add_selectbox1)-1)].reset_index(drop=True)

        df_pay_year_select['거래금액_증감'] = (df_pay_year_select['거래금액'] - df_pay_year_select_2022['거래금액']) / df_pay_year_select_2022['거래금액']
        df_pay_year_select['거래횟수_증감'] = (df_pay_year_select['거래횟수'] - df_pay_year_select_2022['거래횟수']) / df_pay_year_select_2022['거래횟수']

        col1, col2, col3, col4, col5 = st.columns(5)
        columns = [col1, col2, col3, col4, col5]

        for i,col in zip(range(len(df_pay_year_select)),columns):
            col.metric(label= df_pay_year_select['거래구분'][i], value = df_pay_year_select['거래금액'][i],delta = "{:.2%}".format(df_pay_year_select['거래금액_증감'][i]))
        for i,col in zip(range(len(df_pay_year_select)),columns):
            col.metric(label= df_pay_year_select['거래구분'][i], value = df_pay_year_select['거래횟수'][i],delta = "{:.2%}".format(df_pay_year_select['거래횟수_증감'][i]))

        df_pay_year2=df.groupby(['yyyy','pay_type'])[['거래금액']].agg(['sum','count']).reset_index()
        df_pay_year2.columns=['거래연도','거래용도','거래금액','거래횟수']
        df_pay_year2_select = df_pay_year2[df_pay_year2['거래연도']==add_selectbox1].reset_index(drop=True)


        col1, col2= st.columns([2,1])
        col1.subheader('거래용도별 사용금액')

        chart = alt.Chart(df_pay_year2_select).mark_bar().encode(
            x=alt.X('거래용도:N',axis=alt.Axis(labelAngle=0)),
            y='거래금액:Q',color=alt.Color('거래용도:N', legend=None)  # Hide the legend
        ).properties(width=400,height=300)
        col1.altair_chart(chart, use_container_width=True)


        col2.subheader('거래용도별 사용횟수')
        fig, ax = plt.subplots(figsize=(2,2))
        ax.pie(df_pay_year2_select['거래횟수'], labels=df_pay_year2_select['거래용도'], autopct='%1.1f%%',
                shadow=False, startangle=90)
        ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

        col2.pyplot(fig)

        # fig=alt.Chart(df_pay_year2_select).mark_arc().encode(theta="거래횟수",color="거래용도")
        # st.altair_chart(fig,use_container_width=True)
        # col1, col2, col3 = st.columns([1,2,1])
        # with col2:
        st.subheader('사용 내역')
        st.dataframe(df.drop(['계좌 정보 / 결제 정보','은행'],axis=1),width=5000000)
        
    elif add_selectbox == '월별':
        add_selectbox2 = st.selectbox('YEAR-MONTH', tuple(df['yyyymm'].drop_duplicates().tolist()))
        df_pay_month = df.groupby(['yyyymm','거래구분'])[['거래금액']].agg(['sum','count']).reset_index()
        df_pay_month.columns=['거래연월','거래구분','거래금액','거래횟수']
        df_pay_month_select = df_pay_month[df_pay_month['거래연월']==add_selectbox2].reset_index(drop=True)
        date_obj=datetime.strptime(add_selectbox2, '%Y-%m')
        previous_month = date_obj - timedelta(days=date_obj.day)
        previous_month_str = previous_month.strftime('%Y-%m')
        df_pay_month_select_2022 = df_pay_month[df_pay_month['거래연월']==str(previous_month_str)].reset_index(drop=True)

        col1, col2, col3, col4, col5 = st.columns(5)
        columns = [col1, col2, col3, col4, col5]

        for i,col in zip(range(len(df_pay_month_select)),columns):
            col.metric(label= df_pay_month_select['거래구분'][i], value = df_pay_month_select['거래금액'][i])
        for i,col in zip(range(len(df_pay_month_select)),columns):
            col.metric(label= df_pay_month_select['거래구분'][i], value = df_pay_month_select['거래횟수'][i])

        st.dataframe(df_pay_month_select)
        st.dataframe(df_pay_month_select_2022)

    # elif add_selectbox == '일별':
    #     add_selectbox2 = st.selectbox('YEAR-MONTH-DAY', tuple(df['yyyymmdd'].drop_duplicates().tolist()))
    #     df_pay_month = df.groupby(['yyyymm','거래구분'])[['거래금액']].agg(['sum','count']).reset_index()
    #     df_pay_month.columns=['거래연월','거래구분','거래금액','거래횟수']
    #     df_pay_month_select = df_pay_month[df_pay_month['거래연월']==add_selectbox2].reset_index(drop=True)

    #     col1, col2, col3, col4, col5 = st.columns(5)
    #     columns = [col1, col2, col3, col4, col5]

    #     for i,col in zip(range(len(df_pay_month_select)),columns):
    #         col.metric(label= df_pay_month_select['거래구분'][i], value = df_pay_month_select['거래금액'][i])
    #     for i,col in zip(range(len(df_pay_month_select)),columns):
    #         col.metric(label= df_pay_month_select['거래구분'][i], value = df_pay_month_select['거래횟수'][i])

    #     st.dataframe(df_pay_month_select)


if uploaded_file is None:
    st.write('업로드된 데이터가 없습니다.')











