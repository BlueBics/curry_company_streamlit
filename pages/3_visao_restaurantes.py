from haversine import haversine
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import streamlit as st
from PIL import Image
import folium
from streamlit_folium import folium_static
st.set_page_config(page_title='Visão Restaurantes', layout='wide')

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

def distancia(df, fig):
    if fig == False:
        df['distance'] = (df.apply(
                            lambda x: haversine((x['Restaurant_latitude'], 
                                                 x['Restaurant_longitude']), 
                                                (x['Delivery_location_latitude'], 
                                                 x['Delivery_location_longitude'])),
                                                axis=1))
        avg_distance = np.round(df['distance'].mean(), 2)
        return avg_distance
    else:
        df['distance'] = (df.apply(
                            lambda x: haversine((x['Restaurant_latitude'], 
                                                 x['Restaurant_longitude']), 
                                                (x['Delivery_location_latitude'], 
                                                 x['Delivery_location_longitude'])),
                                                axis=1))
        avg_distance = df.loc[:, ['City', 'distance']].groupby('City').mean().reset_index()
        fig = (go.Figure( 
                   data=[go.Pie(
                       labels=avg_distance['City'], 
                       values=avg_distance['distance'], 
                       pull=[0,0.1,0])]))
        return fig
        
def tempo_festival(df, festival):    
    tempo_festival = (df[['Festival', 'Time_taken(min)']]
                      .groupby('Festival')
                      .agg({'Time_taken(min)':['mean', 'std']})
                      .reset_index())
    tempo_festival.columns = ['Festival', 'avg_time_taken', 'time_taken_std']
    tempo_festival = (np.round(tempo_festival.loc[tempo_festival['Festival'] == festival, 
                                                              'avg_time_taken'], 2))
    return tempo_festival

def bar_chart_time_mean_std(df):
    tempo_medio_cidade = (df[['City', 'Time_taken(min)']]
                          .groupby('City')
                          .agg({'Time_taken(min)':['mean', 'std']})
                          .reset_index())
    tempo_medio_cidade.columns = ['City', 'time_taken_mean', 'time_taken_std']
    fig = go.Figure()
    fig.add_trace(go.Bar(name='Control',
                              x=tempo_medio_cidade['City'],
                              y=tempo_medio_cidade['time_taken_mean'],
                              error_y=dict(type='data', 
                              array=tempo_medio_cidade['time_taken_std'])
                        ))
    fig.update_layout(barmode='group')
    return fig

def sunburst(df):    
    tempo_medio_cidade_tra = (df[['City', 'Road_traffic_density', 'Time_taken(min)']]
                              .groupby(['City', 'Road_traffic_density'])
                              .agg({'Time_taken(min)':['mean', 'std']})
                              .reset_index())
    tempo_medio_cidade_tra.columns = ['City', 'traffic', 'time_taken_mean', 'time_taken_std']
    fig = px.sunburst(tempo_medio_cidade_tra, 
                      path=['City', 'traffic'], 
                      values='time_taken_mean',
                      color='time_taken_std', 
                      color_continuous_scale='RdBu', 
                      color_continuous_midpoint = np.average(
                      tempo_medio_cidade_tra['time_taken_std']))
    return fig

def tempo_cidade_tipo_pedido(df):
    tempo_medio_cidade_order = (df[['City', 'Type_of_order', 'Time_taken(min)']]
                                    .groupby(['City', 'Type_of_order'])
                                    .agg({'Time_taken(min)':['mean', 'std']})
                                    .reset_index())
    tempo_medio_cidade_order.columns = ['City', 
                                            'type_of_order', 
                                            'time_taken_mean', 
                                            'time_taken_std']
    return tempo_medio_cidade_order

#FONTE
df = pd.read_csv("dataset/train.csv")

data = transformacoes(df)
  


####################################
# STREAMLIT
####################################

############################################
#SIDEBAR
############################################
st.header( 'Marketplace - Visão Restaurantes')
# image_path = 'C:\\Users\\marci\\repos_cds\\FTC\\c06\\47_criando_pagina_empresa\\streamlit.png'
image = Image.open("streamlit.png")
st.sidebar.image(image, width=120)

st.sidebar.markdown('# Cury Company')
st.sidebar.markdown('## Fastest Delivery in Town')
st.sidebar.markdown("""---""")
st.sidebar.markdown('## Selecione uma data limite')

date_slider = st.sidebar.slider(
    'Até qual valor?',
    value = pd.datetime(2022, 3, 1),
    min_value = pd.datetime(2022, 2, 11),
    max_value = pd.datetime(2022, 4, 13),
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
tab1, tab2, tab3 = st.tabs(['Visão Gerencial','-', '-'])

with tab1:
    with st.container():
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            entregadores_unicos = df['Delivery_person_ID'].nunique()
            col1.metric('Entregadores Únicos', entregadores_unicos)
        with col2:
            avg_distance = distancia(data, fig = False)
            col2.metric('Distância Média', avg_distance)
        with col3:
            tempo = tempo_festival(data, festival = 'Yes')
            col3.metric('Festival Tempo Médio',tempo)
        with col4:
            tempo = tempo_festival(data, festival = 'No')
            col4.metric('Tempo Médio',tempo)
    with st.container():
        st.markdown("""---""")
        st.subheader('Comparação Distância Média')
        fig = distancia(data, fig = True)    
        st.plotly_chart(fig, use_container_width=True)
    with st.container():
        st.markdown("""---""")
        st.subheader('Distribuição de Tempo')        
        col1, col2 = st.columns(2)
        with col1:   
            fig = bar_chart_time_mean_std(data)
            st.plotly_chart(fig, use_container_width=True)    
        with col2:
            fig = sunburst(data)
            st.plotly_chart(fig, use_container_width=True)
    with st.container():        
        st.markdown("""---""")
        st.markdown('Tempo Médio por Cidade e Tipo de Pedido')
        tempo_medio_cidade_order = tempo_cidade_tipo_pedido(data)
        st.dataframe(tempo_medio_cidade_order)
    


        
        
        
        