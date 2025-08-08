import streamlit as st
import json
from datetime import datetime
import random
import requests
import chromadb
from sentence_transformers import SentenceTransformer

# RAG Bilgi Tabanı
KNOWLEDGE_BASE = [
    {
        "id": "paket_megapaket100",
        "content": "MegaPaket 100: 150 TL aylık ücret, 100Mbps internet hızı, limitsiz konuşma, 50GB mobil internet, fiber altyapı gerektirir, en popüler paketimizdir.",
        "category": "paket_bilgisi"
    },
    {
        "id": "paket_ekonomik",
        "content": "Ekonomik Paket: 80 TL aylık ücret, 25Mbps internet hızı, 1000 dakika konuşma, 10GB mobil internet, öğrenciler için %20 indirim.",
        "category": "paket_bilgisi"
    },
    {
        "id": "paket_premium",
        "content": "Premium Paket: 200 TL aylık ücret, 200Mbps internet hızı, limitsiz konuşma ve SMS, 100GB mobil internet, 7/24 öncelikli destek.",
        "category": "paket_bilgisi"
    },
    {
        "id": "paket_degisim_prosedur",
        "content": "Paket değişikliği için: Müşteri kimlik doğrulaması gerekli, mevcut sözleşme kontrolü yapılır, yeni paket 24 saat içinde aktifleşir, ilk fatura döneminde her iki paket de ücretlendirilir.",
        "category": "prosedur"
    },
    {
        "id": "fatura_gecikme",
        "content": "Fatura gecikme durumunda: 15 gün süre verilir, gecikme faizi uygulanır, 30 gün sonra hat kapatılır, 60 gün sonra tahsilat sürecine girer.",
        "category": "fatura"
    },
    {
        "id": "teknik_destek",
        "content": "Teknik destek için: Modem yeniden başlatılması, kablo kontrolü, fiber hat testi yapılır. Sorun devam ederse teknisyen randevusu verilir.",
        "category": "teknik_destek"
    },
    {
        "id": "iptal_prosedur", 
        "content": "Abonelik iptali için: 30 gün önceden bildirim, erken iptal cezası hesaplanır, cihaz iade edilir, son fatura düzenlenir.",
        "category": "iptal"
    }
]

@st.cache_resource
def setup_rag_system():
    """RAG sistemini kur"""
    # ChromaDB client
    chroma_client = chromadb.Client()
    
    # Collection oluştur
    try:
        collection = chroma_client.get_collection("telecom_kb")
    except:
        collection = chroma_client.create_collection("telecom_kb")
    
    # Embedding model
    embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
    
    # Bilgi tabanını ekle
    if collection.count() == 0:  # Boşsa ekle
        for item in KNOWLEDGE_BASE:
            embedding = embedding_model.encode([item["content"]])[0].tolist()
            collection.add(
                documents=[item["content"]],
                embeddings=[embedding],
                metadatas=[{"category": item["category"]}],
                ids=[item["id"]]
            )
    
    return collection, embedding_model
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
        # RAG sistemini kur
        self.rag_collection, self.embedding_model = setup_rag_system()
        
    def search_knowledge_base(self, query, n_results=2):
        """Bilgi tabanında arama yap"""
        try:
            # Query'yi embed et
            query_embedding = self.embedding_model.encode([query])[0].tolist()
            
            # Benzer belgeleri bul
            results = self.rag_collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results
            )
            
            return results['documents'][0] if results['documents'] else []
        except Exception as e:
            return []
        
    def get_ollama_response(self, user_message, context=""):
        """RAG + Ollama ile AI yanıt üret"""
        
        # 1. Bilgi tabanından ilgili bilgileri bul
        relevant_info = self.search_knowledge_base(user_message)
        
        # 2. Kullanıcı bilgilerini al
        user_info = ""
        if self.current_user:
            user_data = getUserInfo(self.current_user)
            user_info = f"Müşteri: {user_data.get('name', '')} {user_data.get('surname', '')}, Mevcut Paket: {user_data.get('current_package', '')}"
        
        # 3. RAG bilgilerini prompt'a ekle
        knowledge_context = ""
        if relevant_info:
            knowledge_context = "İlgili bilgiler:\n" + "\n".join(relevant_info)
        
        prompt = f"""Sen profesyonel bir Türk Telekom çağrı merkezi temsilcisisin.

{knowledge_context}

{user_info}
{context}

KURALLAR:
- Yukarıdaki bilgileri kullanarak yanıt ver
- Kısa ve net ol (maksimum 2 cümle)
- Eğer bilgi yoksa, "Bu konuda size yardımcı olmak için daha detaylı bilgi almam gerekiyor" de

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
                
                # Yanıtı temizle
                if ai_response.startswith("Temsilci:"):
                    ai_response = ai_response[9:].strip()
                
                return ai_response
            else:
                return "Özür dilerim, şu anda teknik bir sorun yaşıyoruz."
                
        except Exception as e:
            return self.get_smart_response(user_message, context)
    
    def get_smart_response(self, user_message, context=""):
        """Akıllı yanıt sistemi (fallback)"""
        msg = user_message.lower()
        
        # Paket seçimi (1,2,3 numaraları)
        if msg.strip() in ["1", "2", "3"]:
            return self.handle_package_selection(msg.strip())
        
        # Yüksek internet isteği
        if any(word in msg for word in ["yüksek", "hızlı", "güçlü", "premium", "en iyi"]) and "internet" in msg:
            return "Size Premium Paket (200Mbps) öneriyorum! 200 TL'ye limitsiz internet ve konuşma. Onaylıyor musunuz?"
        
        # Ekonomik paket isteği  
        if any(word in msg for word in ["ucuz", "ekonomik", "uygun", "az"]) and any(word in msg for word in ["paket", "fiyat"]):
            return "Size Ekonomik Paket öneriyorum! 80 TL'ye 25Mbps internet. Onaylıyor musunuz?"
        
        # Genel paket soruları
        if "paket" in msg:
            return "Hangi tür paket arıyorsunuz? Yüksek hızlı internet mi, ekonomik çözüm mü?"
        elif "fatura" in msg:
            return "Fatura bilgilerinizi kontrol ediyorum. Bekleyiniz..."
        elif "problem" in msg or "sorun" in msg:
            return "Sorununuzu anlıyorum. Size hemen yardımcı olacağım."
        else:
            return "Size nasıl yardımcı olabilirim? Paket değişikliği, fatura sorgusu veya teknik destek için buradayım."
        """Paket seçimini işle"""
        if not self.current_user:
            return "Önce telefon numaranızı söylemeniz gerekiyor."
        
        packages = getAvailablePackages(self.current_user)
        
        try:
            selected_idx = int(selection) - 1
            if 0 <= selected_idx < len(packages):
                selected_package = packages[selected_idx]
                
                # Paket değişikliğini başlat
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
        
        if "paket değiştir" in user_message.lower() or "paket değişikliği" in user_message.lower():
            return self.handle_package_change_ai(user_message)
        elif "kimliğim" in user_message.lower() or "bilgilerim" in user_message.lower():
            return self.handle_user_info(user_message)
        elif user_message.startswith("555"):
            return self.identify_user(user_message)
        else:
            # Ollama AI yanıtı
            context = f"Mevcut kullanıcı: {self.current_user}" if self.current_user else "Kullanıcı henüz tanımlanmadı"
            return self.get_ollama_response(user_message, context)
    
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
        📋 Bilgileriniz:
        - Ad Soyad: {user_info['name']} {user_info['surname']}
        - Mevcut Paket: {user_info['current_package']}
        - Sözleşme Bitiş: {user_info['contract_end_date']}
        - Ödeme Durumu: {user_info['payment_status']}
        """
    
    def handle_package_change_ai(self, message):
        """Basit paket değişikliği simülasyonu"""
        if not self.current_user:
            return "Önce telefon numaranızı söylemeniz gerekiyor."
        
        # Mevcut paketleri al
        packages = getAvailablePackages(self.current_user)
        package_info = "📦 Mevcut Paketlerimiz:\n"
        for i, pkg in enumerate(packages, 1):
            package_info += f"{i}. **{pkg['name']}**: {pkg['price']} - {pkg['details']}\n"
        
        return package_info + "\n💬 Hangi paketi tercih edersiniz? Paket numarasını söyleyebilirsiniz."

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
    st.sidebar.write("**Senaryo:** Paket Değişikliği")
    st.sidebar.write("**Agent Durumu:** ✅ Aktif")
    if st.session_state.agent.current_user:
        st.sidebar.write(f"**Mevcut Kullanıcı:** {st.session_state.agent.current_user}")
    
    # Test için hızlı butonlar
    st.sidebar.title("🚀 Hızlı Test")
    st.sidebar.write("Bu numaraları deneyin:")
    st.sidebar.code("5551234567")
    st.sidebar.code("5559876543")

if __name__ == "__main__":
    main()