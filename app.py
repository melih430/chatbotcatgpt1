import streamlit as st
import json
import openai
import os
from dotenv import load_dotenv

# .env dosyasından OpenAI API anahtarını al
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Sayfa ayarları
st.set_page_config(page_title="catgpt", page_icon="🐱")
st.title("🐱 catgpt: Kedi Bilgi Chatbotu")

# Bilgi tabanını yükle
@st.cache_data
def load_knowledge_base():
    with open("catgpt_kedi_bilgi_tabani.json", "r", encoding="utf-8") as f:
        return json.load(f)

knowledge_base = load_knowledge_base()

# GPT yorum üretici
def gpt_yorum_uret(konu_ozeti):
    try:
        yanit = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Sen bir kedi uzmanısın. Kullanıcının verdiği kedi hikayesi hakkında yorum yap."},
                {"role": "user", "content": f"Senaryo: {konu_ozeti}\nBu senaryo hakkında yorum yap."}
            ],
            temperature=0.7
        )
        return yanit["choices"][0]["message"]["content"].strip()
    except Exception as e:
        return f"GPT yorumu alınamadı: {e}"

# Mesaj geçmişi
if "messages" not in st.session_state:
    st.session_state.messages = []

# Önceki mesajları göster
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Kullanıcıdan giriş
user_input = st.chat_input("Bir ırk, kategori veya mekan yaz (örnek: Maine Coon, Patiland)...")

def kedi_bilgisi_ara(sorgu):
    sorgu = sorgu.lower()
    sonuçlar = []
    for item in knowledge_base:
        if (sorgu in item["ırk"].lower() or
            sorgu in item["kategori"].lower() or
            sorgu in item["mekan"].lower()):
            sonuçlar.append(item)
    return sonuçlar[:1]  # sadece 1 tane senaryo örneği yorum için yeterli

# Sorgu işleme
if user_input:
    st.chat_message("user").markdown(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})

    senaryolar = kedi_bilgisi_ara(user_input)

    if senaryolar:
        senaryo = senaryolar[0]
        başlık = senaryo['başlık']
        açıklama = senaryo['açıklama']
        mesaj = f"📘 **{başlık}**\n\n{açıklama}"

        # GPT yorumu üret
        yorum = gpt_yorum_uret(açıklama)
        tam_cevap = f"{mesaj}\n\n---\n\n💬 **catgpt Yorumu:**\n{yorum}"

        st.chat_message("assistant").markdown(tam_cevap)
        st.session_state.messages.append({"role": "assistant", "content": tam_cevap})
    else:
        cevap = "😿 Üzgünüm, bu konuda bilgi bulamadım."
        st.chat_message("assistant").markdown(cevap)
        st.session_state.messages.append({"role": "assistant", "content": cevap})
