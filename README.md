İş İlanı ve Yetenek Analiz Botu
Bu proje, iş arama sitesi olan kariyer.net'ten ilanları otomatik olarak tarayan, verileri temizleyip veritabanında saklayan ve sektörde en çok aranan yetkinlikleri (Python, SQL, İletişim vb.) analiz ederek görselleştiren bir veri mühendisliği projesidir.

🚀 Proje Hakkında
Teknoloji dünyasında hangi yeteneklerin daha değerli olduğunu anlamak zor olabilir. Bu proje sayesinde manuel olarak yüzlerce ilanı okumak yerine;

İlanları otomatik topluyoruz (Data Scraping).

Verileri temizleyip yapılandırıyoruz (Data Cleaning).

Hangi teknik (Hard Skills) ve sosyal (Soft Skills) yeteneklerin daha popüler olduğunu veriyle kanıtlıyoruz (Data Analysis).

✨ Temel Özellikler
Otomatik Veri Toplama: Selenium ile dinamik web sitelerinden veri çeker.

Akıllı Veritabanı Yönetimi: Duplicate ilanları link kontrolü ile engeller, sadece yeni ilanları kaydeder.

Gelişmiş Veri Temizliği: HTML etiketlerini, gereksiz boşlukları ve bozuk karakterleri temizler.

Kategorili Yetenek Analizi: İlan metinleri içinde belirlediğimiz yetenekleri  ayrı ayrı sayar.

Görsel Raporlama: Sonuçları Matplotlib kullanarak anlaşılır grafiklere döker.

🛠️ Kurulum ve Çalıştırma
Projeyi bilgisayarınızda çalıştırmak için aşağıdaki adımları izleyin:

1. Projeyi İndirin:

git clone https://github.com/kullaniciadi/is-ilani-analizi.git
cd is-ilani-analizi

2. Gerekli Kütüphaneleri Yükleyin:

pip install -r requirements.txt
(Eğer requirements.txt dosyanız yoksa manuel olarak: pip install selenium matplotlib)

3. WebDriver Ayarı:

Bilgisayarınızdaki Chrome sürümüne uygun chromedriverı indirin ve proje klasörüne atın.

4. Çalıştırın:

python main.py
📂 Proje Mimarisi (Modüller)
Proje, Sorumlulukların Ayrılığı (Separation of Concerns) ilkesine göre 3 ana modüle bölünmüştür:

Plaintext
├── scraper.py       # [Modül 1] Web'den ham veriyi çeken bot (Veri Toplama).
├── database.py      # [Modül 2] Veri temizliği, deduplication ve SQLite işlemleri.
├── main.py          # [Modül 3] Analiz mantığı, görselleştirme ve ana akış.
├── is_ilanlari.db   # [Çıktı] Verilerin kalıcı saklandığı veritabanı.
└── README.md        # Proje dokümantasyonu.
📊 Örnek Senaryo
Program çalıştığında konsolda şuna benzer bir akış gerçekleşir:

Plaintext
> Bot başlatılıyor...
> [SCRAPER] 50 adet ilan başarıyla çekildi.
> [DATABASE] Temizlik yapılıyor...
> [DATABASE] Rapor: 15 yeni ilan veritabanına eklendi. (35 ilan zaten mevcuttu, atlandı.)
> [ANALİZ] Veriler işleniyor...
> [SONUÇ] En çok aranan yetenek: Python (28 İlan)