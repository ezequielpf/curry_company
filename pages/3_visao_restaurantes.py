# Libraries
import pandas as pd
import streamlit as st
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from PIL import Image
from haversine import haversine

st.set_page_config(page_title='Visão Restaurantes', page_icon='🍝', layout='wide')

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

def distance(df1, fig):
    cols = ['Restaurant_latitude', 'Restaurant_longitude', 'Delivery_location_latitude', 'Delivery_location_longitude']
    df1['Avg_Distance'] = df1.loc[:, cols].apply(lambda x: haversine(
                                                        (x['Restaurant_latitude'], x['Restaurant_longitude']),
                                                        (x['Delivery_location_latitude'], x['Delivery_location_longitude'])), axis=1)
    if fig == False:
        avg_distance = np.round(df1['Avg_Distance'].mean(), 2)
        return avg_distance
    else:
        avg_distance = df1.loc[:, ['City', 'Avg_Distance']].groupby(['City']).mean().reset_index()
        fig = go.Figure(data=[go.Pie(labels=avg_distance['City'], values=avg_distance['Avg_Distance'], pull=[0, 0.1, 0])])
        return fig

def avg_std_time_delivery(df1, statistics, festival):
    """ 
    Esta função calcula o tempo médio e o desvio padrão do tempo tempo de entrega.
    Parâmetros:
        Input:
            - df: Dataframe com os dados necessários para o cálculo
            - statistics: tipo de operação estatística que será retornada
                Opções: 'mean_delivery_time' ou 'std_delivery_time'
            - festival: uma string com 'Yes' or 'No' indicando se os pedidos foram feitos, ou não, durante o festival
        Output:
            - df: Dataframe com 2 colunas e 1 linha
    """
    cols = ['Time_taken(min)', 'Festival']
    lines = df1['Festival'] == festival
    df_aux = df1.loc[lines, cols].groupby(['Festival']).agg({'Time_taken(min)': ['mean','std']})
    df_aux.columns = ['mean_delivery_time', 'std_delivery_time']
    df_aux = df_aux.reset_index()
    df_aux = np.round(df_aux[statistics], 2)
    return df_aux

def avg_std_time_on_traffic(df1):
    cols = ['Time_taken(min)', 'City', 'Road_traffic_density']
    df_aux = df1.loc[:, cols].groupby(['City', 'Road_traffic_density']).agg({'Time_taken(min)': ['mean','std']})
    df_aux.columns = ['mean_delivery_time', 'std_delivery_time']
    df_aux = df_aux.reset_index()
    fig = px.sunburst(df_aux, path=['City', 'Road_traffic_density'], values='mean_delivery_time',
                    color='std_delivery_time', color_continuous_scale='RdBu_r',
                    color_continuous_midpoint=np.average(df_aux['std_delivery_time']))
    return fig

# ======================================================= Início da estrutura lógica do código =====================================
# Import dataset
df = pd.read_csv('./datasets/train.csv')

# Limpando os dados
df1 = clean_code(df)


# ====================================================================================
# Barra lateral do Streamlit
# ====================================================================================
st.header('Marketplace - Visão Restaurantes')

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
tab1, tab2, tab3 = st.tabs(['Visão Gerencial', '_', '_'])
with tab1:

    with st.container():
        st.title('Overall metrics')

        with st.container():
            col1, col2, col3 = st.columns(3)

            with col1:
                deliver_unique = len(df1.loc[:, 'Delivery_person_ID'].unique())
                col1.metric('Entregadores únicos', deliver_unique)

            with col2:
                avg_distance = distance(df1, fig=False)
                col2.metric('Distância média', avg_distance)

            with col3:
                df_aux = avg_std_time_delivery(df1, statistics='mean_delivery_time', festival='Yes')
                col3.metric('Tempo médio durante Festival', df_aux)

        with st.container():
            col4, col5, col6 = st.columns(3)

            with col4:
                df_aux = avg_std_time_delivery(df1, statistics='std_delivery_time', festival='Yes')
                col4.metric('Desvio padrão durante Festival', df_aux)

            with col5:
                df_aux = avg_std_time_delivery(df1, statistics='mean_delivery_time', festival='No')
                col5.metric('Tempo médio fora do Festival', df_aux)

            with col6:
                df_aux = avg_std_time_delivery(df1, statistics='std_delivery_time', festival='No')
                col6.metric('Desvio padrão fora do Festival', df_aux)

        st.markdown("""___""")

    with st.container():
        col7, col8 = st.columns(2)

        with col7:
            st.markdown('#### Tempo médio da entrega por cidade')
            cols = ['Time_taken(min)', 'City']
            df_aux = df1.loc[:, cols].groupby(['City']).agg({'Time_taken(min)': ['mean','std']})
            df_aux.columns = ['mean_delivery_time', 'std_delivery_time']
            df_aux = df_aux.reset_index()
            
            fig = go.Figure()
            fig.add_trace(go.Bar(name = 'Control', x=df_aux['City'], y=df_aux['mean_delivery_time'], error_y=dict(type='data', array=df_aux['std_delivery_time'])))
            fig.update_layout(barmode='group')
            st.plotly_chart(fig, use_container_width=True)

        with col8:
            st.markdown('#### Distâncias')
            cols = ['Time_taken(min)', 'City', 'Type_of_order']
            df_aux = df1.loc[:, cols].groupby(['City', 'Type_of_order']).agg({'Time_taken(min)': ['mean','std']})
            df_aux.columns = ['mean_delivery_time', 'std_delivery_time']
            df_aux = df_aux.reset_index()
            st.dataframe(df_aux)

        st.markdown("""___""")

    with st.container():
        st.title('Distribuição do tempo')
        col9, col10 = st.columns(2, gap='medium')

        with col9:  
            fig = distance(df1, fig=True)
            st.plotly_chart(fig, use_container_width=True)
            
        with col10:
            fig = avg_std_time_on_traffic(df1)
            st.plotly_chart(fig, use_container_width=True)

        st.markdown("""___""")