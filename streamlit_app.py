import streamlit as st
from supabase import create_client, Client

# Configurazione della pagina per dispositivi mobili
st.set_page_config(page_title="Premio Cugurra", page_icon="⚽", layout="centered")

# Inizializzazione della connessione a Supabase usando i dati segreti (Secrets)
@st.cache_resource
def init_connection():
    url = st.secrets["SUPABASE_URL"].strip().rstrip("/")
    key = st.secrets["SUPABASE_KEY"].strip()
    return create_client(url, key)

try:
    supabase: Client = init_connection()
except Exception as e:
    st.error("Errore di connessione al database. Verifica le credenziali nei Secrets.")
    st.stop()

st.title("⚽ Premio Cugurra")
st.write("Inserisci i tuoi pronostici per la giornata!")

# Gestione dello stato della sessione per il login
if "loggato" not in st.session_state:
    st.session_state.loggato = False
    st.session_state.utente_id = None
    st.session_state.nome_fb = ""
    st.session_state.ruolo = "tifoso"

# Schermata di Login
if not st.session_state.loggato:
    st.subheader("Accesso Utente")
    nome_input = st.text_input("Nome Facebook").strip()
    pin_input = st.text_input("PIN Segreto", type="password").strip()
    
    if st.button("Entra"):
        if nome_input and pin_input:
            # Controllo credenziali nel database
            try:
                res = supabase.table("utenti").select("id", "ruolo").eq("nome_facebook", nome_input).eq("pin_segreto", pin_input).execute()
                if res.data:
                    st.session_state.loggato = True
                    st.session_state.utente_id = res.data[0]["id"]
                    st.session_state.nome_fb = nome_input
                    st.session_state.ruolo = res.data[0]["ruolo"]
                    st.rerun()
                else:
                    st.error("Nome Facebook o PIN errati. Riprova.")
            except Exception as e:
                st.error(f"Errore durante il login: {e}")
        else:
            st.warning("Compila entrambi i campi.")

# Schermata ad accesso eseguito
else:
    st.success(f"Benvenuto, {st.session_state.nome_fb}! ({st.session_state.ruolo.upper()})")
    
    if st.button("Disconnetti"):
        st.session_state.loggato = False
        st.session_state.utente_id = None
        st.session_state.nome_fb = ""
        st.session_state.ruolo = "tifoso"
        st.rerun()
        
    st.divider()
    
    # SEZIONE ADMIN: Pannello di gestione
    if st.session_state.ruolo == "admin":
        st.subheader("🛠️ Pannello Amministratore")
        # Qui in futuro aggiungeremo le funzioni per inserire i risultati reali, calcolare i punti, ecc.
        st.info("Pannello attivo. Qui potrai gestire il gioco.")
        
    st.divider()

    # SEZIONE UTENTE: Inserimento Pronostico
    st.subheader("📝 Inserisci il tuo Pronostico")
    
    # Selezione della giornata di campionato
    giornata = st.number_input("Giornata di Campionato", min_value=1, max_value=38, value=1, step=1)
    
    # Campo di testo per i pronostici (es. Cagliari - Milan 1-1, ecc.)
    pronostico_testo = st.text_area("Scrivi qui i tuoi pronostici (es. SquadraA-SquadraB 1-0)", height=150)
    
    if st.button("Invia Pronostico"):
        if pronostico_testo.strip():
            try:
                # Controlla se esiste già un pronostico per questa giornata
                controllo = supabase.table("pronostici").select("id").eq("utente_id", st.session_state.utente_id).eq("giornata", giornata).execute()
                
                if controllo.data:
                    # Se esiste, lo aggiorna
                    supabase.table("pronostici").update({"pronostico_testo": pronostico_testo}).eq("utente_id", st.session_state.utente_id).eq("giornata", giornata).execute()
                    st.success(f"Pronostico della Giornata {giornata} aggiornato con successo!")
                else:
                    # Se non esiste, lo inserisce ex novo
                    supabase.table("pronostici").insert({
                        "utente_id": st.session_state.utente_id,
                        "giornata": giornata,
                        "pronostico_testo": pronostico_testo
                    }).execute()
                    st.success(f"Pronostico della Giornata {giornata} salvato con successo!")
            except Exception as e:
                st.error(f"Errore durante il salvataggio: {e}")
        else:
            st.warning("Il testo del pronostico non può essere vuoto.")
