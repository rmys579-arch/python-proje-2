import scrapy #web sitesinden istenilen veriyi çekebilmek için bu kütüphaneyi içeri aktarıyoruz.

class JobAdItem(scrapy.Item):
    """
    Bu, benim Item tanımım. Çektiğim veriyi bir sonraki kişiye (Veri Mimarı) 
    teslim etmek için kullandığım veri yapısıdır. Yapılandırılmış bir Python 
    sözlüğü (dictionary) gibidir.
    """
    job_title = scrapy.Field()          # İş ilanının başlığını tutacak.
    company_name = scrapy.Field()       # İlanı yayınlayan şirketin adını tutacak.
    summary_description = scrapy.Field()# İş açıklamasının kısa özetini tutacak.
    ad_link = scrapy.Field()            # Tekrarlayan ilanları kontrol etmek için benzersiz link.#  1. Proje Kurulum Değişkenleri 
# Arama anahtar kelimesini buraya ayarlıyorum. Başlangıç için Python Developer seçtik.
SEARCH_KEYWORD = "Python-Developer" 

# Kariyer.net için başlangıç URL'ini oluşturuyorum. Bot, işe bu sayfadan başlayacak.
START_URL = f"https://www.kariyer.net/is-ilanlari/{SEARCH_KEYWORD}-is-ilanlari"
