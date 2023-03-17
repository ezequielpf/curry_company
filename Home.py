import streamlit as st
from PIL import Image

st.set_page_config(
    page_title='Home',
    page_icon='📊'
)

#image_path = '/home/ezequiel/Documentos/Comunidade_DS/Analise_dados_com_python/'
image = Image.open('logo.jpeg')
st.sidebar.image(image, width=120)

st.sidebar.markdown('# Curry Company')
st.sidebar.markdown('## Fastest Delivery in Town')
st.sidebar.markdown("""___""")

st.write('## Curry Company Growth Dashboard')

st.markdown(
    """
    Growth Dashboard foi construído para acompanhas as métricas de crescimento dos entregadores e restaurantes.
    ### Como utilizar este Dashboard?
    - Visão Empresa:
        - Visão Gerencial: métricas gerais de comportamento
        - Visão Tática: indicadores semanais de crescimento
        - Visão Geográfica: insights de geolocalização
    - Visão Entregador:
        - Acompanhamento dos indicadores semanais de cresciemnto
    - Visão Restaurantes:
        - Indicadores semanais de crescimento dos restaurantes
    ### Ask for help
    - Time de Data Science no Discord
    """)