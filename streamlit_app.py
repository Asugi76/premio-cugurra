import streamlit as str_lib
import pandas as pd
from supabase import create_client, Client
from datetime import datetime, timezone, timedelta
import zoneinfo
import streamlit.components.v1 as components
from collections import Counter
import extra_streamlit_components as stx

# --- FUSO ORARIO ITALIA ---
FUSO_ITALIA = zoneinfo.ZoneInfo("Europe/Rome")

# --- CONFIGURAZIONE PAGINA ---
str_lib.set_page_config(page_title="Premio Cugurra", page_icon="⚽", layout="wide")

# --- INIZIALIZZAZIONE COOKIE MANAGER (PERSISTENZA SESSIONE) ---
cookie_manager = stx.CookieManager(key="cugurra_cookie_mgr")

# --- AUTO-SCROLL IN ALTO AD OGNI RICARICAMENTO ---
components.html(
    """
    <script>
        window.parent.scrollTo(0, 0);
    </script>
    """,
    height=0,
)

# --- SUPABASE ---
SUPABASE_URL = "https://kbbxjfxltkchzvkyofdr.supabase.co"
SUPABASE_KEY = "sb_publishable_vT3i8G3_Lz8QQnDmhUqVOA_83_y_y3B"
STORAGE_BASE_URL = f"{SUPABASE_URL}/storage/v1/object/public/LOGHI_E_GRAFICHE/"
SFONDO_URL = f"{STORAGE_BASE_URL}sfondo.jpg"
DEFAULT_LOGO_URL = f"{STORAGE_BASE_URL}DEFAULT.png"

# Lista definitiva delle 10 domande segrete
LISTA_DOMANDE_SEGRETE = [
    "Qual è il nome del tuo primo animale domestico?",
    "Qual è il cognome da nubile di tua madre?",
    "Qual è il titolo del tuo libro preferito?",
    "In che città hai dato il tuo primo bacio?",
    "Qual è il nome del tuo migliore amico/a d'infanzia?",
    "Qual è il nome e cognome della tua attrice o del tuo attore preferito/a?",
    "Qual è il titolo del tuo film preferito in assoluto?",
    "In quale mese è il compleanno del tuo migliore amico/a?",
    "Qual era il tuo soprannome da bambino/a?",
    "Qual è la tua destinazione dei sogni per le vacanze?"
]

@str_lib.cache_resource
def init_supabase(): 
    return create_client(SUPABASE_URL, SUPABASE_KEY)

db = init_supabase()

# --- CSS & STILI ---
str_lib.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Press+Start+2P&display=swap');

    .stApp {{
        background: linear-gradient(rgba(18, 22, 31, 0.88), rgba(18, 22, 31, 0.95)), 
                    url('{SFONDO_URL}') no-repeat center center fixed !important;
        background-size: cover !important;
        color: #f8fafc !important;
    }}

    h1 {{ 
        color: #ffffff !important; 
        text-align: center !important; 
        white-space: nowrap !important;
        font-size: 1.8rem !important;
    }}
    
    h2, h3 {{ color: #38bdf8 !important; text-align: center; }}
    
    .single-line-title {{
        text-align: center !important;
        color: #38bdf8 !important;
        white-space: nowrap !important;
        font-size: 1.6rem !important;
        margin-bottom: 1rem !important;
    }}
    
    label, .stRadio label, .stTextInput label, .stSelectbox label, div[data-baseweb="radio"] span, div[data-baseweb="radio"] p {{
        color: #ffffff !important;
        font-weight: 600 !important;
        opacity: 1 !important;
    }}

    input, textarea, select, div[data-baseweb="select"] > div {{
        background-color: #1e293b !important;
        color: #f8fafc !important;
        border-color: #334155 !important;
    }}
    
    .stTextInput input, .stTextArea textarea {{
        color: #f8fafc !important;
        background-color: #1e293b !important;
        font-size: 16px !important;
    }}

    div[data-baseweb="select"] * {{
        color: #f8fafc !important;
        background-color: #1e293b !important;
    }}

    .stButton > button {{
        background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%) !important;
        color: #ffffff !important;
        font-weight: 700 !important;
        border: 1px solid #38bdf8 !important;
        border-radius: 10px !important;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
        transition: all 0.2s ease-in-out;
    }}
    
    .stButton > button:hover {{
        background: linear-gradient(135deg, #0369a1 0%, #075985 100%) !important;
        border-color: #7dd3fc !important;
        box-shadow: 0 6px 8px rgba(0, 0, 0, 0.4);
    }}

    div.row-widget.stRadio > div {{
        flex-direction: row;
        justify-content: center;
        gap: 8px;
        background-color: rgba(15, 23, 42, 0.95);
        padding: 10px;
        border-radius: 14px;
        border: 1px solid #334155;
        margin-bottom: 20px;
    }}
    
    div.row-widget.stRadio label {{
        background-color: #1e293b !important;
        color: #ffffff !important;
        font-weight: 700 !important;
        padding: 10px 18px !important;
        border-radius: 10px !important;
        border: 1px solid #475569 !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
        cursor: pointer;
    }}
    
    div.row-widget.stRadio label:hover {{
        border-color: #38bdf8 !important;
        background-color: #334155 !important;
    }}

    div.row-widget.stRadio input[type="radio"] {{
        display: none;
    }}

    .streamlit-expanderHeader {{
        background-color: rgba(30, 41, 59, 0.95) !important;
        border: 1px solid #334155 !important;
        border-radius: 10px !important;
        color: #38bdf8 !important;
        font-weight: 700 !important;
        font-size: 1.05rem !important;
        padding: 12px 16px !important;
        transition: all 0.2s ease-in-out;
    }}
    
    .streamlit-expanderHeader:hover {{
        border-color: #38bdf8 !important;
        background-color: rgba(51, 65, 85, 0.95) !important;
        box-shadow: 0 4px 12px rgba(56, 189, 248, 0.2);
    }}
    
    .streamlit-expanderContent {{
        background-color: rgba(15, 23, 42, 0.9) !important;
        border: 1px solid #334155 !important;
        border-top: none !important;
        border-bottom-left-radius: 10px !important;
        border-bottom-right-radius: 10px !important;
        padding: 20px !important;
    }}

    @media (max-width: 768px) {{
        h1 {{ font-size: 1.3rem !important; }}
        .single-line-title {{ font-size: 1.2rem !important; }}
    }}
    </style>
""", unsafe_allow_html=True)

# --- HELPER FUNCTIONS & LOGICA PUNTEGGI ---
def get_config_valore(chiave_target, default_val):
    try:
        res = db.table("configurazione").select("valore").eq("chiave", chiave_target).execute()
        return res.data[0]['valore'] if res.data else default_val
    except:
        return default_val

def get_fase():
    return get_config_valore("fase_corrente", "TEST")

def get_stagione():
    return get_config_valore("stagione_corrente", "2026/27")

def get_url_scudetto(nome_squadra):
    if not nome_squadra:
        return DEFAULT_LOGO_URL
    return f"{STORAGE_BASE_URL}{nome_squadra.strip().upper()}.png"

def get_url_competizione(nome_competizione):
    mapping_comp = {
        "Serie A": "comp_seriea.png", "Serie B": "comp_serieb.png",
        "Coppa Italia": "comp_coppaitalia.png", "Supercoppa Italiana": "comp_supercoppaitaliana.png",
        "Champions League": "comp_championsleague.png", "Europa League": "comp_europaleague.png",
        "Conference League": "comp_conferenceleague.png", "Mondiale per Club": "comp_mondialeclub.png",
        "Amichevole": "comp_amichevole.png", "Torneo Amichevole": "comp_torneoamichevole.png"
    }
    filename = mapping_comp.get(nome_competizione, "DEFAULT.png")
    return f"{STORAGE_BASE_URL}{filename}"

def check_limite_iscrizioni(fase_str):
    if fase_str == "TEST":
        return True
    try:
        stagione_str = get_stagione()
        parti = stagione_str.split("/")
        if len(parti) == 2:
            anno_fine = int("20" + parti[1]) if len(parti[1]) == 2 else int(parti[1])
            limite_data = datetime(anno_fine, 2, 2, 23, 59, 59, tzinfo=FUSO_ITALIA)
            if datetime.now(FUSO_ITALIA) > limite_data:
                return False
    except:
        pass
    return True

def ricalcola_punteggi_partita(id_partita):
    """
    Ricalcola e sovrascrive i punteggi di tutti gli utenti per una specifica partita
    seguendo rigorosamente la gerarchia, le esclusive e le regole del regolamento.
    """
    try:
        partita_res = db.table("partite").select("*").eq("id", id_partita).execute()
        if not partita_res.data:
            return
        partita = partita_res.data[0]
        
        res_cag = partita.get("risultato_cagliari", 0)
        res_avv = partita.get("risultato_avversario", 0)
        
        m_cag_reali = partita.get("marcatori_cagliari_reali", []) or []
        m_avv_reali = partita.get("marcatori_avversario_reali", []) or []
        a_cag_reali = partita.get("autogol_cagliari_reali", []) or []
        a_avv_reali = partita.get("autogol_avversario_reali", []) or []
        e_cag_reali = partita.get("espulsi_cagliari_reali", []) or []
        e_avv_reali = partita.get("espulsi_avversario_reali", []) or []

        reale_marc_cag_counts = Counter(filter(None, m_cag_reali))
        reale_marc_avv_counts = Counter(filter(None, m_avv_reali))
        reale_auto_cag_counts = Counter(filter(None, a_cag_reali))
        reale_auto_avv_counts = Counter(filter(None, a_avv_reali))

        pronostici_res = db.table("pronostici").select("*").eq("id_partita", id_partita).execute()
        pronostici_utenti = pronostici_res.data or []

        for pron in pronostici_utenti:
            utente = pron["utente"]
            p_cag = pron.get("gol_cagliari", 0)
            p_avv = pron.get("gol_avversario", 0)
            
            p_marc_cag_counts = Counter(filter(None, pron.get("marcatori_cagliari", []) or []))
            p_marc_avv_counts = Counter(filter(None, pron.get("marcatori_avversario", []) or []))
            p_auto_cag_counts = Counter(filter(None, pron.get("autogol_cagliari", []) or []))
            p_auto_avv_counts = Counter(filter(None, pron.get("autogol_avversario", []) or []))
            
            p_esp_cag = set(filter(None, pron.get("espulsi_cagliari", []) or []))
            p_esp_avv = set(filter(None, pron.get("espulsi_avversario", []) or []))

            punti_generale = 0
            punti_masters = 0
            punti_bomber = 0

            bonus_esp = len(p_esp_cag.intersection(set(e_cag_reali))) + len(p_esp_avv.intersection(set(e_avv_reali)))

            if p_cag == 0 and res_cag == 0 and p_avv == 0 and res_avv == 0:
                punti_generale = 8
            else:
                risultato_esatto = (p_cag == res_cag and p_avv == res_avv)
                marcatori_esatti_tutti = (
                    p_marc_cag_counts == reale_marc_cag_counts and 
                    p_marc_avv_counts == reale_marc_avv_counts and 
                    p_auto_cag_counts == reale_auto_cag_counts and 
                    p_auto_avv_counts == reale_auto_avv_counts
                )
                
                if risultato_esatto and marcatori_esatti_tutti:
                    punti_generale = 15
                elif risultato_esatto and p_marc_cag_counts == reale_marc_cag_counts and p_auto_cag_counts == reale_auto_cag_counts:
                    punti_generale = 10
                    punti_masters = 10
                elif (p_cag > p_avv and res_cag > res_avv) or (p_cag < p_avv and res_cag < res_avv) or (p_cag == p_avv and res_cag == res_avv):
                    punti_generale = 5
                elif p_marc_cag_counts == reale_marc_cag_counts and p_auto_cag_counts == reale_auto_cag_counts and len(p_marc_cag_counts) > 0:
                    punti_generale = 3
                else:
                    punti_generale = 0

            punti_generale += bonus_esp

            for giocatore, gol_pred in p_marc_cag_counts.items():
                if giocatore in reale_marc_cag_counts and reale_marc_cag_counts[giocatore] > 0:
                    punti_bomber += 1
                    if gol_pred == reale_marc_cag_counts[giocatore]:
                        punti_bomber += reale_marc_cag_counts[giocatore]

            db.table("punteggi_partita").upsert({
                "id_partita": id_partita, 
                "utente": utente,
                "punti_generale": punti_generale, 
                "punti_masters": punti_masters,
                "punti_bomber": punti_bomber
            }, on_conflict="id_partita, utente").execute()
    except Exception as e:
        str_lib.error(f"Errore durante il ricalcolo dei punteggi: {e}")

def mostra_footer():
    str_lib.divider()
    url_logo = f"{STORAGE_BASE_URL}CUGURRAOFFICIAL.png"
    str_lib.markdown(f"""
    <div style="text-align: center; color: #fbbf24; font-weight: bold; background-color: rgba(30, 41, 59, 0.9); padding: 15px; border-radius: 12px; border: 1px solid #334155;">
        <img src="{url_logo}" width="90" onerror="this.src='{DEFAULT_LOGO_URL}'" style="margin-bottom: 8px;"><br>
        <p>"Essere cugurra, esserlo nella mente"</p>
        <p style="font-size: 0.8em; color: #94a3b8;">App by Tifosi del Cagliari & Asugi</p>
    </div>
    """, unsafe_allow_html=True)

# --- GESTIONE SESSIONE & RIPRISTINO COOKIE ---
if "autenticato" not in str_lib.session_state:
    str_lib.session_state.update({
        "autenticato": False, "utente_corrente": None, "is_admin": False, "status": None, 
        "gol_singoli": {}, "gol_omologazione": {}, "nuovo_registrato": False, "modalita_auth": None,
        "in_modifica_pronostico": False
    })

auth_cookie = cookie_manager.get("cugurra_auth_session")
if auth_cookie and not str_lib.session_state["autenticato"]:
    if isinstance(auth_cookie, dict) and "utente_corrente" in auth_cookie:
        str_lib.session_state.update({
            "autenticato": True,
            "utente_corrente": auth_cookie.get("utente_corrente"),
            "is_admin": auth_cookie.get("is_admin", False),
            "status": auth_cookie.get("status", "STANDARD")
        })

fase_attuale = get_fase()
stagione_attuale = get_stagione()

# --- LOGIN / REGISTRAZIONE / RECUPERA PIN ---
if not str_lib.session_state["autenticato"]:
    str_lib.markdown("<h1>⚽️ PREMIO CUGURRA ⚽️</h1>", unsafe_allow_html=True)
    str_lib.markdown(f"<h3 style='text-align: center; color: #fbbf24; margin-top: 5px; margin-bottom: 25px;'>Stagione {stagione_attuale} - {fase_attuale}</h3>", unsafe_allow_html=True)
    
    col_scelta1, col_scelta2 = str_lib.columns(2)
    with col_scelta1:
        if str_lib.button("ACCEDI", key="btn_switch_accedi", use_container_width=True):
            str_lib.session_state["modalita_auth"] = "Accedi"
            str_lib.rerun()
    with col_scelta2:
        if str_lib.button("REGISTRATI / RECUPERA PIN", key="btn_switch_registrati", use_container_width=True):
            str_lib.session_state["modalita_auth"] = "Registrati"
            str_lib.rerun()
            
    str_lib.markdown("<br>", unsafe_allow_html=True)
    
    if str_lib.session_state["modalita_auth"] == "Accedi":
        col_l1, _ = str_lib.columns([2, 1])
        with col_l1:
            str_lib.subheader("Accedi al tuo account")
            nome_inserito = str_lib.text_input("Nome Utente Facebook", help="Inserisci nome e cognome come appare su Facebook")
            pin_inserito = str_lib.text_input("PIN personale (4 cifre)", type="password", max_chars=4)
            risposta_inserita = str_lib.text_input("Risposta alla tua Domanda Segreta", type="password", help="Inserisci la risposta segreta scelta in fase di registrazione")
            
            str_lib.markdown("<br>", unsafe_allow_html=True)
            if str_lib.button("Ajò a giocare", key="btn_submit_accedi", use_container_width=True):
                clean_nome = nome_inserito.strip() if nome_inserito else ""
                clean_pin = pin_inserito.strip() if pin_inserito else ""
                clean_risposta = risposta_inserita.strip().lower() if risposta_inserita else ""

                if not clean_nome or not clean_pin or not clean_risposta:
                    str_lib.error("Inserisci Nome Utente, PIN e Risposta alla Domanda Segreta per accedere.")
                elif len(clean_pin) != 4 or not clean_pin.isdigit():
                    str_lib.error("⚠️ Il PIN deve essere composto **esattamente da 4 cifre numeriche**.")
                else:
                    try:
                        res = db.table("utenti").select("*").eq("nome_fb", clean_nome).eq("pin", clean_pin).execute()
                        if res.data:
                            u = res.data[0]
                            risposta_db = (u.get("risposta_segreta") or "").strip().lower()
                            
                            if risposta_db and risposta_db != clean_risposta:
                                str_lib.error("Risposta alla Domanda Segreta non corretta.")
                            else:
                                session_info = {
                                    "utente_corrente": u["nome_fb"], 
                                    "is_admin": u.get('is_admin', False), 
                                    "status": u.get('status', 'STANDARD')
                                }
                                str_lib.session_state.update({
                                    "autenticato": True, "utente_corrente": session_info["utente_corrente"], 
                                    "is_admin": session_info["is_admin"], "status": session_info["status"]
                                })
                                cookie_manager.set(
                                    cookie="cugurra_auth_session",
                                    val=session_info,
                                    expires_at=datetime.now(FUSO_ITALIA) + timedelta(hours=1)
                                )
                                str_lib.rerun()
                        else:
                            str_lib.error("Nome Utente o PIN non corretti. Verifica di non aver inserito spazi extra.")
                    except Exception as e:
                        str_lib.error(f"Errore di connessione: {e}")

    elif str_lib.session_state["modalita_auth"] == "Registrati":
        tab_reg, tab_rec = str_lib.tabs(["📝 Nuova Registrazione", "🔑 Recupera / Modifica PIN"])
        
        with tab_reg:
            col_r1, _ = str_lib.columns([2, 1])
            with col_r1:
                if not check_limite_iscrizioni(fase_attuale):
                    str_lib.error("❌ Le iscrizioni per la stagione in corso sono chiuse. Il termine ultimo era fissato al 2 febbraio.")
                elif str_lib.session_state.get("nuovo_registrato", False):
                    str_lib.warning("⚠️ Benvenuto nel Premio Cugurra! Conserva le tue credenziali d'accesso:")
                    str_lib.markdown(f"**Utente:** `{str_lib.session_state['reg_nome']}`")
                    str_lib.markdown(f"**Email:** `{str_lib.session_state['reg_email']}`")
                    str_lib.markdown(f"**PIN:** `{str_lib.session_state['reg_pin']}`")
                    str_lib.markdown(f"**Domanda Segreta:** `{str_lib.session_state['reg_domanda']}`")
                    str_lib.markdown(f"**Risposta Segreta:** `{str_lib.session_state['reg_risposta']}`")
                    str_lib.markdown("<br>", unsafe_allow_html=True)
                    
                    if str_lib.button("Ajò a giocare", key="btn_ajo_giocare", use_container_width=True):
                        session_info = {
                            "utente_corrente": str_lib.session_state["reg_nome"],
                            "is_admin": False,
                            "status": str_lib.session_state["reg_status"]
                        }
                        str_lib.session_state.update({
                            "autenticato": True, "utente_corrente": session_info["utente_corrente"],
                            "status": session_info["status"], "is_admin": False, "nuovo_registrato": False
                        })
                        cookie_manager.set(
                            cookie="cugurra_auth_session",
                            val=session_info,
                            expires_at=datetime.now(FUSO_ITALIA) + timedelta(hours=1)
                        )
                        str_lib.rerun()
                else:
                    new_nome = str_lib.text_input("Nome Utente Facebook", help="Inserisci il tuo nome e cognome esattamente come lo si legge su Facebook")
                    new_email = str_lib.text_input("Indirizzo Email", help="La tua email verrà utilizzata solo per emergenze")
                    new_pin = str_lib.text_input("PIN personale (esattamente 4 cifre)", type="password", max_chars=4)
                    
                    str_lib.markdown("---")
                    str_lib.markdown("##### 🔒 Domanda e Risposta Segreta")
                    domanda_scelta = str_lib.selectbox("Scegli una Domanda Segreta", LISTA_DOMANDE_SEGRETE)
                    risposta_scelta = str_lib.text_input("Risposta alla Domanda Segreta")

                    str_lib.markdown("<br>", unsafe_allow_html=True)
                    if str_lib.button("Completa Registrazione", key="btn_submit_registrazione", use_container_width=True):
                        clean_pin = new_pin.strip() if new_pin else ""
                        clean_risposta = risposta_scelta.strip() if risposta_scelta else ""

                        if not new_nome or not new_email or not clean_pin or not clean_risposta:
                            str_lib.error("Compila tutti i campi.")
                        elif not clean_pin.isdigit() or len(clean_pin) != 4:
                            str_lib.error("⚠️ Il PIN deve essere composto **esattamente da 4 cifre numeriche**.")
                        else:
                            try:
                                clean_email = new_email.strip().lower()
                                clean_nome = new_nome.strip()

                                check_nome = db.table("utenti").select("nome_fb").eq("nome_fb", clean_nome).execute()
                                if check_nome.data:
                                    str_lib.warning(f"Il nome utente '{clean_nome}' è già utilizzato.")
                                    str_lib.stop()

                                check_email = db.table("utenti").select("email").eq("email", clean_email).execute()
                                if check_email.data:
                                    str_lib.warning(f"L'indirizzo email '{new_email}' risulta già registrato.")
                                    str_lib.stop()

                                nuovo_status = "TOP" if fase_attuale == "TEST" else "STANDARD"
                                db.table("utenti").insert({
                                    "nome_fb": clean_nome, "email": clean_email, "pin": clean_pin, 
                                    "domanda_segreta": domanda_scelta, "risposta_segreta": clean_risposta,
                                    "status": nuovo_status, "is_admin": False
                                }).execute()
                                
                                str_lib.session_state["nuovo_registrato"] = True
                                str_lib.session_state["reg_nome"] = clean_nome
                                str_lib.session_state["reg_email"] = clean_email
                                str_lib.session_state["reg_pin"] = clean_pin
                                str_lib.session_state["reg_domanda"] = domanda_scelta
                                str_lib.session_state["reg_risposta"] = clean_risposta
                                str_lib.session_state["reg_status"] = nuovo_status
                                str_lib.rerun()
                            except Exception as err:
                                str_lib.error(f"Errore durante la registrazione: {err}")

        with tab_rec:
            col_rec1, _ = str_lib.columns([2, 1])
            with col_rec1:
                str_lib.subheader("Recupera o reimposta il tuo PIN")
                rec_nome = str_lib.text_input("Nome Utente Facebook (registrato)", key="rec_nome")
                rec_email = str_lib.text_input("Email (registrata)", key="rec_email")
                
                if str_lib.button("Cerca Account", key="btn_cerca_acc", use_container_width=True):
                    if not rec_nome or not rec_email:
                        str_lib.error("Inserisci Nome Utente ed Email.")
                    else:
                        try:
                            res_rec = db.table("utenti").select("*").eq("nome_fb", rec_nome.strip()).eq("email", rec_email.strip().lower()).execute()
                            if res_rec.data:
                                str_lib.session_state["rec_user_found"] = res_rec.data[0]
                                str_lib.success("Account trovato!")
                            else:
                                str_lib.error("Nessun account trovato.")
                        except Exception as e:
                            str_lib.error(f"Errore durante la ricerca: {e}")

                if "rec_user_found" in str_lib.session_state:
                    u_found = str_lib.session_state["rec_user_found"]
                    domanda_u = u_found.get("domanda_segreta", "Qual è la tua risposta segreta?")
                    
                    str_lib.markdown("---")
                    str_lib.info(f"**Domanda Segreta:** {domanda_u}")
                    ans_check = str_lib.text_input("La tua Risposta Segreta", key="ans_check")
                    new_pin_reset = str_lib.text_input("Nuovo PIN (4 cifre)", type="password", max_chars=4, key="new_pin_reset")

                    if str_lib.button("Reimposta PIN", key="btn_do_reset", use_container_width=True):
                        clean_ans = ans_check.strip().lower() if ans_check else ""
                        clean_new_pin = new_pin_reset.strip() if new_pin_reset else ""
                        db_ans = (u_found.get("risposta_segreta") or "").strip().lower()

                        if clean_ans != db_ans:
                            str_lib.error("Risposta segreta errata.")
                        elif not clean_new_pin.isdigit() or len(clean_new_pin) != 4:
                            str_lib.error("Il PIN deve essere di 4 cifre numeriche.")
                        else:
                            try:
                                db.table("utenti").update({"pin": clean_new_pin}).eq("nome_fb", u_found["nome_fb"]).execute()
                                str_lib.success("PIN aggiornato con successo!")
                                del str_lib.session_state["rec_user_found"]
                            except Exception as ex_u:
                                str_lib.error(f"Errore: {ex_u}")
    str_lib.stop()

# --- BARRA LATERALE ---
str_lib.sidebar.markdown(f"👤 Utente: **{str_lib.session_state.get('utente_corrente')}**")
str_lib.sidebar.markdown(f"⭐ Status: **{str_lib.session_state.get('status')}**")

if str_lib.sidebar.button("Logout", key="sidebar_logout_btn", use_container_width=True):
    try:
        cookie_manager.delete("cugurra_auth_session")
    except Exception:
        pass
    str_lib.session_state.clear()
    str_lib.rerun()

# --- INTERFACCIA PRINCIPALE ---
str_lib.markdown(f"<h1>⚽ Premio Cugurra {stagione_attuale} ({fase_attuale})</h1>", unsafe_allow_html=True)

# --- NAVIGAZIONE ---
if str_lib.session_state["is_admin"]:
    menu_options = ["⚙️ Gestione Admin", "📝 Pronostici", "🏆 Classifiche", "📜 Regolamento"]
else:
    menu_options = ["📝 Pronostici", "🏆 Classifiche", "📜 Regolamento"]

selected_tab = str_lib.radio(
    "Navigazione Principale",
    options=menu_options,
    label_visibility="collapsed",
    horizontal=True
)

str_lib.write("") 

tab_admin = selected_tab if selected_tab == "⚙️ Gestione Admin" else None
is_pronostici = (selected_tab == "📝 Pronostici")
is_classifiche = (selected_tab == "🏆 Classifiche")
is_regolamento = (selected_tab == "📜 Regolamento")

# 1. PRONOSTICI
if is_pronostici:
    if fase_attuale == "ARCHIVIO":
        str_lib.warning("Stagione in archivio. Pronostici disabilitati.")
    else:
        try:
            partite_db = db.table("partite").select("*").order("data_ora").execute().data
        except:
            partite_db = []

        now_italia = datetime.now(FUSO_ITALIA)
        
        partite_future = []
        for p in partite_db:
            if not p.get('omologata', False):
                raw_dt = p['data_ora'].replace("Z", "")
                dt_p = datetime.fromisoformat(raw_dt)
                if dt_p.tzinfo is None:
                    dt_p = dt_p.replace(tzinfo=FUSO_ITALIA)
                else:
                    dt_p = dt_p.astimezone(FUSO_ITALIA)
                if dt_p > now_italia:
                    partite_future.append((dt_p, p))

        partita_tuple = partite_future[0] if partite_future else None
        
        if not partita_tuple:
            str_lib.info("Nessuna partita disponibile per il pronostico in questo momento.")
        else:
            dt_partita, partita = partita_tuple
            iso_timestamp = dt_partita.isoformat()
            
            match_iniziato = now_italia >= dt_partita

            campo_val = partita.get('campo') or partita.get('casa_trasferta') or 'Casa'
            is_cagliari_left = campo_val in ["Casa", "Campo Neutro"]
            squadra_1 = "CAGLIARI" if is_cagliari_left else partita['avversario']
            squadra_2 = partita['avversario'] if is_cagliari_left else "CAGLIARI"
            nome_competizione = partita.get('competizione', 'Serie A')

            pronostico_esistente = None
            try:
                res_pron = db.table("pronostici").select("*").eq("id_partita", partita['id']).eq("utente", str_lib.session_state["utente_corrente"]).execute()
                if res_pron.data:
                    pronostico_esistente = res_pron.data[0]
            except:
                pronostico_esistente = None

            if pronostico_esistente and not str_lib.session_state.get(f"loaded_counts_{partita['id']}", False):
                for key_pref, is_left in [("s1", is_cagliari_left), ("s2", not is_cagliari_left)]:
                    key_m = "marcatori_cagliari" if is_left else "marcatori_avversario"
                    key_a = "autogol_cagliari" if is_left else "autogol_avversario"
                    
                    m_list = pronostico_esistente.get(key_m, []) or []
                    a_list = pronostico_esistente.get(key_a, []) or []
                    
                    c_m = Counter([x for x in m_list if x])
                    for m_name, count in c_m.items():
                        str_lib.session_state.gol_singoli[f"g_{key_pref}_{m_name}_{partita['id']}"] = count
                        
                    c_a = Counter([x for x in a_list if x])
                    for a_name, count in c_a.items():
                        str_lib.session_state.gol_singoli[f"auto_{key_pref}_{a_name}_{partita['id']}"] = count
                        
                str_lib.session_state[f"loaded_counts_{partita['id']}"] = True

            str_lib.markdown(f"""
                <div style="text-align: center; line-height: 1.6; margin-bottom: 20px;">
                    Prossima partita:<br>
                    <span style="color: #fbbf24; font-weight: bold; font-size: 1.2rem;">{squadra_1} vs {squadra_2}, {nome_competizione}</span><br>
                    {dt_partita.strftime('%d/%m/%Y ore %H:%M')}
                </div>
            """, unsafe_allow_html=True)
            
            if match_iniziato:
                str_lib.error("🔒 I pronostici per questa partita sono CHIUSI. Il match è già iniziato.")
            
            if pronostico_esistente:
                p_s1 = pronostico_esistente.get("gol_cagliari" if is_cagliari_left else "gol_avversario", 0)
                p_s2 = pronostico_esistente.get("gol_avversario" if is_cagliari_left else "gol_cagliari", 0)
                
                m1_list = [x for x in (pronostico_esistente.get("marcatori_cagliari" if is_cagliari_left else "marcatori_avversario", []) or []) if x]
                m2_list = [x for x in (pronostico_esistente.get("marcatori_avversario" if is_cagliari_left else "marcatori_cagliari", []) or []) if x]
                
                a1_list = [x for x in (pronostico_esistente.get("autogol_cagliari" if is_cagliari_left else "autogol_avversario", []) or []) if x]
                a2_list = [x for x in (pronostico_esistente.get("autogol_avversario" if is_cagliari_left else "autogol_cagliari", []) or []) if x]
                
                e1_list = [x for x in (pronostico_esistente.get("espulsi_cagliari" if is_cagliari_left else "espulsi_avversario", []) or []) if x]
                e2_list = [x for x in (pronostico_esistente.get("espulsi_avversario" if is_cagliari_left else "espulsi_cagliari", []) or []) if x]
                
                def fmt_dettagli(m_l, a_l):
                    res = []
                    if m_l:
                        c_m = Counter(m_l)
                        res.append("Marcatori: " + ", ".join([f"{k} ({v})" if v > 1 else k for k, v in c_m.items()]))
                    if a_l:
                        c_a = Counter(a_l)
                        res.append("Autogol a favore: " + ", ".join([f"{k} ({v})" if v > 1 else k for k, v in c_a.items()]))
                    return " | ".join(res) if res else "Nessun marcatore/autogol"

                det_s1 = fmt_dettagli(m1_list, a1_list)
                det_s2 = fmt_dettagli(m2_list, a2_list)
                det_esp1 = f"Espulsi: {', '.join(e1_list)}" if e1_list else "Nessun espulso"
                det_esp2 = f"Espulsi: {', '.join(e2_list)}" if e2_list else "Nessun espulso"

                str_lib.success(f"""
                📌 **IL TUO PRONOSTICO ATTUALE:**
                * **Risultato:** {squadra_1} {p_s1} - {p_s2} {squadra_2}
                * **{squadra_1}:** {det_s1} ({det_esp1})
                * **{squadra_2}:** {det_s2} ({det_esp2})
                """)

                col_mod_btn1, _ = str_lib.columns([2, 1])
                with col_mod_btn1:
                    if not match_iniziato:
                        if not str_lib.session_state.get("in_modifica_pronostico", False):
                            if str_lib.button("✏️ Modifica il tuo pronostico", key="btn_enable_edit", use_container_width=True):
                                str_lib.session_state["in_modifica_pronostico"] = True
                                str_lib.rerun()
                        else:
                            str_lib.info("⚠️ Modalità modifica attiva.")
            else:
                str_lib.session_state["in_modifica_pronostico"] = True

            can_edit = (not match_iniziato) and str_lib.session_state.get("in_modifica_pronostico", False)
            
            countdown_html = f"""
            <div style="background-color: #090d16; border: 2px solid #38bdf8; border-radius: 12px; padding: 12px; text-align: center; font-family: 'Press Start 2P', monospace; box-shadow: 0 0 12px rgba(56, 189, 248, 0.3);">
                <div class="pulsing-clock">
                    <div style="font-size: 0.7rem; color: #38bdf8; margin-bottom: 6px; text-transform: uppercase;">⏳ AL FISCHIO D'INIZIO MANCANO ⏳</div>
                    <div id="clock" style="font-size: 1.1rem; color: #fbbf24; text-shadow: 0 0 6px rgba(251, 191, 36, 0.5);">CALCOLO...</div>
                </div>
            </div>
            <script>
                const targetStr = "{iso_timestamp}";
                const targetDate = new Date(targetStr).getTime();
                function updateTimer() {{
                    const nowTime = new Date().getTime();
                    const diff = targetDate - nowTime;
                    if (diff <= 0) {{
                        document.getElementById("clock").innerHTML = "IN CORSO / TERMINATA";
                        return;
                    }}
                    const days = Math.floor(diff / (1000 * 60 * 60 * 24));
                    const hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
                    const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
                    let res = "";
                    if (days > 0) res += days + "g ";
                    res += String(hours).padStart(2, '0') + "h " + String(minutes).padStart(2, '0') + "m";
                    document.getElementById("clock").innerHTML = res;
                }}
                updateTimer();
                setInterval(updateTimer, 1000);
            </script>
            """
            components.html(countdown_html, height=100)
            
            url_comp = get_url_competizione(nome_competizione)
            url_s1 = get_url_scudetto(squadra_1)
            url_s2 = get_url_scudetto(squadra_2)

            str_lib.markdown(f"""
                <div style="display: flex; justify-content: center; align-items: center; margin-top: 15px; margin-bottom: 10px;">
                    <img src="{url_comp}" width="48" onerror="this.src='{DEFAULT_LOGO_URL}'" style="display: block;">
                </div>
            """, unsafe_allow_html=True)

            col_id_1 = f"gs1_{partita['id']}"
            col_id_2 = f"gs2_{partita['id']}"

            if col_id_1 not in str_lib.session_state: 
                val_init_1 = pronostico_esistente.get("gol_cagliari" if is_cagliari_left else "gol_avversario", 0) if pronostico_esistente else 0
                str_lib.session_state[col_id_1] = val_init_1
            if col_id_2 not in str_lib.session_state: 
                val_init_2 = pronostico_esistente.get("gol_avversario" if is_cagliari_left else "gol_cagliari", 0) if pronostico_esistente else 0
                str_lib.session_state[col_id_2] = val_init_2

            col_squadra_1, col_squadra_2 = str_lib.columns(2)

            with col_squadra_1:
                str_lib.markdown(f"""
                    <div style="text-align: center; margin-bottom: 5px;">
                        <img src="{url_s1}" width="60" onerror="this.src='{DEFAULT_LOGO_URL}'" style="display: block; margin: 0 auto 8px auto;">
                        <div style="font-size: 0.85rem; color: #94a3b8; font-weight: 600; margin-bottom: 4px;">Inserisci gol {squadra_1}</div>
                    </div>
                """, unsafe_allow_html=True)
                gol_s1 = str_lib.number_input(f"Inserisci gol {squadra_1}", min_value=0, value=str_lib.session_state[col_id_1], key=col_id_1, label_visibility="collapsed", disabled=not can_edit)

            with col_squadra_2:
                str_lib.markdown(f"""
                    <div style="text-align: center; margin-bottom: 5px;">
                        <img src="{url_s2}" width="60" onerror="this.src='{DEFAULT_LOGO_URL}'" style="display: block; margin: 0 auto 8px auto;">
                        <div style="font-size: 0.85rem; color: #94a3b8; font-weight: 600; margin-bottom: 4px;">Inserisci gol {squadra_2}</div>
                    </div>
                """, unsafe_allow_html=True)
                gol_s2 = str_lib.number_input(f"Inserisci gol {squadra_2}", min_value=0, value=str_lib.session_state[col_id_2], key=col_id_2, label_visibility="collapsed", disabled=not can_edit)

            str_lib.markdown("---")
            rosa_cag = [x.strip() for x in (partita.get("rosa_cagliari") or "").split(",") if x.strip()]
            rosa_avv = [x.strip() for x in (partita.get("rosa_avversaria") or "").split(",") if x.strip()]
            rosa_1 = rosa_cag if is_cagliari_left else rosa_avv
            rosa_2 = rosa_avv if is_cagliari_left else rosa_cag

            def render_team_section(team_name, lista_rosa, lista_opp, key_pref, gol_team_totali):
                str_lib.markdown(f"### {team_name}")
                marcatori = []
                autogol = []
                
                if gol_team_totali == 0:
                    str_lib.info("0 Gol inseriti: sezione marcatori ed autogol nascosta.")
                else:
                    def_marc = []
                    if pronostico_esistente:
                        raw_marc = pronostico_esistente.get("marcatori_cagliari" if (is_cagliari_left and key_pref=="s1") or (not is_cagliari_left and key_pref=="s2") else "marcatori_avversario", []) or []
                        def_marc = [m for m in raw_marc if m]
                    marcatori = str_lib.multiselect(f"Marcatori {team_name}", options=lista_rosa, default=list(dict.fromkeys([m for m in def_marc if m in lista_rosa])), key=f"m_{key_pref}_{partita['id']}", disabled=not can_edit)
                    for m in marcatori:
                        k = f"g_{key_pref}_{m}_{partita['id']}"
                        str_lib.session_state.gol_singoli[k] = str_lib.number_input(f"Gol di {m}", 1, 50, str_lib.session_state.gol_singoli.get(k, 1), key=k, disabled=not can_edit)

                    def_auto = []
                    if pronostico_esistente:
                        raw_auto = pronostico_esistente.get("autogol_cagliari" if (is_cagliari_left and key_pref=="s1") or (not is_cagliari_left and key_pref=="s2") else "autogol_avversario", []) or []
                        def_auto = [a for a in raw_auto if a]
                    autogol = str_lib.multiselect(f"Autogol a favore ({team_name})", options=lista_opp, default=list(dict.fromkeys([a for a in def_auto if a in lista_opp])), key=f"a_{key_pref}_{partita['id']}", disabled=not can_edit)
                    for a in autogol:
                        k = f"auto_{key_pref}_{a}_{partita['id']}"
                        str_lib.session_state.gol_singoli[k] = str_lib.number_input(f"Autogol di {a}", 1, 50, str_lib.session_state.gol_singoli.get(k, 1), key=k, disabled=not can_edit)
                
                def_esp = []
                if pronostico_esistente:
                    raw_esp = pronostico_esistente.get("espulsi_cagliari" if (is_cagliari_left and key_pref=="s1") or (not is_cagliari_left and key_pref=="s2") else "espulsi_avversario", []) or []
                    def_esp = [e for e in raw_esp if e]
                espulsi = str_lib.multiselect(f"Espulsi ({team_name})", options=lista_rosa, default=[e for e in def_esp if e in lista_rosa], max_selections=3, key=f"e_{key_pref}_{partita['id']}", disabled=not can_edit)
                return marcatori, autogol, espulsi

            col_tab1, col_tab2 = str_lib.columns(2)
            with col_tab1: marc1, auto1, esp1 = render_team_section(squadra_1, rosa_1, rosa_2, "s1", gol_s1)
            with col_tab2: marc2, auto2, esp2 = render_team_section(squadra_2, rosa_2, rosa_1, "s2", gol_s2)

            str_lib.markdown("<br>", unsafe_allow_html=True)
            
            btn_label = "Convalida Modifiche" if pronostico_esistente else "Invia Pronostico"
            if str_lib.button(btn_label, key="btn_invia_pronostico", use_container_width=True, disabled=not can_edit):
                tot_gol_s1_calcolati = 0
                for m in marc1:
                    tot_gol_s1_calcolati += str_lib.session_state.gol_singoli.get(f"g_s1_{m}_{partita['id']}", 1)
                for a in auto1:
                    tot_gol_s1_calcolati += str_lib.session_state.gol_singoli.get(f"auto_s1_{a}_{partita['id']}", 1)

                tot_gol_s2_calcolati = 0
                for m in marc2:
                    tot_gol_s2_calcolati += str_lib.session_state.gol_singoli.get(f"g_s2_{m}_{partita['id']}", 1)
                for a in auto2:
                    tot_gol_s2_calcolati += str_lib.session_state.gol_singoli.get(f"auto_s2_{a}_{partita['id']}", 1)

                errore_coerenza = False
                if tot_gol_s1_calcolati != gol_s1:
                    str_lib.error(f"Errore per {squadra_1}: inseriti {gol_s1} gol totali, ma la somma calcolata è {tot_gol_s1_calcolati}.")
                    errore_coerenza = True
                if tot_gol_s2_calcolati != gol_s2:
                    str_lib.error(f"Errore per {squadra_2}: inseriti {gol_s2} gol totali, ma la somma calcolata è {tot_gol_s2_calcolati}.")
                    errore_coerenza = True

                if not errore_coerenza:
                    marc1_expanded = []
                    for m in marc1:
                        cnt = str_lib.session_state.gol_singoli.get(f"g_s1_{m}_{partita['id']}", 1)
                        marc1_expanded.extend([m] * cnt)

                    auto1_expanded = []
                    for a in auto1:
                        cnt = str_lib.session_state.gol_singoli.get(f"auto_s1_{a}_{partita['id']}", 1)
                        auto1_expanded.extend([a] * cnt)

                    marc2_expanded = []
                    for m in marc2:
                        cnt = str_lib.session_state.gol_singoli.get(f"g_s2_{m}_{partita['id']}", 1)
                        marc2_expanded.extend([m] * cnt)

                    auto2_expanded = []
                    for a in auto2:
                        cnt = str_lib.session_state.gol_singoli.get(f"auto_s2_{a}_{partita['id']}", 1)
                        auto2_expanded.extend([a] * cnt)

                    if is_cagliari_left:
                        gol_cag, gol_avv = gol_s1, gol_s2
                        marc_cag, marc_avv = marc1_expanded, marc2_expanded
                        auto_cag, auto_avv = auto1_expanded, auto2_expanded
                        esp_cag, esp_avv = esp1, esp2
                    else:
                        gol_cag, gol_avv = gol_s2, gol_s1
                        marc_cag, marc_avv = marc2_expanded, marc1_expanded
                        auto_cag, auto_avv = auto2_expanded, auto1_expanded
                        esp_cag, esp_avv = esp2, esp1

                    try:
                        db.table("pronostici").upsert(
                            {
                                "id_partita": partita['id'], 
                                "utente": str_lib.session_state["utente_corrente"],
                                "gol_cagliari": gol_cag, 
                                "gol_avversario": gol_avv,
                                "marcatori_cagliari": marc_cag, 
                                "marcatori_avversario": marc_avv,
                                "autogol_cagliari": auto_cag, 
                                "autogol_avversario": auto_avv,
                                "espulsi_cagliari": esp_cag, 
                                "espulsi_avversario": esp_avv
                            },
                            on_conflict="id_partita, utente"
                        ).execute()
                        str_lib.session_state["in_modifica_pronostico"] = False
                        str_lib.success("Pronostico registrato con successo!")
                        str_lib.rerun()
                    except Exception as db_err:
                        str_lib.error(f"Errore durante l'inserimento su Supabase: {db_err}")

# 2. CLASSIFICHE
elif is_classifiche:
    str_lib.markdown("<h2 class='single-line-title'>🏆 Classifiche Ufficiali 🏆</h2>", unsafe_allow_html=True)
    sub_tab1, sub_tab2, sub_tab3, sub_tab4 = str_lib.tabs(["Classifica Generale", "Masters of Cugurras", "Bomber di razza", "Albo d'Oro"])
    
    try:
        punteggi_data = db.table("punteggi_partita").select("*").execute().data
        pronostici_data = db.table("pronostici").select("*").execute().data
    except Exception as e:
        punteggi_data = []
        pronostici_data = []

    df_punteggi = pd.DataFrame(punteggi_data)
    df_pronostici = pd.DataFrame(pronostici_data)

    if not df_punteggi.empty and not df_pronostici.empty:
        partita_counts = df_pronostici.groupby("utente")["id_partita"].nunique().reset_index()
        partita_counts.columns = ["utente", "Partite Giocate"]
    else:
        partita_counts = pd.DataFrame(columns=["utente", "Partite Giocate"])

    with sub_tab1:
        if df_punteggi.empty:
            str_lib.info("In attesa delle prime partite omologate per la classifica generale.")
        else:
            gen_df = df_punteggi.groupby("utente")["punti_generale"].sum().reset_index()
            gen_df = pd.merge(gen_df, partita_counts, on="utente", how="left").fillna(0)
            gen_df["Partite Giocate"] = gen_df["Partite Giocate"].astype(int)
            gen_df = gen_df.sort_values(by=["punti_generale", "Partite Giocate"], ascending=[False, False])
            gen_df.columns = ["Utente", "Punti Totali", "Partite Giocate"]
            str_lib.dataframe(gen_df, use_container_width=True, hide_index=True)

    with sub_tab2:
        if df_punteggi.empty:
            str_lib.info("Classifica Masters of Cugurras vuota.")
        else:
            # CORRETTO: somma effettiva dei punti Masters anziché fare il .count() delle occorrenze
            masters_df = df_punteggi.groupby("utente")["punti_masters"].sum().reset_index()
            masters_df = pd.merge(masters_df, partita_counts, on="utente", how="left").fillna(0)
            masters_df["Partite Giocate"] = masters_df["Partite Giocate"].astype(int)
            masters_df = masters_df.sort_values(by=["punti_masters", "Partite Giocate"], ascending=[False, False])
            masters_df.columns = ["Utente", "Punti Masters", "Partite Giocate"]
            str_lib.dataframe(masters_df, use_container_width=True, hide_index=True)

    with sub_tab3:
        if df_punteggi.empty:
            str_lib.info("Classifica Bomber di razza vuota.")
        else:
            bomber_df = df_punteggi.groupby("utente")["punti_bomber"].sum().reset_index()
            bomber_df = pd.merge(bomber_df, partita_counts, on="utente", how="left").fillna(0)
            bomber_df["Partite Giocate"] = bomber_df["Partite Giocate"].astype(int)
            bomber_df = bomber_df.sort_values(by=["punti_bomber", "Partite Giocate"], ascending=[False, False])
            bomber_df.columns = ["Utente", "Punti Bomber", "Partite Giocate"]
            str_lib.dataframe(bomber_df, use_container_width=True, hide_index=True)

    with sub_tab4:
        str_lib.subheader("📜 Albo d'Oro")
        try:
            res_albo_pub = db.table("albo_doros").select("*").order("stagione", desc=True).execute()
            if res_albo_pub.data:
                df_albo_pub = pd.DataFrame(res_albo_pub.data)
                df_display = df_albo_pub.rename(columns={
                    "stagione": "Stagione", "vincitore_premio_cugurra": "Vincitore Premio Cugurra",
                    "premio_masters_of_cugurras": "Masters of Cugurras", "premio_bomber_di_razza": "Bomber di razza"
                })
                cols_display = [c for c in ["Stagione", "Vincitore Premio Cugurra", "Masters of Cugurras", "Bomber di razza"] if c in df_display.columns]
                str_lib.dataframe(df_display[cols_display], use_container_width=True, hide_index=True)
            else:
                str_lib.info("Nessun dato presente nell'Albo d'Oro.")
        except:
            str_lib.info("Albo d'oro non disponibile.")

# 3. REGOLAMENTO
elif is_regolamento:
    regolamento_html = """
    <!DOCTYPE html>
    <html>
    <head>
    <style>
        body {
            color: #f8fafc;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            background-color: transparent;
            padding: 10px;
            margin: 0;
            text-align: left;
        }
        h2 { color: #38bdf8; font-size: 1.5rem; margin-bottom: 20px; }
        h3 { color: #38bdf8; font-size: 1.1rem; margin-top: 25px; margin-bottom: 8px; }
        ul { margin-top: 0; padding-left: 20px; }
        li { margin-bottom: 8px; line-height: 1.5; color: #cbd5e1; }
        b { color: #ffffff; }
    </style>
    </head>
    <body>
        <h2>📜 Punteggi e Regolamento del Premio Cugurra</h2>
        
        <h3>Limite per le iscrizioni stagionali:</h3>
        <ul>
            <li>Le iscrizioni alla stagione in corso rimangono aperte fino al giorno <b>02 febbraio</b> (compreso) dell'anno solare in cui termina la stagione. Oltre questa data non sarà più possibile registrarsi come nuovi utenti per la stagione attiva.</li>
        </ul>

        <h3>Punteggi assegnati nella Classifica Generale:</h3>
        <ul>
            <li><b>15 Punti:</b> Risultato e marcatori esatti di tutte e due le squadre.</li>
            <li><b>10 Punti:</b> Risultato esatto della partita e marcatori esatti del Cagliari + eventuali autogol a favore dei rossoblu.</li>
            <li><b>8 Punti:</b> Indovini lo 0-0.</li>
            <li><b>5 Punti:</b> Indovini l'esito (1, X, 2).</li>
            <li><b>3 Punti:</b> Tutti i marcatori del Cagliari indovinati.</li>
            <li><b>0 Punti:</b> Non indovini nulla.</li>
            <li><b>Bonus Espulsioni:</b> +1 punto per ogni giocatore espulso indovinato (fino a 3 per squadra).</li>
        </ul>

        <h3>Classifica Masters of Cugurras:</h3>
        <ul>
            <li>Classifica dedicata a chi colleziona i pronostici da 10 punti.</li>
        </ul>

        <h3>Classifica Bomber di razza:</h3>
        <ul>
            <li>1 punto per ogni marcatore del Cagliari indovinato.</li>
            <li>Bonus: +1 punto a gol se si indovina anche il numero esatto di gol reali segnati da quel calciatore.</li>
        </ul>
    </body>
    </html>
    """
    components.html(regolamento_html, height=750, scrolling=True)

# 4. ADMIN
elif tab_admin is not None:
    components.html("<script>window.parent.scrollTo(0, 0);</script>", height=0)
    
    str_lib.markdown("<h2 class='single-line-title'>⚙️ Pannello di Controllo Admin ⚙️</h2>", unsafe_allow_html=True)
    
    with str_lib.expander("⚙️ Gestione Stagione & Fase Globale", expanded=False):
        fase_scelta = str_lib.selectbox("Cambia Fase Globale", ["TEST", "STAGIONE IN CORSO", "ARCHIVIO"], index=["TEST", "STAGIONE IN CORSO", "ARCHIVIO"].index(fase_attuale) if fase_attuale in ["TEST", "STAGIONE IN CORSO", "ARCHIVIO"] else 0)
        
        str_lib.markdown(f"Stagione corrente attiva: **{stagione_attuale}**")
        col_st1, col_st2 = str_lib.columns(2)
        with col_st1:
            if str_lib.button("Aggiorna Fase Globale", key="btn_aggiorna_fase", use_container_width=True):
                db.table("configurazione").update({"valore": fase_scelta}).eq("chiave", "fase_corrente").execute()
                str_lib.success("Fase aggiornata!")
                str_lib.rerun()
        with col_st2:
            if str_lib.button("🚀 Passa a Nuova Stagione (+1 anno & Test)", key="btn_nuova_stagione", use_container_width=True):
                try:
                    parti_anno = stagione_attuale.split("/")
                    if len(parti_anno) == 2:
                        anno1_int = int(parti_anno[0]) + 1
                        anno2_str = str(int(parti_anno[1]) + 1).zfill(2)
                        nuova_stagione_str = f"{anno1_int}/{anno2_str}"
                    else:
                        nuova_stagione_str = "2027/28"
                    
                    db.table("configurazione").update({"valore": nuova_stagione_str}).eq("chiave", "stagione_corrente").execute()
                    db.table("configurazione").update({"valore": "TEST"}).eq("chiave", "fase_corrente").execute()
                    str_lib.success(f"Stagione passata con successo a {nuova_stagione_str} in modalità TEST!")
                    str_lib.rerun()
                except Exception as ex_st:
                    str_lib.error(f"Errore durante il cambio stagione: {ex_st}")

    with str_lib.expander("➕ Inserisci Nuova Partita", expanded=False):
        try:
            lista_comp = [c['nome'] for c in db.table("competizioni").select("nome").order("nome").execute().data]
        except:
            lista_comp = ["Serie A"]
            
        comp = str_lib.selectbox("Competizione", lista_comp, key="new_partita_comp")
        avv = str_lib.text_input("Squadra Avversaria", key="new_partita_avv")
        campo = str_lib.selectbox("Campo", ["Casa", "Trasferta", "Campo Neutro"], key="new_partita_campo")
        data_p = str_lib.date_input("Data Partita", key="new_partita_data")
        
        col_ora_min_1, col_ora_min_2 = str_lib.columns(2)
        with col_ora_min_1:
            ore_sel = str_lib.selectbox("Ora", list(range(0, 24)), index=15, key="new_partita_ora")
        with col_ora_min_2:
            min_sel = str_lib.selectbox("Minuti", [0, 15, 30, 45], index=0, key="new_partita_min")
            
        rosa_cag_input = str_lib.text_area("Convocati Cagliari", key="new_partita_rosa_cag")
        rosa_avv_input = str_lib.text_area("Convocati Avversaria", key="new_partita_rosa_avv")
        
        submitted_partita = str_lib.button("Crea Partita nel Database", key="btn_crea_partita_db", use_container_width=True)

        if submitted_partita:
            if not avv:
                str_lib.error("Inserisci la squadra avversaria.")
            else:
                dt_locale = datetime.combine(data_p, datetime.min.time().replace(hour=ore_sel, minute=min_sel)).replace(tzinfo=FUSO_ITALIA)
                dt_utc = dt_locale.astimezone(zoneinfo.ZoneInfo("UTC"))
                data_ora_unita = dt_utc.isoformat().replace("+00:00", "Z")
                
                id_str = f"{comp}_{avv}_{data_p}".replace(" ", "_")
                db.table("partite").insert({
                    "competizione": comp, "avversario": avv, "campo": campo,
                    "casa_trasferta": campo, "data_ora": data_ora_unita, "id_stringa": id_str,
                    "rosa_cagliari": rosa_cag_input.replace(";", ","),
                    "rosa_avversaria": rosa_avv_input.replace(";", ","),
                    "omologata": False
                }).execute()
                str_lib.success("Partita creata!")

    with str_lib.expander("🏁 Omologazione Partita e Assegnazione Punti", expanded=False):
        str_lib.warning("⚠️ **ATTENZIONE:** L'omologazione inserisce i risultati definitivi e blocco modifiche.")
        
        try:
            partite_non_omologate = db.table("partite").select("*").eq("omologata", False).order("data_ora").execute().data
        except:
            partite_non_omologate = []

        if not partite_non_omologate:
            str_lib.info("Nessuna partita in attesa di omologazione.")
        else:
            dict_omo = {f"{p['competizione']} - Cagliari vs {p['avversario']} ({p['data_ora'][:10]}) [ID: {p['id']}]": p for p in partite_non_omologate}
            scelta_omo_str = str_lib.selectbox("Seleziona partita da omologare", list(dict_omo.keys()), key="select_omo")
            p_omo = dict_omo[scelta_omo_str]

            campo_omo = p_omo.get('campo') or p_omo.get('casa_trasferta') or 'Casa'
            is_cag_left_omo = campo_omo in ["Casa", "Campo Neutro"]
            s1_omo = "CAGLIARI" if is_cag_left_omo else p_omo['avversario']
            s2_omo = p_omo['avversario'] if is_cag_left_omo else "CAGLIARI"

            str_lib.markdown(f"### Risultato Ufficiale: {s1_omo} vs {s2_omo}")
            col_go1, col_go2 = str_lib.columns(2)
            with col_go1: gol_uff_s1 = str_lib.number_input(f"Gol {s1_omo} (Ufficiali)", min_value=0, value=0, key="gol_u_s1")
            with col_go2: gol_uff_s2 = str_lib.number_input(f"Gol {s2_omo} (Ufficiali)", min_value=0, value=0, key="gol_u_s2")

            rosa_cag_l = [x.strip() for x in (p_omo.get("rosa_cagliari") or "").split(",") if x.strip()]
            rosa_avv_l = [x.strip() for x in (p_omo.get("rosa_avversaria") or "").split(",") if x.strip()]
            rosa_t1 = rosa_cag_l if is_cag_left_omo else rosa_avv_l
            rosa_t2 = rosa_avv_l if is_cag_left_omo else rosa_cag_l

            str_lib.markdown("#### Marcatori e Dettagli")
            col_mo1, col_mo2 = str_lib.columns(2)
            with col_mo1:
                str_lib.markdown(f"**{s1_omo}**")
                marc_uff_1 = str_lib.multiselect(f"Marcatori {s1_omo}", options=rosa_t1, key="mu_1")
                for m in marc_uff_1:
                    k_m1 = f"omo_g_s1_{m}_{p_omo['id']}"
                    str_lib.session_state.gol_omologazione[k_m1] = str_lib.number_input(f"Gol di {m}", 1, 20, 1, key=k_m1)
                auto_uff_1 = str_lib.multiselect(f"Autogol a favore di {s1_omo}", options=rosa_t2, key="au_1")
                for a in auto_uff_1:
                    k_a1 = f"omo_auto_s1_{a}_{p_omo['id']}"
                    str_lib.session_state.gol_omologazione[k_a1] = str_lib.number_input(f"Autogol di {a}", 1, 20, 1, key=k_a1)
                esp_uff_1 = str_lib.multiselect(f"Espulsi {s1_omo}", options=rosa_t1, key="eu_1")

            with col_mo2:
                str_lib.markdown(f"**{s2_omo}**")
                marc_uff_2 = str_lib.multiselect(f"Marcatori {s2_omo}", options=rosa_t2, key="mu_2")
                for m in marc_uff_2:
                    k_m2 = f"omo_g_s2_{m}_{p_omo['id']}"
                    str_lib.session_state.gol_omologazione[k_m2] = str_lib.number_input(f"Gol di {m}", 1, 20, 1, key=k_m2)
                auto_uff_2 = str_lib.multiselect(f"Autogol a favore di {s2_omo}", options=rosa_t1, key="au_2")
                for a in auto_uff_2:
                    k_a2 = f"omo_auto_s2_{a}_{p_omo['id']}"
                    str_lib.session_state.gol_omologazione[k_a2] = str_lib.number_input(f"Autogol di {a}", 1, 20, 1, key=k_a2)
                esp_uff_2 = str_lib.multiselect(f"Espulsi {s2_omo}", options=rosa_t2, key="eu_2")

            btn_omologa = str_lib.button("Conferma e Omologa Partita", key="btn_conferma_omologa", use_container_width=True)

            if btn_omologa:
                marc1_expanded = []
                for m in marc_uff_1:
                    cnt = str_lib.session_state.gol_omologazione.get(f"omo_g_s1_{m}_{p_omo['id']}", 1)
                    marc1_expanded.extend([m] * cnt)

                auto1_expanded = []
                for a in auto_uff_1:
                    cnt = str_lib.session_state.gol_omologazione.get(f"omo_auto_s1_{a}_{p_omo['id']}", 1)
                    auto1_expanded.extend([a] * cnt)

                marc2_expanded = []
                for m in marc_uff_2:
                    cnt = str_lib.session_state.gol_omologazione.get(f"omo_g_s2_{m}_{p_omo['id']}", 1)
                    marc2_expanded.extend([m] * cnt)

                auto2_expanded = []
                for a in auto_uff_2:
                    cnt = str_lib.session_state.gol_omologazione.get(f"omo_auto_s2_{a}_{p_omo['id']}", 1)
                    auto2_expanded.extend([a] * cnt)

                if is_cag_left_omo:
                    res_cag, res_avv = gol_uff_s1, gol_uff_s2
                    m_cag, m_avv = marc1_expanded, marc2_expanded
                    a_cag, a_avv = auto1_expanded, auto2_expanded
                    e_cag, e_avv = esp_uff_1, esp_uff_2
                else:
                    res_cag, res_avv = gol_uff_s2, gol_uff_s1
                    m_cag, m_avv = marc2_expanded, marc1_expanded
                    a_cag, a_avv = auto2_expanded, auto1_expanded
                    e_cag, e_avv = esp_uff_2, esp_uff_1
                
                db.table("partite").update({
                    "risultato_cagliari": res_cag, "risultato_avversario": res_avv,
                    "marcatori_cagliari_reali": m_cag, "marcatori_avversario_reali": m_avv,
                    "autogol_cagliari_reali": a_cag, "autogol_avversario_reali": a_avv,
                    "espulsi_cagliari_reali": e_cag, "espulsi_avversario_reali": e_avv,
                    "omologata": True
                }).eq("id", p_omo["id"]).execute()

                ricalcola_punteggi_partita(p_omo["id"])

                str_lib.success("Partita omologata e punteggi ricalcolati e sovrascritti correttamente!")
                str_lib.rerun()

    with str_lib.expander("🛠️ Modifica o Elimina Partite Attive", expanded=False):
        try:
            partite_attive = db.table("partite").select("*").eq("omologata", False).order("data_ora").execute().data
        except:
            partite_attive = []

        if not partite_attive:
            str_lib.info("Nessuna partita attiva da modificare.")
        else:
            dict_partite = {f"{p['competizione']} - Cagliari vs {p['avversario']} ({p['data_ora'][:10]}) [ID: {p['id']}]": p for p in partite_attive}
            scelta_partita_str = str_lib.selectbox("Seleziona partita attiva da modificare o eliminare", list(dict_partite.keys()))
            p_selezionata = dict_partite[scelta_partita_str]

            with str_lib.form("form_modifica_partita"):
                m_comp = str_lib.text_input("Competizione", value=p_selezionata.get("competizione", ""))
                m_avv = str_lib.text_input("Squadra Avversaria", value=p_selezionata.get("avversario", ""))
                
                attuale_campo = p_selezionata.get("campo") or p_selezionata.get("casa_trasferta") or "Casa"
                idx_campo = ["Casa", "Trasferta", "Campo Neutro"].index(attuale_campo) if attuale_campo in ["Casa", "Trasferta", "Campo Neutro"] else 0
                m_campo = str_lib.selectbox("Campo", ["Casa", "Trasferta", "Campo Neutro"], index=idx_campo)
                
                try:
                    raw_dt_edit = p_selezionata['data_ora'].replace("Z", "")
                    dt_esistente = datetime.fromisoformat(raw_dt_edit)
                    if dt_esistente.tzinfo is None:
                        dt_esistente = dt_esistente.replace(tzinfo=FUSO_ITALIA)
                    else:
                        dt_esistente = dt_esistente.astimezone(FUSO_ITALIA)
                    init_date = dt_esistente.date()
                    init_hour = dt_esistente.hour
                    init_minute_idx = [0, 15, 30, 45].index(dt_esistente.minute) if dt_esistente.minute in [0, 15, 30, 45] else 0
                except:
                    init_date = datetime.now(FUSO_ITALIA).date()
                    init_hour = 15
                    init_minute_idx = 0

                m_data = str_lib.date_input("Data Partita", value=init_date)
                m_ora = str_lib.selectbox("Ora", list(range(0, 24)), index=init_hour)
                m_min = str_lib.selectbox("Minuti", [0, 15, 30, 45], index=init_minute_idx)
                
                m_rosa_cag = str_lib.text_area("Convocati Cagliari", value=p_selezionata.get("rosa_cagliari", ""))
                m_rosa_avv = str_lib.text_area("Convocati Avversaria", value=p_selezionata.get("rosa_avversaria", ""))

                col_mod1, col_mod2 = str_lib.columns(2)
                with col_mod1:
                    submit_mod = str_lib.form_submit_button("Salva Modifiche", use_container_width=True)
                with col_mod2:
                    submit_del = str_lib.form_submit_button("Elimina Partita", use_container_width=True)

                if submit_mod:
                    dt_locale = datetime.combine(m_data, datetime.min.time().replace(hour=m_ora, minute=m_min)).replace(tzinfo=FUSO_ITALIA)
                    dt_utc = dt_locale.astimezone(zoneinfo.ZoneInfo("UTC"))
                    data_ora_unita = dt_utc.isoformat().replace("+00:00", "Z")
                    
                    id_str = f"{m_comp}_{m_avv}_{m_data}".replace(" ", "_")

                    ora_attuale = datetime.now(FUSO_ITALIA)

                    if dt_locale < ora_attuale:
                        str_lib.warning("⚠️ **Attenzione:** Stai impostando una data/ora antecedente al momento attuale. La modifica verrà comunque salvata.")

                    db.table("partite").update({
                        "competizione": m_comp, "avversario": m_avv, "campo": m_campo,
                        "casa_trasferta": m_campo, "data_ora": data_ora_unita, "id_stringa": id_str,
                        "rosa_cagliari": m_rosa_cag.replace(";", ","),
                        "rosa_avversaria": m_rosa_avv.replace(";", ",")
                    }).eq("id", p_selezionata["id"]).execute()
                    str_lib.success("Partita aggiornata con successo!")
                    str_lib.rerun()

                if submit_del:
                    db.table("partite").delete().eq("id", p_selezionata["id"]).execute()
                    str_lib.success("Partita eliminata!")
                    str_lib.rerun()

    with str_lib.expander("👥 Gestione Utenti, Status & Reset PIN", expanded=False):
        try:
            utenti_db = db.table("utenti").select("*").execute().data
        except:
            utenti_db = []
            
        if utenti_db:
            df_utenti = pd.DataFrame(utenti_db)
            cols_to_show = [c for c in ['nome_fb', 'email', 'status', 'is_admin'] if c in df_utenti.columns]
            str_lib.dataframe(df_utenti[cols_to_show], use_container_width=True)
            
            utenti_tutti = [u['nome_fb'] for u in utenti_db]
            utenti_non_admin = [u['nome_fb'] for u in utenti_db if not u.get('is_admin', False)]
            
            str_lib.markdown("---")
            str_lib.markdown("#### 🔑 Reset PIN & Sicurezza Utenti")
            col_pass1, col_pass2 = str_lib.columns(2)
            with col_pass1:
                target_reset_user = str_lib.selectbox("Seleziona Utente per Reset PIN", utenti_tutti, key="select_user_reset_pin")
                new_forced_pin = str_lib.text_input("Nuovo PIN a 4 cifre", max_chars=4, key="input_forced_pin")
            with col_pass2:
                str_lib.write("")
                str_lib.write("")
                if str_lib.button("Forza Aggiornamento PIN", key="btn_force_pin", use_container_width=True):
                    if not new_forced_pin.isdigit() or len(new_forced_pin.strip()) != 4:
                        str_lib.error("Il PIN deve essere esattamente di 4 cifre numeriche.")
                    else:
                        try:
                            db.table("utenti").update({"pin": new_forced_pin.strip()}).eq("nome_fb", target_reset_user).execute()
                            str_lib.success(f"PIN aggiornato per {target_reset_user}")
                        except Exception as ex_p:
                            str_lib.error(f"Errore: {ex_p}")
            
            str_lib.markdown("---")
            str_lib.markdown("#### ⭐ Modifica Status o Elimina Utente")
            if utenti_non_admin:
                utente_target = str_lib.selectbox("Seleziona Utente da gestire", utenti_non_admin)
                
                col_u1, col_u2, col_u3 = str_lib.columns(3)
                azione_utente = "Promuovi a TOP"
                with col_u1:
                    if str_lib.button("Promuovi TOP", key="btn_promuovi", use_container_width=True):
                        azione_utente = "Promuovi a TOP"
                with col_u2:
                    if str_lib.button("Retrocedi STANDARD", key="btn_retrocedi", use_container_width=True):
                        azione_utente = "Retrocedi a STANDARD"
                with col_u3:
                    if str_lib.button("Elimina", key="btn_elimina_utente", use_container_width=True):
                        azione_utente = "Elimina Utente"
                
                str_lib.write(f"Azione selezionata: **{azione_utente}** per l'utente **{utente_target}**")
                btn_esegui_utente = str_lib.button("Esegui Modifica Utente", key="btn_esegui_mod_utente", use_container_width=True)

                if btn_esegui_utente:
                    try:
                        if azione_utente == "Elimina Utente":
                            db.table("utenti").delete().eq("nome_fb", utente_target).execute()
                            str_lib.success(f"Utente {utente_target} rimosso.")
                        else:
                            nuovo_status = "TOP" if azione_utente == "Promuovi a TOP" else "STANDARD"
                            db.table("utenti").update({"status": nuovo_status}).eq("nome_fb", utente_target).execute()
                            str_lib.success(f"Utente {utente_target} ora ha status {nuovo_status}.")
                        str_lib.rerun()
                    except Exception as err:
                        str_lib.error(f"Errore: {err}")

    with str_lib.expander("📜 Gestione Albo d'Oro", expanded=False):
        try:
            res_albo_admin = db.table("albo_doros").select("*").order("stagione", desc=True).execute()
            if res_albo_admin.data:
                df_albo_admin = pd.DataFrame(res_albo_admin.data)
                edited_df = str_lib.data_editor(
                    df_albo_admin, num_rows="dynamic", use_container_width=True, key="editor_albo_admin"
                )
                btn_salva_albo = str_lib.button("Salva Modifiche Albo d'Oro", key="btn_salva_albo", use_container_width=True)

                if btn_salva_albo:
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
                        str_lib.success("Albo d'Oro aggiornato con successo!")
                        str_lib.rerun()
                    except Exception as ex_albo:
                        str_lib.error(f"Errore durante l'aggiornamento: {ex_albo}")
        except:
            str_lib.info("Impossibile caricare l'albo d'oro per la gestione.")

mostra_footer()
