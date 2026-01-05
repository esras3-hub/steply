import streamlit as st
import google.generativeai as genai
from PIL import Image

# --- 1. API VE GÜVENLİK ---
# API Key'i Streamlit Secrets üzerinden alıyoruz
try:
    API_KEY = st.secrets["API_KEY"]
    genai.configure(api_key=API_KEY)
except:
    st.error("API Key bulunamadı! Lütfen Secrets ayarlarına 'API_KEY' ekleyin.")

# --- 2. MODEL AYARI ---
model = genai.GenerativeModel('gemini-1.5-flash')

# --- 3. HAFIZA (SESSION STATE) KURULUMU ---
# Uygulama ilk açıldığında hafızayı boşaltıyoruz
if "chat" not in st.session_state:
    st.session_state.chat = model.start_chat(history=[])
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- 4. STEPLY ARAYÜZÜ ---
st.set_page_config(page_title="Steply | İnteraktif Öğretmen", page_icon="🪜")

st.markdown("<h1 style='text-align: center;'>🪜 Steply İnteraktif</h1>", unsafe_allow_html=True)
st.caption("Öğrenciye cevabı doğrudan söylemez, adım adım buldurur.")

# Yan Menü: Yeni Ders Başlat
with st.sidebar:
    if st.button("Yeni Derse Başla (Hafızayı Sil)"):
        st.session_state.chat = model.start_chat(history=[])
        st.session_state.messages = []
        st.rerun()

# Fotoğraf Yükleme
yuklenen_gorsel = st.file_uploader("Sorunun fotoğrafını çek veya yükle", type=["jpg", "png", "jpeg"])

# Sohbet Geçmişini Göster
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# Kullanıcı Girişi
if prompt := st.chat_input("Buraya yaz (Örn: Çözmeye başlayalım!)"):
    
    # 1. Kullanıcı mesajını ekrana bas ve hafızaya ekle
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    # 2. Steply'nin yanıtını oluştur
    with st.chat_message("assistant"):
        with st.spinner("Steply düşünüyor..."):
            
            # Steply'ye gizli talimat (Prompt Engineering)
            # Eğer bu ilk mesajsa, görevi hatırla
            sistem_komutu = (
                "Senin adın Steply. İnteraktif bir öğretmensin. "
                "Görevin: Sorunun tamamını çözüp öğrenciye vermek DEĞİLDİR. "
                "1. Sadece İLK ADIMI açıkla. "
                "2. Ardından öğrenciye bir soru sorarak onun katılımını bekle. "
                "3. Öğrenci doğru cevap verirse bir sonraki adıma geç. "
                "4. Yanlış yaparsa ipucu ver ama cevabı söyleme. "
                "Asla listenin tamamını tek seferde paylaşma."
            )
            
            # İçerik hazırlığı (Görsel varsa ekle)
            icerik = [sistem_komutu, prompt]
            if yuklenen_gorsel and len(st.session_state.messages) == 1:
                gorsel = Image.open(yuklenen_gorsel)
                icerik.append(gorsel)
                st.image(gorsel, caption="İncelenen Soru", width=300)

            # Yanıtı al
            response = st.session_state.chat.send_message(icerik)
            st.write(response.text)
            
            # Yanıtı hafızaya ekle
            st.session_state.messages.append({"role": "assistant", "content": response.text})