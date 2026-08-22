import streamlit as st
import pandas as pd
from supabase import create_client, Client
from datetime import datetime, timezone

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="Premio Cugurra", page_icon="⚽", layout="wide")

# --- CSS / STYLING DEFINITIVO (FORZATURA TEMA UNICO E INPUT) ---
st.markdown("""
    <style>
    /* Forzatura globale tema scuro fisso */
    .stApp { background-color: #12161f !important; color: #f8fafc !important; }
    h1, h2, h3 { color: #38bdf8 !important; }
    
    /* Correzione critica campi di input e select per dispositivi mobili e desktop */
    input, textarea, select, div[data-baseweb="select"] > div {
        background-color: #1e293b !important;
        color: #f8fafc !important;
        border-color: #334155 !important;
    }
    
    /* Testo e placeholder nei campi di input */
    .stTextInput input, .stTextArea textarea, .stNumberInput input {
        color: #f8fafc !important;
        background-color: #1e293b !important;
        font-size: 1.1em !important;
        text-align: center !important;
    }

    /* Dropdown / Selectbox */
    div[data-baseweb="select"] * {
        color: #f8fafc !important;
        background-color: #1e293b !important;
    }

    .stButton>button { 
        background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%) !important; 
        color: white !important; 
        font-weight: bold !important; 
        padding: 0.8rem !important; 
        width: 100% !important; 
        border-radius: 10px !important; 
        border: none !important; 
    }
    .stButton>button:hover { 
        background: linear-gradient(135deg, #0369a1 0%, #0284c7 100%) !important; 
    }
    
    /* Contenitore Pronostico Squadra Compatto */
    .prediction-box {
        background-color: #1e293b !important;
        border: 1px solid #334155 !important;
        border-radius: 12px !important;
        padding: 15px !important;
        text-align: center !important;
        margin-bottom: 10px !important;
    }
    
    /* Stile Retrò per il Countdown */
    @import url('https://fonts.googleapis.com/css2?family=Press+Start+2P&display=swap');
    .retro-timer-container {
        background-color: #090d16 !important;
        border: 2px solid #38bdf8 !important;
        border-radius: 8px !important;
        padding: 12px !important;
        text-align: center !important;
        margin-bottom: 20px !important;
        box-shadow: 0 0 10px rgba(56, 189, 248, 0.3) !important;
    }
    .retro-timer-title {
        font-family: 'Press Start 2P', monospace !important;
        font-size: 0.75rem !important;
        color: #94a3b8 !important;
        margin-bottom: 8px !important;
        text-transform: uppercase !important;
    }
    .retro-timer-clock {
        font-family: 'Press Start 2P', monospace !important;
        font-size: 1.1rem !important;
        color: #fbbf24 !important;
        letter-spacing: 2px !important;
    }

    @media (max-width: 640px) {
        .prediction-box { padding: 8px !important; margin-bottom: 5px !important; }
        h3 { font-size: 1.2rem !important; }
    }
    </style>
""", unsafe_allow_html=True)

# --- SUPABASE ---
SUPABASE_URL = "https://kbbxjfxltkchzvkyofdr.supabase.co"
SUPABASE_KEY = "sb_publishable_vT3i8G3_Lz8QQnDmhUqVOA_83_y_y3B"
STORAGE_BASE_URL = f"{SUPABASE_URL}/storage/v1/object/public/LOGHI_E_GRAFICHE/"

@st.cache_resource
def init_supabase(): return create_client(SUPABASE_URL, SUPABASE_KEY)
db = init_supabase()

def get_fase():
    try:
        res = db.table("configurazione").select("valore").eq("chiave", "fase_corrente").execute()
        return res.data[0]['valore'] if res.data else "TEST"
    except:
        return "TEST"

def get_url_scudetto(nome_squadra):
    if not nome_squadra:
        return f"{STORAGE_BASE_URL}DEFAULT.png"
    return f"{STORAGE_BASE_URL}{nome_squadra.strip().upper()}.png"

def mostra_footer():
    st.divider()
    url_logo = f"{STORAGE_BASE_URL}CUGURRAOFFICIAL.png"
    st.markdown(f"""
    <div style="text-align: center; color: #fbbf24; font-weight: bold; background-color: #1e293b; padding: 15px; border-radius: 12px; border: 1px solid #334155;">
        <img src="{url_logo}" width="90" style="margin-bottom: 8px;"><br>
        <p>"Essere cugurra, esserlo nella mente"</p>
        <p style="font-size: 0.8em; color: #94a3b8;">App by Tifosi del Cagliari & Asugi</p>
    </div>
    """, unsafe_allow_html=True)

# --- GESTIONE SESSIONE ---
if "autenticato" not in st.session_state:
    st.session_state.update({"autenticato": False, "utente_corrente": None, "is_admin": False, "status": None, "gol_singoli": {}, "gol_omologazione": {}})

fase_attuale = get_fase()

# --- LOGIN / REGISTRAZIONE ---
if not st.session_state["autenticato"]:
    st.title("⚽ Premio Cugurra - Accesso")
    scelta_accesso = st.radio("Seleziona operazione:", ["Accedi", "Registrati"], horizontal=True)
    
    if scelta_accesso == "Accedi":
        col_l1, _ = st.columns([2, 1])
        with col_l1:
            nome_inserito = st.text_input("Nome Facebook / Utente")
            pin_inserito = st.text_input("PIN Segreto", type="password")
            if st.button("Accedi"):
                try:
                    res = db.table("utenti").select("*").eq("nome_fb", nome_inserito).eq("pin", pin_inserito).execute()
                    if res.data:
                        u = res.data[0]
                        st.session_state.update({
                            "autenticato": True, 
                            "utente_corrente": u["nome_fb"], 
                            "is_admin": u.get('is_admin', False), 
                            "status": u.get('status')
                        })
                        st.rerun()
                    else:
                        st.error("Nome o PIN non corretti.")
                except Exception as e:
                    st.error(f"Errore di connessione: {e}")
    else:
        col_r1, _ = st.columns([2, 1])
        with col_r1:
            new_nome = st.text_input("Nome Facebook / Utente")
            new_email = st.text_input("Email")
            new_pin = st.text_input("PIN Segreto", type="password")
            if st.button("Completa Registrazione"):
                if not new_nome or not new_pin or not new_email:
                    st.error("Compila tutti i campi.")
                else:
                    try:
                        check_nome = db.table("utenti").select("nome_fb").eq("nome_fb", new_nome).execute()
                        if check_nome.data:
                            st.warning(f"Il nome utente '{new_nome}' è già utilizzato.")
                        else:
                            check_email = db.table("utenti").select("email").eq("email", new_email).execute()
                            if check_email.data:
                                st.error("Attenzione: questa email risulta già associata a un altro account.")
                            else:
                                nuovo_status = "TOP" if fase_attuale == "TEST" else "STANDARD"
                                db.table("utenti").insert({
                                    "nome_fb": new_nome, "email": new_email, "pin": new_pin, 
                                    "status": nuovo_status, "is_admin": False
                                }).execute()
                                st.success("Registrato correttamente! Passa alla scheda 'Accedi'.")
                    except Exception as err:
                        st.error(f"Errore durante la registrazione: {err}")
    st.stop()

# --- BARRA LATERALE ---
st.sidebar.markdown(f"👤 Utente: **{st.session_state['utente_corrente']}**")
st.sidebar.markdown(f"⭐ Status: **{st.session_state['status']}**")
st.sidebar.markdown(f"📌 Stagione: **{fase_attuale}**")
if st.sidebar.button("Logout"):
    st.session_state.clear()
    st.rerun()

# --- INTERFACCIA PRINCIPALE ---
st.title(f"⚽ Premio Cugurra 2026/27 ({fase_attuale})")
tabs = st.tabs(["⚙️ Admin", "📝 Pronostici", "🏆 Classifiche", "📜 Regolamento"])

# 1. ADMIN
with tabs[0]:
    if st.session_state["is_admin"]:
        st.header("⚙️ Gestione Stagione")
        fase_scelta = st.selectbox("Cambia Fase Globale", ["TEST", "STAGIONE IN CORSO", "ARCHIVIO"], index=["TEST", "STAGIONE IN CORSO", "ARCHIVIO"].index(fase_attuale) if fase_attuale in ["TEST", "STAGIONE IN CORSO", "ARCHIVIO"] else 0)
        if st.button("Aggiorna Fase Globale"):
            db.table("configurazione").update({"valore": fase_scelta}).eq("chiave", "fase_corrente").execute()
            st.success("Fase aggiornata!")
            st.rerun()
            
        st.divider()
        st.subheader("👥 Gestione Utenti")
        try:
            utenti_db = db.table("utenti").select("*").execute().data
        except:
            utenti_db = []
            
        if utenti_db:
            df_utenti = pd.DataFrame(utenti_db)
            cols_to_show = [c for c in ['nome_fb', 'email', 'status', 'is_admin'] if c in df_utenti.columns]
            st.dataframe(df_utenti[cols_to_show], use_container_width=True)
            
            utenti_non_admin = [u['nome_fb'] for u in utenti_db if not u.get('is_admin', False)]
            if utenti_non_admin:
                utente_target = st.selectbox("Seleziona Utente da gestire", utenti_non_admin)
                azione = st.radio("Azione:", ["Promuovi a TOP", "Retrocedi a STANDARD", "Elimina Utente"])
                if st.button("Esegui Modifica Utente"):
                    try:
                        if azione == "Elimina Utente":
                            db.table("utenti").delete().eq("nome_fb", utente_target).execute()
                            st.success(f"Utente {utente_target} rimosso.")
                        else:
                            nuovo_status = "TOP" if azione == "Promuovi a TOP" else "STANDARD"
                            db.table("utenti").update({"status": nuovo_status}).eq("nome_fb", utente_target).execute()
                            st.success(f"{utente_target} ora è {nuovo_status}.")
                        st.rerun()
                    except Exception as err:
                        st.error(f"Errore: {err}")

        st.divider()
        with st.expander("📜 Aggiorna / Inserisci Albo d'Oro"):
            with st.form("form_albo"):
                stag = st.text_input("Stagione (es. 2026-27)")
                vinc = st.text_input("Vincitore Premio Cugurra")
                mast = st.text_input("Masters of Cugurras")
                bomb = st.text_input("Bomber di Razza")
                if st.form_submit_button("Salva nell'Albo d'Oro"):
                    if stag and vinc:
                        db.table("albo_doros").insert({
                            "stagione": stag, "vincitore_premio_cugurra": vinc,
                            "premio_masters_of_cugurras": mast, "premio_bomber_di_razza": bomb
                        }).execute()
                        st.success("Stagione aggiunta!")

        st.divider()
        st.subheader("Inserisci Nuova Partita")
        try:
            lista_comp = [c['nome'] for c in db.table("competizioni").select("nome").order("nome").execute().data]
        except:
            lista_comp = ["Serie A"]
            
        with st.form("form_nuova_partita"):
            comp = st.selectbox("Competizione", lista_comp)
            avv = st.text_input("Squadra Avversaria")
            campo = st.selectbox("Campo", ["Casa", "Trasferta", "Campo Neutro"])
            data_p = st.date_input("Data Partita")
            ore_sel = st.selectbox("Ora", list(range(0, 24)), index=15)
            min_sel = st.selectbox("Minuti", [0, 15, 30, 45], index=0)
            rosa_cag_input = st.text_area("Convocati Cagliari", "")
            rosa_avv_input = st.text_area("Convocati Avversaria", "")
            
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
                    st.success("Partita creata!")

        st.divider()
        st.subheader("🏁 Omologazione Partita & Calcolo Automatico Punti")
        try:
            partite_non_omologate = db.table("partite").select("*").eq("omologata", False).order("data_ora").execute().data
        except:
            partite_non_omologate = []

        if not partite_non_omologate:
            st.info("Nessuna partita in attesa di omologazione.")
        else:
            dict_omolog = {f"{p['competizione']} - Cagliari vs {p['avversario']} ({p['data_ora'][:10]}) [ID: {p['id']}]": p for p in partite_non_omologate}
            scelta_omo_str = st.selectbox("Seleziona partita da omologare", list(dict_omolog.keys()), key="select_omo")
            p_omo = dict_omolog[scelta_omo_str]

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

            st.markdown("#### Marcatori e Dettagli")
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
                except:
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

                st.success("Partita omologata e punti assegnati automaticamente!")
                st.rerun()

        st.divider()
        st.subheader("🛠️ Modifica o Elimina Partite Esistenti")
        try:
            partite_admin = db.table("partite").select("*").order("data_ora").execute().data
        except:
            partite_admin = []

        if partite_admin:
            dict_partite = {f"{p['competizione']} - Cagliari vs {p['avversario']} ({p['data_ora'][:10]}) [ID: {p['id']}]": p for p in partite_admin}
            scelta_partita_str = st.selectbox("Seleziona partita da modificare o eliminare", list(dict_partite.keys()))
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
                except:
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
                    st.success("Partita aggiornata!")
                    st.rerun()

                if submit_del:
                    db.table("partite").delete().eq("id", p_selezionata["id"]).execute()
                    st.success("Partita eliminata!")
                    st.rerun()
    else:
        st.warning("Accesso negato. Area riservata agli amministratori.")

# 2. PRONOSTICI
with tabs[1]:
    if fase_attuale == "ARCHIVIO":
        st.warning("Stagione in archivio. Pronostici disabilitati.")
    else:
        try:
            partite_db = db.table("partite").select("*").order("data_ora").execute().data
        except:
            partite_db = []

        now_utc = datetime.now(timezone.utc)
        partita = next((p for p in partite_db if datetime.fromisoformat(p['data_ora'].replace("Z", "+00:00")) > now_utc and not p.get('omologata', False)), None)
        
        if not partita:
            st.info("Nessuna partita disponibile per il pronostico in questo momento.")
        else:
            dt_partita = datetime.fromisoformat(partita['data_ora'].replace("Z", "+00:00"))
            
            diff = dt_partita - now_utc
            if diff.total_seconds() > 0:
                giorni = diff.days
                ore, resto = divmod(diff.seconds, 3600)
                minuti, secondi = divmod(resto, 60)
                str_countdown = f"{giorni}g {ore:02d}h {minuti:02d}m {secondi:02d}s" if giorni > 0 else f"{ore:02d}h {minuti:02d}m {secondi:02d}s"
            else:
                str_countdown = "IN CORSO / TERMINATA"

            campo_val = partita.get('campo') or partita.get('casa_trasferta') or 'Casa'
            is_cagliari_left = campo_val in ["Casa", "Campo Neutro"]
            squadra_1 = "CAGLIARI" if is_cagliari_left else partita['avversario']
            squadra_2 = partita['avversario'] if is_cagliari_left else "CAGLIARI"

            st.subheader(f"Prossima partita: {squadra_1} vs {squadra_2} ({dt_partita.strftime('%d/%m/%Y ore %H:%M')})")
            
            st.markdown(f"""
                <div class="retro-timer-container">
                    <div class="retro-timer-title">⏱️ Tempo al calcio d'inizio</div>
                    <div class="retro-timer-clock">{str_countdown}</div>
                </div>
            """, unsafe_allow_html=True)
            
            col_s1, col_mid, col_s2 = st.columns([2, 0.6, 2])
            
            with col_s1:
                st.markdown('<div class="prediction-box">', unsafe_allow_html=True)
                _, img_col1, _ = st.columns([1, 2, 1])
                with img_col1:
                    st.image(get_url_scudetto(squadra_1), width=90)
                gol_s1 = st.number_input(f"Gol {squadra_1}", min_value=0, value=0, key=f"gs1_{partita['id']}")
                st.markdown('</div>', unsafe_allow_html=True)
                
            with col_mid:
                st.markdown("<h2 style='text-align: center; margin-top: 40px;'>VS</h2>", unsafe_allow_html=True)
                
            with col_s2:
                st.markdown('<div class="prediction-box">', unsafe_allow_html=True)
                _, img_col2, _ = st.columns([1, 2, 1])
                with img_col2:
                    st.image(get_url_scudetto(squadra_2), width=90)
                gol_s2 = st.number_input(f"Gol {squadra_2}", min_value=0, value=0, key=f"gs2_{partita['id']}")
                st.markdown('</div>', unsafe_allow_html=True)

            is_goleada_1 = gol_s1 > 9
            is_goleada_2 = gol_s2 > 9

            st.markdown("---")
            rosa_cag = [x.strip() for x in (partita.get("rosa_cagliari") or "").split(",") if x.strip()]
            rosa_avv = [x.strip() for x in (partita.get("rosa_avversaria") or "").split(",") if x.strip()]
            rosa_1 = rosa_cag if is_cagliari_left else rosa_avv
            rosa_2 = rosa_avv if is_cagliari_left else rosa_cag

            def render_team_section(team_name, lista_rosa, lista_opp, is_goleada, key_pref):
                st.markdown(f"### {team_name}")
                if is_goleada:
                    st.info("Goleada attivata (>9 gol): marcatori disabilitati.")
                    marcatori = []
                else:
                    marcatori = st.multiselect(f"Marcatori {team_name}", options=lista_rosa, key=f"m_{key_pref}_{partita['id']}")
                    for m in marcatori:
                        k = f"g_{key_pref}_{m}_{partita['id']}"
                        st.session_state.gol_singoli[k] = st.number_input(f"Gol di {m}", 1, 50, st.session_state.gol_singoli.get(k, 1), key=k)

                autogol = st.multiselect(f"Autogol a favore ({team_name})", options=lista_opp, key=f"a_{key_pref}_{partita['id']}")
                for a in autogol:
                    k = f"auto_{key_pref}_{a}_{partita['id']}"
                    st.session_state.gol_singoli[k] = st.number_input(f"Autogol di {a}", 1, 50, st.session_state.gol_singoli.get(k, 1), key=k)
                
                espulsi = st.multiselect(f"Espulsi ({team_name})", options=lista_rosa, max_selections=3, key=f"e_{key_pref}_{partita['id']}")
                return marcatori, autogol, espulsi

            col_tab1, col_tab2 = st.columns(2)
            with col_tab1: marc1, auto1, esp1 = render_team_section(squadra_1, rosa_1, rosa_2, is_goleada_1, "s1")
            with col_tab2: marc2, auto2, esp2 = render_team_section(squadra_2, rosa_2, rosa_1, is_goleada_2, "s2")

            st.markdown("<br>", unsafe_allow_html=True)
            col_btn1, col_btn2 = st.columns(2)
            
            with col_btn1:
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
                        if is_cagliari_left:
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
                        st.success("Pronostico registrato con successo!")

            with col_btn2:
                if st.button("Cancella i dati inseriti"):
                    keys_to_clear = [k for k in st.session_state.keys() if str(partita['id']) in k or k.startswith("gs")]
                    for k in keys_to_clear:
                        del st.session_state[k]
                    st.success("Dati cancellati. Ricaricamento...")
                    st.rerun()

# 3. CLASSIFICHE
with tabs[2]:
    st.header("🏆 Classifiche Ufficiali")
    sub_tab1, sub_tab2, sub_tab3 = st.tabs(["Generale", "Masters of Cugurras", "Bomber di Razza"])
    with sub_tab1: st.write("In attesa delle prime partite.")
    with sub_tab2: st.write("Classifica pronostici da 10 punti.")
    with sub_tab3: st.write("Punti marcatori.")

# 4. REGOLAMENTO
with tabs[3]:
    st.header("📜 Punteggi e Regolamento del Premio Cugurra")
    st.markdown("""
    ### 1) Punteggi Classifica Generale:
    * **15 Punti:** Risultato e marcatori esatti di tutte e due le squadre.
    * **12 Punti:** Goleada di una squadra (+ di 9 gol) + numero esatto dei gol della squadra che la subisce.
    * **10 Punti:** Risultato e marcatori SOLO del Cagliari esatti.
    * **8 Punti:** Indovini lo 0-0, OPPURE solo la goleada di una squadra.
    * **5 Punti:** Indovini l'esito (1, X, 2).
    * **3 Punti:** Tutti i marcatori del Cagliari indovinati.
    * **0 Punti:** Non indivini nulla.
    * **Bonus Espulsioni:** +1 punto per ogni giocatore espulso indovinato (fino a 3 per squadra).

    ### 2) Masters of Cugurras:
    * Classifica dedicata a chi colleziona i pronostici da 10 punti.

    ### 3) Bomber di Razza:
    * 1 punto per ogni marcatore del Cagliari indovinato.
    * Bonus: +1 punto a gol se si indovina anche il numero esatto di gol reali segnati da quel calciatore.
    """)

# --- ALBO D'ORO IN FONDO ALLA PAGINA ---
st.divider()
st.header("📜 Albo d'Oro Storico")
try:
    res_albo = db.table("albo_doros").select("*").order("stagione", desc=True).execute()
    if res_albo.data:
        df_albo = pd.DataFrame(res_albo.data)
        df_albo = df_albo.rename(columns={
            "stagione": "Stagione", "vincitore_premio_cugurra": "Vincitore",
            "premio_masters_of_cugurras": "Masters", "premio_bomber_di_razza": "Bomber"
        })
        st.dataframe(df_albo, use_container_width=True, hide_index=True)
    else:
        st.info("Nessun dato presente nell'Albo d'Oro.")
except:
    st.info("Albo d'oro non disponibile.")

mostra_footer()
