import streamlit as st
import requests
from bs4 import BeautifulSoup
from google import genai

# ==============================================================================
# CONFIGURATION DE LA PAGE & STYLISATION (THÈME CLAIR PUBNARRATIVES)
# ==============================================================================
st.set_page_config(
    page_title="PubNarratives Studio | Moteur Rythmique Capillaire",
    page_icon="🎬",
    layout="wide"
)

st.markdown("""
<style>
    .main {
        background-color: #FDFBF7;
        color: #1C1917;
    }
    .stButton>button {
        background-color: #D97706;
        color: white;
        border-radius: 8px;
        font-weight: bold;
        border: none;
        padding: 0.6rem 1.2rem;
    }
    .stButton>button:hover {
        background-color: #B45309;
        color: white;
    }
    .badge-niche {
        background-color: #EFEAE1;
        color: #845309;
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 700;
        text-transform: uppercase;
    }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# OUTILS D'EXTRACTION DU CONTENU PRODUIT DEPUIS L'URL
# ==============================================================================
def extraire_donnees_url(url: str) -> dict:
    """
    Extrait les balises sémantiques et descriptifs de la fiche produit.
    """
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    
    # 1. Tentative via Jina Reader
    try:
        jina_url = f"https://r.jina.ai/{url}"
        response = requests.get(jina_url, headers=headers, timeout=10)
        if response.status_code == 200 and len(response.text) > 200:
            return {
                "source": "jina",
                "texte": response.text[:4000],
                "url": url
            }
    except Exception:
        pass

    # 2. Repli BeautifulSoup direct
    try:
        res = requests.get(url, headers=headers, timeout=8)
        soup = BeautifulSoup(res.text, 'html.parser')
        
        titre = soup.find('title').get_text() if soup.find('title') else ""
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        description = meta_desc['content'] if meta_desc and 'content' in meta_desc.attrs else ""
        paragraphes = " ".join([p.get_text().strip() for p in soup.find_all('p')[:8]])
        
        contenu_agrege = f"TITRE: {titre}\nDESCRIPTION: {description}\nCONTENU: {paragraphes}"
        return {
            "source": "scraping_direct",
            "texte": contenu_agrege[:3500],
            "url": url
        }
    except Exception as e:
        return {
            "source": "erreur",
            "texte": f"Impossible d'extraire automatiquement l'URL ({str(e)}).",
            "url": url
        }

# ==============================================================================
# MOTEUR DE GÉNÉRATION RYTHMIQUE STORYBRAND & KAREN PEARLMAN (GEMINI)
# ==============================================================================
def orchestrer_production_rythmique(api_key: str, model_name: str, url_data: dict, niche_focus: str):
    """
    Génère le script et le découpage selon les principes de Cutting Rhythms (Karen Pearlman).
    """
    system_prompt = f"""
    Tu es un Directeur Artistique et Monteur Publicitaire d'élite, certifié StoryBrand (Donald Miller) et maître du découpage rythmique (théorie de Karen Pearlman dans 'Cutting Rhythms').
    PubNarratives produit des spots publicitaires narratifs verticaux (9:16) pour des marques e-commerce de soins capillaires.
    
    NICHE ACTIVE : {niche_focus} (Brosses démêlantes, peignes ergonomiques, bonnets chauffants en lin, bonnets en satin réversibles, serviettes en bambou, etc.).
    
    CONSIGNES DE DIRECTION ÉDITORIALE & NOMENCLATURE :
    - N'invente aucun nom de produit fantaisiste. Utilise obligatoirement la formule naturelle : "Chez [Nom de la Marque], [Nom générique exact de l'outil]".
    - Exemple : "Chez Atelier Kambia, cette brosse démêlante flexible..." ou "Chez Atelier Kambia, ce bonnet en satin réversible...".
    - Le client est le HÉROS, l'outil est le GUIDE qui lui permet de remporter sa journée face à la douleur capillaire (casse, traction, nœuds, assèchement).
    
    CONSIGNES RYTHMIQUES AVANCÉES (KAREN PEARLMAN - 'CUTTING RHYTHMS') :
    Le dynamisme ne vient pas d'un découpage stérile de plans uniformément courts. Il provient d'une composition alternant micro-pulsations, phrasés de trajectoire et modulations de tension/relâchement :
    1. TIMING & CADENCE (Pacing) : Structure entre 8 et 12 plans rythmés sur 45 secondes (durées dynamiques de 1.5s à 5s selon l'intensité émotionnelle et physique de l'action).
    2. TRAJECTORY PHRASING (Phrasé d'Énergie) : Pour chaque raccord entre deux plans, définis s'il s'agit d'une 'COLLISION' (choc visuel, rupture d'axe, contraste brutal pour susciter la tension) ou d'un 'LINKAGE' (continuité de mouvement fluide, match on action pour prolonger l'énergie).
    3. THROWING THE ENERGY : Chaque plan doit 'jeter' une intention cinétique ou émotionnelle que le plan suivant 'reçoit' ou amplifie.
    4. ACCENTS & RESPIRATIONS : Les plans de crise/douleur sont syncopés et serrés ; le plan de révélation de l'outil est magnifié et stabilisé ; les plans d'usage fluide créent un soulagement sensoriel (ASMR).
    5. CONTINUITÉ DU PRODUIT : Pour le plan de démonstration du produit, ordonne au prompt IA :
       'incorporating the uploaded reference image of the product to ensure exact visual branding consistency'.
    """

    user_prompt = f"""
    ANALYSE CE PRODUIT ET COMPOSE LE MASTER RYTHMIQUE :
    URL : {url_data['url']}
    Informations extraites de la boutique :
    \"\"\"{url_data['texte']}\"\"\"

    LIVRABLE EXIGÉ AU FORMAT SUIVANT :
    =======================================================
    1. BRANDSCRIPT SB7 SYNTHÉTIQUE (Héros, Vilain, Problème Interne, Guide, Plan, Succès)
    =======================================================
    2. SCRIPT VOIX OFF GLOBAL (Chronométré pour 45s / ~110-125 mots français parlés)
    =======================================================
    3. STORYBOARD RYTHMIQUE PEARLMAN (Format 9:16 Vertical, 8 à 12 plans)
    Pour chaque plan :
       - PLAN N° [Timecode précis : ex. 00s-02s] | DURÉE : [ex. 2s]
       - RÔLE RYTHMIQUE : [Tension / Choc / Respiration / Relâchement / Climax]
       - VOIX OFF : [Extrait exact correspondant]
       - PHRASÉ DE TRAJECTOIRE : [COLLISION d'énergie OU LIAISON cinétique (Linkage) avec le plan précédent]
       - STOCK FOOTAGE B-ROLL : [5 à 7 mots-clés de recherche vidéo en anglais]
       - PROMPT VIDÉO IA (Anglais) : [Description cinématique 9:16 ultra-précise, incluant la clause d'image de référence pour le produit]
       - SOUND DESIGN & STRESS : [Ponctuation sonore, bruitage ASMR, impact ou transition de souffle]
    =======================================================
    4. NOTE D'INTENTION MUSICALE & CHORÉGRAPHIQUE (BPM conseillé, instruments, modulation des basses)
    """

    client = genai.Client(api_key=api_key)
    full_prompt = f"{system_prompt}\n\n{user_prompt}"
    
    response = client.models.generate_content(
        model=model_name,
        contents=full_prompt
    )
    return response.text

# ==============================================================================
# INTERFACE UTILISATEUR
# ==============================================================================
def main():
    st.markdown('<span class="badge-niche">Niche Active : Outils & Accessoires Capillaires</span>', unsafe_allow_html=True)
    st.title("🎬 PubNarratives Rythmic Studio Engine")
    st.markdown("Générateur de spots publicitaires à fort impact narratif et cinétique (Framework StoryBrand + Théorie du Rythme de Karen Pearlman).")
    st.divider()

    # Détection automatique de la clé dans les Secrets Streamlit
    cle_secrete = ""
    if "GEMINI_API_KEY" in st.secrets:
        cle_secrete = st.secrets["GEMINI_API_KEY"]

    # Barre latérale
    with st.sidebar:
        st.header("🔑 Clé API Google")
        api_key_input = st.text_input(
            "Clé API Gemini",
            value=cle_secrete,
            type="password",
            placeholder="AIzaSy...",
            help="Détectée automatiquement depuis st.secrets si configurée."
        )
        
        if cle_secrete and api_key_input == cle_secrete:
            st.success("✅ Clé API détectée via st.secrets")
            
        st.caption("Gérez vos clés sur [aistudio.google.com](https://aistudio.google.com).")
        
        model_name = st.selectbox(
            "Modèle Gemini Actif",
            ["gemini-3.8-flash", "gemini-3.7-flash", "gemini-3.5-flash-lite"],
            index=0,
            help="gemini-3.8-flash est le modèle préconisé pour l'analyse publicitaire et la mise en scène complexe."
        )

    # Zone centrale
    st.subheader("🔗 Produit à orchestrer")
    url_input = st.text_input(
        "Collez l'URL de la fiche produit (brosse, bonnet en satin, bonnet chauffant, etc.) :",
        value="https://atelier-kambia.fr/products/bonnet-en-satin-reversible-avec-cordon-reglable-taille-unique"
    )

    if st.button("🚀 Extraire & Composer le Découpage Rythmique", use_container_width=True):
        api_key_finale = api_key_input.strip()
        
        if not api_key_finale:
            st.error("⚠️ Veuillez renseigner votre clé API Gemini (dans la barre latérale ou via st.secrets).")
            return

        with st.status("🛠️ Composition du flux publicitaire dynamique...", expanded=True) as status:
            st.write("1. Extraction des atouts de la fiche produit...")
            donnees_url = extraire_donnees_url(url_input)
            
            if donnees_url["source"] == "erreur":
                st.warning("Scraping direct limité par le site hôte. Utilisation des paramètres contextuels de l'URL.")
                donnees_url["texte"] = f"Produit extrait de l'URL : {url_input}. Bonnet en satin réversible ajustable pour préserver l'hydratation, réduire la friction nocturne et éliminer la casse des boucles."

            st.write(f"2. Orchestration StoryBrand et découpage cinétique Karen Pearlman ({model_name})...")
            try:
                resultat = orchestrer_production_rythmique(
                    api_key=api_key_finale,
                    model_name=model_name,
                    url_data=donnees_url,
                    niche_focus="Outils et Soins Capillaires Texturés (3A à 4C)"
                )
                status.update(label="✅ Master rythmique composé avec succès !", state="complete", expanded=False)
                
                st.subheader("🎬 Livrable de Production Publicitaire")
                st.markdown(resultat)

                st.download_button(
                    label="💾 Télécharger le dossier de tournage et montage (.txt)",
                    data=resultat,
                    file_name="PubNarratives_Rythmic_Master.txt",
                    mime="text/plain",
                    use_container_width=True
                )
            except Exception as e:
                status.update(label="❌ Erreur de génération", state="error")
                st.error(f"Erreur API Gemini : {str(e)}")

if __name__ == "__main__":
    main()
