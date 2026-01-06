import streamlit as st
import google.generativeai as genai
from PIL import Image
import json
import os

# --- 1. AYARLAR VE GÜVENLİK ---
# Streamlit Secrets üzerinden API anahtarını çekiyoruz
if "API_KEY" not in st.secrets:
    st.error("❌ Hata: API Anahtarı Streamlit Secrets'a eklenmemiş! Lütfen ayarlardan ekleyin.")
    st.stop()

genai.configure(api_key=st.secrets["API_KEY"])
model = genai.GenerativeModel('gemini-1.5-flash')

# --- 2. DURUM YÖNETİMİ (SESSION STATE) ---
if "step_count" not in st.session_state:
    st.session_state.step_count = 1
if "current_question" not in st.session_state:
    st.session_state.current_question = None

# --- 3. DAYANIKLI SORU MOTORU ---
def soru_getir(metin=None, gorsel=None):
    prompt = (
        f"Sen Steply'sin. İnteraktif bir öğretmensin. "
        f"Adım {st.session_state.step_count} için bir quiz hazırlaman gerek. "
        "Sadece şu JSON formatında cevap ver, başka hiçbir açıklama yazma:\n"
        "{\"soru\": \"...\", \"A\": \"...\", \"B\": \"...\", \"C\": \"...\", \"D\": \"...\", \"dogru_cevap\": \"A\", \"aciklama\": \"...\"}"
    )
    icerik = [prompt]
    if metin:
        icerik.append(f"Problem/Konu: {metin}")
    if gorsel:
        icerik.append(gorsel)

    try:
        response = model.generate_content(icerik)
        text = response.text.strip()
        # JSON temizleme (Markdown işaretlerini kaldırır)
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0]
        elif "```" in text:
            text = text.split("```")[1].split("```")[0]
        
        return json.loads(text.strip())
    except Exception as e:
        st.warning("Steply bir format hatası yaptı. Lütfen tekrar deneyin.")
        return None

# --- 4. ARAYÜZ VE LOGO ---
st.set_page_config(page_title="Steply", page_icon="🪜")

# Klasördeki logo dosyalarını kontrol et (büyük/küçük harf duyarlılığını çözer)
def logoyu_yukle():
    for dosya in os.listdir("."):
        if dosya.lower().startswith("logo") and dosya.lower().endswith((".png", ".jpg", ".jpeg", ".webp")):
            return dosya
    return None

bulunan_logo = logoyu_yukle()
if bulunan_logo:
    st.image(bulunan_logo, width=150)
else:
    st.title("🪜 Steply")

# --- 5. GİRİŞ ALANLARI ---
st.write("### İnteraktif Çözüm Asistanı")
soru_input = st.text_area("Sorunu buraya yaz veya aşağıdan fotoğraf yükle:", height=100)
gorsel_input = st.file_uploader("Bir fotoğraf yükle", type=["jpg", "jpeg", "png"])

# Öğretmeye Başla Butonu
if st.session_state.current_question is None:
    if st.button("Öğretmeye Başla 🚀", use_container_width=True):
        if soru_input or gorsel_input:
            with st.spinner("Steply hazırlanıyor..."):
                gorsel_verisi = Image.open(gorsel_input) if gorsel_input else None
                st.session_state.current_question = soru_getir(soru_input, gorsel_verisi)
                st.rerun()
        else:
            st.warning("Lütfen bir soru yazın veya fotoğraf yükleyin.")

# --- 6. ETKİLEŞİM ALANI (QUIZ) ---
if st.session_state.current_question:
    q = st.session_state.current_question
    st.write("---")
    st.subheader(f"Adım {st.session_state.step_count}: {q.get('soru', 'Soru yüklenemedi')}")

    # Şık butonları
    col1, col2 = st.columns(2)
    with col1:
        btnA = st.button(f"A) {q.get('A', '')}", use_container_width=True)
        btnB = st.button(f"B) {q.get('B', '')}", use_container_width=True)
    with col2:
        btnC = st.button(f"C) {q.get('C', '')}", use_container_width=True)