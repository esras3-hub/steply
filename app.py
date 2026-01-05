import streamlit as st
import google.generativeai as genai
from PIL import Image

# --- 1. API AYARLARI ---
# Kendi API anahtarını buraya yapıştır:
API_KEY = "AIzaSyDR2gSSYpvZHi1Xu3bakMUdLDvCYDLzWdM"
genai.configure(api_key=API_KEY)

# --- 2. MODEL SEÇİMİ ---
def get_steply_model():
    try:
        available_models = [
            m.name for m in genai.list_models() 
            if 'generateContent' in m.supported_generation_methods
        ]
        flash_models = [m for m in available_models if 'flash' in m]
        return flash_models[0] if flash_models else available_models[0]
    except:
        return 'models/gemini-1.5-flash'

# --- 3. STEPLY ARAYÜZÜ ---
st.set_page_config(page_title="Steply | Adım Adım Çözüm", page_icon="🪜", layout="centered")

# Logo ve Başlık
st.markdown("<h1 style='text-align: center; color: #4A90E2;'>🪜 Steply</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Soruları fotoğraf çek, yükle ve <b>adım adım</b> çözümün tadını çıkar!</p>", unsafe_allow_html=True)

st.info("Sistem Kontrolü: Steply v1.0 aktif ve hazır.")

# Giriş Alanları
with st.container():
    st.write("---")
    yuklenen_gorsel = st.file_uploader("Bir fotoğraf yükle veya sürükle", type=["jpg", "jpeg", "png"])
    soru_metni = st.text_input("Özel bir sorun var mı?", placeholder="Örn: Bu problemi 5. sınıf seviyesinde anlat.")

if yuklenen_gorsel:
    gorsel = Image.open(yuklenen_gorsel)
    st.image(gorsel, caption="İşlenecek Görsel", use_column_width=True)

# Çözme Butonu
if st.button("Adım Adım Çöz 🚀", use_container_width=True):
    if not yuklenen_gorsel and not soru_metni:
        st.warning("Lütfen Steply'nin çözmesi için bir fotoğraf veya metin ekle.")
    else:
        with st.spinner('Steply adımları hesaplıyor...'):
            try:
                model_adi = get_steply_model()
                model = genai.GenerativeModel(model_adi)
                
                # Steply'nin karakterini belirleyen özel komut (Prompt)
                steplay_komutu = (
                    "Senin adın Steply. Bir eğitim asistanısın. "
                    "Gelen soruyu veya görseli analiz et ve mutlaka şu kurallara uy:\n"
                    "1. Çözümü mutlaka '1, 2, 3...' şeklinde numaralandırılmış adımlarla ver.\n"
                    "2. Her adımın başına açıklayıcı bir başlık koy.\n"
                    "3. En sonda bir 'Özet' veya 'Püf Noktası' bölümü ekle.\n"
                    "4. Dilin samimi ve teşvik edici olsun."
                )
                
                icerik = [steplay_komutu]
                if soru_metni: icerik.append(f"Kullanıcı Sorusu: {soru_metni}")
                if yuklenen_gorsel: icerik.append(gorsel)

                cevap = model.generate_content(icerik)
                
                st.write("---")
                st.subheader("🪜 Steply'nin Çözüm Adımları")
                st.markdown(cevap.text)
                
            except Exception as e:
                st.error(f"Steply bir hata ile karşılaştı: {e}")

# Alt Bilgi
st.markdown("<br><hr><center><small>Steply - Senin Akıllı Çözüm Ortağın</small></center>", unsafe_allow_html=True)