import streamlit as st
import pandas as pd 
import plotly.express as px
from streamlit_option_menu import option_menu
from PIL import Image
from millify import millify




st.set_page_config (page_title= "POINT TRS", page_icon="📈", layout="wide")
image = Image.open('image.jpg') 
st.image(image, width = 250)

#st.header ("Analyse TRS SHINKO & MS20")
st.title ("Analyse Taux de Rendement Synthétique")
st.subheader ("Accueil")

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
with st.expander("Data preview"):
    st.dataframe(df_selection)

#st.title(":bar_chart: Suivis TRS")
st.markdown("##")



#___________________________
@st.cache_data(ttl=0)
def load_css(file_name):
    with open(file_name, "r") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Load the CSS file
load_css("style.css")

Nombr_arrets= int(df_selection["Arrêts"].count())
Durées_arrets= int(df_selection["Durées (h)"].sum())
Durée_arret_jr = round(int(Durées_arrets/24),1)
moyenne = round(df_selection["Durées (h)"].mean(),1)


# Arrange metrics in columns with the blue background style
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(
        f"""
        <div class="metric-container">
            <p class="metric-label">Nombre total des arrets</p>
            <p class="metric-value">{Nombr_arrets}</p>
        </div>
        """,
        unsafe_allow_html=True
    )

with col2:
    st.markdown(
        f"""
        <div class="metric-container">
            <p class="metric-label">Durées total des arrets</p>
            <p class="metric-value">{Durées_arrets} h</p>
        </div>
        """,
        unsafe_allow_html=True
    )

with col3:
    st.markdown(
        f"""
        <div class="metric-container">
            <p class="metric-label">Dureée des arrets en jours</p>
            <p class="metric-value">{Durée_arret_jr} Jours</p>
        </div>
        """,
        unsafe_allow_html=True
    )
with col4:
    st.markdown(
        f"""
        <div class="metric-container">
            <p class="metric-label">Durée moyenne d'un arret</p>
            <p class="metric-value">{moyenne} h</p>
        </div>
        """,
        unsafe_allow_html=True
    )

coll100, coll200,coll300 = st.columns([3,3,4])
fig24 = px.pie (df_selection,  values="Durées (h)" , names="Machine", color="Machine", hole= .4,  color_discrete_sequence=px.colors.diverging.RdYlGn)
fig24.update_traces(textposition='inside')
fig24.update_layout({
                                    'uniformtext_minsize':18,'uniformtext_mode':'hide',
                                    'height' : 410, 'font': {'size':15},
                                    'plot_bgcolor': 'rgba(0, 0, 0, 0)',
                                    'paper_bgcolor': 'rgba(0, 0, 0, 0)',})
coll100.write(fig24)

fig25 = px.pie (df_selection,  values="Durées (h)" , names="Équipe", color="Équipe", hole= .4,  color_discrete_sequence=px.colors.sequential.Aggrnyl)
fig25.update_traces(textposition='inside')
fig25.update_layout({
                                    'uniformtext_minsize':18,'uniformtext_mode':'hide',
                                    'height' : 410, 'font': {'size':15},
                                    'plot_bgcolor': 'rgba(0, 0, 0, 0)',
                                    'paper_bgcolor': 'rgba(0, 0, 0, 0)',})
coll200.write(fig25)

fig26 = px.pie (df_selection,  values="Durées (h)" , names="Arrêts", color="Arrêts", hole= .4,  color_discrete_sequence=px.colors.sequential.Blugrn_r)
fig26.update_traces(textposition='inside')
fig26.update_layout({
                                    'uniformtext_minsize':18,'uniformtext_mode':'hide',
                                    'height' : 410, 'font': {'size':15},
                                    'plot_bgcolor': 'rgba(0, 0, 0, 0)',
                                    'paper_bgcolor': 'rgba(0, 0, 0, 0)',})
coll300.write(fig26)

df1= pd.read_excel(
    io='CALCUL_TRS.xlsx',
    engine='openpyxl',
    sheet_name='Pareto',
    skiprows=4,
    usecols='B:D',
    nrows=15,
)
df1["PC"] = (df1["PC"] * 100).round(0).astype(int)

figpareto = px.bar(df1, x="Arrêts", y="Durées (m)", text="Durées (m)", 
             labels={"Durées (m)": "Durations (minutes)", "Arrêts": "Causes of Downtime"},
             color_discrete_sequence=px.colors.sequential.Blugrn_r)
figpareto.add_scatter(x=df1["Arrêts"], y=df1["PC"], mode="lines+markers+text", 
                name="Cumulative %", text=df1["PC"], textposition="top center",
                line=dict(color="red", width=2),
                yaxis="y2")

figpareto.update_layout(
    title="Pareto Diagram of Downtime Causes",
    yaxis=dict(title="Durations (minutes)", side="left"),
    yaxis2=dict(title="CP", overlaying="y", side="right", range=[0, 110]),
    xaxis=dict(title="Arrêts", tickangle=-45),
    legend=dict(title="Legend"), 
    template="plotly_white"
)

figpareto.add_hline(y=80, line_dash="dash", line_color="green", 
               annotation_text="80%",annotation_position="right",
              yref="y2")
st.write(figpareto)
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

