import streamlit as st
import pandas as pd
from supabase import create_client, Client
from datetime import datetime, timezone
import streamlit.components.v1 as components

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="Premio Cugurra", page_icon="⚽", layout="wide")

# --- SUPABASE ---
SUPABASE_URL = "https://kbbxjfxltkchzvkyofdr.supabase.co"
SUPABASE_KEY = "sb_publishable_vT3i8G3_Lz8QQnDmhUqVOA_83_y_y3B"
STORAGE_BASE_URL = f"{SUPABASE_URL}/storage/v1/object/public/LOGHI_E_GRAFICHE/"
SFONDO_URL = f"{STORAGE_BASE_URL}sfondo.jpg"

@st.cache_resource
def init_supabase(): 
    return create_client(SUPABASE_URL, SUPABASE_KEY)

db = init_supabase()

# --- CSS / STYLING DEFINITIVO ---
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Press+Start+2P&display=swap');

    /* Sfondo Globale con sovrapposizione scura per la massima leggibilità */
    .stApp {{
        background: linear-gradient(rgba(18, 22, 31, 0.88), rgba(18, 22, 31, 0.95)), 
                    url('{SFONDO_URL}') no-repeat center center fixed !important;
        background-size: cover !important;
        color: #f8fafc !important;
    }}

    h1, h2, h3 {{ color: #38bdf8 !important; }}
    
    /* Etichette dei campi di input rese ben visibili e bianche */
    .stTextInput label, .stSelectbox label, .stDateInput label, .stTextArea label, div[data-baseweb="select"] label {{
        color: #ffffff !important;
        font-weight: 600 !important;
    }}

    /* Input generici e selectbox */
    input, textarea, select, div[data-baseweb="select"] > div {{
        background-color: #1e293b !important;
        color: #f8fafc !important;
        border-color: #334155 !important;
    }}
    
    .stTextInput input, .stTextArea textarea {{
        color: #f8fafc !important;
        background-color: #1e293b !important;
        font-size: 1em !important;
    }}

    div[data-baseweb="select"] * {{
        color: #f8fafc !important;
        background-color: #1e293b !important;
    }}

    /* Input Gol Cicciotti per i Punteggi Principali */
    .big-score-input input {{
        font-size: 2.2rem !important;
        font-weight: bold !important;
        height: 65px !important;
        text-align: center !important;
        color: #fbbf24 !important;
        background-color: #0f172a !important;
        border: 2px solid #38bdf8 !important;
        border-radius: 12px !important;
    }}

    /* Container Box Pronostico */
    .prediction-box {{
        background-color: rgba(30, 41, 59, 0.85) !important;
        border: 1px solid #334155 !important;
        border-radius: 12px !important;
        padding: 15px !important;
        margin-bottom: 10px !important;
    }}

    /* --- PULSANTI GENERALI STREAMLIT --- */
    .stButton button {{
        background: linear-gradient(135deg, #1e3a8a 0%, #1e40af 100%) !important;
        color: #fbbf24 !important;
        font-weight: bold !important;
        border: 1px solid #38bdf8 !important;
        border-radius: 10px !important;
        padding: 0.75rem !important;
        width: 100% !important;
    }}
    .stButton button p {{
        color: #fbbf24 !important;
    }}
    .stButton button:hover {{
        background: linear-gradient(135deg, #1d4ed8 0%, #1e40af 100%) !important;
        color: #ffffff !important;
    }}

    .btn-danger button {{
        background: linear-gradient(135deg, #dc2626 0%, #991b1b 100%) !important;
        color: #ffffff !important;
        font-weight: bold !important;
        padding: 0.75rem !important;
        border-radius: 10px !important;
        border: none !important;
        width: 100% !important;
    }}
    .btn-danger button p {{
        color: #ffffff !important;
    }}
    .btn-danger button:hover {{
        background: linear-gradient(135deg, #b91c1c 0%, #7f1d1d 100%) !important;
    }}

    .btn-primary-custom button {{
        background: linear-gradient(135deg, #1e3a8a 0%, #1e40af 100%) !important;
        color: #fbbf24 !important;
        font-weight: bold !important;
        padding: 0.75rem !important;
        border-radius: 10px !important;
        border: none !important;
        width: 100% !important;
    }}
    .btn-primary-custom button p {{
        color: #fbbf24 !important;
    }}
    .btn-primary-custom button:hover {{
        background: linear-gradient(135deg, #1d4ed8 0%, #1e40af 100%) !important;
    }}

    @media (max-width: 640px) {{
        .prediction-box {{ padding: 10px !important; }}
        .big-score-input input {{ font-size: 1.8rem !important; height: 55px !important; }}
    }}
    </style>
""", unsafe_allow_html=True)

# --- HELPER FUNCTIONS ---
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

def get_url_competizione(nome_competizione):
    if not nome_competizione:
        return ""
    filename = f"comp_{nome_competizione.lower().replace(' ', '').replace('(', '').replace(')', '')}.png"
    return f"{STORAGE_BASE_URL}{filename}"

def mostra_footer():
    st.divider()
    url_logo = f"{STORAGE_BASE_URL}CUGURRAOFFICIAL.png"
    st.markdown(f"""
    <div style="text-align: center; color: #fbbf24; font-weight: bold; background-color: rgba(30, 41, 59, 0.9); padding: 15px; border-radius: 12px; border: 1px solid #334155;">
        <img src="{url_logo}" width="90" style="margin-bottom: 8px;"><br>
        <p>"Essere cugurra, esserlo nella mente"</p>
        <p style="font-size: 0.8em; color: #94a3b8;">App by Tifosi del Cagliari & Asugi</p>
    </div>
    """, unsafe_allow_html=True)

# --- GESTIONE SESSIONE ---
if "autenticato" not in st.session_state:
    st.session_state.update({
        "autenticato": False, 
        "utente_corrente": None, 
        "is_admin": False, 
        "status": None, 
        "gol_singoli": {}, 
        "gol_omologazione": {},
        "nuovo_registrato": False
    })

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
            if st.session_state.get("nuovo_registrato", False):
                st.warning("⚠️ Benvenuto nel Premio Cugurra! Prima di esaltarti troppo, faresti bene a conservare e salvare le tue credenziali: nome utente, email e PIN, scriviteli da qualche parte… che poi non abbiamo voglia di venirti in soccorso se hai la memoria corta!")
                st.markdown(f"**Utente:** `{st.session_state['reg_nome']}`")
                st.markdown(f"**Email:** `{st.session_state['reg_email']}`")
                st.markdown(f"**PIN:** `{st.session_state['reg_pin']}`")
                st.markdown("<br>", unsafe_allow_html=True)
                
                st.markdown('<div class="btn-primary-custom">', unsafe_allow_html=True)
                if st.button("Ajò a giocare"):
                    st.session_state.update({
                        "autenticato": True,
                        "utente_corrente": st.session_state["reg_nome"],
                        "status": st.session_state["reg_status"],
                        "is_admin": False,
                        "nuovo_registrato": False
                    })
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)
            else:
                new_nome = st.text_input("Nome Facebook / Utente")
                new_email = st.text_input("Indirizzo Email (fondamentale contro i cloni)")
                new_pin = st.text_input("PIN Segreto", type="password")
                if st.button("Completa Registrazione"):
                    if not new_nome or not new_email or not new_pin:
                        st.error("Compila tutti i campi inclusa l'email.")
                    else:
                        try:
                            clean_email = new_email.strip().lower()
                            clean_nome = new_nome.strip()

                            check_nome = db.table("utenti").select("nome_fb").eq("nome_fb", clean_nome).execute()
                            if check_nome.data:
                                st.warning(f"Il nome utente '{clean_nome}' è già utilizzato.")
                                st.stop()

                            check_email = db.table("utenti").select("email").eq("email", clean_email).execute()
                            if check_email.data:
                                st.warning(f"L'indirizzo email '{new_email}' risulta già registrato.")
                                st.stop()

                            nuovo_status = "TOP" if fase_attuale == "TEST" else "STANDARD"
                            db.table("utenti").insert({
                                "nome_fb": clean_nome, 
                                "email": clean_email, 
                                "pin": new_pin, 
                                "status": nuovo_status, 
                                "is_admin": False
                            }).execute()
                            
                            st.session_state["nuovo_registrato"] = True
                            st.session_state["reg_nome"] = clean_nome
                            st.session_state["reg_email"] = clean_email
                            st.session_state["reg_pin"] = new_pin
                            st.session_state["reg_status"] = nuovo_status
                            st.rerun()
                        except Exception as err:
                            err_str = str(err).lower()
                            if "unique" in err_str or "duplicate" in err_str or "already exists" in err_str:
                                st.error(f"Errore: L'indirizzo email '{new_email}' o il nome utente sono già presenti nel sistema.")
                            else:
                                st.error(f"Errore durante la registrazione: {err}")
    st.stop()

# --- BARRA LATERALE ---
st.sidebar.markdown(f"👤 Utente: **{st.session_state.get('utente_corrente')}**")
st.sidebar.markdown(f"⭐ Status: **{st.session_state.get('status')}**")
if st.session_state.get('status') == "TOP" or st.session_state.get('status') == "ADMIN":
    st.sidebar.caption("👑 *Privilegio TOP: Iscrizione automatica per le stagioni successive.*")
st.sidebar.markdown(f"📌 Stagione: **{fase_attuale}**")
if st.sidebar.button("Logout"):
    st.session_state.clear()
    st.rerun()

# --- INTERFACCIA PRINCIPALE ---
st.title(f"⚽ Premio Cugurra 2026/27 ({fase_attuale})")

if st.session_state["is_admin"]:
    tabs = st.tabs(["📝 Pronostici", "🏆 Classifiche", "📜 Regolamento", "⚙️ Admin"])
    tab_pronostici, tab_classifiche, tab_regolamento, tab_admin = tabs
else:
    tabs = st.tabs(["📝 Pronostici", "🏆 Classifiche", "📜 Regolamento"])
    tab_pronostici, tab_classifiche, tab_regolamento = tabs
    tab_admin = None

# 1. PRONOSTICI
with tab_pronostici:
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
            st.info("Nessuna partita attiva al momento per i pronostici.")
        else:
            pid = partita['id']
            casa = partita['squadra_casa']
            fuori = partita['squadra_fuori']
            comp = partita.get('competizione', 'Serie A')
            
            c_url = get_url_scudetto(casa)
            f_url = get_url_scudetto(fuori)
            comp_url = get_url_competizione(comp)
            
            st.markdown(f"""
            <div style="background-color: rgba(30, 41, 59, 0.9); padding: 20px; border-radius: 12px; border: 1px solid #334155; text-align: center; margin-bottom: 20px;">
                <p style="color: #38bdf8; font-weight: bold; font-size: 1.1em; margin-bottom: 15px;">{comp}</p>
                <table style="width: 100%; border: none; background: transparent;">
                    <tr style="background: transparent;">
                        <td style="width: 38%; text-align: center; background: transparent; border: none;">
                            <img src="{c_url}" width="80" style="margin-bottom: 8px;"><br>
                            <b style="color: #f8fafc; font-size: 1.1em;">{casa}</b>
                        </td>
                        <td style="width: 24%; text-align: center; background: transparent; border: none; vertical-align: middle;">
                            <span style="color: #fbbf24; font-size: 1.4em; font-weight: bold;">VS</span><br>
                            <img src="{comp_url}" width="40" style="margin-top: 6px;">
                        </td>
                        <td style="width: 38%; text-align: center; background: transparent; border: none;">
                            <img src="{f_url}" width="80" style="margin-bottom: 8px;"><br>
                            <b style="color: #f8fafc; font-size: 1.1em;">{fuori}</b>
                        </td>
                    </tr>
                </table>
            </div>
            """, unsafe_allow_html=True)

            try:
                esistente = db.table("pronostici").select("*").eq("partita_id", pid).eq("utente", st.session_state["utente_corrente"]).execute().data
                dati_esistenti = esistente[0] if esistente else None
            except:
                dati_esistenti = None

            val_cag = dati_esistenti['gol_casa'] if dati_esistenti else 0
            val_avv = dati_esistenti['gol_fuori'] if dati_esistenti else 0
            val_marc = dati_esistenti.get('marcatori_cagliari', '') or ''
            val_auto = dati_esistenti.get('autogol_cagliari', 0) if dati_esistenti else 0

            with st.form("form_pronostico"):
                col_g1, col_g2 = st.columns(2)
                with col_g1:
                    p_cag = st.number_input(f"Gol {casa}", min_value=0, max_value=20, value=val_cag, key="input_gol_casa")
                with col_g2:
                    p_avv = st.number_input(f"Gol {fuori}", min_value=0, max_value=20, value=val_avv, key="input_gol_fuori")
                
                p_marc = st.text_input("Marcatori del Cagliari (separati da virgola)", value=val_marc)
                p_auto = st.number_input("Autogol a favore", min_value=0, max_value=10, value=val_auto)
                
                if st.form_submit_button("Invia / Aggiorna Pronostico"):
                    payload = {
                        "partita_id": pid,
                        "utente": st.session_state["utente_corrente"],
                        "gol_casa": p_cag,
                        "gol_fuori": p_avv,
                        "marcatori_cagliari": p_marc,
                        "autogol_cagliari": p_auto
                    }
                    try:
                        if dati_esistenti:
                            db.table("pronostici").update(payload).eq("id", dati_esistenti['id']).execute()
                        else:
                            db.table("pronostici").insert(payload).execute()
                        st.success("Pronostico salvato con successo!")
                    except Exception as e:
                        st.error(f"Errore nel salvataggio: {e}")

        st.subheader("📜 I tuoi pronostici passati")
        try:
            miei_pron = db.table("pronostici").select("*, partite(*)").eq("utente", st.session_state["utente_corrente"]).execute().data
            if miei_pron:
                for mp in miei_pron:
                    p_info = mp['partite']
                    if p_info:
                        st.markdown(f"- **{p_info['squadra_casa']} vs {p_info['squadra_fuori']}** ({p_info.get('competizione','Serie A')}) | Tuo Pronostico: `{mp['gol_casa']} - {mp['gol_fuori']}` | Punti: **{mp.get('punti_generale', 0)}**")
            else:
                st.caption("Non hai ancora inserito pronostici.")
        except:
            pass

# 2. CLASSIFICHE
with tab_classifiche:
    st.subheader("🏆 Classifiche Ufficiali")
    sub_tab1, sub_tab2, sub_tab3 = st.tabs(["Generale", "Masters of Cugurras", "📜 Albo d'Oro"])
    
    with sub_tab1:
        st.markdown("### Classifica Generale")
        try:
            utenti_res = db.table("utenti").select("nome_fb").execute().data
            pron_res = db.table("pronostici").select("utente, punti_generale").execute().data
            
            classifica = {}
            for u in utenti_res:
                classifica[u['nome_fb']] = 0
            for p in pron_res:
                if p['utente'] in classifica:
                    classifica[p['utente']] += (p.get('punti_generale') or 0)
            
            df_gen = pd.DataFrame(list(classifica.items()), columns=["Utente", "Punti"]).sort_values(by="Punti", ascending=False).reset_index(drop=True)
            df_gen.index = df_gen.index + 1
            st.dataframe(df_gen, use_container_width=True)
        except Exception as e:
            st.error(f"Errore caricamento classifica: {e}")

    with sub_tab2:
        st.markdown("### Masters of Cugurras")
        try:
            pron_m = db.table("pronostici").select("utente, punti_masters").execute().data
            masters = {}
            for u in utenti_res:
                masters[u['nome_fb']] = 0
            for p in pron_m:
                if p['utente'] in masters:
                    masters[p['utente']] += (p.get('punti_masters') or 0)
            
            df_mas = pd.DataFrame(list(masters.items()), columns=["Utente", "Punti Masters"]).sort_values(by="Punti Masters", ascending=False).reset_index(drop=True)
            df_mas.index = df_mas.index + 1
            st.dataframe(df_mas, use_container_width=True)
        except Exception as e:
            st.error(f"Errore caricamento Masters: {e}")

    with sub_tab3:
        st.markdown("### 📜 Albo d'Oro")
        st.info("Qui trovi lo storico dei vincitori delle passate edizioni del Premio Cugurra.")
        try:
            albo = db.table("albo_doro").select("*").order("stagione", desc=True).execute().data
            if albo:
                df_albo = pd.DataFrame(albo)
                st.dataframe(df_albo, use_container_width=True)
            else:
                st.caption("Nessun albo d'oro inserito al momento.")
        except:
            st.caption("Tabella albo d'oro non ancora configurata nel database.")

# 3. REGOLAMENTO
with tab_regolamento:
    st.subheader("📜 Regolamento Ufficiale Premio Cugurra")
    st.markdown("""
    Benvenuti nel regolamento ufficiale del **Premio Cugurra**. Giocare è semplice, ma vincere richiede intuito e un pizzico di sana gufata sportiva.

    ### 🎯 Tabella Punteggi:
    * **15 Punti:** Risultato esatto della partita, marcatori esatti del Cagliari, eventuali autogol a favore dei rossoblu e marcatore del primo gol della partita.
    * **12 Punti:** Risultato esatto della partita, marcatori esatti del Cagliari + eventuali autogol a favore dei rossoblu, ma sbagliando il marcatore del primo gol.
    * **10 Punti:** Risultato esatto della partita e marcatori esatti del Cagliari + eventuali autogol a favore dei rossoblu.
    * **Punti Parziali:** Vengono assegnati punti extra in base all'esito corretto del match o ai singoli marcatori azzeccati secondo i criteri stabiliti dalla giuria.

    ### 👑 Status Utenti:
    * **TEST / STANDARD:** Posizione di partenza per i nuovi iscritti.
    * **TOP:** Chi mantiene lo status TOP ha l'iscrizione garantita e automatica per le stagioni successive.
    """)

# 4. ADMIN (Visibile solo agli amministratori)
if st.session_state["is_admin"] and tab_admin is not None:
    with tab_admin:
        st.subheader("⚙️ Pannello di Amministrazione")
        adm_sub1, adm_sub2, adm_sub3 = st.tabs(["Gestione Partite", "Omologazione", "Configurazione"])
        
        with adm_sub1:
            st.markdown("### Inserisci Nuova Partita")
            try:
                comp_list_res = db.table("competizioni").select("nome").execute().data
                opzioni_comp = [c['nome'] for c in comp_list_res] if comp_list_res else ["Serie A"]
            except:
                opzioni_comp = ["Serie A"]

            with st.form("form_nuova_partita"):
                c_casa = st.text_input("Squadra di Casa")
                c_fuori = st.text_input("Squadra Fuori")
                c_comp = st.selectbox("Competizione", opzioni_comp)
                c_data = st.date_input("Data Partita")
                c_ora = st.text_input("Ora (HH:MM in UTC)", value="13:00")
                
                if st.form_submit_button("Crea Partita"):
                    try:
                        dt_str = f"{c_data}T{c_ora}:00Z"
                        db.table("partite").insert({
                            "squadra_casa": c_casa.strip(),
                            "squadra_fuori": c_fuori.strip(),
                            "competizione": c_comp,
                            "data_ora": dt_str,
                            "omologata": False
                        }).execute()
                        st.success("Partita creata con successo!")
                    except Exception as e:
                        st.error(f"Errore creazione partita: {e}")

        with adm_sub2:
            st.markdown("### Omologazione Partite")
            try:
                partite_non_omologate = db.table("partite").select("*").eq("omologata", False).execute().data
                if partite_non_omologate:
                    sel_p = st.selectbox("Seleziona partita da omologare", partite_non_omologate, format_func=lambda x: f"{x['squadra_casa']} vs {x['squadra_fuori']} ({x.get('competizione','Serie A')}) - {x['data_ora']}")
                    
                    if sel_p:
                        with st.form("form_omologazione"):
                            r_casa = st.number_input("Gol effettivi Casa", min_value=0, max_value=20, value=0)
                            r_fuori = st.number_input("Gol effettivi Fuori", min_value=0, max_value=20, value=0)
                            r_marc = st.text_input("Marcatori reali Cagliari (separati da virgola)")
                            r_auto = st.number_input("Autogol reali a favore", min_value=0, max_value=10, value=0)
                            
                            if st.form_submit_button("Omologa e Calcola Punti"):
                                m_cag = [m.strip().lower() for m in r_marc.split(",") if m.strip()]
                                a_cag = int(r_auto)
                                
                                db.table("partite").update({
                                    "gol_casa_reale": r_casa,
                                    "gol_fuori_reale": r_fuori,
                                    "marcatori_reali_cagliari": r_marc,
                                    "autogol_reali_cagliari": a_cag,
                                    "omologata": True
                                }).eq("id", sel_p['id']).execute()
                                
                                pronostici_match = db.table("pronostici").select("*").eq("partita_id", sel_p['id']).execute().data
                                for pr in pronostici_match:
                                    p_cag = pr['gol_casa']
                                    p_avv = pr['gol_fuori']
                                    p_marc_cag = {m.strip().lower() for m in (pr.get('marcatori_cagliari') or '').split(",") if m.strip()}
                                    p_auto_cag = pr.get('autogol_cagliari', 0)
                                    
                                    punti_gen = 0
                                    punti_mas = 0
                                    
                                    risultato_esatto = (p_cag == r_casa and p_avv == r_fuori)
                                    
                                    if risultato_esatto and set(m_cag) == p_marc_cag and set([1]*a_cag) == set([1]*p_auto_cag):
                                        punti_gen = 10
                                        punti_masters = 10
                                    elif risultato_esatto:
                                        punti_gen = 5 
                                    
                                    db.table("pronostici").update({
                                        "punti_generale": punti_gen,
                                        "punti_masters": punti_mas
                                    }).eq("id", pr['id']).execute()
                                    
                                st.success("Partita omologata e punteggi calcolati con successo!")
                else:
                    st.info("Nessuna partita inattiva o da omologare.")
            except Exception as e:
                st.error(f"Errore durante l'omologazione: {e}")

        with adm_sub3:
            st.markdown("### Configurazione Generale App")
            fase_attuale_val = get_fase()
            nuova_fase = st.selectbox("Stato della Stagione", ["TEST", "2026/27", "ARCHIVIO"], index=["TEST", "2026/27", "ARCHIVIO"].index(fase_attuale_val) if fase_attuale_val in ["TEST", "2026/27", "ARCHIVIO"] else 0)
            if st.button("Aggiorna Fase"):
                try:
                    db.table("configurazione").update({"valore": nuova_fase}).eq("chiave", "fase_corrente").execute()
                    st.success(f"Fase aggiornata a: {nuova_fase}")
                    st.rerun()
                except Exception as e:
                    st.error(f"Errore aggiornamento fase: {e}")

# --- FOOTER FINALE ---
mostra_footer()
