# Libraries
import pandas as pd
import streamlit as st
from PIL import Image
from haversine import haversine

st.set_page_config(page_title='Visão Entregadores', page_icon=':bike:', layout='wide')

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

def top_delivers(df1, ascend):
    cols = ['Delivery_person_ID', 'Time_taken(min)', 'City']
    df_aux = df1.loc[:, cols].groupby(['City','Delivery_person_ID']).max().sort_values(by=['City', 'Time_taken(min)'], ascending=ascend).reset_index()

    df_aux01 = df_aux.loc[df_aux['City'] == 'Metropolitian', :].head(10)
    df_aux02 = df_aux.loc[df_aux['City'] == 'Urban', :].head(10)
    df_aux03 = df_aux.loc[df_aux['City'] == 'Semi-Urban', :].head(10)

    df_aux = pd.concat([df_aux01, df_aux02, df_aux03]).reset_index(drop=True)
    return df_aux
    
# ======================================================= Início da estrutura lógica do código =====================================
# Import dataset
df = pd.read_csv('./datasets/train.csv')

# Limpando os dados
df1 = clean_code(df)


# ====================================================================================
# Barra lateral do Streamlit
# ====================================================================================
st.header('Marketplace - Visão Entragadores')

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
        st.title('Overall Metrics')
        col1, col2, col3, col4 = st.columns(4, gap='large')
        with col1:
            maior_idade = df1.loc[:, "Delivery_person_Age"].max()
            col1.metric('Maior idade', maior_idade)            
        with col2:
            menor_idade = df1.loc[:, "Delivery_person_Age"].min()
            col2.metric('Menor idade', menor_idade)
        with col3:   
            melhor_condicao = df1.loc[:, "Vehicle_condition"].max()
            col3.metric('Melhor condição do veículo', melhor_condicao)
        with col4:
            pior_condicao = df1.loc[:, "Vehicle_condition"].min()
            col4.metric('Pior condição do veículo', pior_condicao)
        st.markdown("""___""")
    
    with st.container():
        st.title('Avaliações')
        col1, col2 = st.columns(2, gap='large')
        with col1:
            st.markdown('##### Avaliação média por entregador')
            df_avg_ratings_per_deliver = df1.loc[:, ['Delivery_person_Ratings', 'Delivery_person_ID']].groupby(['Delivery_person_ID']).mean().reset_index()
            st.dataframe(df_avg_ratings_per_deliver)
            
        with col2:
            st.markdown('##### Avaliação média por condição de trânsito') 
            cols = ['Delivery_person_Ratings', 'Road_traffic_density']
            df_avg_std_rating_by_traffic = df1.loc[:, cols].groupby(['Road_traffic_density']).agg(['mean', 'std'])
            ## mudança dos nomes das colunas
            df_avg_std_rating_by_traffic.columns = ['Mean', 'std']
            df_avg_std_rating_by_traffic = df_avg_std_rating_by_traffic.reset_index()
            st.dataframe(df_avg_std_rating_by_traffic)

            st.markdown('##### Avaliação média por clima')
            cols = ['Delivery_person_Ratings', 'Weatherconditions']
            df_avg_std_rating_by_weather = df1.loc[:, cols].groupby(['Weatherconditions']).agg(['mean', 'std'])
            df_avg_std_rating_by_weather.columns = ['mean', 'std']
            df_avg_std_rating_by_weather = df_avg_std_rating_by_weather.reset_index()
            st.dataframe(df_avg_std_rating_by_weather)
        st.markdown("""___""")

    with st.container():
        st.title('Velocidade de entrega')
        col1, col2 = st.columns(2, gap='large')
        with col1:
            st.markdown('##### Top entregadores mais rápidos')
            df_aux = top_delivers(df1, ascend=True)
            st.dataframe(df_aux)

        with col2:
            st.markdown('##### Top entregadores mais lentos')
            df_aux = top_delivers(df1, ascend=False)
            st.dataframe(df_aux)