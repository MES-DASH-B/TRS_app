import streamlit as st
import pandas as pd 
import plotly.express as px
from streamlit_option_menu import option_menu
from PIL import Image
from millify import millify
import numpy as np
import plotly.graph_objects as go
import paho.mqtt.client as mqtt
import json
import time
import threading
from datetime import datetime
import pytz
import os


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
    selected = option_menu(menu_title=None,options=["SUIVI TRS","SUIVI ARRETS", "ANALYS.", "CAUSE ARRET", "MQTT"],icons=["speedometer","tools", "graph-up-arrow", "pc-display-horizontal", "layout-wtf"],
        menu_icon="cast",default_index=0,orientation="vertical",
        styles={
            "nav-link": { "--hover-color": "#93d6f5"},
            "nav-link-selected": {"background-color": "Black"},})
 #-----------------------------------------------------------------------------------------------------------------------------------------------------------------------   
#----------------------------------------------------------------------------------------------------------------------------------------------------------------------- 
if selected == "CAUSE ARRET":

        if "cause_d_arret" not in st.session_state:
            st.session_state["cause_d_arret"] = ""
        if "commentaire" not in st.session_state:
            st.session_state["commentaire"] = ""
        if "duree_arret" not in st.session_state:
            st.session_state["duree_arret"] = 0

        # ✅ Interface Streamlit (Ajout des commentaires en premier)
        st.title("📡 Monitoring MQTT - Novus DigiRail")

        # ✅ Ajouter une zone de saisie pour les commentaires et la durée d'arrêt
        st.subheader("📝 Enregistrement des Commentaires et Durée d'Arrêt")

        cause_options = ["Manque main d'oeuvre", "Panne", "MN1, MN2, TPM", "Rupture appro.", "Mise en route", "Problème Qulité", "Changement de série", "Changement de botte", "Réglage", "Réunion, Pause"]
        st.session_state["cause_d_arret"] = st.selectbox("🔹 Sélectionnez la cause d'arrêt", cause_options, index=0)
        st.session_state["commentaire"] = st.text_area("💬 Ajoutez un commentaire", st.session_state["commentaire"])
        st.session_state["duree_arret"] = st.number_input("⏳ Durée d'arrêt (en minutes)", min_value=0, value=st.session_state["duree_arret"])

        excel_file = "data.xlsx"

        # ✅ Fonction pour stocker les commentaires et réinitialiser les champs
        def save_commentaire():
            if st.session_state["cause_d_arret"] and st.session_state["commentaire"] and st.session_state["duree_arret"] >= 0:
                # Vérifier si le fichier Excel existe
                if not os.path.exists(excel_file):
                    df = pd.DataFrame(columns=["Date", "Cause d'arrêt", "Commentaire", "Durée d'arrêt"])
                    df.to_excel(excel_file, index=False)

                # Charger l'ancien fichier
                df = pd.read_excel(excel_file, sheet_name=None)
                df_comments = df.get("Commentaires", pd.DataFrame(columns=["Date", "Cause d'arrêt", "Commentaire", "Durée d'arrêt"]))
                
                # Ajouter les nouvelles données
                new_data = {
                    "Date": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    "Cause d'arrêt": st.session_state["cause_d_arret"],
                    "Commentaire": st.session_state["commentaire"],
                    "Durée d'arrêt": st.session_state["duree_arret"]
                }
                
                df_comments = pd.concat([df_comments, pd.DataFrame([new_data])], ignore_index=True)

                # Sauvegarde dans Excel
                with pd.ExcelWriter(excel_file, engine="openpyxl", mode="a", if_sheet_exists="replace") as writer:
                    df_comments.to_excel(writer, sheet_name="Commentaires", index=False)

                # ✅ Réinitialisation des champs après l'enregistrement
                st.session_state["cause_d_arret"] = "Cause 1"
                st.session_state["commentaire"] = ""
                st.session_state["duree_arret"] = 0

                return True
            return False

        # ✅ Afficher un bouton pour enregistrer les commentaires
        button_placeholder = st.empty()

        if button_placeholder.button("✅ Enregistrer le Commentaire", use_container_width=True):
            button_placeholder.empty()
            st.markdown('<style>div.stButton>button{background-color: green;color: white;}</style>', unsafe_allow_html=True)
            
            success = save_commentaire()

            if success:
                st.success("✅ Commentaire et durée d'arrêt enregistrés avec succès!")
            else:
                st.error("❌ Erreur lors de l'enregistrement.")



if selected == "MQTT":


        # ✅ Configuration MQTT
        mqtt_broker = "192.168.0.230"
        mqtt_topic = "NOVUS/device1/events"

        # ✅ Variables globales
        messages = []
        last_update = None  

        # ✅ Callback pour gérer les messages MQTT reçus
        def on_message(client, userdata, msg):
            global last_update

            message = json.loads(msg.payload.decode())
            messages.append(message)  
            print(f"Message reçu: {message}")

            timestamp = message.get("channels", {}).get("timestamp", None)
            if timestamp:
                utc_time = datetime.utcfromtimestamp(timestamp)
                local_time = utc_time.replace(tzinfo=pytz.utc).astimezone(pytz.timezone("Europe/Paris"))
                last_update = local_time.strftime('%Y-%m-%d %H:%M:%S')
                print(f"Timestamp mis à jour: {last_update}")

        # ✅ Fonction pour démarrer MQTT
        def start_mqtt():
            client = mqtt.Client()
            client.on_message = on_message
            client.connect(mqtt_broker, 1883, 60)
            client.subscribe(mqtt_topic)
            client.loop_forever()

        # ✅ Lancer MQTT dans un thread séparé
        mqtt_thread = threading.Thread(target=start_mqtt, daemon=True)
        mqtt_thread.start()

        # ✅ Affichage des valeurs reçues
        st.write(f"Broker MQTT: {mqtt_broker} | Topic: {mqtt_topic}")
        st.write("🔴 Données reçues en temps réel")

        chd1_value_display = st.empty()
        chd2_value_display = st.empty()
        chd3_value_display = st.empty()
        last_update_display = st.empty()
        no_message_received_display = st.empty()

        # ✅ Boucle pour afficher et stocker les messages MQTT
        while True:
            if messages:
                latest_message = messages[-1]
                chd1_value = latest_message.get("channels", {}).get("chd1_value", 0)
                chd2_value = latest_message.get("channels", {}).get("chd2_value", 0)
                chd3_value = latest_message.get("channels", {}).get("chd3_value", 0)

                chd1_value_display.markdown(f"**Chd1 (Quantité totale):** {chd1_value}")
                chd2_value_display.markdown(f"**Chd2 (Rebuts):** {chd2_value}")
                chd3_value_display.markdown(f"**Chd3 (État machine):** {chd3_value}")

                if last_update:
                    last_update_display.markdown(f"**Dernière mise à jour:** {last_update}")
                    no_message_received_display.empty()
                else:
                    last_update_display.markdown("**Dernière mise à jour:** N/A")

            else:
                no_message_received_display.markdown("**Aucun message reçu**.")

            time.sleep(10)

       
        #---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
        #---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------



if selected == "SUIVI TRS":
    
    df4= pd.read_excel(io='CALCUL_TRS.xlsx',engine='openpyxl',sheet_name='DétailTRS',skiprows=4,usecols='B:AF',nrows=500,)
   
    dfwf= pd.read_excel(io='CALCUL_TRS.xlsx',engine='openpyxl',sheet_name='waterfall',skiprows=4,usecols='B:AA',nrows=500,)
    
    df2= pd.read_excel(io='CALCUL_TRS.xlsx',engine='openpyxl',sheet_name='Semaine',skiprows=4,usecols='B:I',nrows=500,)

    # Interface utilisateur avec Streamlit
    #st.title("Analyse des pertes TRS en Waterfall")

    # Filtres dans la barre latérale
    #periodes = st.sidebar.multiselect("Sélectionner une ou plusieurs périodes", dfwf["Période"].unique(), default=dfwf["Période"].unique())
    #semaines = st.sidebar.multiselect("Sélectionner une ou plusieurs semaines", dfwf["Semaine"].unique(), default=dfwf["Semaine"].unique())
    #dates = st.sidebar.multiselect("Sélectionner une ou plusieurs dates", list(dfwf["Date"].unique()), default=list(dfwf["Date"].unique()))
    
    semaine_S = np.union1d(dfwf["Semaine"].unique(), df4["Semaine"].unique())
    #semaine_S= dfwf["Semaine"].unique()
    selected_semaine = st.sidebar.selectbox("Select a Week:", semaine_S)
    dfwf_filtered = dfwf[dfwf["Semaine"] == selected_semaine]
    filtered_data = df4[df4["Semaine"] == selected_semaine]
    df_grouped = dfwf_filtered.groupby("Cause des pertes", as_index=False)["Pourcentage perte"].sum()
    df_grouped["Pourcentage perte"] = df_grouped["Pourcentage perte"].astype(float) / 4


    pie_data = pd.DataFrame({"Category": ["TRS1", "Pertes"],"Value": [filtered_data["TRS1"].values[0], filtered_data["cible"].values[0] - filtered_data["TRS1"].values[0]]})
    fig24 = px.pie(pie_data, names="Category", values="Value", hole=0.4,  color_discrete_map={"TRS1": "green", "Pertes": "lightgray"})
    fig24.update_traces(textposition='inside')
    fig24.update_layout(title="MS20", uniformtext_minsize=18, uniformtext_mode='hide', height=410,font={'size': 15}, plot_bgcolor='rgba(0, 0, 0, 0)', paper_bgcolor='rgba(0, 0, 0, 0)')
    
    pie_data2 = pd.DataFrame({"Category2": ["TRS2", "Pertes"],"Value2": [filtered_data["TRS2"].values[0], filtered_data["cible"].values[0] - filtered_data["TRS2"].values[0]]})
    fig25 = px.pie(pie_data2, names="Category2", values="Value2", hole=0.4,  color_discrete_map={"TRS2": "green", "Pertes": "lightgray"})
    fig25.update_traces(textposition='inside')
    fig25.update_layout(title="SHINKO 1",uniformtext_minsize=18, uniformtext_mode='hide', height=410,font={'size': 15}, plot_bgcolor='rgba(0, 0, 0, 0)', paper_bgcolor='rgba(0, 0, 0, 0)')
    
    pie_data3 = pd.DataFrame({"Category3": ["TRS3", "Pertes"],"Value3": [filtered_data["TRS3"].values[0], filtered_data["cible"].values[0] - filtered_data["TRS3"].values[0]]})
    fig26 = px.pie(pie_data3, names="Category3", values="Value3", hole=0.4,  color_discrete_map={"TRS3": "green", "Pertes": "lightgray"})
    fig26.update_traces(textposition='inside')
    fig26.update_layout(title="SHINKO 2",uniformtext_minsize=18, uniformtext_mode='hide', height=410,font={'size': 15}, plot_bgcolor='rgba(0, 0, 0, 0)', paper_bgcolor='rgba(0, 0, 0, 0)')
    
    pie_data4 = pd.DataFrame({"Category4": ["TRS4", "Pertes"],"Value4": [filtered_data["TRS4"].values[0], filtered_data["cible"].values[0] - filtered_data["TRS4"].values[0]]})
    fig27 = px.pie(pie_data4, names="Category4", values="Value4", hole=0.4,  color_discrete_map={"TRS4": "green", "Pertes": "lightgray"})
    fig27.update_traces(textposition='inside')
    fig27.update_layout(title="SHINKO3",uniformtext_minsize=18, uniformtext_mode='hide', height=410,font={'size': 15}, plot_bgcolor='rgba(0, 0, 0, 0)', paper_bgcolor='rgba(0, 0, 0, 0)')
    
    

    # Display the pie chart in Streamlit
    coll100, coll200, coll300, coll400 = st.columns([3, 3, 3, 3])
    coll100.write(fig24)
    coll200.write(fig25)
    coll300.write(fig26)
    coll400.write(fig27)
    
    #coll100, coll200,coll300 = st.columns([3,3,4])
    #fig24 = px.pie (filtered_data ,  values="TRS1" ,color="cible", hole= .4,  color_discrete_sequence=px.colors.diverging.RdYlGn)
    #fig24.update_traces(textposition='inside')
    #fig24.update_layout({'uniformtext_minsize':18,'uniformtext_mode':'hide','height' : 410, 'font': {'size':15},'plot_bgcolor': 'rgba(0, 0, 0, 0)','paper_bgcolor': 'rgba(0, 0, 0, 0)',})
    #coll100.write(fig24)
    
    # Filtrage des données
    #df_filtered = dfwf[(df["Période"].isin(periodes)) & (dfwf["Semaine"].isin(semaines)) & (dfwf["Date"].isin(dates))]

    # Calcul des moyennes par cause d'arrêt si plusieurs jours sont sélectionnés
    #df_grouped = df_filtered.groupby("Cause des pertes", as_index=False)["Pourcentage perte"].mean()

    # Ajouter le TRS initial à 100%
    base_trs = 100
    values = [base_trs] + [-p for p in df_grouped["Pourcentage perte"]]
    labels = ["TRS 100%"] + list(df_grouped["Cause des pertes"])
    measurements = ["absolute"] + ["relative"] * len(df_grouped)

    # Créer le graphique Waterfall
    fig = go.Figure(go.Waterfall(
        name="Pertes TRS",
        orientation="v",
        measure=measurements,
        x=labels,
        y=values,
        text=[f"{v:.1f}%" for v in values],
        textposition="outside",
        connector=dict(line=dict(width=2))  # Make connectors thicker
            
    ))
    # Increase text & bar width
    fig.update_traces(textfont=dict(size=16, family="Arial Black", color="dimgray"), width=0.8) # Larger text & bars

    fig.update_layout(
        title="Pertes TRS MS20 par cause d'arrêt",
        xaxis_title="Causes d'arrêt",
        yaxis_title="Pourcentage de perte (%)",
        height=550,
        showlegend=False
    )
    #------------------------------------------------------------------------------------ Start waterfall Shinko 1
    df_grouped1 = dfwf_filtered.groupby("Cause des pertes1", as_index=False)["Pourcentage perte1"].mean()
    base_trs1 = 100
    values1 = [base_trs1] + [-p for p in df_grouped1["Pourcentage perte1"]]
    labels1 = ["TRS1 100%"] + list(df_grouped1["Cause des pertes1"])
    measurements1 = ["absolute"] + ["relative"] * len(df_grouped1)
    
    fig1 = go.Figure(go.Waterfall(
        name="Pertes TRS1",
        orientation="v",
        measure=measurements1,
        x=labels1,
        y=values1,
        text=[f"{v:.1f}%" for v in values1],
        textposition="outside"
    ))
    fig1.update_traces(textfont=dict(size=16, family="Arial Black", color="dimgray"), width=0.8) # Larger text & bars
    fig1.update_layout(
        title="Pertes TRS SHINKO 1 par cause d'arrêt",
        xaxis_title="Causes d'arrêt",
        yaxis_title="Pourcentage de perte (%)",
        height=550,
        showlegend=False
    )
    #____________________________________________________________________________________ End waterfall shinko 1
    
    #------------------------------------------------------------------------------------ Start waterfall Shinko 2
    df_grouped2 = dfwf_filtered.groupby("Cause des pertes2", as_index=False)["Pourcentage perte2"].mean()
    base_trs2 = 100
    values2 = [base_trs2] + [-p for p in df_grouped2["Pourcentage perte2"]]
    labels2 = ["TRS2 100%"] + list(df_grouped2["Cause des pertes2"])
    measurements2 = ["absolute"] + ["relative"] * len(df_grouped2)
    
    fig2 = go.Figure(go.Waterfall(
        name="Pertes TRS2",
        orientation="v",
        measure=measurements2,
        x=labels2,
        y=values2,
        text=[f"{v:.1f}%" for v in values2],
        textposition="outside"
    ))
    fig2.update_traces(textfont=dict(size=16, family="Arial Black", color="dimgray"), width=0.8) # Larger text & bars
    fig2.update_layout(
        title="Pertes TRS SHINKO 2 par cause d'arrêt",
        xaxis_title="Causes d'arrêt",
        yaxis_title="Pourcentage de perte (%)",
        height=550,
        showlegend=False
    )
    #____________________________________________________________________________________ End waterfall shinko 2
    
    #------------------------------------------------------------------------------------ Start waterfall Shinko 3
    df_grouped3 = dfwf_filtered.groupby("Cause des pertes3", as_index=False)["Pourcentage perte3"].mean()
    base_trs3 = 100
    values3 = [base_trs3] + [-p for p in df_grouped3["Pourcentage perte3"]]
    labels3 = ["TRS3 100%"] + list(df_grouped3["Cause des pertes3"])
    measurements3 = ["absolute"] + ["relative"] * len(df_grouped3)
    
    fig3 = go.Figure(go.Waterfall(
        name="Pertes TRS3",
        orientation="v",
        measure=measurements3,
        x=labels3,
        y=values3,
        text=[f"{v:.1f}%" for v in values3],
        textposition="outside"
    ))
    fig3.update_traces(textfont=dict(size=16, family="Arial Black", color="dimgray"), width=0.8) # Larger text & bars
    fig3.update_layout(
        title="Pertes TRS SHINKO 3 par cause d'arrêt",
        xaxis_title="Causes d'arrêt",
        yaxis_title="Pourcentage de perte (%)",
        height=550,
        showlegend=False
    )
    #____________________________________________________________________________________ End waterfall shinko 3
    # Afficher le graphique
    col11, col21, col22, col23= st.columns(4)
    col11.plotly_chart(fig)
    col21.plotly_chart(fig1)
    col22.plotly_chart(fig2)
    col23.plotly_chart(fig3)

    figS = px.line(df2, x="Semaine",y="TRS",color="Machine ", color_discrete_sequence=px.colors.sequential.Blues_r, text="TRS", height=700 )
    figS.update_traces(line=dict(width=6), textposition="top center", textfont=dict(size=16))
    st.write(figS)
            
if selected == "SUIVI ARRETS":
    
    df= pd.read_excel(io='CALCUL_TRS.xlsx',engine='openpyxl',sheet_name='Arrêts',skiprows=4,usecols='B:H',nrows=500,)

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

    with col1:st.markdown(f"""<div class="metric-container"><p class="metric-label">Nombre total des arrets</p><p class="metric-value">{Nombr_arrets}</p></div>""",unsafe_allow_html=True)

    with col2:st.markdown(f"""<div class="metric-container"><p class="metric-label">Durées total des arrets</p><p class="metric-value">{Durées_arrets} h</p></div>""",unsafe_allow_html=True)

    with col3:st.markdown(f"""<div class="metric-container"><p class="metric-label">Dureée des arrets en jours</p><p class="metric-value">{Durée_arret_jr} Jours</p></div>""",unsafe_allow_html=True)

    with col4:st.markdown(f"""<div class="metric-container"><p class="metric-label">Durée moyenne d'un arret</p><p class="metric-value">{moyenne} h</p></div>""",unsafe_allow_html=True)


    coll101,coll100, coll200,coll300 = st.columns([3,3,3,4])

    # Compter les arrêts par machine
    arrets_par_machine = df_selection["Machine"].value_counts().reset_index()
    arrets_par_machine.columns = ["Machine", "Nombre d'arrêts"]

    # Nombre total d'arrêts
    total_arrets = df_selection.shape[0]

    # Interface Streamlit
    #st.title("Analyse des Arrêts Machines")
    #st.write(f"Nombre total d'arrêts : **{total_arrets}**")

    # Création du pie chart (donut)
    fig = px.pie(
        arrets_par_machine,
        names="Machine",
        values="Nombre d'arrêts",
        color_discrete_sequence=px.colors.diverging.RdBu_r,
        hole=0.4  # Effet donut
    )

    # Masquer le nom des machines et afficher uniquement le nombre d'arrêts
    fig.update_traces(texttemplate="%{value}", textfont_size=20)

    # Ajouter le total des arrêts au centre avec le nombre au-dessus du mot "arrêts"
    fig.update_layout(
        title=dict(text="Répartition des arrêts par machine", font=dict(size=16),x=0.0, xanchor="left"),
        annotations=[
            dict(
                text=f"<b>{total_arrets}</b><br>arrêts",  # Met le nombre en gras et "arrêts" en-dessous
                x=0.5, y=0.5,  # Position centrale
                font=dict(size=22),  # Taille et couleur du texte
                showarrow=False
            )
        ], uniformtext_minsize=18,uniformtext_mode="hide",height=410,font=dict(size=15),plot_bgcolor="rgba(0, 0, 0, 0)",paper_bgcolor="rgba(0, 0, 0, 0)"
    )

    #st.plotly_chart(fig)
    coll101.write(fig)


    fig24 = px.pie (df_selection,  values="Durées (h)" , names="Machine", color="Machine", hole= .4,  color_discrete_sequence=px.colors.diverging.RdBu_r)
    fig24.update_traces(textposition='inside')
    fig24.update_layout(
        title=dict(text="Taux arrêts par machine", font=dict(size=16),x=0.0, xanchor="left"),
        uniformtext_minsize=18,uniformtext_mode="hide",height=410,font=dict(size=15),plot_bgcolor="rgba(0, 0, 0, 0)",paper_bgcolor="rgba(0, 0, 0, 0)")
    coll100.write(fig24)

    fig25 = px.pie (df_selection,  values="Durées (h)" , names="Équipe", color="Équipe", hole= .4,  color_discrete_sequence=px.colors.sequential.RdBu_r)
    fig25.update_traces(textposition='inside')
    fig25.update_layout(
        title=dict(text="Taux arrêts par équipe", font=dict(size=16),x=0.0, xanchor="left"),
        uniformtext_minsize=18,uniformtext_mode="hide",height=410,font=dict(size=15),plot_bgcolor="rgba(0, 0, 0, 0)",paper_bgcolor="rgba(0, 0, 0, 0)")
    coll200.write(fig25)

    fig26 = px.pie (df_selection,  values="Durées (h)" , names="Arrêts", color="Arrêts", hole= .4,  color_discrete_sequence=px.colors.sequential.RdBu_r)
    fig26.update_traces(textposition='inside')
    fig26.update_layout(
        title=dict(text="Taux arrêts par cause", font=dict(size=16),x=0.0, xanchor="left"),
        uniformtext_minsize=18,uniformtext_mode="hide",height=410,font=dict(size=15),plot_bgcolor="rgba(0, 0, 0, 0)",paper_bgcolor="rgba(0, 0, 0, 0)")
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

    fig33 = px.bar(df_selection, x="Date", y="Arrêts", color="Machine", color_discrete_sequence=px.colors.sequential.Blues_r, hover_name="Durées (m)")
    fig33.update_layout(
        bargap=0.2,  # Reduce gap to make bars thicker
        bargroupgap=0.05  # Space between grouped bars
    )
    a1.write(fig33)

    fig34 = px.bar(df_selection, x="Date", y="Durées (m)", color="Arrêts", template = 'plotly', hover_name="Machine")
    b1.write(fig34)


#-----------------------------------------------------------------------------
if selected == "ANALYS.":
    df2= pd.read_excel(io='CALCUL_TRS.xlsx',engine='openpyxl',sheet_name='Semaine',skiprows=4,usecols='B:I',nrows=500,)
        
    df3= pd.read_excel(io='CALCUL_TRS.xlsx',engine='openpyxl',sheet_name='TRS Machine',skiprows=4,usecols='B:H',nrows=500,)
    
    df4= pd.read_excel(io='CALCUL_TRS.xlsx',engine='openpyxl',sheet_name='DétailTRS',skiprows=4,usecols='B:AE',nrows=500,)
    
    
    #st.dataframe(df2)
    
    #Semaine = st.sidebar.multiselect(
    #    "Choisir la semaine:",
    #    options = df4["Semaine"].unique(),
    #    default = df4["Semaine"].unique())
    
    #df4_selection = df4.query("Semaine == @Semaine")
    
        # Get unique values from "Semaine" column
    semaines = df4["Semaine"].unique()

    # Sidebar filter
    selected_semaine = st.sidebar.selectbox("Select a Week:", semaines)

    # Filter the DataFrame based on the selected week
    df_filtered = df4[df4["Semaine"] == selected_semaine]

    # Display the filtered data
    #st.write(df_filtered)


    Objectifs1= int(df_filtered["Objectif1"].sum())
    Qté1= int(df_filtered["Qté produite1"].sum())
    Écart1= int(df_filtered["Écart1"].sum())
    trs1= int((df_filtered["TRS1"].sum())*100)

    st.subheader("MS20")
    col11, col21, col31, col41 = st.columns(4)

    with col11:
        st.markdown(f"""<div class="metric-container"><p class="metric-label">Objectif de production</p><p class="metric-value">{Objectifs1}</p></div>""",unsafe_allow_html=True)
    with col21:
        st.markdown(f"""<div class="metric-container"><p class="metric-label">Quantité produite</p><p class="metric-value">{Qté1}</p></div>""",unsafe_allow_html=True)
    with col31:
        st.markdown(f"""<div class="metric-container"><p class="metric-label">Écart production</p><p class="metric-value">{Écart1}</p></div>""",unsafe_allow_html=True)
    with col41:
        st.markdown(f"""<div class="metric-container"><p class="metric-label">TRS machine</p><p class="metric-value">{trs1} %</p></div>""",unsafe_allow_html=True)


    Objectifs2= int(df_filtered["Objectif2"].sum())
    Qté2= int(df_filtered["Qté produite2"].sum())
    Écart2= int(df_filtered["Écart2"].sum())
    trs2= int((df_filtered["TRS2"].sum())*100)

    st.subheader("SHINKO 1 (V831)")
    col110, col210, col310, col410 = st.columns(4)

    with col110:
        st.markdown(f"""<div class="metric-container"><p class="metric-label">Objectif de production</p><p class="metric-value">{Objectifs2}</p></div>""",unsafe_allow_html=True)
    with col210:
        st.markdown(f"""<div class="metric-container"><p class="metric-label">Quantité produite</p><p class="metric-value">{Qté2}</p></div>""",unsafe_allow_html=True)
    with col310:
        st.markdown(f"""<div class="metric-container"><p class="metric-label">Écart production</p><p class="metric-value">{Écart2}</p></div>""",unsafe_allow_html=True)
    with col410:
        st.markdown(f"""<div class="metric-container"><p class="metric-label">TRS machine</p><p class="metric-value">{trs2} %</p></div>""",unsafe_allow_html=True)
        

    Objectifs3= int(df_filtered["Objectif3"].sum())
    Qté3= int(df_filtered["Qté produite3"].sum())
    Écart3= int(df_filtered["Écart3"].sum())
    trs3= int((df_filtered["TRS3"].sum())*100)
    
    st.subheader("SHINKO 2 (V832)")
    col111, col211, col311, col411 = st.columns(4)
    
    with col111:
        st.markdown(f"""<div class="metric-container"><p class="metric-label">Objectif de production</p><p class="metric-value">{Objectifs3}</p></div>""",unsafe_allow_html=True)
    with col211:
        st.markdown(f"""<div class="metric-container"><p class="metric-label">Quantité produite</p><p class="metric-value">{Qté3}</p></div>""",unsafe_allow_html=True)
    with col311:
        st.markdown(f"""<div class="metric-container"><p class="metric-label">Écart production</p><p class="metric-value">{Écart3}</p></div>""",unsafe_allow_html=True)
    with col411:
        st.markdown(f"""<div class="metric-container"><p class="metric-label"TRS machine</p><p class="metric-value">{trs3} %</p></div>""",unsafe_allow_html=True)


    Objectifs4= int(df_filtered["Objectif4"].sum())
    Qté4= int(df_filtered["Qté produite4"].sum())
    Écart4= int(df_filtered["Écart4"].sum())
    trs4= int((df_filtered["TRS4"].sum())*100)
    
    st.subheader("SHINKO 3 (V833)")
    col112, col212, col312, col412 = st.columns(4)
    
    with col112:
        st.markdown(f"""<div class="metric-container"><p class="metric-label">Objectif de production</p><p class="metric-value">{Objectifs4}</p></div>""",unsafe_allow_html=True)
    with col212:
        st.markdown(f"""<div class="metric-container"><p class="metric-label">Quantité produite</p><p class="metric-value">{Qté4}</p></div>""",unsafe_allow_html=True)
    with col312:
        st.markdown(f"""<div class="metric-container"><p class="metric-label">Écart production</p><p class="metric-value">{Écart4}</p></div>""",unsafe_allow_html=True)
    with col412:
        st.markdown(f"""<div class="metric-container"><p class="metric-label">TRS machine</p><p class="metric-value">{trs4} %</p></div>""",unsafe_allow_html=True)

    df3["TRS 1"] = (df3["TRS 1"] * 100).round(0).astype(int)
    figTRS = px.line(df3, x="Date",y=df3["TRS 1"],color="Machine",color_discrete_sequence=px.colors.sequential.Blues_r, text="TRS 1")
    figTRS.update_traces(line=dict(width=5), textposition="top left", textfont=dict(size=16))
    st.write(figTRS)

    figqté = px.bar(df3, x="Date",y=df3["Quantité E1+E2"],color="Machine", color_discrete_sequence=px.colors.sequential.Blues_r )
    st.write(figqté)


    
    df5= pd.read_excel(
        io='CALCUL_TRS.xlsx',
        engine='openpyxl',
        sheet_name='Arrêts',
        skiprows=4,
        usecols='B:H',
        nrows=500,
        )
    
    
    colsun1, colsun2 = st.columns(2)
    figsun = px.sunburst(df5,path=['Machine', 'pds','Date', 'Arrêts'], values='Durées (m)', height=800, color_discrete_sequence=px.colors.sequential.Bluyl_r)
    colsun1.write(figsun)

    figref = px.sunburst(df2,path=['Machine ', 'Ref','Semaine','Qté produite'], values='TRS', height=800, color_discrete_sequence=px.colors.sequential.Blues_r)
    colsun2.write(figref)
    
    
    
    fighist = px.histogram(df2, x="Qté produite",y="Machine ",color="Ref", color_discrete_sequence=px.colors.sequential.GnBu_r )
    st.write(fighist)
    
    figtrs1=go.Figure()
    
    figtrs1.add_trace(go.Scatter(x=df4["Semaine"], y=df4["TRS1"], mode='lines', name='Line chart', line=dict(color='blue',width=2)))
    
    figtrs1.add_trace(go.Bar(x=df4["Semaine"], y=df4["Qté produite1"], name='Histogramt', marker=dict(color='gray'), yaxis='y2'))
    
    figtrs1.update_layout(title="line chart with scaled histogram", xaxis_title="Semainer", yaxis=dict(title="Line chart values", side="left"), yaxis2=dict(title="histogram values(large scale)", overlaying="y", side="right",showgrid=False),barmode='overlay')
    #figtrs1.show()
    st.write(figtrs1) 

