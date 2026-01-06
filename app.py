def soru_getir(metin_input=None, gorsel_input=None):
    sistem_komutu = (
        "Sen Steply'sin. İnteraktif bir öğretmensin. "
        "Adım {0} için bir çoktan seçmeli soru hazırla. ".format(st.session_state.step_count) +
        "Sadece şu JSON formatında cevap ver (başka hiçbir metin ekleme):\n"
        "{\n"
        "  \"soru\": \"Soru metni\",\n"
        "  \"A\": \"Şık A\", \"B\": \"Şık B\", \"C\": \"Şık C\", \"D\": \"Şık D\",\n"
        "  \"dogru_cevap\": \"A\", \"aciklama\": \"Kısa not\"\n"
        "}"
    )
    
    icerik = [sistem_komutu]
    if metin_input: icerik.append(f"Problem: {metin_input}")
    if gorsel_input: icerik.append(gorsel_input)

    try:
        response = model.generate_content(icerik)
        # JSON'ı temizle (Bazen model ```json ... ``` ekler, onu siliyoruz)
        raw_text = response.text
        start_idx = raw_text.find('{')
        end_idx = raw_text.rfind('}') + 1
        clean_json = raw_text[start_idx:end_idx]
        
        return json.loads(clean_json)
    except Exception as e:
        # Eğer hata alırsak ekranda ne olduğunu görelim
        st.error(f"Steply soruyu hazırlayamadı. Hata: {e}")
        return None