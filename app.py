import streamlit as st
import google.generativeai as genai
from PIL import Image
import json

# --- 1. AYARLAR VE GÜVENLİK ---
try:
    API_KEY = st.secrets["API_KEY"]
    genai.configure(api_key=API_KEY)
except:
    st.error("Lütfen Streamlit Secrets'a 'API_KEY' ekleyin.")

model = genai.GenerativeModel('gemini-1.5-flash')

# --- 2. DURUM YÖNETİMİ (SESSION STATE) ---
if "step_count" not in st.session_state:
    st.session_state.step_count = 1
if "current_question" not in st.session_state:
    st.session_state.current_question = None
if "quiz_finished" not in st.session_state:
    st.session_state.quiz_finished = False

# --- 3. YARDIMCI FONKSİYON: SORU OLUŞTURUCU ---
def soru_getir(ipucu=None):
    prompt = (
        "Senin adın Steply. İnteraktif bir öğretmensin. "
        "Görevin öğrenciye bir problemde adım adım rehberlik etmek. "
        "Şu anki adım için bir çoktan seçmeli soru hazırla. "
        "CEVABINI MUTLAKA ŞU JSON FORMATINDA VER (Sadece JSON olsun, başka metin ekleme):\n"
        "{\n"
        "  'soru': 'Sıradaki adım için soru metni',\n"
        "  'A': 'Şık A',\n"
        "  'B': 'Şık B',\n"
        "  'C': 'Şık C',\n"
        "  'D': 'Şık D',\n"
        "  'dogru_cevap': 'A veya B veya C veya D',\n"
        "  'aciklama': 'Doğru cevabın neden doğru olduğuna dair kısa bir not'\n"
        "}"
    )
    # Eğer bir görsel veya metin girildiyse onu da ekle
    response = model.generate_content(prompt)
    try:
        # Gemini bazen ```json ... ``` içinde verir, onu temizliyoruz
        temiz_json = response.text.replace('```json', '').replace('```', '').strip()
        return json.loads(temiz_json)
    except:
        return None

# --- 4. ARAYÜZ ---
st.title("🪜 Steply: Tıklamalı Quiz Modu")
st.info("Doğru adımı seçerek ilerle!")

yuklenen_gorsel = st.file_uploader("Soru görselini yükle", type=["jpg", "png", "jpeg"])

if yuklenen_gorsel and st.session_state.current_question is None:
    with st.spinner("Steply ilk adımı hazırlıyor..."):
        # İlk soruyu oluştur
        st.session_state.current_question = soru_getir()

# --- 5. ETKİLEŞİM ALANI ---
if st.session_state.current_question:
    q = st.session_state.current_question
    
    st.subheader(f"Adım {st.session_state.step_count}:")
    st.write(q['soru'])

    # Şıklar için butonlar
    col1, col2 = st.columns(2)
    with col1:
        btnA = st.button(f"A) {q['A']}", use_container_width=True)
        btnB = st.button(f"B) {q['B']}", use_container_width=True)
    with col2:
        btnC = st.button(f"C) {q['C']}", use_container_width=True)
        btnD = st.button(f"D) {q['D']}", use_container_width=True)

    # Cevap Kontrolü
    secilen = None
    if btnA: secilen = "A"
    if btnB: secilen = "B"
    if btnC: secilen = "C"
    if btnD: secilen = "D"

    if secilen:
        if secilen == q['dogru_cevap']:
            st.success(f"Harika! Doğru cevap: {secilen}. \n\n {q['aciklama']}")
            if st.button("Sonraki Adıma Geç ➡️"):
                st.session_state.step_count += 1
                st.session_state.current_question = soru_getir()
                st.rerun()
        else:
            st.error(f"Maalesef yanlış. {secilen} şıkkı doğru değil. Tekrar dene!")

# --- 6. SIFIRLAMA ---
if st.sidebar.button("Dersi Sıfırla"):
    st.session_state.step_count = 1
    st.session_state.current_question = None
    st.rerun()