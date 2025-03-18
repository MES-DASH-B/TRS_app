import streamlit as st
import pandas as pd 
import plotly.express as px
from streamlit_option_menu import option_menu
from PIL import Image
from millify import millify
import numpy as np
import plotly.graph_objects as go



st.set_page_config (page_title= "POINT TRS", page_icon="📈", layout="wide")
image = Image.open('image.jpg') 
st.image(image, width = 250)

#st.header ("Analyse TRS SHINKO & MS20")
st.subheader  ("Analyse Taux de Rendement Synthétique")
#st.subheader ("Accueil")

@st.cache_data(ttl=0)
def load_css(file_name):
    with open(file_name, "r") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
# Load the CSS file
load_css("style.css")



with st.sidebar:
    selected = option_menu(menu_title=None,options=["ACCUEIL", "ANALYS MAINT.", "TPM", "ARRETS"],icons=["pc-display-horizontal", "graph-up-arrow", "tools", "layout-wtf"],
        menu_icon="cast",default_index=0,orientation="vertical",
        styles={
            "nav-link": { "--hover-color": "#93d6f5"},
            "nav-link-selected": {"background-color": "Black"},})
        
if selected == "ACCUEIL":
    
    df= pd.read_excel(
        io='CALCUL_TRS.xlsx',
        engine='openpyxl',
        sheet_name='Arrêts',
        skiprows=4,
        usecols='B:H',
        nrows=100,
        )

    #st.dataframe(df)

    st.sidebar.header("Filitre référance:")
    Équipe = st.sidebar.multiselect(
        "Choisir l'équipe:",
        options = df["Équipe"].unique(),
        default = df["Équipe"].unique())
    
    df_selection = df.query("Équipe == @Équipe")
    #with st.expander("Data preview"):
    #    st.dataframe(df_selection)

    #st.title(":bar_chart: Suivis TRS")
    st.markdown("##")


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
                labels={"Durées (m)": "Durée arrêts  (minutes)", "Arrêts": "Causes of Downtime"},
                color_discrete_sequence=px.colors.sequential.Blugrn_r)
    figpareto.add_scatter(x=df1["Arrêts"], y=df1["PC"], mode="lines+markers+text", 
                    name="Cumulative %", text=df1["PC"], textposition="top center",
                    line=dict(color="red", width=2),
                    yaxis="y2")

    figpareto.update_layout(
        title="Pareto Diagram of Downtime Causes",
        yaxis=dict(title="Durations (minutes)", side="left"),
        yaxis2=dict(title="CP", overlaying="y", side="right", range=[0, 110]),
        xaxis=dict(title="Arrêts"),
        legend=dict(title="Legend"), 
        template="plotly_white"
    )

    figpareto.add_hline(y=80, line_dash="dash", line_color="green", 
                annotation_text="80%",annotation_position="right",
                yref="y2")
    st.write(figpareto)
    st.markdown("----") 

#with st.sidebar:
    #selected = option_menu(menu_title=None,options=["Secteur Traction/Torsion", "Secteur Compression", "Secteur Form","Secteur E-Mobility"],icons=["asterisk", "asterisk","asterisk","asterisk"],menu_icon="cast",default_index=0,orientation="vertical",
        #styles={"container": {"background-color": "#ffffff"},"icon": {"color": "Black", "font-size": "20px"}, "nav-link": {"font-size": "15px", "text-align": "left", "margin":"0px", "--hover-color": "#93d6f5"},"nav-link-selected": {"background-color": "red"},})
#if selected == "Secteur Traction/Torsion" :

        

    fig101 = px.histogram(df_selection, x="Durées (h)",y="Machine",color="Arrêts", template = 'plotly' )
    st.write(fig101)

    a1, b1 = st.columns(2)

    fig33 = px.bar(df_selection, x="Date", y="Arrêts", color="Machine", template = 'plotly', hover_name="Durées (m)")
    fig33.update_layout(
        bargap=0.2,  # Reduce gap to make bars thicker
        bargroupgap=0.05  # Space between grouped bars
    )
    a1.write(fig33)

    fig34 = px.bar(df_selection, x="Date", y="Durées (m)", color="Arrêts", template = 'plotly', hover_name="Machine")
    b1.write(fig34)


#-----------------------------------------------------------------------------
if selected == "ANALYS MAINT.":
    df2= pd.read_excel(
        io='CALCUL_TRS.xlsx',
        engine='openpyxl',
        sheet_name='Semaine',
        skiprows=4,
        usecols='B:I',
        nrows=100,
        )
        
    df3= pd.read_excel(
        io='CALCUL_TRS.xlsx',
        engine='openpyxl',
        sheet_name='TRS Machine',
        skiprows=4,
        usecols='B:H',
        nrows=150,
        )
    #st.dataframe(df2)
    
    Semaine = st.sidebar.multiselect(
        "Choisir la semaine:",
        options = df2["Semaine"].unique(),
        default = df2["Semaine"].unique())
    
    df2_selection = df2.query("Semaine == @Semaine")
    
        # Get unique values from "Semaine" column
    semaines = df2["Semaine"].unique()

    # Sidebar filter
    selected_semaine = st.sidebar.selectbox("Select a Week:", semaines)

    # Filter the DataFrame based on the selected week
    df_filtered = df2[df2["Semaine"] == selected_semaine]

    # Display the filtered data
    #st.write(df_filtered)

    df3["TRS 1"] = (df3["TRS 1"] * 100).round(0).astype(int)
    figTRS = px.line(df3, x="Date",y=df3["TRS 1"],color="Machine",template = 'plotly' )
    st.write(figTRS)
    
    figqté = px.area(df3, x="Date",y=df3["Quantité E1+E2"],color="Machine", template = 'plotly' )
    st.write(figqté)
    
    figtrs1=go.Figure()
    
    figtrs1.add_trace(go.Scatter(x=df3["Date"], y=df3["TRS 1"], mode='lines+markers', name='Line chart', line=dict(color='blue',width=2)))
    
    figtrs1.add_trace(go.Bar(x=df3["Date"], y=df3["Quantité E1+E2"], name='Histogramt', marker=dict(color='orange'), yaxis='y2'))
    
    figtrs1.update_layout(title="line chart with scaled histogram", xaxis_title="Date", yaxis=dict(title="Line chart values", side="left"), yaxis2=dict(title="histogram values(large scale)", overlaying="y", side="right",showgrid=False),barmode='overlay')
    #figtrs1.show()
    st.write(figtrs1)
    
    figS = px.line(df2, x="Semaine",y="TRS",color="Machine ", template = 'plotly' )
    st.write(figS)
    
    
        