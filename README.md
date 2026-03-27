# Müzayede Sistemi 

**Ekip Üyeleri:** 
* Umut Kuzu (221307016)
* Türkay Jafarlı()

**Tarih:** 27.03.2026

---

## 1. Giriş

### 1.1. Problemin Tanımı
Geleneksel (monolitik) yazılım mimarileri, özellikle müzayede ve anlık teklif verme gibi yoğun eşzamanlı trafiğin (concurrent traffic) yaşandığı sistemlerde darboğazlara (bottleneck) neden olmaktadır. Sistemin herhangi bir modülünde (örneğin kimlik doğrulama) yaşanan bir çökme, tüm uygulamanın erişilemez hale gelmesine yol açmaktadır. Ayrıca, istemcilerin (client) arka plandaki servislerin karmaşık ağ yapılarını bilmek zorunda kalması, hem güvenlik zafiyetleri yaratmakta hem de sistemin ölçeklenebilirliğini kısıtlamaktadır. 

### 1.2. Projenin Amacı
Bu projenin temel amacı, modern yazılım mühendisliği standartlarına uygun, **Mikroservis Mimarisi** tabanlı, güvenli ve yüksek erişilebilirliğe sahip bir "Müzayede Sistemi" geliştirmektir. 

Bu doğrultuda sistem;
* Tüm dış trafiği tek bir merkezden karşılayıp iç ağdaki servislere güvenle yönlendiren bir **Dispatcher (API Gateway)**,
* Her biri kendi bağımsız NoSQL (MongoDB) veritabanına sahip, izole edilmiş mikroservisler (`Item Service`, `Auth Service`, `Bid Service`),
* Hata payını minimize etmek için **Test-Driven Development (TDD)** disiplini,
* Endüstri standartlarında API tasarımı için **Richardson Olgunluk Modeli (RMM) Seviye 2** prensipleri,
* Sistem taşınabilirliğini ve izolasyonunu en üst düzeye çıkaran **Konteynerizasyon (Docker)** teknolojileri kullanılarak inşa edilmiştir.

* ## 2. Sistem Tasarımı ve Teorik Altyapı

### 2.1. Literatür İncelemesi

Modern yazılım mühendisliği literatüründe, özellikle eşzamanlı kullanıcı sayısının yüksek olduğu (müzayede sistemleri gibi) uygulamalarda geleneksel **Monolitik** mimarilerin yetersiz kaldığı görülmektedir. Monolitik yapılarda tüm iş mantığının, arayüzün ve veri erişim katmanının tek bir çalıştırılabilir dosya (executable) içinde bulunması; sistemin ölçeklenebilirliğini kısıtlamakta ve "Single Point of Failure" (Tek Nokta Hatası) riskini artırmaktadır.

Bu problemleri aşmak için literatürde **Mikroservis Mimarisi** öne çıkmaktadır. Mikroservis yaklaşımı, karmaşık bir uygulamayı, her biri kendi iş domaininden (domain-driven design) sorumlu, bağımsız olarak dağıtılabilen (deployable) ve ölçeklenebilen küçük servislere böler. Projemizde yer alan `Auth`, `Item` ve `Bid` servisleri bu izolasyon prensibine göre tasarlanmış olup, her birinin kendi bağımsız veri tabanına (MongoDB) sahip olması sağlanarak "Database per Service" deseni uygulanmıştır.

Mikroservis mimarilerinde ortaya çıkan "istemcilerin (client) çok sayıda servisle nasıl güvenli iletişim kuracağı" problemi ise literatürde **API Gateway (Dispatcher) Tasarım Deseni** ile çözülmektedir. API Gateway, tüm dış trafiği karşılayan tek bir giriş noktası (Single Entry Point) olarak çalışır. Projemizde Dispatcher birimi; ters vekil sunucusu (Reverse Proxy), merkezi yetkilendirme (Centralized Authentication - JWT) ve yük dağıtımı görevlerini üstlenerek iç ağdaki servisleri dış dünyanın karmaşasından ve güvenlik tehditlerinden izole etmektedir.

Son olarak, servisler arası iletişimin standartlaştırılması için  **REST (Representational State Transfer)** mimari stili benimsenmiştir. REST mimarisinin olgunluk seviyesini ölçmek için kullanılan **Richardson Olgunluk Modeli (RMM)**, projemizin API tasarım rehberi olmuştur.

---

### 2.2. Dispatcher (API GATEWAY)

Dispatcher, sistemin "Giriş Kapısı" (Entry Point) olarak işlev gören, tüm dış istekleri karşılayan, kimlik doğrulaması yapan ve trafiği ilgili mikroservislere yönlendiren merkezi birimdir. Bu birim, projenin en kritik bileşeni olup tamamen asenkron bir yapıda tasarlanmıştır.

### 2.2.1. TDD (Test-Driven Development) Uygulaması

Dispatcher geliştirilirken TDD disiplini uygulanmış; fonksiyonel kodlar yazılmadan önce test_dispatcher.py üzerinden beklenen davranışlar kurgulanmıştır.

* Red Phase : İlk aşamada **/health** ve **/items** yönlendirme testleri yazılmıştır. **test_get_items_routing** testinde, henüz arka plan servisleri ayağa kaldırılmadığı için sistemin 502 Bad Gateway dönmesi beklenmiş ve test bu şekilde doğrulanmıştır.
* Green Phase : Testleri karşılayacak FastAPI endpoint'leri ve httpx asenkron istemcisi eklenerek testlerin başarıyla geçmesi sağlanmıştır.

```python
def test_health_check(client):
    """Dispatcher'ın çalışıp çalışmadığını kontrol eden  test."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_get_items_routing(client):
    """Dispatcher'ın /items isteğini yönlendirip yönlendirmediğini test eder."""
    
    response = client.get("/items")
    assert response.status_code == 502
```

### 2.2.2. RESTful Mimari ve RMM Seviye 2 Standartları

Dispatcher, **Richardson Olgunluk Modeli (RMM) Seviye 2** prensiplerine tam uyum sağlar.  
Bu uyum, hem HTTP fiillerinin (verbs) doğru kullanımı hem de dönen durum kodları (status codes) ile pekiştirilmiştir.



### Teknoloji ve Port

- Servis dış dünyaya **8000 portu** üzerinden hizmet verir.
- Kullanılan teknolojiler:
  - **FastAPI** → Web framework
  - **httpx** → Asenkron HTTP iletişimi
  - **jose (JWT)** → Kimlik doğrulama ve güvenlik



### HTTP Fiil Kullanımı

CRUD işlemleri için standart HTTP metodları kullanılır:

- `GET`
- `POST`
- `PUT`
- `DELETE`

Bu istekler, ilgili mikroservislere **asenkron olarak proxy edilir**.



### Durum Kodları (Status Codes)

- **201 Created**  
  `proxy_post_items` ve `proxy_place_bid` fonksiyonlarında, başarılı kaynak oluşturma sonrası döndürülür.

- **204 No Content**  
  `proxy_delete_item` fonksiyonunda, başarılı silme işlemi sonrası gövdesiz yanıt olarak döndürülür.

- **401 Unauthorized**  
  `verify_access` fonksiyonunda, token eksikliği veya geçersizliği durumunda fırlatılır.

- **502 Bad Gateway**  
  Arka plandaki mikroservislere ulaşılamadığı durumlarda, TDD senaryolarına uygun olarak üretilir.


 ### 2.2.3. Çalışma Mantığı ve Akış Diyagramı

Dispatcher, asenkron G/Ç (I/O) desteği sunan FastAPI framework'ü ile geliştirilmiştir. Dış dünyadan gelen istekler `8000 portu` üzerinden karşılanır ve iç ağdaki (internal network) ilgili servislere `(Item:8001, Auth:8002, Bid:8003)` asenkron olarak iletilir.

* Asenkron İletişim: Tüm yönlendirme işlemleri **httpx.AsyncClient** kullanılarak **non-blocking** (bloklanmayan) yapıda gerçekleştirilir.

* Merkezi Güvenlik: `verify_access` fonksiyonu aracılığıyla ``JWT (JSON Web Token)`` tabanlı kimlik doğrulaması yapılır. ``python-jose`` kütüphanesi ile token içerisindeki sub (kullanıcı kimliği) alanı çözümlenerek yetkilendirme sağlanır.

* Loglama: Her istek ve hata durumu logging modülü üzerinden takip edilerek sistemin izlenebilirliği artırılmıştır.

* Dependency Injection	Depends(verify_access) kullanılarak sadece yetkili kullanıcıların kritik işlemleri (silme, güncelleme, teklif verme) yapması sağlanır.  


