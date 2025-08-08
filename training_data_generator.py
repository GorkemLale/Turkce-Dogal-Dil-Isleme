import json

# 50 Training örneği - Türkçe Telekom Çağrı Merkezi
training_data = [
    # Paket Bilgilendirme
    {"instruction": "Ekonomik 8 GB paket nedir?", "output": "Ekonomik 8 GB paketi 149 TL aylık ücretle 8GB mobil internet sunar. Başlangıç seviyesi kullanıcılar için uygundur."},
    {"instruction": "Mega 35 GB hakkında bilgi ver", "output": "Mega 35 GB paketi 199 TL aylık ücretle 35GB mobil internet sunar. Aktif kullanıcılar için ideal bir pakettir."},
    {"instruction": "Ultra 60 GB paketi nasıl?", "output": "Ultra 60 GB paketi 259 TL aylık ücretle 60GB mobil internet sunar. Yoğun kullanıcılar için tasarlanmıştır."},
    {"instruction": "Premium 50 GB paket özellikleri", "output": "Premium 50 GB paketi 299 TL aylık ücretle 50GB mobil internet sunar. Premium seviye hizmet içerir."},
    {"instruction": "Standart 20 GB paket fiyatı", "output": "Standart 20 GB paketi 199 TL aylık ücretle 20GB mobil internet sunar. Ortalama kullanım için uygundur."},
    
    # Paket Değişikliği Talepleri
    {"instruction": "Mega 35 GB'ye geçmek istiyorum", "output": "Mega 35 GB paketine geçiş için kullanım bilgilerinizi kontrol ediyorum. Bu paket 199 TL aylık ücretle 35GB mobil internet sunar."},
    {"instruction": "Daha büyük bir pakete geçebilir miyim?", "output": "Tabii ki! Size Ultra 60 GB (259 TL) veya Max 70 GB (349 TL) paketlerini önerebilirim. Hangisi ilginizi çekiyor?"},
    {"instruction": "Paketimi değiştirmek istiyorum", "output": "Paket değişikliği için önce telefon numaranızı söylemeniz gerekiyor. Sonra size en uygun paketi önerebilirim."},
    {"instruction": "En ucuz pakete geçmek istiyorum", "output": "En ekonomik seçeneğimiz Ekonomik 8 GB paketi, 149 TL aylık ücretle 8GB mobil internet sunar."},
    {"instruction": "İnternetim çok çabuk bitiyor", "output": "Kullanım bilgilerinizi kontrol ederek size daha yüksek kapasiteli paket önerebilirim. Hangi paketi kullanıyorsunuz?"},
    
    # Müşteri Tanımlama
    {"instruction": "5551234567", "output": "Merhaba Ahmet Yılmaz! Mevcut paketiniz SuperNet 50. Size nasıl yardımcı olabilirim?"},
    {"instruction": "5559876543", "output": "Merhaba Ayşe Kaya! Mevcut paketiniz Ekonomik Paket. Size nasıl yardımcı olabilirim?"},
    {"instruction": "Kimliğimi doğrulayabilir misiniz?", "output": "Tabii ki! Lütfen telefon numaranızı söyleyiniz, size yardımcı olabileyim."},
    
    # Sistem Fonksiyon Kullanımı
    {"instruction": "Kullanımımı kontrol eder misiniz?", "output": "Kullanım bilgilerinizi kontrol ediyorum... Lütfen bekleyiniz."},
    {"instruction": "Kota durumumu öğrenebilir miyim?", "output": "Mevcut kota kullanımınızı sistemden sorguluyorum. Telefon numaranızı söyleyebilir misiniz?"},
    
    # Hata Durumları
    {"instruction": "Sistem hatası oluştu", "output": "Özür dilerim, şu anda sistemsel bir sorun yaşıyoruz. Size alternatif çözümler önerebilirim."},
    {"instruction": "Bilgilerime ulaşamıyorsunuz", "output": "Sistemde geçici bir sorun var. Tahmini kullanımınıza göre size paket önerisi yapabilirim."},
    
    # Genel Sorular
    {"instruction": "Adın ne?", "output": "Ben Türk Telekom AI asistanınızım. Size paket değişikliği konusunda yardımcı oluyorum."},
    {"instruction": "Kim bu?", "output": "Ben Türk Telekom çağrı merkezi AI asistanıyım. Size nasıl yardımcı olabilirim?"},
    {"instruction": "Merhaba", "output": "Merhaba! Türk Telekom çağrı merkezine hoş geldiniz. Size nasıl yardımcı olabilirim?"},
    
    # Tatil Paketleri
    {"instruction": "Tatil paketi var mı?", "output": "Evet! Tatil Extra 40 GB paketimiz var. 30 gün geçerli, 199 TL ücretle 40GB mobil internet sunar."},
    {"instruction": "Geçici paket istiyorum", "output": "Geçici ihtiyaçlarınız için Tatil Extra 40 GB paketimizi önerebilirim. 30 gün geçerli, 199 TL."},
    
    # İş/Kurumsal Sorular
    {"instruction": "İş için daha büyük paket lazım", "output": "İş kullanımı için Pro 45 GB (259 TL) veya Premium 50 GB (299 TL) paketlerini önerebilirim."},
    {"instruction": "Kurumsal paket var mı?", "output": "İş kullanımı için Pro 45 GB paketimiz mevcut. 259 TL aylık ücretle 45GB mobil internet sunar."},
    
    # Fiyat Sorguları
    {"instruction": "En pahalı paket hangisi?", "output": "En yüksek kapasiteli paketimiz Max 70 GB, 349 TL aylık ücretle 70GB mobil internet sunar."},
    {"instruction": "200 TL'ye hangi paket alırım?", "output": "199 TL'ye Mega 35 GB veya Standart 20 GB paketlerini alabilirsiniz. Hangisini tercih edersiniz?"},
    
    # Karşılaştırma Soruları
    {"instruction": "Mega ve Ultra paket farkı nedir?", "output": "Mega 35 GB (199 TL) ve Ultra 60 GB (259 TL) paketleri arasında 25GB fark var. Ultra daha yoğun kullanım için."},
    {"instruction": "Hangi paket daha uygun?", "output": "Kullanım alışkanlığınıza bağlı. Orta kullanım için Standart 20 GB, yoğun kullanım için Mega 35 GB önerebilirim."},
    
    # Olumsuz Durumlar
    {"instruction": "Paket değişikliği yapılamıyor", "output": "Paket değişikliği sorunu için alternatif çözümler arayalım. Taahhüt durumunuzu kontrol edebilir miyim?"},
    {"instruction": "İşlem başarısız oldu", "output": "İşlem sorunu için özür dilerim. Tekrar deneyebilir veya alternatif çözüm önerebilirim."},
    
    # Teknik Sorular
    {"instruction": "Paket ne zaman aktif olur?", "output": "Paket değişikliği genellikle 24 saat içinde aktifleşir. Sistem onayından sonra SMS bilgilendirmesi gelecek."},
    {"instruction": "Taahhüt var mı?", "output": "Taahhüt durumunuzu kontrol ediyorum. Telefon numaranızı söyleyebilir misiniz?"},
    
    # Müşteri Memnuniyetsizliği
    {"instruction": "Paketim sürekli bitiyor", "output": "Anlıyorum, bu durumda daha yüksek kapasiteli pakete geçmenizi öneriyorum. Kullanımınızı kontrol edelim."},
    {"instruction": "Çok pahalı", "output": "Bütçenize uygun seçenekler arayalım. Ekonomik 8 GB (149 TL) veya Başlangıç 12 GB (179 TL) nasıl?"},
    
    # Detaylı Açıklamalar
    {"instruction": "Tüm paketleri listele", "output": "Ekonomik 8GB (149 TL), Standart 20GB (199 TL), Mega 35GB (199 TL), Ultra 60GB (259 TL), Max 70GB (349 TL)."},
    {"instruction": "Orta seviye paket öner", "output": "Orta 30 GB paketini önerebilirim. 229 TL aylık ücretle 30GB mobil internet sunar."},
    
    # Özel Durumlar
    {"instruction": "Öğrenciyim, indirim var mı?", "output": "Öğrenci indirimleri için müşteri hizmetlerimizle iletişime geçmenizi öneriyorum. Size uygun paketi bulalım."},
    {"instruction": "Yaşlıyım, basit paket istiyorum", "output": "Size Ekonomik 8 GB paketini önerebilirim. Basit ve uygun fiyatlı, 149 TL aylık."},
    
    # Yönlendirme
    {"instruction": "Başka kimle konuşabilirim?", "output": "Ben size paket konularında yardımcı oluyorum. Başka konular için müşteri hizmetlerine yönlendirebilirim."},
    {"instruction": "İnsan temsilci istiyorum", "output": "Paket değişikliği konusunda size yardımcı olabilirim. Hangi konuda destek istiyorsunuz?"},
    
    # Onay ve Tamamlama
    {"instruction": "Tamam, bu paketi seçiyorum", "output": "Harika! Seçiminizi işleme alıyorum. Paket değişikliği 24 saat içinde aktifleşecek."},
    {"instruction": "Vazgeçtim", "output": "Sorun değil. Başka bir konuda size yardımcı olabilir miyim?"},
    
    # Acil Durumlar
    {"instruction": "Acil paket değişikliği", "output": "Acil durumunuzu anlıyorum. Hemen kullanım bilgilerinizi kontrol edip size en uygun paketi önereyim."},
    {"instruction": "Hemen değiştirin", "output": "Paket değişikliği talebinizi öncelikli olarak işleme alıyorum. Hangi paketi seçmek istiyorsunuz?"},
    
    # Bilgi Teyidi
    {"instruction": "Doğru anladın mı?", "output": "Evet, talebinizi doğru anladım. Size en uygun paketi önermeye çalışıyorum."},
    {"instruction": "Emin misin?", "output": "Evet, önerdiğim paket bilgileri doğru. Size uygun olup olmadığını kontrol edelim."},
    
    # Son Örnekler
    {"instruction": "Teşekkürler", "output": "Size yardımcı olabildiğim için memnunum. Başka bir konuda destek istiyorsanız buradayım."},
    {"instruction": "Güle güle", "output": "İyi günler! Türk Telekom'u tercih ettiğiniz için teşekkür ederiz."},
    {"instruction": "Yeterli bilgi aldım", "output": "Memnun olduğunuza sevindim. Paket değişikliği tamamlandığında SMS ile bilgilendirileceksiniz."},
    {"instruction": "Başka sorum yok", "output": "Anlıyorum. İyi günler dilerim, ihtiyacınız olduğunda buradayım."},
    {"instruction": "Bu kadar yeterli", "output": "Tabii ki! Size yardımcı olabildiğim için mutluyum. İyi günler!"}
]

# JSON formatında kaydet
with open('training_data.json', 'w', encoding='utf-8') as f:
    json.dump(training_data, f, ensure_ascii=False, indent=2)

print(f"✅ {len(training_data)} training örneği oluşturuldu!")
print("📄 Dosya: training_data.json")
print("\n📊 Örnek kategoriler:")
print("- Paket bilgilendirme: 5 örnek")
print("- Paket değişikliği: 5 örnek") 
print("- Müşteri tanımlama: 3 örnek")
print("- Hata durumları: 2 örnek")
print("- Genel sorular: 35 örnek")
print("\n🎯 Fine-tune için hazır!")