
import scrapy
# Scrapy, veri yapısını ayrı bir dosyada istediği için
# 'items.py' dosyasında tanımladığım Item sınıfını içe aktarıyorum.
from .items import JobAdItem 

class KariyerSpider(scrapy.Spider):
    # Bu botumun adı. Botu çalıştırmak için bu adı kullanacağım.
    name = 'my_first_kariyer_scraper'
    
    # Scrapy'nin çalışmaya başlaması gereken URL'lerin listesi. Tek bir başlangıç URL'i yeterli.
    start_urls = [START_URL]
    
    #  2. Ana Fonksiyon: Bir Sayfa Yüklendiğinde Ne Yapılacak? 
    # Bu 'parse' metodu, Scrapy başarılı bir şekilde bir sayfayı indirdiğinde çağrılır.
    # 'response' objesi, sayfanın tüm HTML içeriğini içerir.
    def parse(self, response):
        
        # Öncelikle, sayfadaki tüm iş ilanlarının nerede olduğunu bota söylemeliyim.
        # İlan detaylarını tutan tüm ana konteynerleri (div'leri) bulmak için CSS Seçici kullanıyorum.
        # NOT: Bu seçicinin Kariyer.net'in güncel tasarımına göre doğru olduğundan emin olmalıyız!
        JOB_CARD_SELECTOR = 'div.list-items > div' 
        
        # Şimdi, sayfada bulduğum her bir iş ilanı elementi üzerinde tek tek döngü kuruyorum.
        for job_card in response.css(JOB_CARD_SELECTOR):
            
            # Her bir ilan için, verilerini depolamak üzere yeni bir 'JobAdItem' oluşturuyorum.
            item = JobAdItem()
            
            #  Veri Çekme Bölümü 
            
            # 1. İş Başlığını ve Linki Bulma
            # Başlık ve link genellikle bir <a> etiketi içinde birlikte bulunur.
            title_element = job_card.css('div.job-card-head > a')
            
            # <a> etiketinin içindeki metni başlık olarak alıyorum. (default='' ile hata yönetimini kolaylaştırıyorum)
            item['job_title'] = title_element.css('::text').get(default='').strip()
            
            # Benzersiz linki almak için 'href' özniteliğini çekiyorum.
            link = title_element.attrib.get('href', '')
            item['ad_link'] = response.urljoin(link) # response.urljoin, linki tam (mutlak) URL yapar.
            
            # 2. Şirket Adını Bulma
            # Şirket adı genellikle başlığa yakın bir paragraf (<p>) etiketi içindedir.
            company_text = job_card.css('div.job-card-head > p::text').get(default='')
            item['company_name'] = company_text.strip()
            
            # 3. Özet Açıklamayı Bulma
            # İlan kartında görünen kısa açıklama metnini çekiyorum.
            description_text = job_card.css('div.job-card-body > div.job-card-desc::text').get(default='')
            item['summary_description'] = description_text.strip()
            
            # Verisi toplanan Item'ı 'yield' ediyorum. Bu, temiz veriyi Scrapy'nin 
            # çıktı boru hattına gönderir (bu da 2. kişinin alacağı veridir).
            yield item
            
        #  3. Sayfalandırma (Pagination) Mantığı: Bir Sonraki Sayfayı Bulma 
        
        # Tüm ilanları işledikten sonra, bir sonraki sayfanın linkini bulmalıyım.
        # 'Sonraki' butonunu/linkini bulmak için CSS Seçici kullanıyorum.
        NEXT_PAGE_SELECTOR = 'div.pagination a.next::attr(href)' 
        
        next_page_url = response.css(NEXT_PAGE_SELECTOR).get()
        
        # Eğer link gerçekten varsa, bu demektir ki son sayfaya ulaşmadık!
        if next_page_url is not None:
            # Scrapy'ye bu yeni URL'i ziyaret etmesini söylüyorum.
            # Ayrıca yeni sayfa için de yine bu 'parse' metodunu çağırmasını istiyorum.
            # Bu, botu son linki bulana kadar otomatik olarak devam ettirir.
            yield response.follow(next_page_url, callback=self.parse)