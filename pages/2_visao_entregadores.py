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
st.set_page_config(page_title='Visão Entregadores', layout='wide')

#FUNCOES
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

def top_delivers(df, asc):
    delivery_speed = (df.loc[:,['Delivery_person_ID', 'City', 'Time_taken(min)']]
                          .groupby(['City', 'Delivery_person_ID'])
                          .mean()
                          .sort_values(['City', 'Time_taken(min)'], ascending = asc)
                          .reset_index())
    df_metro = delivery_speed.loc[delivery_speed['City'] == 'Metropolitian', :].head(10)
    df_urban = delivery_speed.loc[delivery_speed['City'] == 'Urban', :].head(10)
    df_semi = delivery_speed.loc[delivery_speed['City'] == 'Semi-Urban', :].head(10)
    df_aux = pd.concat([df_metro, df_urban, df_semi]).reset_index(drop=True)
    return df_aux
        


#FONTE
df = pd.read_csv("dataset/train.csv")
#LIMPEZA
data = transformacoes(df)




####################################
# STREAMLIT
####################################

############################################
#SIDEBAR
############################################
st.header( 'Marketplace - Visão Entregadores')
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
tab1, tab2, tab3 = st.tabs(['Visão Gerencial', '-', '-'])

with tab1:
    with st.container():
        st.title('Overall Metrics')
        col1, col2, col3, col4 = st.columns(4, gap='large')
        with col1:
            #MAIOR IDADE DOS ENTREGADORES
            idade_max = data['Delivery_person_Age'].max()
            col1.metric('Maior Idade' ,idade_max)
        with col2:
            #MENOR IDADE DOS ENTREGADORES
            idade_min = data['Delivery_person_Age'].min()
            col2.metric('Menor Idade' ,idade_min)
        with col3:     
            #MELHOR CONDICAO DE VEICULO
            veiculo_condicao_max = data['Vehicle_condition'].max()
            col3.metric('Melhor Veículo', veiculo_condicao_max)
        with col4:
            #PIOR CONDICAO DE VEICULO
            veiculo_condicao_min = data['Vehicle_condition'].min()
            col4.metric('Pior Veículo', veiculo_condicao_min)
            
    with st.container():
        st.markdown("""---""")
        st.markdown('# Avaliações')
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown('##### Avaliação Média por Entregador')
            score_medio_entregador = (data[['Delivery_person_ID', 'Delivery_person_Ratings']]
                                      .groupby('Delivery_person_ID')
                                      .mean()
                                      .reset_index())
            score_medio_entregador.columns = ['Delivery_person_ID', 'mean_score']
            st.dataframe(score_medio_entregador, height = 490)

        with col2:
            st.markdown('##### Avaliação Média por Trânsito')
            score_traffic = (data[['Road_traffic_density', 'Delivery_person_Ratings']]
                             .groupby('Road_traffic_density')
                             .agg({'Delivery_person_Ratings': ['mean', 'std']})
                             .reset_index())
            score_traffic.columns = ['Road_traffic_density', 'mean_score', 'std_score']
            st.dataframe(score_traffic)
            
            st.markdown('##### Avaliação Média por Clima')
            score_weather = (data[['Weatherconditions', 'Delivery_person_Ratings']]
                             .groupby('Weatherconditions')
                             .agg({'Delivery_person_Ratings':['mean', 'std']})
                             .reset_index())
            score_weather.columns = ['Weatherconditions', 'mean_score', 'std_score']
            st.dataframe(score_weather)
            
    with st.container():
        st.markdown("""---""")
        st.markdown('Velocidade de Entrega')
        col1, col2 = st.columns(2)
        with col1:
            st.markdown('##### Top 10 Entregadores mais Rápidos')
            df_aux = top_delivers(data, asc = True)
            st.dataframe(df_aux, height = 280)
        with col2:
            st.markdown('##### Top 10 Entregadores mais Lentos')
            df_aux = top_delivers(data, asc = False)
            st.dataframe(df_aux, height = 280)
            
