import streamlit as st
import datetime
from zoneinfo import ZoneInfo
import sqlite3
import pandas as pd
import numpy as np
import streamlit.components.v1 as components

# ==========================================
# 1. CONFIGURAZIONE PAGINA & STILI CSS INTEGRALI
# ==========================================
st.set_page_config(
    page_title="Premio Cugurra",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Iniezione completa dello stile CSS per l'applicazione
st.markdown("""
    <style>
    /* Stili Generali */
    .main { 
        padding: 1.5rem; 
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    /* Card Personalizzate */
    .card-cugurra {
        background-color: #1f2937;
        color: #f3f4f6;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        margin-bottom: 20px;
        border-left: 5px solid #10b981;
    }
    
    .card-stat {
        background-color: #111827;
        color: #ffffff;
        padding: 15px;
        border-radius: 10px;
        text-align: center;
        border: 1px solid #374151;
    }

    .stat-val {
        font-size: 28px;
        font-weight: bold;
        color: #10b981;
    }

    .stat-label {
        font-size: 14px;
        color: #9ca3af;
        text-transform: uppercase;
    }

    /* Box Countdown Timer JS */
    .countdown-container {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        border: 2px solid #38bdf8;
        border-radius: 12px;
        padding: 15px;
        text-align: center;
        color: #ffffff;
        margin-bottom: 25px;
        box-shadow: 0 10px 15px -3px rgba(56, 189, 248, 0.2);
    }

    .countdown-title {
        font-size: 14px;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        color: #94a3b8;
        margin-bottom: 5px;
    }

    .countdown-time {
        font-family: 'Courier New', Courier, monospace;
        font-size: 26px;
        font-weight: bold;
        color: #38bdf8;
    }

    /* Tabella Classifica Personalizzata */
    .dataframe {
        width: 100% !important;
        border-collapse: collapse !important;
    }
    
    .stButton > button {
        border-radius: 8px;
        font-weight: bold;
        transition: all 0.3s ease;
    }

    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }

    /* Footer Personalizzato */
    .cugurra-footer {
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        background-color: #0f172a;
        color: #94a3b8;
        text-align: center;
        padding: 8px;
        font-size: 12px;
        border-top: 1px solid #1e293b;
        z-index: 999;
    }
    </style>
""", unsafe_allow_html=True)


# ==========================================
# 2. GESTIONE DATABASE SQLITE INTEGRALE
# ==========================================
DB_FILE = "cugurra.db"

def get_connection():
    return sqlite3.connect(DB_FILE, check_same_thread=False)

def init_db():
    conn = get_connection()
    c = conn.cursor()
    
    # 1. Tabella Utenti
    c.execute('''
        CREATE TABLE IF NOT EXISTS utenti (
            username TEXT PRIMARY KEY,
            password TEXT NOT NULL,
            ruolo TEXT NOT NULL DEFAULT 'user',
            data_iscrizione TEXT NOT NULL
        )
    ''')
    
    # 2. Tabella Partite
    c.execute('''
        CREATE TABLE IF NOT EXISTS partite (
            id_partita INTEGER PRIMARY KEY AUTOINCREMENT,
            squadra_casa TEXT NOT NULL,
            squadra_trasferta TEXT NOT NULL,
            data_ora_limite TEXT NOT NULL,
            stato TEXT NOT NULL DEFAULT 'aperta',
            risultato_casa INTEGER,
            risultato_trasferta INTEGER,
            marcatori_reali TEXT,
            giornata INTEGER DEFAULT 1,
            competizione TEXT DEFAULT 'Serie A'
        )
    ''')
    
    # 3. Tabella Pronostici
    c.execute('''
        CREATE TABLE IF NOT EXISTS pronostici (
            id_pronostico INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            id_partita INTEGER NOT NULL,
            gol_casa INTEGER NOT NULL,
            gol_trasferta INTEGER NOT NULL,
            marcatori_pronostico TEXT,
            punti_esito INTEGER DEFAULT 0,
            punti_marcatori INTEGER DEFAULT 0,
            punti_assegnati INTEGER DEFAULT 0,
            data_inserimento TEXT NOT NULL,
            FOREIGN KEY(username) REFERENCES utenti(username),
            FOREIGN KEY(id_partita) REFERENCES partite(id_partita),
            UNIQUE(username, id_partita)
        )
    ''')
    
    # 4. Tabella Rosa Marcatori
    c.execute('''
        CREATE TABLE IF NOT EXISTS rosa (
            id_giocatore INTEGER PRIMARY KEY AUTOINCREMENT,
            nome_giocatore TEXT NOT NULL,
            ruolo TEXT NOT NULL,
            attivo INTEGER DEFAULT 1
        )
    ''')

    # 5. Tabella Log Operazioni / Audit Admin
    c.execute('''
        CREATE TABLE IF NOT EXISTS log_admin (
            id_log INTEGER PRIMARY KEY AUTOINCREMENT,
            admin_username TEXT NOT NULL,
            azione TEXT NOT NULL,
            timestamp TEXT NOT NULL
        )
    ''')

    # Utente Admin di Default se il DB è vuoto
    c.execute("SELECT * FROM utenti WHERE username = 'admin'")
    if not c.fetchone():
        now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        c.execute("INSERT INTO utenti (username, password, ruolo, data_iscrizione) VALUES ('admin', 'admin123', 'admin', ?)", (now_str,))
        
    conn.commit()
    conn.close()

init_db()

def run_query(query, params=(), fetch=None):
    conn = get_connection()
    c = conn.cursor()
    c.execute(query, params)
    data = None
    if fetch == "one":
        data = c.fetchone()
    elif fetch == "all":
        data = c.fetchall()
    conn.commit()
    conn.close()
    return data

def log_admin_action(admin_user, azione):
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    run_query("INSERT INTO log_admin (admin_username, azione, timestamp) VALUES (?, ?, ?)", (admin_user, azione, now_str))


# ==========================================
# HELPER FUNZIONI PER GESTIONE STRINGHE GIOCATORI
# ==========================================
def parse_lista_giocatori(stringa_input):
    """
    Normalizza e pulisce qualsiasi stringa di marcatori accettando virgole (,) e punti e virgola (;)
    Preserva gli spazi interni dei doppi cognomi e rimuove gli spazi di testa/coda.
    """
    if not stringa_input:
        return []
    stringa_pulita = stringa_input.replace(";", ",")
    elementi = [m.strip() for m in stringa_pulita.split(",") if m.strip()]
    return elementi


# ==========================================
# 3. LOGICA DI CALCOLO PUNTEGGI
# ==========================================
def calcola_punteggio_pronostico(p_casa, p_trasferta, res_casa, res_trasferta, marcatori_p, marcatori_r):
    punti_esito = 0
    punti_marcatori = 0

    totale_gol_reali = res_casa + res_trasferta
    is_goleada_reale = totale_gol_reali > 9

    # 1. CONTROLLO RISULTATO ESATTO
    if p_casa == res_casa and p_trasferta == res_trasferta:
        if is_goleada_reale:
            punti_esito = 12
        elif res_casa == 0 and res_trasferta == 0:
            punti_esito = 8
        else:
            punti_esito = 10
            
    # 2. CONTROLLO ESITO 1X2 E DIFFERENZA RETI
    else:
        segno_pronostico = 1 if p_casa > p_trasferta else (-1 if p_casa < p_trasferta else 0)
        segno_reale = 1 if res_casa > res_trasferta else (-1 if res_casa < res_trasferta else 0)

        if segno_pronostico == segno_reale:
            diff_pronostico = p_casa - p_trasferta
            diff_reale = res_casa - res_trasferta
            if diff_pronostico == diff_reale:
                punti_esito = 7
            else:
                punti_esito = 5
        else:
            punti_esito = 0

    # 3. BONUS MARCATORI (+5 PUNTI CIASCUNO)
    if marcatori_p and marcatori_r:
        lista_p = [m.lower() for m in parse_lista_giocatori(marcatori_p)]
        lista_r = [m.lower() for m in parse_lista_giocatori(marcatori_r)]
        
        for m in lista_p:
            if m in lista_r:
                punti_marcatori += 5
                lista_r.remove(m)

    punti_totali = punti_esito + punti_marcatori
    return punti_esito, punti_marcatori, punti_totali


# ==========================================
# 4. GESTIONE STATO DELLA SESSIONE
# ==========================================
if "user" not in st.session_state:
    st.session_state.user = None
if "role" not in st.session_state:
    st.session_state.role = None
if "gol_singoli" not in st.session_state:
    st.session_state.gol_singoli = {}

def login_user(username, password):
    user = run_query("SELECT username, ruolo FROM utenti WHERE username = ? AND password = ?", (username, password), fetch="one")
    if user:
        st.session_state.user = user[0]
        st.session_state.role = user[1]
        return True
    return False

def logout_user():
    st.session_state.user = None
    st.session_state.role = None
    st.session_state.gol_singoli = {}
    st.rerun()


# ==========================================
# 5. SIDEBAR & BARRA DI NAVIGAZIONE
# ==========================================
st.sidebar.title("⚽ Premio Cugurra")
st.sidebar.caption("App Ufficiale Gestione Schedine e Classifica")

if st.session_state.user:
    st.sidebar.markdown(f"👤 Utente collegato: **{st.session_state.user}**")
    st.sidebar.markdown(f"🏷️ Ruolo: `{st.session_state.role.upper()}`")
    if st.sidebar.button("🚪 Logout", key="btn_logout"):
        logout_user()
else:
    st.sidebar.subheader("🔐 Area Riservata")
    username_input = st.sidebar.text_input("Username", key="login_user")
    password_input = st.sidebar.text_input("Password", type="password", key="login_pass")
    if st.sidebar.button("Accedi", key="btn_login"):
        if login_user(username_input, password_input):
            st.sidebar.success("Login riuscito!")
            st.rerun()
        else:
            st.sidebar.error("Credenziali non corrette.")

st.sidebar.divider()

menu_options = [
    "🏆 Classifica Generale", 
    "🎯 Inserisci Pronostici", 
    "📜 Le Mie Schedine",
    "📊 Statistiche Avanzate",
    "📖 Regolamento Punteggi"
]

if st.session_state.role == "admin":
    menu_options.append("🛠️ Pannello Amministrazione")

scelta_menu = st.sidebar.radio("Sezioni Disponibili", menu_options)


# ==========================================
# 6. SEZIONE: CLASSIFICA GENERALE
# ==========================================
if scelta_menu == "🏆 Classifica Generale":
    st.title("🏆 Classifica Generale Premio Cugurra")
    st.markdown("La classifica si aggiorna automaticamente in seguito all'omologazione delle partite da parte degli amministratori.")

    query_classifica = """
        SELECT 
            u.username,
            COALESCE(SUM(p.punti_assegnati), 0) as totale_punti,
            COALESCE(SUM(p.punti_esito), 0) as punti_esiti,
            COALESCE(SUM(p.punti_marcatori), 0) as punti_marcatori,
            COUNT(p.id_pronostico) as giocate
        FROM utenti u
        LEFT JOIN pronostici p ON u.username = p.username
        GROUP BY u.username
        ORDER BY totale_punti DESC, punti_esiti DESC, punti_marcatori DESC
    """
    res_classifica = run_query(query_classifica, fetch="all")

    if res_classifica:
        df = pd.DataFrame(res_classifica, columns=["Giocatore", "Punti Totali", "Punti Esito", "Punti Marcatori", "Schedine Giocate"])
        df.index = np.arange(1, len(df) + 1)
        
        col_p1, col_p2, col_p3 = st.columns(3)
        if len(df) >= 1:
            with col_p1:
                st.markdown(f"""
                    <div class="card-stat">
                        <div class="stat-label">🥇 1° Posto</div>
                        <div class="stat-val">{df.iloc[0]['Giocatore']}</div>
                        <div>{df.iloc[0]['Punti Totali']} Punti</div>
                    </div>
                """, unsafe_allow_html=True)
        if len(df) >= 2:
            with col_p2:
                st.markdown(f"""
                    <div class="card-stat">
                        <div class="stat-label">🥈 2° Posto</div>
                        <div class="stat-val">{df.iloc[1]['Giocatore']}</div>
                        <div>{df.iloc[1]['Punti Totali']} Punti</div>
                    </div>
                """, unsafe_allow_html=True)
        if len(df) >= 3:
            with col_p3:
                st.markdown(f"""
                    <div class="card-stat">
                        <div class="stat-label">🥉 3° Posto</div>
                        <div class="stat-val">{df.iloc[2]['Giocatore']}</div>
                        <div>{df.iloc[2]['Punti Totali']} Punti</div>
                    </div>
                """, unsafe_allow_html=True)

        st.divider()
        st.dataframe(df, use_container_width=True)
    else:
        st.info("Nessun punteggio ancora registrato nel sistema.")


# ==========================================
# 7. SEZIONE: INSERIMENTO PRONOSTICI & JS COUNTDOWN
# ==========================================
elif scelta_menu == "🎯 Inserisci Pronostici":
    st.title("🎯 Compila i Tuoi Pronostici")

    if not st.session_state.user:
        st.warning("Per poter compilare o modificare un pronostico devi prima effettuare il login dal menu laterale.")
    else:
        partite_aperte = run_query("""
            SELECT id_partita, squadra_casa, squadra_trasferta, data_ora_limite, giornata, competizione 
            FROM partite 
            WHERE stato = 'aperta'
            ORDER BY data_ora_limite ASC
        """, fetch="all")

        if not partite_aperte:
            st.info("Al momento non ci sono partite aperte su cui piazzare i pronostici.")
        else:
            dict_partite = {
                f"[{p[5]} - Giornata {p[4]}] {p[1]} vs {p[2]} (Scadenza: {p[3]})": p 
                for p in partite_aperte
            }
            
            partita_selezionata = st.selectbox("Seleziona l'incontro da pronosticare", list(dict_partite.keys()))
            p_data = dict_partite[partita_selezionata]
            
            id_partita = p_data[0]
            casa = p_data[1]
            trasferta = p_data[2]
            limite_str = p_data[3]

            # Countdown Javascript Dinamico
            js_countdown = f"""
            <div class="countdown-container">
                <div class="countdown-title">Tempo Rimasto per Inviare la Schedina</div>
                <div class="countdown-time" id="timer">--d --h --m --s</div>
            </div>
            <script>
            function updateTimer() {{
                var targetDate = new Date("{limite_str.replace(' ', 'T')}").getTime();
                var now = new Date().getTime();
                var difference = targetDate - now;

                if (difference <= 0) {{
                    document.getElementById("timer").innerHTML = "PRONOSTICI CHIUSI";
                    document.getElementById("timer").style.color = "#ef4444";
                    return;
                }}

                var days = Math.floor(difference / (1000 * 60 * 60 * 24));
                var hours = Math.floor((difference % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
                var minutes = Math.floor((difference % (1000 * 60 * 60)) / (1000 * 60));
                var seconds = Math.floor((difference % (1000 * 60)) / 1000);

                document.getElementById("timer").innerHTML = days + "g " + hours + "o " + minutes + "m " + seconds + "s ";
            }}
            setInterval(updateTimer, 1000);
            updateTimer();
            </script>
            """
            components.html(js_countdown, height=100)

            # Verifica Pronostico Esistente nel DB
            existing_p = run_query("""
                SELECT gol_casa, gol_trasferta, marcatori_pronostico 
                FROM pronostici 
                WHERE username = ? AND id_partita = ?
            """, (st.session_state.user, id_partita), fetch="one")

            val_casa = existing_p[0] if existing_p else 0
            val_trasferta = existing_p[1] if existing_p else 0
            
            # PARSING RIGOROSO: normalizza gli spazi e accetta virgole/punti e virgola
            val_marcatori = parse_lista_giocatori(existing_p[2]) if (existing_p and existing_p[2]) else []

            st.markdown(f"### Match: **{casa}** vs **{trasferta}**")
            
            col1, col2 = st.columns(2)
            with col1:
                g_casa = st.number_input(f"Gol {casa}", min_value=0, max_value=20, value=val_casa, key=f"gc_{id_partita}")
            with col2:
                g_trasferta = st.number_input(f"Gol {trasferta}", min_value=0, max_value=20, value=val_trasferta, key=f"gt_{id_partita}")

            st.divider()
            st.subheader("⚽ Marcatori Pronosticati")
            
            rosa_db = run_query("SELECT nome_giocatore FROM rosa WHERE attivo = 1 ORDER BY nome_giocatore ASC", fetch="all")
            lista_rosa = [r[0].strip() for r in rosa_db] if rosa_db else []

            # Calcola le occorrenze dei marcatori salvati nel DB
            for m in val_marcatori:
                if m not in st.session_state.gol_singoli:
                    st.session_state.gol_singoli[m] = val_marcatori.count(m)

            # Multiselect con corrispondenza esatta di nome (doppi cognomi inclusi)
            marcatori_sel = st.multiselect(
                "Seleziona i marcatori per la partita (opzionale)",
                options=lista_rosa,
                default=list(set([m for m in val_marcatori if m in lista_rosa])),
                key=f"msel_{id_partita}"
            )

            # Reset Dinamico UX per elementi deselezionati
            keys_da_rimuovere = [k for k in st.session_state.gol_singoli if k not in marcatori_sel]
            for k in keys_da_rimuovere:
                del st.session_state.gol_singoli[k]

            marcatori_finali = []
            if marcatori_sel:
                st.write("Dettaglio reti per ciascun marcatore scelto:")
                for m in marcatori_sel:
                    val_init = st.session_state.gol_singoli.get(m, 1)
                    cnt = st.number_input(f"Gol segnati da {m}", min_value=1, max_value=10, value=val_init, key=f"cnt_{m}_{id_partita}")
                    st.session_state.gol_singoli[m] = cnt
                    marcatori_finali.extend([m] * cnt)

            str_marcatori = ", ".join(marcatori_finali)

            st.divider()
            if st.button("💾 Invia / Aggiorna Pronostico", use_container_width=True):
                tz_roma = ZoneInfo("Europe/Rome")
                ora_attuale = datetime.datetime.now(tz_roma)
                limite_dt = datetime.datetime.strptime(limite_str, "%Y-%m-%d %H:%M:%S").replace(tzinfo=tz_roma)

                if ora_attuale >= limite_dt:
                    st.error("⏰ Operazione fallita: Il termine ultimo per inviare il pronostico a questa partita è scaduto.")
                else:
                    now_inserimento = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    if existing_p:
                        run_query("""
                            UPDATE pronostici 
                            SET gol_casa = ?, gol_trasferta = ?, marcatori_pronostico = ?, data_inserimento = ? 
                            WHERE username = ? AND id_partita = ?
                        """, (g_casa, g_trasferta, str_marcatori, now_inserimento, st.session_state.user, id_partita))
                    else:
                        run_query("""
                            INSERT INTO pronostici (username, id_partita, gol_casa, gol_trasferta, marcatori_pronostico, data_inserimento) 
                            VALUES (?, ?, ?, ?, ?, ?)
                        """, (st.session_state.user, id_partita, g_casa, g_trasferta, str_marcatori, now_inserimento))
                    
                    st.success("✅ Pronostico salvato con successo!")


# ==========================================
# 8. SEZIONE: LE MIE SCHEDINE (STORICO)
# ==========================================
elif scelta_menu == "📜 Le Mie Schedine":
    st.title("📜 Storico Pronostici")

    if not st.session_state.user:
        st.warning("Effettua il login per consultare lo storico dei tuoi pronostici.")
    else:
        query_mie_schedine = """
            SELECT 
                p.squadra_casa,
                p.squadra_trasferta,
                pr.gol_casa,
                pr.gol_trasferta,
                pr.marcatori_pronostico,
                p.risultato_casa,
                p.risultato_trasferta,
                p.marcatori_reali,
                pr.punti_esito,
                pr.punti_marcatori,
                pr.punti_assegnati,
                p.stato
            FROM pronostici pr
            JOIN partite p ON pr.id_partita = p.id_partita
            WHERE pr.username = ?
            ORDER BY p.id_partita DESC
        """
        schedine = run_query(query_mie_schedine, (st.session_state.user,), fetch="all")

        if not schedine:
            st.info("Non hai ancora piazzato alcun pronostico.")
        else:
            for s in schedine:
                casa, tras, p_c, p_t, m_p, r_c, r_t, m_r, pts_e, pts_m, pts_tot, stato = s
                
                with st.expander(f"{casa} vs {tras} — Stato: {stato.upper()} (Punti Totali: {pts_tot})"):
                    c1, c2 = st.columns(2)
                    with c1:
                        st.markdown("**Il Tuo Pronostico:**")
                        st.write(f"Risultato: {p_c} - {p_t}")
                        st.write(f"Marcatori: {m_p if m_p else 'Nessuno'}")
                    with c2:
                        st.markdown("**Risultato Reale Match:**")
                        if stato == 'chiusa':
                            st.write(f"Risultato Finale: {r_c} - {r_t}")
                            st.write(f"Marcatori Reali: {m_r if m_r else 'Nessuno'}")
                        else:
                            st.write("In attesa di omologazione...")
                    
                    st.divider()
                    st.markdown(f"Breakdown Punti: **Esito:** `{pts_e}` | **Marcatori:** `{pts_m}` | **Totale:** `{pts_tot}`")


# ==========================================
# 9. SEZIONE: STATISTICHE AVANZATE
# ==========================================
elif scelta_menu == "📊 Statistiche Avanzate":
    st.title("📊 Statistiche e Analisi Premio Cugurra")
    
    tot_partite = run_query("SELECT COUNT(*) FROM partite WHERE stato = 'chiusa'", fetch="one")[0]
    tot_pronostici = run_query("SELECT COUNT(*) FROM pronostici", fetch="one")[0]
    tot_punti_distribuiti = run_query("SELECT COALESCE(SUM(punti_assegnati), 0) FROM pronostici", fetch="one")[0]

    kpi1, kpi2, kpi3 = st.columns(3)
    with kpi1:
        st.metric("Partite Omologate", tot_partite)
    with kpi2:
        st.metric("Pronostici Totali Inviati", tot_pronostici)
    with kpi3:
        st.metric("Punti Totali Assegnati", tot_punti_distribuiti)

    st.divider()
    st.subheader("Marcatori Più Pronosticati")
    
    marcatori_all = run_query("SELECT marcatori_pronostico FROM pronostici WHERE marcatori_pronostico IS NOT NULL AND marcatori_pronostico != ''", fetch="all")
    if marcatori_all:
        conteggio_m = {}
        for row in marcatori_all:
            lista = parse_lista_giocatori(row[0])
            for m in lista:
                conteggio_m[m] = conteggio_m.get(m, 0) + 1
        
        df_m = pd.DataFrame(list(conteggio_m.items()), columns=["Giocatore", "Volte Pronosticato"]).sort_values(by="Volte Pronosticato", ascending=False)
        st.bar_chart(df_m.set_index("Giocatore"))
    else:
        st.info("Nessun dato relativo ai marcatori disponibile.")


# ==========================================
# 10. SEZIONE: REGOLAMENTO PUNTEGGI
# ==========================================
elif scelta_menu == "📖 Regolamento Punteggi":
    st.title("📖 Regolamento Premio Cugurra")
    st.markdown("""
    <div class="card-cugurra">
        <h3>Sistema Ufficiale Assegnazione Punteggi</h3>
        <p>Il punteggio di ogni schedina viene calcolato al termine dell'omologazione della partita da parte degli amministratori.</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    #### 1. Punteggi Risultato ed Esito
    * **12 Punti**: Risultato Esatto indovinato in caso di **Goleada Reale** (>9 gol complessivi registrati nel match vero).
    * **10 Punti**: Risultato Esatto indovinato in una partita standard.
    * **8 Punti**: Risultato Esatto indovinato per il punteggio di **0-0**.
    * **7 Punti**: Esito 1X2 indovinato CON **differenza reti esatta** (es. pronosticato 3-1, finale 2-0).
    * **5 Punti**: Esito 1X2 indovinato MA differenza reti errata (es. pronosticato 2-1, finale 1-0).
    * **0 Punti**: Esito 1X2 errato.

    #### 2. Bonus Marcatori Extra
    * **+5 Punti**: Assegnati per ciascun marcatore esatto azzeccato nell'elenco inviato. Se un giocatore viene pronosticato con una doppietta ed effettivamente segna 2 gol nel match omologato, verranno assegnati 10 punti bonus totali.
    """)


# ==========================================
# 11. PANNELLO AMMINISTRAZIONE INTEGRALE (ADMIN)
# ==========================================
elif scelta_menu == "🛠️ Pannello Amministrazione" and st.session_state.role == "admin":
    st.title("🛠️ Pannello Amministrazione ed Omologazione")

    tab_partita, tab_omologa, tab_rosa, tab_utenti, tab_logs = st.tabs([
        "➕ Nuova Partita", 
        "⚖️ Omologazione Match", 
        "🏃 Gestione Rosa", 
        "👥 Gestione Utenti",
        "📋 Log Sistema"
    ])

    # TAB 1: CREAZIONE PARTITA
    with tab_partita:
        st.subheader("Crea e Apri Nuova Partita")
        col_a, col_b = st.columns(2)
        with col_a:
            s_casa = st.text_input("Squadra Casa", value="Cagliari")
            giornata_num = st.number_input("Numero Giornata", min_value=1, max_value=38, value=1)
        with col_b:
            s_trasferta = st.text_input("Squadra Trasferta")
            comp_name = st.text_input("Competizione", value="Serie A")

        col_d, col_t = st.columns(2)
        with col_d:
            d_limite = st.date_input("Data Limite Pronostici", datetime.date.today())
        with col_t:
            t_limite = st.time_input("Ora Limite Pronostici", datetime.time(15, 0))

        str_limite_completa = f"{d_limite} {t_limite.strftime('%H:%M:%S')}"

        if st.button("🚀 Pubblica Partita", use_container_width=True):
            if s_casa and s_trasferta:
                run_query("""
                    INSERT INTO partite (squadra_casa, squadra_trasferta, data_ora_limite, giornata, competizione, stato) 
                    VALUES (?, ?, ?, ?, ?, 'aperta')
                """, (s_casa, s_trasferta, str_limite_completa, giornata_num, comp_name))
                log_admin_action(st.session_state.user, f"Creata partita {s_casa} vs {s_trasferta}")
                st.success("Partita pubblicata con successo!")
                st.rerun()
            else:
                st.error("Inserire entrambe le squadre per continuare.")

    # TAB 2: OMOLOGAZIONE MATCH E CALCOLO PUNTEGGI AUTOMATICO
    with tab_omologa:
        st.subheader("Omologazione Risultati Reali")
        partite_da_omologare = run_query("SELECT id_partita, squadra_casa, squadra_trasferta FROM partite WHERE stato = 'aperta'", fetch="all")

        if not partite_da_omologare:
            st.info("Nessuna partita in attesa di omologazione.")
        else:
            dict_om = {f"ID {p[0]}: {p[1]} vs {p[2]}": p[0] for p in partite_da_omologare}
            match_sel_str = st.selectbox("Seleziona Incontro", list(dict_om.keys()))
            id_p_om = dict_om[match_sel_str]

            c_res1, c_res2 = st.columns(2)
            with c_res1:
                res_c_real = st.number_input("Gol Reali Casa", min_value=0, max_value=25, value=0, key="om_real_c")
            with c_res2:
                res_t_real = st.number_input("Gol Reali Trasferta", min_value=0, max_value=25, value=0, key="om_real_t")

            st.divider()
            st.subheader("Marcatori Reali Incontro")
            rosa_db = run_query("SELECT nome_giocatore FROM rosa WHERE attivo = 1 ORDER BY nome_giocatore ASC", fetch="all")
            lista_rosa = [r[0].strip() for r in rosa_db] if rosa_db else []

            m_reali_sel = st.multiselect("Seleziona marcatori che hanno segnato", options=lista_rosa, key="om_m_select")
            
            m_reali_finali = []
            if m_reali_sel:
                for mr in m_reali_sel:
                    cnt_m = st.number_input(f"Numero gol segnati da {mr}", min_value=1, max_value=10, value=1, key=f"om_cnt_{mr}")
                    m_reali_finali.extend([mr] * cnt_m)

            str_m_reali = ", ".join(m_reali_finali)

            st.divider()
            if st.button("⚖️ Omologa Partita e Assegna Punti", use_container_width=True):
                # 1. Chiusura partita ed inserimento dati reali
                run_query("""
                    UPDATE partite 
                    SET risultato_casa = ?, risultato_trasferta = ?, marcatori_reali = ?, stato = 'chiusa' 
                    WHERE id_partita = ?
                """, (res_c_real, res_t_real, str_m_reali, id_p_om))

                # 2. Rilevamento pronostici e calcolo tramite algoritmo esatto
                pronostici_match = run_query("""
                    SELECT id_pronostico, gol_casa, gol_trasferta, marcatori_pronostico 
                    FROM pronostici 
                    WHERE id_partita = ?
                """, (id_p_om,), fetch="all")

                for pr in pronostici_match:
                    id_pr, p_c, p_t, m_p = pr[0], pr[1], pr[2], pr[3]
                    p_esito, p_marcatori, p_totali = calcola_punteggio_pronostico(p_c, p_t, res_c_real, res_t_real, m_p, str_m_reali)
                    
                    run_query("""
                        UPDATE pronostici 
                        SET punti_esito = ?, punti_marcatori = ?, punti_assegnati = ? 
                        WHERE id_pronostico = ?
                    """, (p_esito, p_marcatori, p_totali, id_pr))

                log_admin_action(st.session_state.user, f"Omologata partita ID {id_p_om}")
                st.success("Omologazione salvata e punti distribuiti agli utenti!")
                st.rerun()

    # TAB 3: GESTIONE ROSA
    with tab_rosa:
        st.subheader("Aggiungi Giocatore alla Rosa")
        col_g1, col_g2 = st.columns(2)
        with col_g1:
            new_player = st.text_input("Nome e Cognome Giocatore")
        with col_g2:
            role_player = st.selectbox("Ruolo", ["Portiere", "Difensore", "Centrocampista", "Attaccante"])

        if st.button("➕ Aggiungi Giocatore"):
            if new_player:
                new_player_clean = new_player.strip()
                run_query("INSERT INTO rosa (nome_giocatore, ruolo, attivo) VALUES (?, ?, 1)", (new_player_clean, role_player))
                log_admin_action(st.session_state.user, f"Aggiunto giocatore {new_player_clean}")
                st.success(f"Giocatore {new_player_clean} aggiunto correttamente!")
                st.rerun()

        st.divider()
        st.subheader("Rosa Attuale")
        rosa_db = run_query("SELECT id_giocatore, nome_giocatore, ruolo, attivo FROM rosa ORDER BY nome_giocatore ASC", fetch="all")
        if rosa_db:
            df_rosa = pd.DataFrame(rosa_db, columns=["ID", "Nome Giocatore", "Ruolo", "Stato Attivo"])
            st.dataframe(df_rosa, use_container_width=True)

    # TAB 4: GESTIONE UTENTI
    with tab_utenti:
        st.subheader("Registra Nuovo Utente")
        u_name = st.text_input("Username", key="create_u_name")
        u_pass = st.text_input("Password", type="password", key="create_u_pass")
        u_role = st.selectbox("Ruolo", ["user", "admin"], key="create_u_role")

        if st.button("👤 Crea Account"):
            if u_name and u_pass:
                try:
                    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    run_query("INSERT INTO utenti (username, password, ruolo, data_iscrizione) VALUES (?, ?, ?, ?)", (u_name.strip(), u_pass, u_role, now_str))
                    log_admin_action(st.session_state.user, f"Registrato nuovo utente {u_name.strip()}")
                    st.success(f"Utente {u_name.strip()} registrato con successo!")
                except sqlite3.IntegrityError:
                    st.error("Username già registrato nel database.")

        st.divider()
        st.subheader("Utenti Registrati")
        utenti_db = run_query("SELECT username, ruolo, data_iscrizione FROM utenti", fetch="all")
        if utenti_db:
            st.dataframe(pd.DataFrame(utenti_db, columns=["Username", "Ruolo", "Data Iscrizione"]), use_container_width=True)

    # TAB 5: LOG DI SISTEMA
    with tab_logs:
        st.subheader("Registro Log Operazioni Amministrative")
        logs = run_query("SELECT id_log, admin_username, azione, timestamp FROM log_admin ORDER BY id_log DESC", fetch="all")
        if logs:
            st.dataframe(pd.DataFrame(logs, columns=["ID Log", "Admin", "Azione Eseguita", "Data/Ora"]), use_container_width=True)
        else:
            st.info("Nessuna operazione registrata nei log.")


# ==========================================
# 12. FOOTER DI CHIUSURA DELL'APPLICAZIONE
# ==========================================
def mostra_footer():
    st.markdown("""
        <div class="cugurra-footer">
            Premio Cugurra v2.4 &copy; 2026 — Schedine & Statistiche Web App | Powered by Streamlit & SQLite
        </div>
    """, unsafe_allow_html=True)

mostra_footer()
