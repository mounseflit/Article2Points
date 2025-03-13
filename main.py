import streamlit as st
import requests
from bs4 import BeautifulSoup
import re
import json
import urllib.parse
import os
import shutil



def scrape_text_from_url(url):

    response = requests.get(url)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch the URL: {url}")
    soup = BeautifulSoup(response.content, 'html.parser')
    for script_or_style in soup(['script', 'style']):
        script_or_style.decompose()
    text = soup.get_text()
    text = re.sub(r'\s+', ' ', text).strip()

    return text


def call_llm_api(article_text, slidenumber , wordnumber, language):

    api_url = "https://a.picoapps.xyz/ask-ai?prompt="
    prompt = '''Article scraped text and content and Data : '''  + article_text + ''' 
    Task :  You are an llm in json mode now, you generate directly a json, no more, no less, where you summarize this article in '''  +  str(slidenumber) + ''' bullet points in a journalist narrative reporting style format that highlight the main key points from the article, and keep the coherence between each bullet point like a story video content, make it in '''  + language + ''' and dont use Unicodes like "u00e9" put a real "é".
    NB:  Make '''  +  str(slidenumber) + ''' short bullet points (arround ''' +  str(wordnumber) + ''' words max per each) in a narrative style like a reporter and all these bullet points summarize and narrate it in a great way that gives the user a great general idea about the article and don't miss the main ideas but try to keep the flow running and coherence between each bullet point in a way where you can read them and feel like you are reading one article. and there is '''  +  str(slidenumber) + ''' bullet point and dont forget that you need to genertare a '''  + language + ''' text.
    Example :  {"summary": ["Bullet point 1", "Bullet point 2", "Bullet point 3",...], "Total": "x" , "Tone": "Tone of the best voice over for it"}
    IMPORTANT : The article text is the only input you have, you can't use any other data or information, you can't use any other source or external data, dont helucinate, dont imagine, dont make up, dont add, dont remove, dont change, dont modify, dont do anything else, just summarize the article in bullet points format that highlight the main key points from the article, no Unicodes, and do it in '''  + language + ''' and Focus on Generating the right characthers and not giving Unicode like in french use é,à,è,ù... please never generate Unicodes.and for numbers dont put a "." like in "1.600" write directly "1600"; and if mentioned use "S.M. ..." for King Mohammed VI. and generate only the json no intro no outro no nothing else, just the json, no more, no less.
    '''
    
    encoded_prompt = urllib.parse.quote(prompt)
    full_url = f"{api_url}{encoded_prompt}"
    response = requests.get(full_url)
    if response.status_code != 200:
        raise Exception(f"Failed to call the LLM API: {response.status_code}")
    result = response.json()

    return result


def save_and_clean_json(response, file_path):
    # First, handle the case where response is a string
    if isinstance(response, str):
        response = json.loads(response.replace('\n', '').replace('\\', ''))
    
    # If response is a dict and contains 'response' key
    if isinstance(response, dict) and 'response' in response:
        response = response['response']
        # If response is still a string, parse it
        if isinstance(response, str):
            response = json.loads(response.replace('\n', '').replace('\\', ''))

    # Write the cleaned JSON to file
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(response, f, ensure_ascii=False, indent=4)
    
    return response


def fix_unicode(text):
     # Preprocess text - replace common Unicode characters
    # French characters
    text = text.replace('\\u00e9', 'é').replace('\\u00e8', 'è').replace('\\u00ea', 'ê')
    text = text.replace('\\u00e0', 'à').replace('\\u00e2', 'â').replace('\\u00f9', 'ù')
    text = text.replace('\\u00fb', 'û').replace('\\u00ee', 'î').replace('\\u00ef', 'ï')
    text = text.replace('\\u00e7', 'ç').replace('\\u0153', 'œ').replace('\\u00e6', 'æ')
    text = text.replace('\\u20ac', '€').replace('\\u00ab', '«').replace('\\u00bb', '»')
    text = text.replace('\\u2013', '–').replace('\\u2014', '—').replace('\\u2018', '‘')
    text = text.replace('\\u2019', '’').replace('\\u201a', '‚').replace('\\u201c', '“')
    text = text.replace('\\u201d', '”').replace('\\u201e', '„').replace('\\u2026', '…')
    text = text.replace('\\u2030', '‰').replace('\\u0152', 'Œ').replace('\\u00a0', ' ')
    text = text.replace('\\u00b0', '°').replace('\\u00a3', '£').replace('\\u00a7', '§')
    text = text.replace('\\u00b7', '·').replace('\\u00bf', '¿').replace('\\u00a9', '©')
    text = text.replace('\\u00ae', '®').replace('\\u2122', '™').replace('\\u00bc', '¼')
    text = text.replace('\\u00bd', '½').replace('\\u00be', '¾').replace('\\u00b1', '±')
    text = text.replace('\\u00d7', '×').replace('\\u00f7', '÷').replace('\\u00a2', '¢')
    text = text.replace('\\u00a5', '¥').replace('\\u00ac', '¬').replace('\\u00b6', '¶')
    text = text.replace('\\u2022', '•')

    # Spanish characters
    text = text.replace('\\u00f1', 'ñ').replace('\\u00ed', 'í').replace('\\u00f3', 'ó')
    text = text.replace('\\u00fa', 'ú').replace('\\u00fc', 'ü').replace('\\u00a1', '¡')
    text = text.replace('\\u00bf', '¿').replace('\\u00e1', 'á').replace('\\u00e9', 'é')
    text = text.replace('\\u00f3', 'ó').replace('\\u00fa', 'ú').replace('\\u00fc', 'ü')
    # German characters
    text = text.replace('\\u00df', 'ß').replace('\\u00e4', 'ä').replace('\\u00f6', 'ö')
    text = text.replace('\\u00fc', 'ü')

    # Italian characters
    text = text.replace('\\u00e0', 'à').replace('\\u00e8', 'è').replace('\\u00e9', 'é')
    text = text.replace('\\u00ec', 'ì').replace('\\u00f2', 'ò').replace('\\u00f9', 'ù')
    text = text.replace('\\u00f9', 'ù')

    # Russian characters
    text = text.replace('\\u0410', 'А').replace('\\u0411', 'Б').replace('\\u0412', 'В')
    text = text.replace('\\u0413', 'Г').replace('\\u0414', 'Д').replace('\\u0415', 'Е')
    text = text.replace('\\u0416', 'Ж').replace('\\u0417', 'З').replace('\\u0418', 'И')
    text = text.replace('\\u0419', 'Й').replace('\\u041a', 'К').replace('\\u041b', 'Л')
    text = text.replace('\\u041c', 'М').replace('\\u041d', 'Н').replace('\\u041e', 'О')
    text = text.replace('\\u041f', 'П').replace('\\u0420', 'Р').replace('\\u0421', 'С')
    text = text.replace('\\u0422', 'Т').replace('\\u0423', 'У').replace('\\u0424', 'Ф')
    text = text.replace('\\u0425', 'Х').replace('\\u0426', 'Ц').replace('\\u0427', 'Ч')
    text = text.replace('\\u0428', 'Ш').replace('\\u0429', 'Щ').replace('\\u042a', 'Ъ')
    text = text.replace('\\u042b', 'Ы').replace('\\u042c', 'Ь').replace('\\u042d', 'Э')
    text = text.replace('\\u042e', 'Ю').replace('\\u042f', 'Я').replace('\\u0430', 'а')
    text = text.replace('\\u0431', 'б').replace('\\u0432', 'в').replace('\\u0433', 'г')
    text = text.replace('\\u0434', 'д').replace('\\u0435', 'е').replace('\\u0436', 'ж')
    text = text.replace('\\u0437', 'з').replace('\\u0438', 'и').replace('\\u0439', 'й')
    text = text.replace('\\u043a', 'к').replace('\\u043b', 'л').replace('\\u043c', 'м')
    text = text.replace('\\u043d', 'н').replace('\\u043e', 'о').replace('\\u043f', 'п')
    text = text.replace('\\u0440', 'р').replace('\\u0441', 'с').replace('\\u0442', 'т')
    text = text.replace('\\u0443', 'у').replace('\\u0444', 'ф').replace('\\u0445', 'х')
    text = text.replace('\\u0446', 'ц').replace('\\u0447', 'ч').replace('\\u0448', 'ш')
    text = text.replace('\\u0449', 'щ').replace('\\u044a', 'ъ').replace('\\u044b', 'ы')
    text = text.replace('\\u044c', 'ь').replace('\\u044d', 'э').replace('\\u044e', 'ю')
    text = text.replace('\\u044f', 'я')
    
    # Arabic characters - generic replacement for common encoding issues
    text = text.replace('\\u0627', 'ا').replace('\\u064a', 'ي').replace('\\u0644', 'ل')
    text = text.replace('\\u062a', 'ت').replace('\\u0646', 'ن').replace('\\u0633', 'س')
    text = text.replace('\\u0645', 'م').replace('\\u0631', 'ر').replace('\\u0648', 'و')
    text = text.replace('\\u0639', 'ع').replace('\\u062f', 'د').replace('\\u0628', 'ب')
    text = text.replace('\\u0649', 'ى').replace('\\u0629', 'ة').replace('\\u062c', 'ج')
    text = text.replace('\\u0642', 'ق').replace('\\u0641', 'ف').replace('\\u062d', 'ح')
    text = text.replace('\\u0635', 'ص').replace('\\u0637', 'ط').replace('\\u0632', 'ز')
    text = text.replace('\\u0634', 'ش').replace('\\u063a', 'غ').replace('\\u062e', 'خ')
    text = text.replace('\\u0623', 'أ').replace('\\u0621', 'ء').replace('\\u0624', 'ؤ')
    text = text.replace('\\u0626', 'ئ').replace('\\u0625', 'إ').replace('\\u0651', 'ّ')
    text = text.replace('\\u0652', 'ْ').replace('\\u064b', 'ً').replace('\\u064c', 'ٌ')
    text = text.replace('\\u064d', 'ٍ').replace('\\u064f', 'ُ').replace('\\u0650', 'ِ')
    text = text.replace('\\u064e', 'َ').replace('\\u0653', 'ٓ').replace('\\u0654', 'ٔ')
    text = text.replace('\\u0670', 'ٰ').replace('\\u0671', 'ٱ').replace('\\u0672', 'ٲ')
    text = text.replace('\\u0673', 'ٳ').replace('\\u0675', 'ٵ').replace('\\u0676', 'ٶ')
    text = text.replace('\\u0677', 'ٷ').replace('\\u0678', 'ٸ').replace('\\u0679', 'ٹ')
    text = text.replace('\\u067a', 'ٺ').replace('\\u067b', 'ٻ').replace('\\u067c', 'ټ')
    text = text.replace('\\u067d', 'ٽ').replace('\\u067e', 'پ').replace('\\u067f', 'ٿ')
    text = text.replace('\\u0680', 'ڀ').replace('\\u0681', 'ځ').replace('\\u0682', 'ڂ')
    text = text.replace('\\u0683', 'ڃ').replace('\\u0684', 'ڄ').replace('\\u0685', 'څ')
    text = text.replace('\\u0686', 'چ').replace('\\u0687', 'ڇ').replace('\\u0688', 'ڈ')
    text = text.replace('\\u0689', 'ډ').replace('\\u068a', 'ڊ').replace('\\u068b', 'ڋ')
    text = text.replace('\\u068c', 'ڌ').replace('\\u068d', 'ڍ').replace('\\u068e', 'ڎ')
    text = text.replace('\\u068f', 'ڏ').replace('\\u0690', 'ڐ').replace('\\u0691', 'ڑ')
    text = text.replace('\\u0692', 'ڒ').replace('\\u0693', 'ړ').replace('\\u0694', 'ڔ')
    text = text.replace('\\u0695', 'ڕ').replace('\\u0696', 'ږ').replace('\\u0697', 'ڗ')
    text = text.replace('\\u0698', 'ژ').replace('\\u0699', 'ڙ').replace('\\u069a', 'ښ')
    text = text.replace('\\u069b', 'ڛ').replace('\\u069c', 'ڜ').replace('\\u069d', 'ڝ')
    text = text.replace('\\u069e', 'ڞ').replace('\\u069f', 'ڟ').replace('\\u06a0', 'ڠ')
    text = text.replace('\\u06a1', 'ڡ').replace('\\u06a2', 'ڢ').replace('\\u06a3', 'ڣ')
    text = text.replace('\\u06a4', 'ڤ').replace('\\u06a5', 'ڥ').replace('\\u06a6', 'ڦ')
    text = text.replace('\\u06a7', 'ڧ').replace('\\u06a8', 'ڨ').replace('\\u06a9', 'ک')
    text = text.replace('\\u06aa', 'ڪ').replace('\\u06ab', 'ګ').replace('\\u06ac', 'ڬ')
    text = text.replace('\\u06ad', 'ڭ').replace('\\u06ae', 'ڮ').replace('\\u06af', 'گ')
    text = text.replace('\\u06b0', 'ڰ').replace('\\u06b1', 'ڱ').replace('\\u06b2', 'ڲ')
    text = text.replace('\\u06b3', 'ڳ').replace('\\u06b4', 'ڴ').replace('\\u06b5', 'ڵ')
    text = text.replace('\\u06b6', 'ڶ').replace('\\u06b7', 'ڷ').replace('\\u06b8', 'ڸ')
    text = text.replace('\\u06b9', 'ڹ').replace('\\u06ba', 'ں').replace('\\u06bb', 'ڻ')

    return text




def main():
    st.title("Résumez vos Articles en Points Clairs pour Le Matin ✨📝")
    
    # Create sidebar for settings
    st.sidebar.header("Settings")
    language = st.sidebar.selectbox(
        "Sélectionner la langue",
        ["Anglais", "Francais", "Espagnol", "Arabe", "Allemand", "Russe", "Italien", "Portugais"],
        index=1
    )

    slidenumber = st.sidebar.slider(
        "Nombre Maximal des Points et Idées",
        min_value=2,
        max_value=20,
        value=6
    )

    wordnumber = st.sidebar.slider(
        "Nombre Maximal des Mots par Point",
        min_value=10,
        max_value=50,
        value=20
    )
   
    
    # Main content area
    
    st.subheader("Choisissez comment fournir le contenu de votre article :")
    input_method = st.radio("Sélectionnez la méthode d’entrée :", ["Entrez un URL", "Écrire/Coller le texte de l’article"])
    article_text_input = " "
    url = " "
    
    if input_method == "Entrez un URL":
        url = st.text_input("Entrez l'URL de l’article:")
        article_text_input = None
        
    else:
        article_text_input = st.text_area("Écrire ou Coller le texte de l’article :", height=300)
        url = None  # Set URL to None when using direct text input
    
    # Make sure article_text is defined in both cases
    if st.button("Créer un résumé"):
            with st.spinner("Traitement de l’article..."):
                if input_method == "Entrez un URL":  # If URL is provided
                    if not url or url.strip() == "":
                        st.error("Veuillez fournir une URL..")
                        st.stop()
                    article_text = scrape_text_from_url(url)
                    st.success("Article récupéré avec succès !")
                else:  # If direct text input is provided
                    if not article_text_input or article_text_input.strip() == "":
                        st.error("Veuillez fournir du text.")
                        st.stop()
                    article_text = article_text_input
                    st.success("Article traité avec succès !")

            with st.spinner("Génération du résumé..."):
                llm_response = call_llm_api(article_text, slidenumber, wordnumber, language)
                Json = save_and_clean_json(llm_response, "summary.json")
                st.success("Résumé généré avec succès !")

            if 'summary' in Json:
                for i, point in enumerate(Json['summary']):
                    cleaned_point = fix_unicode(point)
                    st.write(f"• {cleaned_point}")


if __name__ == "__main__":
    main()
