from haversine import haversine
import datetime
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import streamlit as st
from PIL import Image
import folium
from streamlit_folium import folium_static
pd.set_option('display.max_columns', None)
st.set_page_config(page_title='Visão Empresa', layout='wide')

###########################
# FUNCOES #################
###########################

##TRANSFORMACOES E FEATURES
def transformacoes(df):
    """ Esta funcao realiza a limpeza do dataframe
        
        Tipos de limpeza:
        1. Remocao dos dados NaN
        2. Mudanca no tipo de coluna de dados
        3. Remocao de espacos nas strings
        4. Formatacao de culuna de datas
        5. Limpeza da coluna de tempo
        
        Input: Dataframe
        Output: Dataframe
        
    """
    
    ###RETIRANDO ESPACOS
    cols_st = list(df.select_dtypes('object').columns)
    for c in cols_st:
        df[c] = df[c].str.strip()
    ###RETIRANDO VALORES NAN
    cols = list(df.columns)
    for c in cols:
        df = df.loc[df[c] != 'NaN', :]
    ###TRANSFORMACOES
    df['Weatherconditions'] = df['Weatherconditions'].str.replace('conditions ','')
    df['Time_taken(min)'] = df['Time_taken(min)'].apply(lambda x: x.split()[1])
    df['Time_taken(min)'] = df['Time_taken(min)'].astype('int64')
    df['Order_Date'] =  pd.to_datetime(df['Order_Date'], format = '%d-%m-%Y')
    df['week_of_year'] = df['Order_Date'].dt.strftime( '%U')
    df['Delivery_person_Age'] = df['Delivery_person_Age'].astype('int64')
    df['Delivery_person_Ratings'] = df['Delivery_person_Ratings'].astype('float64')
    df['multiple_deliveries'] = df['multiple_deliveries'].astype('int64')
    df['Time_Orderd'] = pd.to_datetime(df['Time_Orderd'], format= '%H:%M:%S').dt.time
    df['Time_Order_picked'] = pd.to_datetime(df['Time_Order_picked'], format= '%H:%M:%S').dt.time
    df = df.reset_index(drop=True)
    return df

##STREAMLIT
###METRICAS DOS PEDIDOS
def order_metrics(df):           
    pedidos_dia = df[['Order_Date', 'ID']].groupby('Order_Date').count().reset_index()
    pedidos_dia.columns = ['Order_Date', 'Count']
    fig = px.bar(pedidos_dia, x='Order_Date', y='Count')
    return fig
###SHARE DOS PEDIDOS POR TRAFEGO
def traffic_orders_share(df):                
    pedidos_trafego = df[['Road_traffic_density', 'ID']].groupby('Road_traffic_density').count().reset_index()
    pedidos_trafego.columns = ['Road_traffic_density', 'count']
    fig = px.pie(pedidos_trafego, values = 'count', names = 'Road_traffic_density')
    return fig
###PEDIDOS POR TRAFEGO E TIPO DE CIDADE
def traffic_order_city(df):
    cidade_trafego = df[['City', 'Road_traffic_density', 'ID']].groupby(['City', 'Road_traffic_density']).count().reset_index()
    cidade_trafego.columns = ['City', 'Road_traffic_density', 'Count']
    fig = px.scatter(cidade_trafego, x='City', y='Road_traffic_density', size= 'Count', color='City')
    return fig
###PEDIDOS POR SEMANA
def order_by_week(df):
    pedidos_semana = df[['week_of_year', 'ID']].groupby('week_of_year').count().reset_index()
    pedidos_semana.columns = ['week_of_year', 'number_of_deliveries']
    fig = px.line(pedidos_semana,x='week_of_year', y='number_of_deliveries')
    return fig
###PEDIDOS POR ENTREGADOR POR SEMANA
def order_share_by_week(df):
    pedidos_semana = df[['week_of_year', 'ID']].groupby('week_of_year').count().reset_index()
    pedidos_semana.columns = ['week_of_year', 'number_of_deliveries']
    unique_person_week = df[['week_of_year', 'Delivery_person_ID']].groupby('week_of_year').nunique().reset_index()
    unique_person_week.columns = ['week_of_year', 'unique_delivery_person_count']
    aux = pd.merge(unique_person_week, pedidos_semana, how='inner')
    aux['orders_by_num_of_delperson'] = round(aux['number_of_deliveries'] / aux['unique_delivery_person_count'], 3)
    fig = px.line(aux,x='week_of_year', y='orders_by_num_of_delperson')
    return fig
### MAPA
def country_map(df):
    mapa = folium.Map()
    centro = df[['City', 'Road_traffic_density', 'Delivery_location_latitude', 'Delivery_location_longitude']].groupby(['City', 'Road_traffic_density']).median().reset_index()
    for index, row in centro.iterrows():
        folium.Marker([row['Delivery_location_latitude'], row['Delivery_location_longitude']]).add_to(mapa)
    folium_static(mapa, width = 1024, height = 600)
    return None

# FONTE
df = pd.read_csv('dataset/train.csv')

# TRANSFORMACOES E FEATURES
data = transformacoes(df)


####################################
# STREAMLIT
####################################

############################################
#SIDEBAR
############################################
st.header( 'Marketplace - Visão Clientes')
# image_path = 'C:\\Users\\marci\\repos_cds\\FTC\\c06\\47_criando_pagina_empresa\\streamlit.png'
image = Image.open("streamlit.png")
st.sidebar.image(image, width=120)

st.sidebar.markdown('# Cury Company')
st.sidebar.markdown('## Fastest Delivery in Town')
st.sidebar.markdown("""---""")
st.sidebar.markdown('## Selecione uma data limite')

date_slider = st.sidebar.slider(
    'Até qual valor?',
    value = datetime.datetime(2022, 3, 1),
    min_value = datetime.datetime(2022, 2, 11),
    max_value = datetime.datetime(2022, 4, 13),
    format='DD-MM-YYYY'
                    )
st.sidebar.markdown("""---""")
#FILTRO DE DATA
linhas_filtradas = data['Order_Date'] < date_slider
data = data.loc[linhas_filtradas, :]
st.sidebar.markdown("""---""")

traffic_options = st.sidebar.multiselect(
    'Quais as condições de trânsito?',
    list(data['Road_traffic_density'].unique()),
    default = list(data['Road_traffic_density'].unique())
    )
#FILTRO DE TRANSITO
linhas_filtradas = data['Road_traffic_density'].isin(traffic_options)
data = data.loc[linhas_filtradas, :]

st.sidebar.markdown("""---""")
st.sidebar.markdown('### Powered by CDS')

############################################
#MAIN
############################################

tab1, tab2, tab3 = st.tabs(['Visão Gerencial', 'Visão Tática', 'Visão Geográfica'])

#### TAB VISAO GERENCIAL
with tab1:
    with st.container():
        st.header('Pedidos por Dia')
        fig = order_metrics(data)        
        st.plotly_chart(fig, use_container_width=True)
               
    with st.container():
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('##### Pedidos por Trânsito')
            fig = traffic_orders_share(data)
            st.plotly_chart(fig, use_container_width=True)
                 
        with col2:
            st.markdown('##### Pedidos por Tipo de cidade e Trânsito')
            fig = traffic_order_city(data)
            st.plotly_chart(fig, use_container_width=True)
            
####TAB VISAO TATICA
with tab2:
    with st.container():
        st.markdown('# Deliveries per Week of Year')
        fig = order_by_week(data)
        st.plotly_chart(fig, use_container_width=True)
            
    with st.container():
        st.markdown('# Deliveries per Delivery person per Week')
        fig = order_share_by_week(data)
        st.plotly_chart(fig,use_container_width =True)
        

####TAB VISAO GEOGRAFICA
with tab3:
    st.markdown('# Map')
    country_map(data)
    
    


    
    
    