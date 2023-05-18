import streamlit as st
from PIL import Image

st.set_page_config(
    page_title='Home',
    layout='wide'
    )

#image_path = 'C:\\Users\\marci\\repos_cds\\FTC\\c06\\47_criando_pagina_empresa\\streamlit.png'
image = Image.open("streamlit.png")
st.sidebar.image(image, width = 120)

st.sidebar.markdown('# Cury Company')
st.sidebar.markdown('## Fastest Delivery in Town')
st.sidebar.markdown("""---""")

st.write("# Curry Company Growth Dashboard")
st.markdown(
        """
        Dashboard construído para acompanhar as métricas de crescimento dos Entregadores, Restaurantes e Empresa.
        ### Como utilizar?
            - Visão Empresa:
                - Visdão Gerencial: Métricas gerais de comportament.
                - Visão Tática: Indicadores semanais de crescimento.
                - Visão Geográfica: Insights de geolocalização.
            - Visão entregador:
                - Acompanhamento dos indicadores semanais de crescimento.
            - Visão Restaurante:
                - Indicadores semanais de crescimento dos restaurantes.        
        """
)
