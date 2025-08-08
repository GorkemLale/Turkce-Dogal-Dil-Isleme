import streamlit as st
import json
from datetime import datetime
import random

# Mock fonksiyonlar (sahte veri tabanı)
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
    success = random.choice([True, False])  # Rastgele başarı/başarısızlık
    
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
        
    def process_message(self, user_message):
        """Kullanıcı mesajını işle ve yanıt üret"""
        
        # Basit intent tanıma (gerçek projede LLM kullanacaksınız)
        if "paket değiştir" in user_message.lower() or "paket değişikliği" in user_message.lower():
            return self.handle_package_change(user_message)
        elif "kimliğim" in user_message.lower() or "bilgilerim" in user_message.lower():
            return self.handle_user_info(user_message)
        elif user_message.startswith("555"):  # Telefon numarası girildi
            return self.identify_user(user_message)
        else:
            return "Merhaba! Size nasıl yardımcı olabilirim? Telefon numaranızı söyleyebilir misiniz?"
    
    def identify_user(self, phone_number):
        """Kullanıcıyı tanımla"""
        user_info = getUserInfo(phone_number.strip())
        
        if "error" not in user_info:
            self.current_user = phone_number.strip()
            return f"Merhaba {user_info['name']} {user_info['surname']}! Mevcut paketiniz: {user_info['current_package']}. Size nasıl yardımcı olabilirim?"
        else:
            return "Üzgünüm, bu telefon numarasına ait kayıt bulunamadı. Lütfen numaranızı kontrol edin."
    
    def handle_user_info(self, message):
        """Kullanıcı bilgilerini göster"""
        if not self.current_user:
            return "Önce telefon numaranızı söylemeniz gerekiyor."
            
        user_info = getUserInfo(self.current_user)
        return f"""
        Bilgileriniz:
        - Ad Soyad: {user_info['name']} {user_info['surname']}
        - Mevcut Paket: {user_info['current_package']}
        - Sözleşme Bitiş: {user_info['contract_end_date']}
        - Ödeme Durumu: {user_info['payment_status']}
        """
    
    def handle_package_change(self, message):
        """Paket değişikliği işlemini yönet"""
        if not self.current_user:
            return "Önce telefon numaranızı söylemeniz gerekiyor."
        
        # Mevcut paketleri göster
        packages = getAvailablePackages(self.current_user)
        
        package_list = "Mevcut Paketlerimiz:\n"
        for pkg in packages:
            package_list += f"- {pkg['name']}: {pkg['price']} ({pkg['details']})\n"
        
        return package_list + "\nHangi paketi seçmek istiyorsunuz?"

# Streamlit arayüzü
def main():
    st.title("🎯 TEKNOFEST Çağrı Merkezi Demo")
    st.write("Türkçe Doğal Dil İşleme Yarışması - Senaryo Kategorisi")
    
    # Session state'de agent'i tut
    if 'agent' not in st.session_state:
        st.session_state.agent = CallCenterAgent()
    
    # Konuşma geçmişi
    if 'messages' not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Merhaba! Telekom çağrı merkezine hoş geldiniz. Size nasıl yardımcı olabilirim?"}
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
    st.sidebar.write("**Senaryo:** Paket Değişikliği")
    st.sidebar.write("**Agent Durumu:** ✅ Aktif")
    if st.session_state.agent.current_user:
        st.sidebar.write(f"**Mevcut Kullanıcı:** {st.session_state.agent.current_user}")
    
    # Test için hızlı butonlar
    st.sidebar.title("🚀 Hızlı Test")
    if st.sidebar.button("Test Telefon: 5551234567"):
        st.rerun()
    if st.sidebar.button("Paket Değiştirmek İstiyorum"):
        st.rerun()

if __name__ == "__main__":
    main()