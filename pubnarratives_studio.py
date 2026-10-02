import streamlit as st
import requests
from bs4 import BeautifulSoup
from google import genai

# ==============================================================================
# CONFIGURATION DE LA PAGE & STYLISATION (THÈME CLAIR PUBNARRATIVES)
# ==============================================================================
st.set_page_config(
    page_title="PubNarratives Studio | Moteur Démo Capillaire",
    page_icon="✨",
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
    Extrait les balises sémantiques, le texte et les descriptifs depuis l'URL du produit.
    """
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    
    # 1. Tentative via Jina Reader (Transformation en Markdown)
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
# MOTEUR DE GÉNÉRATION D'EXPERTISE NARRATIVE (GOOGLE GEMINI)
# ==============================================================================
def orchestrer_production_gemini(api_key: str, model_name: str, url_data: dict, niche_focus: str):
    """
    Exécute le prompt maître de Direction Artistique via le SDK Google GenAI.
    """
    system_prompt = f"""
    Tu es le Directeur Artistique en chef et Concepteur-Rédacteur certifié StoryBrand chez PubNarratives.
    PubNarratives crée des spots publicitaires narratifs de 45 à 60 secondes au format vertical (9:16) pour des marques e-commerce.
    
    NICHE ACTIVE : {niche_focus} (Englobe tous les outils de soin capillaire : brosses démêlantes, peignes, bonnets chauffants, bonnets en satin, serviettes microfibre, etc.).
    
    TON OBJECTIF :
    À partir des informations brutes de la page produit fournie, génère un livrable complet de production prêt pour le tournage et le montage.
    
    RÈGLES DE NOMENCLATURE DU PRODUIT :
    - N'invente jamais de nom de produit imaginaire. Utilise toujours la formule : "Chez [Nom de la Marque], [Nom générique du produit]".
    - Exemple : "Chez Atelier Kambia, notre brosse démêlante flexible..." ou "Chez Atelier Kambia, ce bonnet en satin réversible...".
    
    RÈGLES STORYBRAND (SB7) STRICTES :
    - Le client est le HÉROS, l'outil est le GUIDE qui lui permet de remporter sa journée.
    - Ancre le script sur une DOULEUR VISCÉRALE liée aux cheveux texturés (casse, traction au réveil ou au démêlage, déshydratation, friction du coton, temps perdu).
    - Zéro jargon théorique : style direct, punchy, naturel et persuasif.
    
    RÈGLE DE MONTAGE & SÉQUENÇAGE VIDÉO :
    - Structure entre 5 et 7 séquences rythmées.
    - Pour CHAQUE séquence :
        1. Timecode précis et extrait exact de la voix off.
        2. 5 à 7 MOTS-CLÉS DE RECHERCHE VIDÉO EN ANGLAIS pour trouver des capsules B-Roll en stock vidéo.
        3. PROMPT VIDÉO IA EN ANGLAIS ultra-descriptif (sujet, cadrage vertical 9:16, mouvement de caméra, éclairage).
        4. CLAUSE OBLIGATOIRE DU PRODUIT : Pour la séquence où l'outil entre en scène, le prompt IA DOIT impérativement intégrer la mention :
           'incorporating the uploaded reference image of the product to ensure exact visual branding consistency'.
    """

    user_prompt = f"""
    ANALYSE CE PRODUIT ET CRÉE LA DÉMO :
    URL du produit : {url_data['url']}
    Données extraites de la boutique :
    \"\"\"{url_data['texte']}\"\"\"

    FOURNIS LE DOSSIER STRUCTURÉ EXACTEMENT COMME SUIT :
    1. BRANDSCRIPT SB7 DE POSITIONNEMENT (Synthétique)
    2. SCRIPT VOIX OFF GLOBAL (Format 45s à 60s, ~110-130 mots français, chronométré)
    3. STORYBOARD DÉTAILLÉ (Séquence par séquence avec Timecode, Voix Off, Mots-clés B-Roll en anglais, Prompt IA en anglais, Sound Design)
    4. RECOMMANDATIONS SOUND DESIGN (Style musical, tempo BPM, bruitages ASMR/SFX)
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
    st.markdown('<span class="badge-niche">Niche Active : Soins & Accessoires Capillaires</span>', unsafe_allow_html=True)
    st.title("⚡ PubNarratives Demo Production Engine")
    st.markdown("Transformez l'URL d'un outil de soin capillaire en un dossier de production publicitaire complet (StoryBrand SB7 + Prompts IA + Mots-clés B-Roll).")
    st.divider()

    # Détection de la clé dans les Secrets Streamlit
    cle_secrete = ""
    if "GEMINI_API_KEY" in st.secrets:
        cle_secrete = st.secrets["GEMINI_API_KEY"]

    # Barre latérale : Clé Google Gemini & Modèles récents
    with st.sidebar:
        st.header("🔑 Clé API Google")
        
        api_key_input = st.text_input(
            "Clé API Gemini",
            value=cle_secrete,
            type="password",
            placeholder="AIzaSy...",
            help="Récupérée automatiquement depuis les Secrets Streamlit si configurée."
        )
        
        if cle_secrete and api_key_input == cle_secrete:
            st.success("✅ Clé API détectée via st.secrets")
            
        st.caption("Gérez ou générez vos clés sur [aistudio.google.com](https://aistudio.google.com).")
        
        model_name = st.selectbox(
            "Modèle Gemini",
            ["gemini-3.8-flash", "gemini-3.7-flash", "gemini-3.5-flash-lite"],
            index=0,
            help="gemini-3.8-flash est le modèle recommandé par l'API pour la génération et le raisonnement long horizon."
        )

    # Zone centrale
    st.subheader("🔗 Produit à analyser")
    url_input = st.text_input(
        "Collez l'URL de la fiche produit :",
        value="https://atelier-kambia.fr/products/bonnet-en-satin-reversible-avec-cordon-reglable-taille-unique"
    )

    if st.button("🚀 Extraire & Générer la Démo", use_container_width=True):
        api_key_finale = api_key_input.strip()
        
        if not api_key_finale:
            st.error("⚠️ Veuillez renseigner votre clé API Gemini (manuellement ou dans les Secrets Streamlit).")
            return

        with st.status("🛠️ Génération du flux publicitaire...", expanded=True) as status:
            st.write("1. Extraction du contenu de la boutique...")
            donnees_url = extraire_donnees_url(url_input)
            
            if donnees_url["source"] == "erreur":
                st.warning("Scraping direct limité par le site hôte. Utilisation des données contextuelles du produit.")
                donnees_url["texte"] = f"Produit capillaire extrait depuis l'URL : {url_input}. Outil ergonomique ou de protection de la fibre (bonnet en satin, brosse démêlante ou accessoire de soin)."

            st.write(f"2. Génération du BrandScript, du script voix off et des prompts via {model_name}...")
            try:
                resultat = orchestrer_production_gemini(
                    api_key=api_key_finale,
                    model_name=model_name,
                    url_data=donnees_url,
                    niche_focus="Outils et Accessoires pour Cheveux Texturés (3A à 4C)"
                )
                status.update(label="✅ Dossier de production généré avec succès !", state="complete", expanded=False)
                
                st.subheader("🎬 Dossier de Production")
                st.markdown(resultat)

                st.download_button(
                    label="💾 Télécharger le dossier complet (.txt)",
                    data=resultat,
                    file_name="PubNarratives_Production.txt",
                    mime="text/plain",
                    use_container_width=True
                )
            except Exception as e:
                status.update(label="❌ Erreur lors de la génération", state="error")
                st.error(f"Erreur API Gemini : {str(e)}")

if __name__ == "__main__":
    main()
