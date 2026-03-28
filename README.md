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

graph TD
    User((İstemci / Browser)) -->|Port: 8000| Disp[Dispatcher Gateway]
    Locust[Locust Test Aracı] -->|Yük Testi: 8000| Disp
    
    subgraph "Merkezi Yönetim (Gateway)"
        Disp -->|Yetki Doğrulama| JWT{JWT Check}
        JWT -->|Hatalı| E401[401 Unauthorized]
        JWT -->|Geçerli / Public| Route[Yönlendirme Tablosu]
    end

    subgraph "İzole Mikroservis Ağı"
        Route -->|Auth İşlemleri| AuthS[Auth Service: 8002]
        Route -->|Ürün CRUD| ItemS[Item Service: 8001]
        Route -->|Teklif Verme| BidS[Bid Service: 8003]
    end

    subgraph "NoSQL Veri İzolasyonu"
        AuthS --- DB_User[(MongoDB: users)]
        ItemS --- DB_Auction[(MongoDB: items)]
        BidS --- DB_Bid[(MongoDB: bids)]
    end

    subgraph "Sunum Katmanı"
        GUI[Streamlit GUI: 8501] -->|API Çağrısı| Disp
    end

    style Disp fill:#f9f,stroke:#333,stroke-width:2px
    style JWT fill:#fff4dd,stroke:#d4a017,stroke-width:2px
    style DB_User fill:#e1f5fe,stroke:#01579b
    style DB_Auction fill:#e1f5fe,stroke:#01579b
    style DB_Bid fill:#e1f5fe,stroke:#01579b
