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

# --- 2. DURUM YÖNETİMİ ---
if "step_count" not in st.session_state:
    st.session_state.step_count = 1
if "current_question" not in st.session_state:
    st.session_state.current_question = None

# --- 3. SORU OLUŞTURUCU ---
def soru_getir(metin_input=None, gorsel_input=None):
    sistem_komutu = (
        "Senin adın Steply. İnteraktif bir öğretmensin. "
        "Görevin bu problemi adım adım çözdürmek. "
        "Şu anki adım (Adım {0}) için bir çoktan seçmeli soru hazırla. ".format(st.session_state.step_count) +
        "CEVABINI MUTLAKA ŞU JSON FORMATINDA VER:\n"
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

# --- 4. AKILLI LOGO YÜKLEYİCİ ---
st.set_page_config(page_title="Steply Quiz", page_icon="🪜")

# Klasördeki dosyaları tara ve logo olabilecek birini bul
def logoyu_bul():
    uzantilar = [".png", ".jpg", ".jpeg", ".webp"]
    # Klasördeki her dosyaya bak
    for dosya in os.listdir("."):
        if dosya.lower().startswith("logo") and any(dosya.lower().endswith(u) for u in uzantilar):
            return dosya
    return None

bulunan_logo = logoyu_bul()

if bulunan_logo:
    st.image(bulunan_logo, width=150)
else:
    # Eğer dosya hala bulunamazsa, GitHub'daki resmin doğrudan linkini kullanabilirsin
    # Örnek: st.image("https://raw.githubusercontent.com/KULLANICI_ADIN/steply/main/logo.png", width=150)
    st.markdown("<h1>🪜 Steply</h1>", unsafe_allow_html=True)
    # Debug bilgisi (Logonun neden gelmediğini anlamak için yan menüde dosya listesini gösterir)
    with st.sidebar:
        st.write("Mevcut Dosyalar:", os.listdir("."))

# --- 5. GİRİŞ ALANLARI VE UYGULAMA AKIŞI ---
# (Buradan sonrası önceki kodla aynı, sadece güvenli olması için temizledim)
st.write("### İnteraktif Çözüm Asistanı")
soru_metni = st.text_area("Sorunu yaz veya aşağıdan fotoğraf yükle:", height=100)
yuklenen_gorsel = st.file_uploader("Fotoğraf yükle", type=["jpg", "png", "jpeg"])

if st.session_state.current_question is None:
    if st.button("Öğretmeye Başla 🚀", use_container_width=True):
        if soru_metni or yuklenen_gorsel:
            with st.spinner("Steply hazırlanıyor..."):
                gorsel_veri = Image.open(yuklenen_gorsel) if yuklenen_gorsel else None
                st.session_state.current_question = soru_getir(soru_metni, gorsel_veri)
                st.rerun()

if st.session_state.current_question:
    q = st.session_state.current_question
    st.subheader(f"Adım {st.session_state.step_count}:")
    st.markdown(f"**{q['soru']}**")
    col1, col2 = st.columns(2)
    with col1:
        btnA = st.button(f"A) {q['A']}", key="btnA")
        btnB = st.button(f"B) {q['B']}", key="btnB")
    with col2:
        btnC = st.button(f"C) {q['C']}", key="btnC")
        btnD = st.button(f"D) {q['D']}", key="btnD")
    
    secilen = None
    if btnA: secilen = "A"
    elif btnB: secilen = "B"
    elif btnC: secilen = "C"
    elif btnD: secilen = "D"

    if secilen:
        if secilen == q['dogru_cevap']:
            st.success(f"✅ Doğru! {q['aciklama']}")
            if st.button("Sonraki Adıma Geç ➡️"):
                st.session_state.step_count += 1
                gorsel_veri = Image.open(yuklenen_gorsel) if yuklenen_gorsel else None
                st.session_state.current_question = soru_getir(soru_metni, gorsel_veri)
                st.rerun()
        else:
            st.error("❌ Yanlış şık, tekrar dene!")

if st.sidebar.button("Dersi Sıfırla / Yeni Soru"):
    st.session_state.step_count = 1
    st.session_state.current_question = None
    st.rerun()