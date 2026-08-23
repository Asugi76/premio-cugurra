import streamlit as st
import pandas as pd
from datetime import datetime, time, date
from supabase import create_client, Client
import json

# ==============================================================================
# --- CONFIGURAZIONE PAGINA & STILI CSS AVANZATI ---
# ==============================================================================
st.set_page_config(
    page_title="Premio Cugurra",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CONNESSIONE SUPABASE GLOBALE ---
SUPABASE_URL = st.secrets["supabase"]["url"]
SUPABASE_KEY = st.secrets["supabase"]["key"]
db: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- INIZIALIZZAZIONE SESSION STATE COMPLETA ---
if "utente_corrente" not in st.session_state:
    if "sessione_utente" in st.session_state:
        st.session_state["utente_corrente"] = st.session_state["sessione_utente"]
    else:
        st.session_state["utente_corrente"] = None

if "gol_singoli" not in st.session_state:
    st.session_state.gol_singoli = {}

if "gol_omologazione" not in st.session_state:
    st.session_state.gol_omologazione = {}

if "filtro_competizione" not in st.session_state:
    st.session_state.filtro_competizione = "Tutte"

# --- FUNZIONE LOGO COMPETIZIONE CON MAPPING ESTESO ---
def get_competizione_logo_filename(nome_competizione):
    mapping = {
        "Serie A": "comp_seriea.png",
        "Serie B": "comp_serieb.png",
        "Coppa Italia": "comp_coppaitalia.png",
        "Supercoppa Italiana": "comp_supercoppaitaliana.png",
        "Champions League": "comp_championsleague.png",
        "Europa League": "comp_europaleague.png",
        "Conference League": "comp_conferenceleague.png",
        "Mondiale per Club": "comp_mondialeclub.png",
        "Amichevole": "comp_amichevole.png",
        "Torneo Amichevole": "comp_torneoamichevole.png"
    }
    return mapping.get(nome_competizione, "comp_seriea.png")

# --- CARICAMENTO CONFIGURAZIONE GLOBALE DELLA STAGIONE ---
try:
    res_conf = db.table("configurazione").select("*").eq("chiave", "fase_corrente").execute()
    fase_attuale = res_conf.data[0]["valore"] if res_conf.data else "TEST"
except Exception:
    fase_attuale = "TEST"

# --- STILI CSS CUSTOM PER INTERFACCIA DARK TEMA ---
st.markdown("""
    <style>
    .stApp {
        background-color: #0d1117;
        color: #e6edf3;
    }
    .btn-primary-custom button {
        background-color: #1f6feb !important;
        color: white !important;
        border-radius: 8px;
        width: 100%;
        font-weight: bold;
        border: none;
        padding: 0.5rem 1rem;
    }
    .btn-primary-custom button:hover {
        background-color: #388bfd !important;
    }
    .card-custom {
        background-color: #161b22;
        border: 1px solid #30363d;
        padding: 1.25rem;
        border-radius: 10px;
        margin-bottom: 1rem;
    }
    </style>
""", unsafe_allow_html=True)

# --- VERIFICA RUOLO AMMINISTRATORE ---
is_admin = False
if st.session_state["utente_corrente"]:
    try:
        res_usr = db.table("utenti").select("is_admin").eq("nome_fb", st.session_state["utente_corrente"]).execute()
        if res_usr.data:
            is_admin = res_usr.data[0].get("is_admin", False)
    except Exception:
        pass

# ==============================================================================
# --- FUNZIONI DI UTILITÀ GLOBALE ---
# ==============================================================================
def mostra_footer():
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: #8b949e; font-size: 0.85rem;'>"
        "Premio Cugurra • Piattaforma Ufficiale Pronostici Cagliari Calcio"
        "</div>", 
        unsafe_allow_html=True
    )

# ==============================================================================
# --- GESTIONE ACCESSO / LOGIN UTENTE ---
# ==============================================================================
if not st.session_state["utente_corrente"]:
    st.title("⚽ Benvenuto al Premio Cugurra")
    st.write("Inserisci il tuo nome Facebook registrato per accedere alla piattaforma e inserire i tuoi pronostici.")
    
    with st.form("form_login"):
        nome_inserito = st.text_input("Il tuo nome Facebook")
        submit_login = st.form_submit_button("Entra")
        if submit_login:
            if nome_inserito.strip():
                try:
                    res_U = db.table("utenti").select("*").eq("nome_fb", nome_inserito.strip()).execute()
                    if res_U.data:
                        st.session_state["utente_corrente"] = nome_inserito.strip()
                        st.success("Accesso effettuato con successo!")
                        st.rerun()
                    else:
                        st.error("Utente non trovato nel database. Contatta l'amministratore.")
                except Exception as e:
                    st.error(f"Errore durante il login: {e}")
            else:
                st.warning("Inserisci un nome valido.")
    st.stop()

# ==============================================================================
# --- BARRA LATERALE E MENU DI NAVIGAZIONE ---
# ==============================================================================
with st.sidebar:
    st.write(f"Utente: **{st.session_state['utente_corrente']}**")
    if is_admin:
        st.markdown("🔴 **Ruolo: Amministratore**")
    else:
        st.markdown("🔵 **Ruolo: Utente**")
        
    if st.button("Logout"):
        st.session_state["utente_corrente"] = None
        st.rerun()
    st.divider()

# --- DEFINIZIONE TAB PRINCIPALI ---
tabs_list = ["Pronostici", "Classifiche", "Regolamento"]
tab_admin = None
if is_admin:
    tabs_list.append("Admin")

tabs = st.tabs(tabs_list)
tab_pronostici = tabs[0]
tab_classifiche = tabs[1]
tab_regolamento = tabs[2]
if is_admin:
    tab_admin = tabs[3]

# ==============================================================================
# --- 1. SEZIONE PRONOSTICI ---
# ==============================================================================
with tab_pronostici:
    st.header("🎯 Inserisci il tuo Pronostico")
    try:
        partite_aperte = db.table("partite").select("*").eq("omologata", False).order("data_ora").execute().data
    except Exception:
        partite_aperte = []

    if not partite_aperte:
        st.info("Nessuna partita disponibile per i pronostici al momento.")
    else:
        dict_part = {f"{p['competizione']} - Cagliari vs {p['avversario']} ({p['data_ora'][:10]}) [ID: {p['id']}]": p for p in partite_aperte}
        scelta_p_str = st.selectbox("Seleziona Partita", list(dict_part.keys()))
        partita = dict_part[scelta_p_str]

        competizione_corrente = partita.get("competizione", "Serie A")
        logo_comp_file = get_competizione_logo_filename(competizione_corrente)

        campo_partita = partita.get('campo') or partita.get('casa_trasferta') or 'Casa'
        is_cag_left = campo_partita in ["Casa", "Campo Neutro"]
        squadra_1 = "CAGLIARI" if is_cag_left else partita['avversario']
        squadra_2 = partita['avversario'] if is_cag_left else "CAGLIARI"

        col_s1, col_vs, col_s2 = st.columns([3, 1, 3])
        with col_s1:
            st.markdown(f"### {squadra_1}")
        with col_vs:
            st.markdown("<h3 style='text-align: center;'>vs</h3>", unsafe_allow_html=True)
            st.markdown(f"<div style='text-align: center;'><img src='app/static/{logo_comp_file}' width='35'></div>", unsafe_allow_html=True)
        with col_s2:
            st.markdown(f"### {squadra_2}")

        col_g1, col_g2 = st.columns(2)
        with col_g1:
            gol_s1 = st.number_input(f"Gol {squadra_1}", min_value=0, max_value=20, value=0, key=f"g_s1_{partita['id']}")
        with col_g2:
            gol_s2 = st.number_input(f"Gol {squadra_2}", min_value=0, max_value=20, value=0, key=f"g_s2_{partita['id']}")

        is_goleada_1 = gol_s1 > 9
        is_goleada_2 = gol_s2 > 9

        rosa_cag_list = [x.strip() for x in (partita.get("rosa_cagliari") or "").split(",") if x.strip()]
        rosa_avv_list = [x.strip() for x in (partita.get("rosa_avversaria") or "").split(",") if x.strip()]

        rosa_team1 = rosa_cag_list if is_cag_left else rosa_avv_list
        rosa_team2 = rosa_avv_list if is_cag_left else rosa_cag_list

        st.markdown("#### Dettagli Marcatori e Cartellini")
        col_m1, col_m2 = st.columns(2)

        with col_m1:
            st.markdown(f"**{squadra_1}**")
            if is_goleada_1:
                st.info(f"Goleada stimata per {squadra_1}: non è richiesto l'inserimento dei marcatori.")
                marc1 = []
            else:
                marc1 = st.multiselect(f"Marcatori {squadra_1}", options=rosa_team1, key=f"marc_1_{partita['id']}")
                for m in marc1:
                    k_m1 = f"g_s1_{m}_{partita['id']}"
                    st.session_state.gol_singoli[k_m1] = st.number_input(f"Gol di {m}", 1, 20, 1, key=k_m1)
            
            auto2 = st.multiselect(f"Autogol a favore di {squadra_1} (fatti da {squadra_2})", options=rosa_team2, key=f"auto_2_{partita['id']}")
            for a in auto2:
                k_a2 = f"auto_s2_{a}_{partita['id']}"
                st.session_state.gol_singoli[k_a2] = st.number_input(f"Autogol di {a}", 1, 20, 1, key=k_a2)
            
            esp1 = st.multiselect(f"Espulsi {squadra_1}", options=rosa_team1, key=f"esp_1_{partita['id']}")

        with col_m2:
            st.markdown(f"**{squadra_2}**")
            if is_goleada_2:
                st.info(f"Goleada stimata per {squadra_2}: non è richiesto l'inserimento dei marcatori.")
                marc2 = []
            else:
                marc2 = st.multiselect(f"Marcatori {squadra_2}", options=rosa_team2, key=f"marc_2_{partita['id']}")
                for m in marc2:
                    k_m2 = f"g_s2_{m}_{partita['id']}"
                    st.session_state.gol_singoli[k_m2] = st.number_input(f"Gol di {m}", 1, 20, 1, key=k_m2)
            
            auto1 = st.multiselect(f"Autogol a favore di {squadra_2} (fatti da {squadra_1})", options=rosa_team1, key=f"auto_1_{partita['id']}")
            for a in auto1:
                k_a1 = f"auto_s1_{a}_{partita['id']}"
                st.session_state.gol_singoli[k_a1] = st.number_input(f"Autogol di {a}", 1, 20, 1, key=k_a1)
            
            esp2 = st.multiselect(f"Espulsi {squadra_2}", options=rosa_team2, key=f"esp_2_{partita['id']}")

        st.markdown('<div class="btn-primary-custom">', unsafe_allow_html=True)
        if st.button("Invia Pronostico"):
            tot_gol_s1_calcolati = 0
            if not is_goleada_1:
                for m in marc1:
                    tot_gol_s1_calcolati += st.session_state.gol_singoli.get(f"g_s1_{m}_{partita['id']}", 1)
            for a in auto2:
                tot_gol_s1_calcolati += st.session_state.gol_singoli.get(f"auto_s2_{a}_{partita['id']}", 1)

            tot_gol_s2_calcolati = 0
            if not is_goleada_2:
                for m in marc2:
                    tot_gol_s2_calcolati += st.session_state.gol_singoli.get(f"g_s2_{m}_{partita['id']}", 1)
            for a in auto1:
                tot_gol_s2_calcolati += st.session_state.gol_singoli.get(f"auto_s1_{a}_{partita['id']}", 1)

            errore_coerenza = False
            if not is_goleada_1 and tot_gol_s1_calcolati != gol_s1:
                st.error(f"Errore per {squadra_1}: inseriti {gol_s1} gol totali, ma la somma calcolata è {tot_gol_s1_calcolati}.")
                errore_coerenza = True
            if not is_goleada_2 and tot_gol_s2_calcolati != gol_s2:
                st.error(f"Errore per {squadra_2}: inseriti {gol_s2} gol totali, ma la somma calcolata è {tot_gol_s2_calcolati}.")
                errore_coerenza = True

            if not errore_coerenza:
                if is_cag_left:
                    gol_cag, gol_avv = gol_s1, gol_s2
                    marc_cag, marc_avv = marc1, marc2
                    auto_cag, auto_avv = auto2, auto1
                    esp_cag, esp_avv = esp1, esp2
                else:
                    gol_cag, gol_avv = gol_s2, gol_s1
                    marc_cag, marc_avv = marc2, marc1
                    auto_cag, auto_avv = auto1, auto2
                    esp_cag, esp_avv = esp2, esp1

                db.table("pronostici").upsert({
                    "id_partita": partita['id'], "utente": st.session_state["utente_corrente"],
                    "gol_cagliari": gol_cag, "gol_avversario": gol_avv,
                    "marcatori_cagliari": marc_cag, "marcatori_avversario": marc_avv,
                    "autogol_cagliari": auto_cag, "autogol_avversario": auto_avv,
                    "espulsi_cagliari": esp_cag, "espulsi_avversario": esp_avv
                }).execute()
                st.success("Pronostico registrato con successo nel database!")
        st.markdown('</div>', unsafe_allow_html=True)

# ==============================================================================
# --- 2. SEZIONE CLASSIFICHE ---
# ==============================================================================
with tab_classifiche:
    st.header("🏆 Classifiche Ufficiali")
    sub_tab1, sub_tab2, sub_tab3, sub_tab4 = st.tabs(["Generale", "Masters of Cugurras", "Bomber di Razza", "Albo d'Oro"])
    
    with sub_tab1:
        st.subheader("Classifica Generale")
        try:
            res_punti = db.table("punteggi_partita").select("utente, punti_generale").execute().data
        except Exception:
            res_punti = []
            
        if res_punti:
            df_p = pd.DataFrame(res_punti)
            df_gen = df_p.groupby("utente", as_index=False)["punti_generale"].sum()
            df_gen = df_gen.sort_values(by="punti_generale", ascending=False).reset_index(drop=True)
            df_gen.index = df_gen.index + 1
            df_gen = df_gen.reset_index().rename(columns={"index": "Posizione", "utente": "Utente", "punti_generale": "Punti"})
            st.dataframe(df_gen[["Posizione", "Utente", "Punti"]], use_container_width=True, hide_index=True)
        else:
            st.info("Nessun punteggio disponibile in classifica generale.")

    with sub_tab2:
        st.subheader("Masters of Cugurras")
        try:
            res_masters = db.table("punteggi_partita").select("utente, punti_masters").execute().data
        except Exception:
            res_masters = []
            
        if res_masters:
            df_m = pd.DataFrame(res_masters)
            df_mast = df_m.groupby("utente", as_index=False)["punti_masters"].sum()
            df_mast = df_mast[df_mast["punti_masters"] > 0]
            df_mast = df_mast.sort_values(by="punti_masters", ascending=False).reset_index(drop=True)
            df_mast.index = df_mast.index + 1
            df_mast = df_mast.reset_index().rename(columns={"index": "Posizione", "utente": "Utente", "punti_masters": "Punti Masters"})
            if not df_mast.empty:
                st.dataframe(df_mast[["Posizione", "Utente", "Punti Masters"]], use_container_width=True, hide_index=True)
            else:
                st.info("Nessun utente ha ancora collezionato punti Masters of Cugurras.")
        else:
            st.info("Nessun dato disponibile per i Masters of Cugurras.")

    with sub_tab3:
        st.subheader("Bomber di Razza")
        try:
            res_bomber = db.table("punteggi_partita").select("utente, punti_bomber").execute().data
        except Exception:
            res_bomber = []
            
        if res_bomber:
            df_b = pd.DataFrame(res_bomber)
            df_bomb = df_b.groupby("utente", as_index=False)["punti_bomber"].sum()
            df_bomb = df_bomb.sort_values(by="punti_bomber", ascending=False).reset_index(drop=True)
            df_bomb.index = df_bomb.index + 1
            df_bomb = df_bomb.reset_index().rename(columns={"index": "Posizione", "utente": "Utente", "punti_bomber": "Punti Bomber"})
            st.dataframe(df_bomb[["Posizione", "Utente", "Punti Bomber"]], use_container_width=True, hide_index=True)
        else:
            st.info("Nessun dato disponibile per Bomber di Razza.")

    with sub_tab4:
        st.subheader("📜 Albo d'Oro")
        try:
            res_albo_pub = db.table("albo_doros").select("*").order("stagione", desc=True).execute()
            if res_albo_pub.data:
                df_albo_pub = pd.DataFrame(res_albo_pub.data)
                df_display = df_albo_pub.rename(columns={
                    "stagione": "Stagione", 
                    "vincitore_premio_cugurra": "Vincitore Premio Cugurra",
                    "premio_masters_of_cugurras": "Masters of Cugurras", 
                    "premio_bomber_di_razza": "Bomber di Razza"
                })
                cols_display = [c for c in ["Stagione", "Vincitore Premio Cugurra", "Masters of Cugurras", "Bomber di Razza"] if c in df_display.columns]
                st.dataframe(df_display[cols_display], use_container_width=True, hide_index=True)
            else:
                st.info("Nessun dato presente nell'Albo d'Oro.")
        except Exception:
            st.info("Albo d'oro non disponibile.")
# ==============================================================================
# --- 3. SEZIONE REGOLAMENTO UFFICIALE DELLA PIATTAFORMA ---
# ==============================================================================
with tab_regolamento:
    st.header("📜 Punteggi e Regolamento del Premio Cugurra")
    st.markdown("""
    ### 1) Punteggi Classifica Generale:
    * **15 Punti:** Risultato e marcatori esatti di tutte e due le squadre.
    * **12 Punti:** Goleada di una squadra (+ di 9 gol) + numero esatto dei gol della squadra che la subisce.
    * **10 Punti:** Risultato esatto della partita e marcatori esatti del Cagliari + eventuali autogol a favore dei rossoblu.
    * **8 Punti:** Indovini lo 0-0, OPPURE solo la goleada di una squadra.
    * **5 Punti:** Indovini l'esito (1, X, 2).
    * **3 Punti:** Tutti i marcatori del Cagliari indovinati.
    * **0 Punti:** Non indovini nulla.
    * **Bonus Espulsioni:** +1 punto per ogni giocatore espulso indovinato (fino a un massimo di 3 per squadra).

    ### 2) Masters of Cugurras:
    * Classifica dedicata esclusivamente a chi colleziona i pronostici da 10 punti.

    ### 3) Bomber di Razza:
    * 1 punto per ogni marcatore del Cagliari indovinato.
    * Bonus: +1 punto a gol se si indovina anche il numero esatto di gol reali segnati da quel calciatore.
    """)

# ==============================================================================
# --- 4. SEZIONE PANNELLO AMMINISTRATORE AVANZATO ---
# ==============================================================================
if tab_admin is not None:
    with tab_admin:
        st.header("⚙️ Gestione Avanzata Stagione")
        
        # --- BLOCCO: CONTROLLO FASE GLOBALE ---
        st.subheader("Controllo Fase Globale")
        fase_scelta = st.selectbox(
            "Cambia Fase Globale", 
            ["TEST", "STAGIONE IN CORSO", "ARCHIVIO"], 
            index=["TEST", "STAGIONE IN CORSO", "ARCHIVIO"].index(fase_attuale) if fase_attuale in ["TEST", "STAGIONE IN CORSO", "ARCHIVIO"] else 0
        )
        if st.button("Aggiorna Fase Globale"):
            db.table("configurazione").update({"valore": fase_scelta}).eq("chiave", "fase_corrente").execute()
            st.success("Fase aggiornata con successo!")
            st.rerun()
            
        st.divider()
        
        # --- BLOCCO: GESTIONE UTENTI & STATUS ---
        st.subheader("👥 Gestione Utenti & Status")
        st.info("ℹ️ **Privilegio Utenti TOP:** Non dovranno più iscriversi nelle stagioni successive.")
        try:
            utenti_db = db.table("utenti").select("*").execute().data
        except Exception:
            utenti_db = []
            
        if utenti_db:
            df_utenti = pd.DataFrame(utenti_db)
            cols_to_show = [c for c in ['nome_fb', 'email', 'status', 'is_admin'] if c in df_utenti.columns]
            st.dataframe(df_utenti[cols_to_show], use_container_width=True)
            
            utenti_non_admin = [u['nome_fb'] for u in utenti_db if not u.get('is_admin', False)]
            if utenti_non_admin:
                utente_target = st.selectbox("Seleziona Utente da gestire", utenti_non_admin, key="sel_usr_manage")
                azione = st.radio("Seleziona Azione:", ["Promuovi a TOP", "Retrocedi a STANDARD", "Elimina Utente"])
                if st.button("Esegui Modifica Utente"):
                    try:
                        if azione == "Elimina Utente":
                            db.table("utenti").delete().eq("nome_fb", utente_target).execute()
                            st.success(f"Utente {utente_target} rimosso correttamente.")
                        else:
                            nuovo_status = "TOP" if azione == "Promuovi a TOP" else "STANDARD"
                            db.table("utenti").update({"status": nuovo_status}).eq("nome_fb", utente_target).execute()
                            st.success(f"Utente {utente_target} aggiornato allo status {nuovo_status}.")
                        st.rerun()
                    except Exception as err:
                        st.error(f"Errore durante l'operazione: {err}")

        st.divider()
        
        # --- BLOCCO: INSERISCI NUOVA PARTITA ---
        st.subheader("➕ Inserisci Nuova Partita")
        try:
            lista_comp = [c['nome'] for c in db.table("competizioni").select("nome").order("nome").execute().data]
        except Exception:
            lista_comp = ["Serie A", "Coppa Italia", "Amichevole"]
            
        with st.form("form_nuova_partita"):
            comp = st.selectbox("Competizione", lista_comp)
            avv = st.text_input("Squadra Avversaria")
            campo = st.selectbox("Campo", ["Casa", "Trasferta", "Campo Neutro"])
            data_p = st.date_input("Data Partita")
            ore_sel = st.selectbox("Ora", list(range(0, 24)), index=15)
            min_sel = st.selectbox("Minuti", [0, 15, 30, 45], index=0)
            rosa_cag_input = st.text_area("Convocati Cagliari (separati da virgola)", "")
            rosa_avv_input = st.text_area("Convocati Avversaria (separati da virgola)", "")
            
            if st.form_submit_button("Crea Partita nel Database"):
                if not avv:
                    st.error("Inserisci la squadra avversaria.")
                else:
                    ora_str = f"{ore_sel:02d}:{min_sel:02d}:00"
                    data_ora_unita = f"{data_p.isoformat()}T{ora_str}"
                    id_str = f"{comp}_{avv}_{data_p}".replace(" ", "_")
                    db.table("partite").insert({
                        "competizione": comp, "avversario": avv, "campo": campo,
                        "casa_trasferta": campo, "data_ora": data_ora_unita, "id_stringa": id_str,
                        "rosa_cagliari": rosa_cag_input.replace(";", ","),
                        "rosa_avversaria": rosa_avv_input.replace(";", ","),
                        "omologata": False
                    }).execute()
                    st.success("Partita creata con successo!")

        st.divider()
        
        # --- BLOCCO: OMOLOGAZIONE PARTITA & CALCOLO PUNTEGGI ---
        st.subheader("🏁 Omologazione Partita")
        st.warning("⚠️ **ATTENZIONE:** L'omologazione inserisce i risultati definitivi, calcola automaticamente tutti i punteggi e **blocca le modifiche successive** sulla partita!")
        
        try:
            partite_non_omologate = db.table("partite").select("*").eq("omologata", False).order("data_ora").execute().data
        except Exception:
            partite_non_omologate = []

        if not partite_non_omologate:
            st.info("Nessuna partita in attesa di omologazione.")
        else:
            dict_omo = {f"{p['competizione']} - Cagliari vs {p['avversario']} ({p['data_ora'][:10]}) [ID: {p['id']}]": p for p in partite_non_omologate}
            scelta_omo_str = st.selectbox("Seleziona partita da omologare", list(dict_omo.keys()), key="select_omo")
            p_omo = dict_omo[scelta_omo_str]

            campo_omo = p_omo.get('campo') or p_omo.get('casa_trasferta') or 'Casa'
            is_cag_left_omo = campo_omo in ["Casa", "Campo Neutro"]
            s1_omo = "CAGLIARI" if is_cag_left_omo else p_omo['avversario']
            s2_omo = p_omo['avversario'] if is_cag_left_omo else "CAGLIARI"

            st.markdown(f"### Risultato Ufficiale: {s1_omo} vs {s2_omo}")
            col_go1, col_go2 = st.columns(2)
            with col_go1: gol_uff_s1 = st.number_input(f"Gol {s1_omo} (Ufficiali)", min_value=0, value=0, key="gol_u_s1")
            with col_go2: gol_uff_s2 = st.number_input(f"Gol {s2_omo} (Ufficiali)", min_value=0, value=0, key="gol_u_s2")

            rosa_cag_l = [x.strip() for x in (p_omo.get("rosa_cagliari") or "").split(",") if x.strip()]
            rosa_avv_l = [x.strip() for x in (p_omo.get("rosa_avversaria") or "").split(",") if x.strip()]
            rosa_t1 = rosa_cag_l if is_cag_left_omo else rosa_avv_l
            rosa_t2 = rosa_avv_l if is_cag_left_omo else rosa_cag_l

            st.markdown("#### Marcatori e Dettagli Ufficiali")
            col_mo1, col_mo2 = st.columns(2)
            with col_mo1:
                st.markdown(f"**{s1_omo}**")
                marc_uff_1 = st.multiselect(f"Marcatori {s1_omo}", options=rosa_t1, key="mu_1")
                for m in marc_uff_1:
                    k_m1 = f"omo_g_s1_{m}_{p_omo['id']}"
                    st.session_state.gol_omologazione[k_m1] = st.number_input(f"Gol di {m}", 1, 20, 1, key=k_m1)
                auto_uff_2 = st.multiselect(f"Autogol a favore di {s1_omo} (fatti da {s2_omo})", options=rosa_t2, key="au_2")
                for a in auto_uff_2:
                    k_a2 = f"omo_auto_s2_{a}_{p_omo['id']}"
                    st.session_state.gol_omologazione[k_a2] = st.number_input(f"Autogol di {a}", 1, 20, 1, key=k_a2)
                esp_uff_1 = st.multiselect(f"Espulsi {s1_omo}", options=rosa_t1, key="eu_1")

            with col_mo2:
                st.markdown(f"**{s2_omo}**")
                marc_uff_2 = st.multiselect(f"Marcatori {s2_omo}", options=rosa_t2, key="mu_2")
                for m in marc_uff_2:
                    k_m2 = f"omo_g_s2_{m}_{p_omo['id']}"
                    st.session_state.gol_omologazione[k_m2] = st.number_input(f"Gol di {m}", 1, 20, 1, key=k_m2)
                auto_uff_1 = st.multiselect(f"Autogol a favore di {s2_omo} (fatti da {s1_omo})", options=rosa_t1, key="au_1")
                for a in auto_uff_1:
                    k_a1 = f"omo_auto_s1_{a}_{p_omo['id']}"
                    st.session_state.gol_omologazione[k_a1] = st.number_input(f"Autogol di {a}", 1, 20, 1, key=k_a1)
                esp_uff_2 = st.multiselect(f"Espulsi {s2_omo}", options=rosa_t2, key="eu_2")

            if st.button("Conferma e Omologa Partita"):
                if is_cag_left_omo:
                    res_cag, res_avv = gol_uff_s1, gol_uff_s2
                    m_cag, m_avv = marc_uff_1, marc_uff_2
                    a_cag, a_avv = auto_uff_2, auto_uff_1
                    e_cag, e_avv = esp_uff_1, esp_uff_2
                else:
                    res_cag, res_avv = gol_uff_s2, gol_uff_s1
                    m_cag, m_avv = marc_uff_2, marc_uff_1
                    a_cag, a_avv = auto_uff_1, auto_uff_2
                    e_cag, e_avv = esp_uff_2, esp_uff_1
                
                db.table("partite").update({
                    "risultato_cagliari": res_cag, "risultato_avversario": res_avv,
                    "marcatori_cagliari_reali": m_cag, "marcatori_avversario_reali": m_avv,
                    "autogol_cagliari_reali": a_cag, "autogol_avversario_reali": a_avv,
                    "espulsi_cagliari_reali": e_cag, "espulsi_avversario_reali": e_avv,
                    "omologata": True
                }).eq("id", p_omo["id"]).execute()

                try:
                    pronostici_utenti = db.table("pronostici").select("*").eq("id_partita", p_omo["id"]).execute().data
                except Exception:
                    pronostici_utenti = []

                for pron in pronostici_utenti:
                    utente = pron["utente"]
                    p_cag = pron.get("gol_cagliari", 0)
                    p_avv = pron.get("gol_avversario", 0)
                    
                    p_marc_cag = set(pron.get("marcatori_cagliari", []) or [])
                    p_marc_avv = set(pron.get("marcatori_avversario", []) or [])
                    p_auto_cag = set(pron.get("autogol_cagliari", []) or [])
                    p_auto_avv = set(pron.get("autogol_avversario", []) or [])
                    p_esp_cag = set(pron.get("espulsi_cagliari", []) or [])
                    p_esp_avv = set(pron.get("espulsi_avversario", []) or [])

                    punti_generale = 0
                    punti_masters = 0
                    punti_bomber = 0

                    is_goleada_cag = p_cag > 9
                    is_goleada_avv = p_avv > 9
                    reale_goleada_cag = res_cag > 9
                    reale_goleada_avv = res_avv > 9

                    bonus_esp = len(p_esp_cag.intersection(set(e_cag))) + len(p_esp_avv.intersection(set(e_avv)))

                    if (is_goleada_cag and not reale_goleada_cag and p_avv == res_avv) or (is_goleada_avv and not reale_goleada_avv and p_cag == res_cag):
                        punti_generale = 12
                    elif is_goleada_cag and is_goleada_avv and reale_goleada_cag and reale_goleada_avv:
                        punti_generale = 8
                    elif p_cag == 0 and res_cag == 0 and p_avv == 0 and res_avv == 0:
                        punti_generale = 8
                    elif is_goleada_cag or is_goleada_avv:
                        punti_generale = 8
                    else:
                        risultato_esatto = (p_cag == res_cag and p_avv == res_avv)
                        marcatori_esatti_tutti = (set(m_cag) == p_marc_cag and set(m_avv) == p_marc_avv and set(a_cag) == p_auto_cag and set(a_avv) == p_auto_avv)
                        
                        if risultato_esatto and marcatori_esatti_tutti:
                            punti_generale = 15
                        elif risultato_esatto and set(m_cag) == p_marc_cag and set(a_cag) == p_auto_cag:
                            punti_generale = 10
                            punti_masters = 10
                        elif (p_cag > p_avv and res_cag > res_avv) or (p_cag < p_avv and res_cag < res_avv) or (p_cag == p_avv and res_cag == res_avv):
                            punti_generale = 5
                        elif set(m_cag) == p_marc_cag and set(a_cag) == p_auto_cag and len(m_cag) > 0:
                            punti_generale = 3
                        else:
                            punti_generale = 0

                    punti_generale += bonus_esp

                    for m_pron in p_marc_cag:
                        if m_pron in m_cag:
                            punti_bomber += 1

                    db.table("punteggi_partita").upsert({
                        "id_partita": p_omo["id"], "utente": utente,
                        "punti_generale": punti_generale, "punti_masters": punti_masters,
                        "punti_bomber": punti_bomber
                    }).execute()

                st.success("Partita omologata e punteggi calcolati con successo!")
                st.rerun()

        st.divider()
        
        # --- BLOCCO: MODIFICA O ELIMINA PARTITE ATTIVE ---
        st.subheader("🛠️ Modifica o Elimina Partite Attive")
        try:
            partite_attive = db.table("partite").select("*").eq("omologata", False).order("data_ora").execute().data
        except Exception:
            partite_attive = []

        if not partite_attive:
            st.info("Nessuna partita attiva da modificare.")
        else:
            dict_partite = {f"{p['competizione']} - Cagliari vs {p['avversario']} ({p['data_ora'][:10]}) [ID: {p['id']}]": p for p in partite_attive}
            scelta_partita_str = st.selectbox("Seleziona partita attiva da modificare o eliminare", list(dict_partite.keys()))
            p_selezionata = dict_partite[scelta_partita_str]

            with st.form("form_modifica_partita"):
                m_comp = st.text_input("Competizione", value=p_selezionata.get("competizione", ""))
                m_avv = st.text_input("Squadra Avversaria", value=p_selezionata.get("avversario", ""))
                
                attuale_campo = p_selezionata.get("campo") or p_selezionata.get("casa_trasferta") or "Casa"
                idx_campo = ["Casa", "Trasferta", "Campo Neutro"].index(attuale_campo) if attuale_campo in ["Casa", "Trasferta", "Campo Neutro"] else 0
                m_campo = st.selectbox("Campo", ["Casa", "Trasferta", "Campo Neutro"], index=idx_campo)
                
                try:
                    dt_esistente = datetime.fromisoformat(p_selezionata['data_ora'].replace("Z", "+00:00"))
                    init_date = dt_esistente.date()
                    init_hour = dt_esistente.hour
                    init_minute_idx = [0, 15, 30, 45].index(dt_esistente.minute) if dt_esistente.minute in [0, 15, 30, 45] else 0
                except Exception:
                    init_date = datetime.today().date()
                    init_hour = 15
                    init_minute_idx = 0

                m_data = st.date_input("Data Partita", value=init_date)
                m_ora = st.selectbox("Ora", list(range(0, 24)), index=init_hour)
                m_min = st.selectbox("Minuti", [0, 15, 30, 45], index=init_minute_idx)
                
                m_rosa_cag = st.text_area("Convocati Cagliari", value=p_selezionata.get("rosa_cagliari", ""))
                m_rosa_avv = st.text_area("Convocati Avversaria", value=p_selezionata.get("rosa_avversaria", ""))

                col_mod1, col_mod2 = st.columns(2)
                with col_mod1:
                    submit_mod = st.form_submit_button("Salva Modifiche")
                with col_mod2:
                    submit_del = st.form_submit_button("Elimina Partita")

                if submit_mod:
                    ora_str = f"{m_ora:02d}:{m_min:02d}:00"
                    data_ora_unita = f"{m_data.isoformat()}T{ora_str}"
                    id_str = f"{m_comp}_{m_avv}_{m_data}".replace(" ", "_")
                    
                    db.table("partite").update({
                        "competizione": m_comp, "avversario": m_avv, "campo": m_campo,
                        "casa_trasferta": m_campo, "data_ora": data_ora_unita, "id_stringa": id_str,
                        "rosa_cagliari": m_rosa_cag.replace(";", ","),
                        "rosa_avversaria": m_rosa_avv.replace(";", ",")
                    }).eq("id", p_selezionata["id"]).execute()
                    st.success("Partita aggiornata con successo!")
                    st.rerun()

                if submit_del:
                    db.table("partite").delete().eq("id", p_selezionata["id"]).execute()
                    st.success("Partita eliminata correttamente!")
                    st.rerun()
                    
        st.divider()
        
        # --- BLOCCO: GESTIONE ALBO D'ORO (ADMIN) ---
        st.subheader("✍️ Gestione Albo d'Oro (Admin)")
        try:
            res_albo_admin = db.table("albo_doros").select("*").order("stagione", desc=True).execute()
            if res_albo_admin.data:
                df_albo_admin = pd.DataFrame(res_albo_admin.data)
                edited_df = st.data_editor(
                    df_albo_admin, 
                    num_rows="dynamic", 
                    use_container_width=True, 
                    key="editor_albo_admin"
                )
                if st.button("Salva Modifiche Albo d'Oro"):
                    try:
                        records = edited_df.to_dict(orient="records")
                        for r in records:
                            row_id = r.get("id")
                            data_to_save = {
                                "stagione": r.get("stagione"),
                                "vincitore_premio_cugurra": r.get("vincitore_premio_cugurra"),
                                "premio_masters_of_cugurras": r.get("premio_masters_of_cugurras"),
                                "premio_bomber_di_razza": r.get("premio_bomber_di_razza")
                            }
                            if pd.notna(row_id) and row_id:
                                db.table("albo_doros").update(data_to_save).eq("id", int(row_id)).execute()
                            else:
                                db.table("albo_doros").insert(data_to_save).execute()
                        st.success("Albo d'Oro aggiornato con successo!")
                        st.rerun()
                    except Exception as ex_albo:
                        st.error(f"Errore durante l'aggiornamento dell'Albo d'Oro: {ex_albo}")
        except Exception:
            st.info("Impossibile caricare l'albo d'oro per la gestione amministrativa.")

# --- RICHIAMO FUNZIONE FOOTER FINALE ---
mostra_footer()
