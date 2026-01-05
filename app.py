import streamlit as st
import google.generativeai as genai
from PIL import Image
import json
import os

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

# --- 3. SORU OLUŞTURUCU FONKSİYON ---
def soru_getir(metin_input=None, gorsel_input=None):
    # Gemini'a giden ana talimat
    sistem_komutu = (
        "Senin adın Steply. İnteraktif bir öğretmensin. "
        "Kullanıcı sana bir soru metni veya bir görsel gönderdi. "
        "Görevin bu problemi adım adım çözdürmek. "
        "Şu anki adım için (Adım {0}) bir çoktan seçmeli soru hazırla. ".format(st.session_state.step_count) +
        "CEVABINI MUTLAKA ŞU JSON FORMATINDA VER (Sadece JSON olsun):\n"
        "{\n"
        "  'soru': 'Sıradaki adım için soru metni',\n"
        "  'A': 'Şık A', 'B': 'Şık B', 'C': 'Şık C', 'D': 'Şık D',\n"
        "  'dogru_cevap': 'A/B/C/D', 'aciklama': 'Kısa not'\n"
        "}"
    )
    
    icerik = [sistem_komutu]
    if metin_input: icerik.append(f"Kullanıcı Sorusu: {metin_input}")
    if gorsel_input: icerik.append(gorsel_input)

    try:
        response = model.generate_content(icerik)
        temiz_json = response.text.replace('```json', '').replace('```', '').strip()
        return json.loads(temiz_json)
    except:
        return None

# --- 4. ARAYÜZ VE LOGO ---
st.set_page_config(page_title="Steply Quiz", page_icon="🪜")

# Logo Kontrolü
LOGO_DOSYA_ADI = "logo.png" 
if os.path.exists(LOGO_DOSYA_ADI):
    st.image(LOGO_DOSYA_ADI, width=150)
else:
    st.markdown("<h1>🪜 Steply</h1>", unsafe_allow_html=True)

st.write("### İnteraktif Çözüm Asistanı")

# --- 5. GİRİŞ ALANLARI ---
with st.container():
    st.info("İster yaz, ister fotoğraf çek. Steply seninle birlikte çözecek!")
    
    # Metin Girişi
    soru_metni = st.text_area("Sorunu buraya yaz:", placeholder="Örn: 2x + 5 = 15 denkleminde x kaçtır?", height=100)
    
    # Görsel Yükleme
    yuklenen_gorsel = st.file_uploader("Veya bir fotoğraf yükle", type=["jpg", "png", "jpeg"])

# Başlat Butonu (Sadece ilk adımda görünür)
if st.session_state.current_question is None:
    if st.button("Öğretmeye Başla 🚀", use_container_width=True):
        if soru_metni or yuklenen_gorsel:
            with st.spinner("Steply soruyu inceliyor ve ilk adımı hazırlıyor..."):
                gorsel_veri = Image.open(yuklenen_gorsel) if yuklenen_gorsel else None
                st.session_state.current_question = soru_getir(soru_metni, gorsel_veri)
                st.rerun()
        else:
            st.warning("Lütfen bir soru yazın veya fotoğraf yükleyin.")

# --- 6. ETKİLEŞİM ALANI ---
if st.session_state.current_question:
    q = st.session_state.current_question
    
    st.write("---")
    st.subheader(f"Adım {st.session_state.step_count}:")
    st.markdown(f"**{q['soru']}**")

    # Şıklar (Tıklanabilir Butonlar)
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
    elif btnB: secilen = "B"
    elif btnC: secilen = "C"
    elif btnD: secilen = "D"

    if secilen:
        if secilen == q['dogru_cevap']:
            st.success(f"✅ Harika! Doğru cevap: {secilen}. \n\n {q['aciklama']}")
            if st.button("Sonraki Adıma Geç ➡️"):
                st.session_state.step_count += 1
                # Bir sonraki soruyu mevcut bağlamla getir
                gorsel_veri = Image.open(yuklenen_gorsel) if yuklenen_gorsel else None
                st.session_state.current_question = soru_getir(soru_metni, gorsel_veri)
                st.rerun()
        else:
            st.error(f"❌ Maalesef yanlış. {secilen} şıkkı doğru değil. Tekrar düşün!")

# --- 7. SIFIRLAMA ---
if st.sidebar.button("Dersi Sıfırla / Yeni Soru"):