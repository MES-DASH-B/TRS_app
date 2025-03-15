import streamlit as st
import pandas as pd 
import plotly.express as px
from streamlit_option_menu import option_menu




st.set_page_config (page_title= "POINT TRS", page_icon="📈", layout="wide")
st.header ("Analyse TRS SHINKO & MS20")
st.title ("mon premier titre streamlit 👹")
st.write ("Bienvenu chez moi")

df= pd.read_excel(
    io='CALCUL_TRS.xlsx',
    engine='openpyxl',
    sheet_name='Arrêts',
    skiprows=4,
    usecols='B:H',
    nrows=200,
)



#st.dataframe(df)

st.sidebar.header("Filitre référance:")
Équipe = st.sidebar.multiselect(
    "Choisir l'équipe:",
    options = df["Équipe"].unique(),
    default = df["Équipe"].unique()

)
df_selection = df.query("Équipe == @Équipe")
st.dataframe(df_selection)

st.title(":bar_chart: Suivis TRS")
st.markdown("##")

total_quantité = int(df_selection["Durées (m)"].sum())
moyenne = round(df_selection["Durées (m)"].mean(),1)
#star_rating = ":star:" * int(round(moyenne, 0))

left_colum, middle_colum, right_colum = st.columns(3)
with left_colum:
    st.subheader("Total Quantité:")
    st.subheader(f"Pièces: {total_quantité:,}")
with middle_colum:
    st.subheader("Moyenne Quantité:")
    st.subheader(f"Pièces: {moyenne:,}")
with right_colum:
    st.subheader("Average sales per")

st.markdown("----") 

with st.sidebar:
    selected = option_menu(menu_title=None,options=["Secteur Traction/Torsion", "Secteur Compression", "Secteur Form","Secteur E-Mobility"],icons=["asterisk", "asterisk","asterisk","asterisk"],menu_icon="cast",default_index=0,orientation="vertical",
        styles={
                "container": {"background-color": "#ffffff"},
                "icon": {"color": "Black", "font-size": "20px"}, 
                "nav-link": {"font-size": "15px", "text-align": "left", "margin":"0px", "--hover-color": "#93d6f5"},
                "nav-link-selected": {"background-color": "red"},})

if selected == "Secteur Traction/Torsion" :
    st.error (f":black_circle: INDICATEURS MAINTENANCE ENTREPRISE. LIGNE PRODUCTION 1 | SUIVI ET ANALYSE : PANNES, ETIQUETTES MTTR, MTBF ")
    with st.sidebar:
        selected = option_menu(menu_title=None,options=["ACCUEIL", "ANALYS MAINT.", "TPM", "ARRETS"],icons=["pc-display-horizontal", "graph-up-arrow", "tools", "layout-wtf"],
            menu_icon="cast",default_index=0,orientation="vertical",
            styles={
                "nav-link": { "--hover-color": "#93d6f5"},
                "nav-link-selected": {"background-color": "Black"},})
        
fig33 = px.bar(df_selection, x="Date", y="Arrêts", color="Machine", template = 'plotly')
st.write(fig33)

fig34 = px.bar(df_selection, x="Date", y="Durées (m)", color="Arrêts", template = 'plotly')
st.write(fig34)

fig101 = px.bar(df_selection, x="Machine",y="Durées (m)",color="Arrêts", template = 'plotly' )
st.write(fig101)
#-----------------------------------------------------------------------------

