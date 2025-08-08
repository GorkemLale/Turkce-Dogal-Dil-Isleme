import streamlit as st
import json
from datetime import datetime
import random
import requests
import re

# Gerçek telekom verileri (JSON'dan çıkarılan)
REAL_TELECOM_DATA = {
    "ekonomik_paket": "Ekonomik 8 GB: Başlangıç seviyesi paket, 8GB mobil internet, aylık ücret düşük, yoğun kullanıcılara uygun değil.",
    "orta_paket": "Orta 30 GB: Orta seviye paket, 30GB mobil internet, standart kullanıcılar için ideal, makul ücret.",
    "mega_paket": "Mega 35 GB: Yüksek kapasiteli paket, 35GB mobil internet, 199 TL aylık, aktif kullanıcılar için.",
    "ultra_paket": "Ultra 60 GB: Premium paket, 60GB mobil internet, 259 TL aylık, çok yoğun kullanıcılar için.",
    "baslangic_paket": "Başlangıç 12 GB: Giriş seviyesi paket, 12GB mobil internet, yeni müşteriler için.",
    "standart_paket": "Standart 20 GB: Standart paket, 20GB mobil internet, 199 TL aylık, ortalama kullanım için.",
    "pro_paket": "Pro 45 GB: Profesyonel paket, 45GB mobil internet, 259 TL aylık, iş kullanımı için.",
    "premium_paket": "Premium 50 GB: Premium seviye paket, 50GB mobil internet, yüksek hız, 299 TL aylık.",
    "tatil_extra": "Tatil Extra 40 GB: Geçici tatil paketi, 40GB mobil internet, 30 gün geçerli, 199 TL.",
    "max_paket": "Max 70 GB: Maksimum kapasiteli paket, 70GB mobil internet, limitsiz özellikleri içerir.",
    
    # Sistem fonksiyonları
    "kullanim_sorgulama": "getUsageInfo fonksiyonu ile müşterinin mevcut kullanımı sorgulanır, kota ve kullanım yüzdesi alınır.",
    "paket_degisikligi": "changePackage fonksiyonu ile paket değişikliği yapılır, başarı/başarısızlık durumu döner.",
    "sozlesme_kontrol": "getContractStatus fonksiyonu ile müşterinin taahhüt durumu kontrol edilir.",
    "fatura_sorgulama": "getBillingInfo fonksiyonu ile fatura bilgileri alınır, ödeme durumu kontrol edilir.",
    
    # Müşteri durumları
    "kota_yetersizligi": "Müşteri kotasının %85-100 arası kullanımında paket yetersizliği sorunu yaşar, yükseltme önerilir.",
    "tatil_kullanimi": "Tatil dönemlerinde yoğun fotoğraf/video paylaşımı nedeniyle geçici paket ihtiyacı doğar.",
    "is_kullanimi": "İş amaçlı yoğun kullanımda kurumsal paketlere yönlendirme yapılır.",
    "hata_durumu": "Sistem hatalarında alternatif çözümler sunulur, müşteri memnuniyeti korunur."
}

def getUserInfo(user_id):
    users_db = {
        "5551234567": {
            "name": "Ahmet", 
            "surname": "Yılmaz", 
            "current_package": "SuperNet 50",
            "contract_end_date": "2025-12-01",
            "payment_status": "Ödendi"
        },
        "5559876543": {
            "name": "Ayşe", 
            "surname": "Kaya", 
            "current_package": "Ekonomik Paket",
            "contract_end_date": "2025-08-15",
            "payment_status": "Bekliyor"
        }
    }
    return users_db.get(user_id, {"error": "Kullanıcı bulunamadı"})

def getAvailablePackages(user_id):
    # Gerçek paket verileri
    packages = [
        {"id": "PN1", "name": "Ekonomik 8 GB", "price": "149 TL", "details": "8GB mobil internet, başlangıç seviyesi"},
        {"id": "PN2", "name": "Başlangıç 12 GB", "price": "179 TL", "details": "12GB mobil internet, yeni müşteriler için"},
        {"id": "PN3", "name": "Standart 20 GB", "price": "199 TL", "details": "20GB mobil internet, ortalama kullanım"},
        {"id": "PN4", "name": "Orta 30 GB", "price": "229 TL", "details": "30GB mobil internet, standart kullanıcılar"},
        {"id": "PN5", "name": "Mega 35 GB", "price": "199 TL", "details": "35GB mobil internet, aktif kullanıcılar"},
        {"id": "PN6", "name": "Tatil Extra 40 GB", "price": "199 TL", "details": "40GB mobil internet, 30 gün geçici"},
        {"id": "PN7", "name": "Pro 45 GB", "price": "259 TL", "details": "45GB mobil internet, iş kullanımı"},
        {"id": "PN8", "name": "Premium 50 GB", "price": "299 TL", "details": "50GB mobil internet, premium seviye"},
        {"id": "PN9", "name": "Ultra 60 GB", "price": "259 TL", "details": "60GB mobil internet, yoğun kullanıcılar"},
        {"id": "PN10", "name": "Max 70 GB", "price": "349 TL", "details": "70GB mobil internet, maksimum kapasite"}
    ]
    return packages

def initiatePackageChange(user_id, package_id):
    success = random.choice([True, False])
    if success:
        return {"success": True, "message": "Paket değişikliği talebiniz alınmıştır. 24 saat içinde aktifleşecektir."}
    else:
        return {"success": False, "error": "Mevcut sözleşmeniz nedeniyle paket değişikliği yapılamıyor."}

class CallCenterAgent:
    def __init__(self):
        self.conversation_history = []
        self.current_user = None
        
    def search_simple_knowledge(self, query):
        query_lower = query.lower()
        found_info = []
        for key, value in REAL_TELECOM_DATA.items():
            if key.replace("_", " ") in query_lower or any(word in query_lower for word in key.split("_")):
                found_info.append(value)
        return found_info[:3]  # En fazla 3 sonuç
        
    def get_ollama_response(self, user_message, context=""):
        relevant_info = self.search_simple_knowledge(user_message)
        
        user_info = ""
        if self.current_user:
            user_data = getUserInfo(self.current_user)
            user_info = f"Müşteri: {user_data.get('name', '')} {user_data.get('surname', '')}, Mevcut Paket: {user_data.get('current_package', '')}"
        
        knowledge_context = ""
        if relevant_info:
            knowledge_context = "Şirket bilgileri:\n" + "\n".join(relevant_info)
        
        prompt = f"""Sen profesyonel bir Türk Telekom çağrı merkezi temsilcisisin.

{knowledge_context}

{user_info}
{context}

KRİTİK KURALLAR:
- SADECE yukarıdaki şirket bilgilerini kullan
- Kendi bilgilerini EKLEME
- Paket isimleri: MegaPaket 100, Ekonomik Paket, Premium Paket (SADECE BUNLAR)
- Eğer yukarıda bilgi yoksa "Bu konuda size yardımcı olmak için daha detay almam gerekiyor" de
- Maksimum 2 cümle yanıt ver

Müşteri: {user_message}
Temsilci:"""

        try:
            response = requests.post('http://localhost:11434/api/generate',
                json={
                    'model': 'mistral:7b-instruct',
                    'prompt': prompt,
                    'stream': False,
                    'options': {'temperature': 0.3, 'top_p': 0.9, 'max_tokens': 120}
                })
            
            if response.status_code == 200:
                result = response.json()
                ai_response = result['response'].strip()
                if ai_response.startswith("Temsilci:"):
                    ai_response = ai_response[9:].strip()
                return ai_response
            else:
                return "Özür dilerim, şu anda teknik bir sorun yaşıyoruz."
        except:
            return self.get_smart_response(user_message, context)
    
    def get_smart_response(self, user_message, context=""):
        msg = user_message.lower()
        
        if msg.strip() in ["1", "2", "3"]:
            return self.handle_package_selection(msg.strip())
        
        if any(word in msg for word in ["yüksek", "hızlı", "premium"]) and "internet" in msg:
            return "Size Premium Paket (200Mbps) öneriyorum! 200 TL'ye limitsiz internet. Onaylıyor musunuz?"
        
        if any(word in msg for word in ["ucuz", "ekonomik"]) and "paket" in msg:
            return "Size Ekonomik Paket öneriyorum! 80 TL'ye 25Mbps internet. Onaylıyor musunuz?"
        
        if "paket" in msg:
            return "Hangi tür paket arıyorsunuz? Yüksek hızlı internet mi, ekonomik çözüm mü?"
        else:
            return "Size nasıl yardımcı olabilirim? Paket değişikliği için buradayım."
    
    def handle_package_selection(self, selection):
        if not self.current_user:
            return "Önce telefon numaranızı söylemeniz gerekiyor."
        
        packages = getAvailablePackages(self.current_user)
        try:
            selected_idx = int(selection) - 1
            if 0 <= selected_idx < len(packages):
                selected_package = packages[selected_idx]
                result = initiatePackageChange(self.current_user, selected_package['id'])
                if result['success']:
                    return f"✅ {selected_package['name']} seçtiniz! {result['message']}"
                else:
                    return f"❌ {result['error']}"
            else:
                return "Lütfen 1, 2 veya 3 numaralarından birini seçin."
        except:
            return "Geçersiz seçim. Lütfen 1, 2 veya 3 yazın."
    
    def confirm_package_change(self, package_name):
        if not self.current_user:
            return "Önce telefon numaranızı söylemeniz gerekiyor."
        
        package_map = {"MegaPaket 100": "PN1", "Ekonomik Paket": "PN2", "Premium Paket": "PN3"}
        package_id = package_map.get(package_name)
        
        if package_id:
            result = initiatePackageChange(self.current_user, package_id)
            if result['success']:
                return f"✅ {package_name} seçtiniz! {result['message']}"
            else:
                return f"❌ {result['error']}"
        else:
            return "Geçersiz paket seçimi."
        
    def process_message(self, user_message):
        # Telefon numarası kontrolü
        clean_msg = user_message.replace(" ", "").replace("-", "")
        if re.match(r'^555\d{7}$', clean_msg):
            return self.identify_user(clean_msg)
        
        # Paket seçimi
        if "megapaket" in user_message.lower() and ("geç" in user_message.lower() or "istiyorum" in user_message.lower()):
            return self.confirm_package_change("MegaPaket 100")
        elif "premium" in user_message.lower() and ("geç" in user_message.lower() or "istiyorum" in user_message.lower()):
            return self.confirm_package_change("Premium Paket")
        elif "ekonomik" in user_message.lower() and ("geç" in user_message.lower() or "istiyorum" in user_message.lower()):
            return self.confirm_package_change("Ekonomik Paket")
        
        if "paket değiştir" in user_message.lower() or "paket değişikliği" in user_message.lower():
            return self.handle_package_change_ai(user_message)
        elif "kimliğim" in user_message.lower() or "bilgilerim" in user_message.lower():
            return self.handle_user_info(user_message)
        else:
            context = f"Mevcut kullanıcı: {self.current_user}" if self.current_user else "Kullanıcı henüz tanımlanmadı"
            return self.get_ollama_response(user_message, context)
    
    def identify_user(self, phone_number):
        clean_phone = phone_number.replace(" ", "").replace("-", "").strip()
        user_info = getUserInfo(clean_phone)
        
        if "error" not in user_info:
            self.current_user = clean_phone
            return f"Merhaba {user_info['name']} {user_info['surname']}! Mevcut paketiniz: {user_info['current_package']}. Size nasıl yardımcı olabilirim?"
        else:
            return "Üzgünüm, bu telefon numarasına ait kayıt bulunamadı. Lütfen numaranızı kontrol edin."
    
    def handle_user_info(self, message):
        if not self.current_user:
            return "Önce telefon numaranızı söylemeniz gerekiyor."
        user_info = getUserInfo(self.current_user)
        return f"""📋 Bilgileriniz:
- Ad Soyad: {user_info['name']} {user_info['surname']}
- Mevcut Paket: {user_info['current_package']}
- Sözleşme Bitiş: {user_info['contract_end_date']}
- Ödeme Durumu: {user_info['payment_status']}"""
    
    def handle_package_change_ai(self, message):
        if not self.current_user:
            return "Önce telefon numaranızı söylemeniz gerekiyor."
        
        packages = getAvailablePackages(self.current_user)
        package_info = "📦 Mevcut Paketlerimiz:\n"
        for i, pkg in enumerate(packages, 1):
            package_info += f"{i}. **{pkg['name']}**: {pkg['price']} - {pkg['details']}\n"
        return package_info + "\n💬 Hangi paketi tercih edersiniz? Paket numarasını söyleyebilirsiniz."

def main():
    st.title("🎯 TEKNOFEST Çağrı Merkezi Demo")
    st.write("Türkçe Doğal Dil İşleme Yarışması - AI + Ollama")
    
    if 'agent' not in st.session_state:
        st.session_state.agent = CallCenterAgent()
    
    if 'messages' not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "🎧 Merhaba! Telekom çağrı merkezine hoş geldiniz. Size nasıl yardımcı olabilirim?"}
        ]
    
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    if prompt := st.chat_input("Mesajınızı yazın..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        response = st.session_state.agent.process_message(prompt)
        st.session_state.messages.append({"role": "assistant", "content": response})
        with st.chat_message("assistant"):
            st.markdown(response)
    
    st.sidebar.title("📊 Proje Durumu")
    st.sidebar.write("**Model:** Ollama Mistral 7B")
    st.sidebar.write("**Özellik:** AI + Akıllı RAG")
    st.sidebar.write("**Durum:** ✅ Aktif")
    if st.session_state.agent.current_user:
        st.sidebar.write(f"**Müşteri:** {st.session_state.agent.current_user}")
    
    st.sidebar.title("🚀 Hızlı Test")
    st.sidebar.code("5551234567")
    st.sidebar.code("Premium paket nedir?")
    st.sidebar.code("MegaPaket 100'e geçmek istiyorum")

if __name__ == "__main__":
    main()