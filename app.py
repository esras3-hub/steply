import streamlit as st
import google.generativeai as genai
from PIL import Image
import json
import os

# --- 1. GÜVENLİK KONTROLÜ ---
if "API_KEY" not in st.secrets:
    st.error("❌ Hata: API Anahtarı Streamlit Secrets'a eklenmemiş!")
    st.stop()

genai.configure(api_key=st.secrets["API_KEY"])
model = genai.GenerativeModel('gemini-1.5-flash')

# --- 2. HAFIZA AYARLARI ---
if "step_count" not in st.session_state: st.session_state.step_count = 1
if "current_question" not in st.session_state: st.session_state.current_question = None

# --- 3. DAYANIKLI SORU MOTORU ---
def soru_getir(metin=None, gorsel=None):
    prompt = (
        f"Sen Steply'sin. Adım {st.session_state.step_count} için bir quiz hazırlaman gerek. "
        "Sadece şu JSON formatında cevap ver, başka hiçbir açıklama yazma:\n"
        "{\"soru\": \"...\", \"A\": \"...\", \"B\": \"...\", \"C\": \"...\", \"D\": \"...\", \"dogru_cevap\": \"A\", \"aciklama\": \"...\"}"
    )
    icerik = [prompt]
    if metin: icerik.append(f"Konu: {metin}")
    if gorsel: icerik.append(gorsel)

    try:
        response = model.generate_content(icerik)
        # JSON temizleme (Kritik nokta)
        text = response.text.strip()
        if "```json" in text: text = text.split("```json")[1].split("```")[0]
        elif "```" in text: text = text.split("```")[1].split("```")[0]
        
        return json.loads(text.strip())
    except Exception as e:
        st.warning(f"Steply bir format hatası yaptı, tekrar deneniyor... (Hata: {e})")
        return None

# --- 4. ARAYÜZ VE LOGO ---
st.set_page_config(page_title="Steply", page_icon="🪜")

# Klasörde logo varsa göster
if os.path.exists("logo.png"): st.image("logo.png", width=120)
else: st.title("🪜 Steply")

# --- 5. UYGULAMA AKIŞI ---
soru_input = st.text_area("Sorunu yaz:", placeholder="Örn: Newton yasaları nedir?")
gorsel_input = st.file_uploader("Veya fotoğraf yükle", type=["jpg", "jpeg", "png"])

if st.session_state.current_question is None:
    if st.button("Öğretmeye Başla 🚀", use_container_width=True):
        if soru_input or gorsel_input:
            with st.spinner("Steply hazırlanıyor..."):
                gorsel_verisi = Image.open(gorsel_input) if gorsel_input else None
                st.session_state.current_question = soru_getir(soru_input, gorsel_verisi)
                st.rerun()

if st.session_state.current_question:
    q = st.session_state.current_question
    st.write("---")
    st.subheader(f"Adım {st.session_state.step_count}: {q.get('soru