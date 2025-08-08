import streamlit as st
import json
from datetime import datetime
import random
import requests

# Basit bilgi tabanı (RAG yerine)
SIMPLE_KNOWLEDGE = {
    "premium paket": "Premium Paket: 200 TL aylık, 200Mbps hız, limitsiz konuşma ve SMS, 100GB mobil internet, 7/24 öncelikli destek sunar.",
    "ekonomik paket": "Ekonomik Paket: 80 TL aylık, 25Mbps hız, 1000 dakika konuşma, 10GB mobil internet, öğrenciler için %20 indirim.",
    "megapaket": "MegaPaket 100: 150 TL aylık, 100Mbps hız, limitsiz konuşma, 50GB mobil internet, en popüler paketimiz.",
    "paket değişim": "Paket değişikliği için kimlik doğrulaması gerekli, yeni paket 24 saat içinde aktifleşir.",
    "fatura gecikme": "Fatura geç ödenirse 15 gün süre verilir, gecikme faizi uygulanır, 30 gün sonra hat kapatılır.",
    "teknik destek": "Teknik sorunlar için modem yeniden başlatılır, kablo kontrolü yapılır, gerekirse teknisyen gönderilir."
}

# Mock fonksiyonlar
def getUserInfo(user_id):
    """Müşteri bilgilerini getir"""
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
    """Mevcut paketleri getir"""
    packages = [
        {
            "id": "PN1", 
            "name": "MegaPaket 100", 
            "price": "150 TL", 
            "details": "100Mbps internet, limitsiz konuşma"
        },
        {
            "id": "PN2", 
            "name": "Ekonomik Paket", 
            "price": "80 TL", 
            "details": "25Mbps internet, 10GB mobil"
        },
        {
            "id": "PN3", 
            "name": "Premium Paket", 
            "price": "200 TL", 
            "details": "200Mbps internet, limitsiz her şey"
        }
    ]
    return packages

def initiatePackageChange(user_id, package_id):
    """Paket değişikliği başlat"""
    success = random.choice([True, False])
    
    if success:
        return {
            "success": True, 
            "message": "Paket değişikliği talebiniz alınmıştır. 24 saat içinde aktifleşecektir."
        }
    else:
        return {
            "success": False, 
            "error": "Mevcut sözleşmeniz nedeniyle paket değişikliği yapılamıyor."
        }

class CallCenterAgent:
    def __init__(self):
        self.conversation_history = []
        self.current_user = None
        
    def search_simple_knowledge(self, query):
        """Basit bilgi tabanında arama"""
        query_lower = query.lower()
        found_info = []
        
        for key, value in SIMPLE_KNOWLEDGE.items():
            if key in query_lower:
                found_info.append(value)
        
        return found_info
        
    def get_ollama_response(self, user_message, context=""):
        """Ollama ile AI yanıt üret"""
        
        # Basit bilgi tabanından bilgi bul
        relevant_info = self.search_simple_knowledge(user_message)
        
        # Kullanıcı bilgilerini al
        user_info = ""
        if self.current_user:
            user_data = getUserInfo(self.current_user)
            user_info = f"Müşteri: {user_data.get('name', '')} {user_data.get('surname', '')}, Mevcut Paket: {user_data.get('current_package', '')}"
        
        # Bilgi tabanı bilgilerini ekle
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
                    'options': {
                        'temperature': 0.3,
                        'top_p': 0.9,
                        'max_tokens': 120
                    }
                })
            
            if response.status_code == 200:
                result = response.json()
                ai_response = result['response'].strip()
                
                if ai_response.startswith("Temsilci:"):
                    ai_response = ai_response[9:].strip()
                
                return ai_response
            else:
                return "Özür dilerim, şu anda teknik bir sorun yaşıyoruz."
                
        except Exception as e:
            return self.get_smart_response(user_message, context)
    
    def get_smart_response(self, user_message, context=""):
        """Fallback akıllı yanıt sistemi"""
        msg = user_message.lower()
        
        if msg.strip() in ["1", "2", "3"]:
            return self.handle_package_selection(msg.strip())
        
        if any(word in msg for word in ["yüksek", "hızlı", "güçlü", "premium", "en iyi"]) and "internet" in msg:
            return "Size Premium Paket (200Mbps) öneriyorum! 200 TL'ye limitsiz internet ve konuşma. Onaylıyor musunuz?"
        
        if any(word in msg for word in ["ucuz", "ekonomik", "uygun", "az"]) and any(word in msg for word in ["paket", "fiyat"]):
            return "Size Ekonomik Paket öneriyorum! 80 TL'ye 25Mbps internet. Onaylıyor musunuz?"
        
        if "paket" in msg:
            return "Hangi tür paket arıyorsunuz? Yüksek hızlı internet mi, ekonomik çözüm mü?"
        elif "fatura" in msg:
            return "Fatura bilgilerinizi kontrol ediyorum. Bekleyiniz..."
        elif "problem" in msg or "sorun" in msg:
            return "Sorununuzu anlıyorum. Size hemen yardımcı olacağım."
        else:
            return "Size nasıl yardımcı olabilirim? Paket değişikliği, fatura sorgusu veya teknik destek için buradayım."
    
    def handle_package_selection(self, selection):
        """Paket seçimini işle"""
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
        
    def process_message(self, user_message):
        """Kullanıcı mesajını işle ve yanıt üret"""
        
        # Telefon numarası kontrolü (555 ile başlayan 10 haneli)
        import re
        clean_msg = user_message.replace(" ", "").replace("-", "")
        if re.match(r'^555\d{7}
    
    def identify_user(self, phone_number):
        """Kullanıcıyı tanımla"""
        # Boşlukları temizle
        clean_phone = phone_number.replace(" ", "").replace("-", "").strip()
        user_info = getUserInfo(clean_phone)
        
        if "error" not in user_info:
            self.current_user = clean_phone
            return f"Merhaba {user_info['name']} {user_info['surname']}! Mevcut paketiniz: {user_info['current_package']}. Size nasıl yardımcı olabilirim?"
        else:
            return "Üzgünüm, bu telefon numarasına ait kayıt bulunamadı. Lütfen numaranızı kontrol edin."
    
    def handle_user_info(self, message):
        """Kullanıcı bilgilerini göster"""
        if not self.current_user:
            return "Önce telefon numaranızı söylemeniz gerekiyor."
            
        user_info = getUserInfo(self.current_user)
        return f"""
        📋 Bilgileriniz:
        - Ad Soyad: {user_info['name']} {user_info['surname']}
        - Mevcut Paket: {user_info['current_package']}
        - Sözleşme Bitiş: {user_info['contract_end_date']}
        - Ödeme Durumu: {user_info['payment_status']}
        """
    
    def handle_package_change_ai(self, message):
        """AI destekli paket değişikliği"""
        if not self.current_user:
            return "Önce telefon numaranızı söylemeniz gerekiyor."
        
        packages = getAvailablePackages(self.current_user)
        package_info = "📦 Mevcut Paketlerimiz:\n"
        for i, pkg in enumerate(packages, 1):
            package_info += f"{i}. **{pkg['name']}**: {pkg['price']} - {pkg['details']}\n"
        
        return package_info + "\n💬 Hangi paketi tercih edersiniz? Paket numarasını söyleyebilirsiniz."

# Streamlit arayüzü
def main():
    st.title("🎯 TEKNOFEST Çağrı Merkezi Demo")
    st.write("Türkçe Doğal Dil İşleme Yarışması - AI + Ollama")
    
    # Session state'de agent'i tut
    if 'agent' not in st.session_state:
        st.session_state.agent = CallCenterAgent()
    
    # Konuşma geçmişi
    if 'messages' not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "🎧 Merhaba! Telekom çağrı merkezine hoş geldiniz. Size nasıl yardımcı olabilirim?"}
        ]
    
    # Konuşma geçmişini göster
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Kullanıcı girişi
    if prompt := st.chat_input("Mesajınızı yazın..."):
        # Kullanıcı mesajını ekle
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Agent yanıtını al
        response = st.session_state.agent.process_message(prompt)
        
        # Assistant yanıtını ekle
        st.session_state.messages.append({"role": "assistant", "content": response})
        with st.chat_message("assistant"):
            st.markdown(response)
    
    # Sidebar - Proje Bilgileri
    st.sidebar.title("📊 Proje Durumu")
    st.sidebar.write("**Model:** Ollama Mistral 7B")
    st.sidebar.write("**Özellik:** Basit RAG + AI")
    st.sidebar.write("**Durum:** ✅ Aktif")
    if st.session_state.agent.current_user:
        st.sidebar.write(f"**Müşteri:** {st.session_state.agent.current_user}")
    
    # Test butonları
    st.sidebar.title("🚀 Hızlı Test")
    st.sidebar.code("5551234567")
    st.sidebar.code("Premium paket nedir?")
    st.sidebar.code("Paket değiştirmek istiyorum")

if __name__ == "__main__":
    main()
, clean_msg):
            return self.identify_user(clean_msg)
        
        # Paket seçimi (MegaPaket 100 gibi isimlerle)
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
    
    def confirm_package_change(self, package_name):
        """Paket değişikliğini onayla"""
        if not self.current_user:
            return "Önce telefon numaranızı söylemeniz gerekiyor."
        
        # Mock package ID bulma
        package_map = {
            "MegaPaket 100": "PN1",
            "Ekonomik Paket": "PN2", 
            "Premium Paket": "PN3"
        }
        
        package_id = package_map.get(package_name)
        if package_id:
            result = initiatePackageChange(self.current_user, package_id)
            if result['success']:
                return f"✅ {package_name} seçtiniz! {result['message']}"
            else:
                return f"❌ {result['error']}"
        else:
            return "Geçersiz paket seçimi."
    
    def identify_user(self, phone_number):
        """Kullanıcıyı tanımla"""
        # Boşlukları temizle
        clean_phone = phone_number.replace(" ", "").replace("-", "").strip()
        user_info = getUserInfo(clean_phone)
        
        if "error" not in user_info:
            self.current_user = clean_phone
            return f"Merhaba {user_info['name']} {user_info['surname']}! Mevcut paketiniz: {user_info['current_package']}. Size nasıl yardımcı olabilirim?"
        else:
            return "Üzgünüm, bu telefon numarasına ait kayıt bulunamadı. Lütfen numaranızı kontrol edin."
    
    def handle_user_info(self, message):
        """Kullanıcı bilgilerini göster"""
        if not self.current_user:
            return "Önce telefon numaranızı söylemeniz gerekiyor."
            
        user_info = getUserInfo(self.current_user)
        return f"""
        📋 Bilgileriniz:
        - Ad Soyad: {user_info['name']} {user_info['surname']}
        - Mevcut Paket: {user_info['current_package']}
        - Sözleşme Bitiş: {user_info['contract_end_date']}
        - Ödeme Durumu: {user_info['payment_status']}
        """
    
    def handle_package_change_ai(self, message):
        """AI destekli paket değişikliği"""
        if not self.current_user:
            return "Önce telefon numaranızı söylemeniz gerekiyor."
        
        packages = getAvailablePackages(self.current_user)
        package_info = "📦 Mevcut Paketlerimiz:\n"
        for i, pkg in enumerate(packages, 1):
            package_info += f"{i}. **{pkg['name']}**: {pkg['price']} - {pkg['details']}\n"
        
        return package_info + "\n💬 Hangi paketi tercih edersiniz? Paket numarasını söyleyebilirsiniz."

# Streamlit arayüzü
def main():
    st.title("🎯 TEKNOFEST Çağrı Merkezi Demo")
    st.write("Türkçe Doğal Dil İşleme Yarışması - AI + Ollama")
    
    # Session state'de agent'i tut
    if 'agent' not in st.session_state:
        st.session_state.agent = CallCenterAgent()
    
    # Konuşma geçmişi
    if 'messages' not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "🎧 Merhaba! Telekom çağrı merkezine hoş geldiniz. Size nasıl yardımcı olabilirim?"}
        ]
    
    # Konuşma geçmişini göster
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Kullanıcı girişi
    if prompt := st.chat_input("Mesajınızı yazın..."):
        # Kullanıcı mesajını ekle
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Agent yanıtını al
        response = st.session_state.agent.process_message(prompt)
        
        # Assistant yanıtını ekle
        st.session_state.messages.append({"role": "assistant", "content": response})
        with st.chat_message("assistant"):
            st.markdown(response)
    
    # Sidebar - Proje Bilgileri
    st.sidebar.title("📊 Proje Durumu")
    st.sidebar.write("**Model:** Ollama Mistral 7B")
    st.sidebar.write("**Özellik:** Basit RAG + AI")
    st.sidebar.write("**Durum:** ✅ Aktif")
    if st.session_state.agent.current_user:
        st.sidebar.write(f"**Müşteri:** {st.session_state.agent.current_user}")
    
    # Test butonları
    st.sidebar.title("🚀 Hızlı Test")
    st.sidebar.code("5551234567")
    st.sidebar.code("Premium paket nedir?")
    st.sidebar.code("Paket değiştirmek istiyorum")

if __name__ == "__main__":
    main()