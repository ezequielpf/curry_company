# Libraries
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import folium
from streamlit_folium import folium_static
from PIL import Image
from haversine import haversine

st.set_page_config(page_title='Visão Empresa', page_icon='📈', layout='wide')

# ====================================================================================
# Funções
# ====================================================================================
def clean_code(df1):
    """ Esta função tem a finalidade de limpar e formatar o dataframe.
        Tipos de limpeza:
        1. Remoção dos dados NaN
        2. Mudança do tipo dos dados
        3. Remoção dos espaços em branco
        4. Formatação das colunas de tempo
        Input: Dataframe
        Output: Dataframe
    """

    # Limpando e formatando Dataframe
    ## criterio para selecionar as linhas diferentes de NaN
    linhas = (df1['Delivery_person_Age'] != 'NaN ') & (df1['multiple_deliveries'] != 'NaN ') & (df1['Road_traffic_density'] != 'NaN ') & (df1['City'] != 'NaN ') & (df1['Festival'] != 'NaN ')

    ## elimitar as linhas com NaN
    df1 = df1.loc[linhas, :]

    ## aterar o tipo para o apropriado
    df1['Delivery_person_Age'] = df1['Delivery_person_Age'].astype(int)
    df1['Delivery_person_Ratings'] = df1['Delivery_person_Ratings'].astype(float)
    df1['Order_Date'] = pd.to_datetime(df1['Order_Date'], format = '%d-%m-%Y')
    df1['multiple_deliveries'] = df1['multiple_deliveries'].astype(int)

    ## Removendo espaços em branco
    df1.loc[:, 'ID'] = df1.loc[:, 'ID'].str.strip()   # o .str acessa o conteúdo da series df1.loc[:, 'ID'] como uma string, permitindo o uso do strip, que só é aplicado sobre strings
    df1.loc[:, 'Road_traffic_density'] = df1.loc[:, 'Road_traffic_density'].str.strip()
    df1.loc[:, 'City'] = df1.loc[:, 'City'].str.strip()
    df1.loc[:, 'Type_of_vehicle'] = df1.loc[:, 'Type_of_vehicle'].str.strip()
    df1.loc[:, 'Type_of_order'] = df1.loc[:, 'Type_of_order'].str.strip()
    df1.loc[:, 'Festival'] = df1.loc[:, 'Festival'].str.strip()

    ## Limpando a coluna Time_taken
    ### lambda x: x**2 --> f(x) = x^2
    df1['Time_taken(min)'] = df1['Time_taken(min)'].apply(lambda x: x.split('(min) ')[1])
    df1['Time_taken(min)'] = df1['Time_taken(min)'].astype(int)
    return df1


def order_metric(df1):
    """ Finalidade da função:
        1. Agrupar a quantidade de entregas por dia
        2. Plotar um gráfico de barras mostrando as entregas por dia
        Input: Dataframe
        Output: Fig
    """
    # filtrando colunas
    cols = ['ID', 'Order_Date']

    # seleção das colunas e agrupando por data
    df_aux = df1.loc[:, cols].groupby('Order_Date').count().reset_index()
    df_aux.head()

    # plotar grafico de barra
    fig = px.bar(df_aux, x='Order_Date', y='ID')
    return fig


def traffic_order_share(df1):
    """ Finalidade da função:
        1. Agrupar a quantidade de entregas por densidade de tráfego
        2. Plotar um gráfico de pizza mostrando a quantidade relativa de entregas em cada densidade de tráfego
        Input: Dataframe
        Output: Fig
    """
    # filtrando colunas
    cols = ['ID', 'Road_traffic_density']

    # agrupa df por tráfego e conta os IDs
    df_aux = df1.loc[:, cols].groupby(['Road_traffic_density']).count().reset_index()

    # cria nova coluna com o valor relativo das entregas por tráfego
    df_aux['relative_deliv'] = df_aux['ID'] / (df_aux['ID'].sum())

    # gráfico de pizza
    fig = px.pie(df_aux, values='relative_deliv', names='Road_traffic_density')
    return fig


def traffic_order_city(df1):
    """ Finalidade da função:
        1. Agrupar a quantidade de entregas por cidade e por densidade de tráfego
        2. Plotar um gráfico de bolha mostrando as entregas por dia
        Input: Dataframe
        Output: Fig
    """
    # filtrando colunas
    cols = ['ID', 'City', 'Road_traffic_density']

    # total de entregas argupadas por cidade e tráfego
    df_aux = df1.loc[:, cols].groupby(['City', 'Road_traffic_density']).count().reset_index()

    # gráfico de bolha
    fig = px.scatter(df_aux, x='City', y='Road_traffic_density', size='ID', color='City')
    return fig


def order_by_week(df1):
    """ Finalidade da função:
        1. Cria uma nova coluna para indicar a qual semana do ano a data do podido se refere
        2. Agrupa os pedidos por semana
        3. Plota um gráfico de linha mostrando as entregas por semana
        Input: Dataframe
        Output: Fig
    """
    # criar a coluna week_of_year
    df1['week_of_year'] = df1['Order_Date'].dt.strftime('%U')      # pega Order_Date (no formato datetime) e aplica .streftime para indicar qual a semana (máscara %U) do ano é aquela data

    # agrupa os pedidos por semana
    df_aux = df1.loc[:, ['ID', 'week_of_year']].groupby(['week_of_year']).count().reset_index()

    # gráfico de linha
    fig = px.line(df_aux, x='week_of_year', y='ID')
    return fig


def order_share_by_week(df1):
    """ Finalidade da função:
        1. Calcula a média de entregas por entregador em cada semana
        2. Plota um gráfico de linha mostrando as entregas médias por entregador por semana
        Input: Dataframe
        Output: Fig
    """
    # pedidos por semana
    cols = ['ID', 'week_of_year']
    df_aux01 = df1.loc[:, cols].groupby(['week_of_year']).count().reset_index()

    # entregadores unicos por semana
    cols = ['Delivery_person_ID', 'week_of_year']
    df_aux02 = df1.loc[:, cols].groupby(['week_of_year']).nunique().reset_index()      # retorna quantos entregadores únicos existem em cada semana

    # juntar os dois dataframes
    df_aux = pd.merge(df_aux01, df_aux02, how='inner')

    # fazer a divisão das colunas
    df_aux['order_by_deliver'] = df_aux['ID'] / df_aux['Delivery_person_ID']

    # gráfico de linha
    fig = px.line(df_aux, x='week_of_year', y='order_by_deliver')
    return fig


def country_map(df1):
    """ Finalidade da função:
        1. Calcula a mediana e o desvio padrão das latitudes e longitudes dos locais de entrega em cada cidade, para cada tráfego
        2. Plota um mapa com as localizações centrais de cada cidade indicando o tipo de tráfego 
        Input: Dataframe
        Output: None
    """
    # filtrando colunas
    cols = ['City', 'Road_traffic_density', 'Delivery_location_latitude', 'Delivery_location_longitude']

    # encontra a mediana das latitudes e longitudes (ponto central) em cada cidade, para cada tráfego
    df_aux = df1.loc[:, cols].groupby(['City', 'Road_traffic_density']).median().reset_index()

    # mostra o país
    latitude = 21.382561028263332
    longitude = 78.88947366027652
    map = folium.Map(location=[latitude, longitude], zoom_start=5)

    for index, location_info in df_aux.iterrows():
        folium.Marker([location_info['Delivery_location_latitude'], location_info['Delivery_location_longitude']],
                    popup=location_info['City'],
                    icon=folium.Icon(color="blue", icon="info-sign")).add_to(map)
    folium_static(map, width=1024, height=600)
# ======================================================= Início da estrutura lógica do código =====================================

# Import dataset
df = pd.read_csv('./datasets/train.csv')

# Limpando os dados
df1 = clean_code(df)


# ====================================================================================
# Barra lateral do Streamlit
# ====================================================================================
st.header('Marketplace - Visão Empresa')

#image_path = '/home/ezequiel/Documentos/Comunidade_DS/Analise_dados_com_python/logo.jpeg'
image = Image.open('logo.jpeg')      # Image.open bem da lib PIL
st.sidebar.image(image, width=120)

st.sidebar.markdown('# Curry Company')
st.sidebar.markdown('## Fastest Delivery in Town')

st.sidebar.markdown("""___""")

st.sidebar.markdown('## Selecione uma data limite')

date_slider = st.sidebar.slider(
    'Até qual valor?',
    value=pd.datetime(2022, 4, 13),
    min_value=pd.datetime(2022, 2, 11),
    max_value=pd.datetime(2022, 4, 6),
    format='DD-MM-YYYY')

st.sidebar.markdown("""___""")

traffic_options = st.sidebar.multiselect(
    'Quais as condições de trânsito?',
    ['Low', 'Medium', 'High', 'Jam'],
    default=['Low', 'Medium', 'High', 'Jam']
)

st.sidebar.markdown("""___""")
st.sidebar.markdown('### Powered by Comunidade DS')

# Filtro de data
linhas = df1['Order_Date'] < date_slider
df1 = df1.loc[linhas, :]

# Filtro de traffic density
linhas = df1['Road_traffic_density'].isin(traffic_options)
df1 = df1.loc[linhas, :]

# ====================================================================================
# Layout do Streamlit
# ====================================================================================
tab1, tab2, tab3 = st.tabs(['Visão Gerencial', 'Visão Tática', 'Visão Geográfica'])

with tab1:
    with st.container():
        st.markdown('# Orders by Day')
        fig = order_metric(df1)
        st.plotly_chart(fig, use_container_width=True)        
    
    with st.container():
        col1, col2 = st.columns(2)
        with col1:
            st.header('Traffic Order Share')
            fig = traffic_order_share(df1)
            st.plotly_chart(fig, use_container_width=True)           
            
        with col2:
            st.header('Traffic Order City')
            fig = traffic_order_city(df1)
            st.plotly_chart(fig, use_container_width=True)
                 
with tab2:
    with st.container():
        st.markdown('# Order by Week')
        fig = order_by_week(df1)
        st.plotly_chart(fig, use_container_width=True)     

    with st.container():
        st.markdown('# Order Share by Week')
        fig = order_share_by_week(df1)
        st.plotly_chart(fig, use_container_width=True)   

with tab3:
    st.markdown('# Country Map')
    country_map(df1)