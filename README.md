# 🏛️ Mikroservis Tabanlı Müzayede Sistemi
### Microservice-Based Auction System

> **Kocaeli Üniversitesi — Teknoloji Fakültesi — Bilişim Sistemleri Mühendisliği**
> Yazılım Geliştirme Laboratuvarı II | Proje 1

| | |
|---|---|
| **Öğrenci / Student** | Umut Kuzu (221307016) , Türkay Jafarli(221307112) |
| **Tarih / Date** | 28.03.2025 |
| **Ders / Course** | Yazılım Geliştirme Laboratuvarı II |

---

## İçindekiler / Table of Contents

1. [Giriş / Introduction](#1-giriş--introduction)
2. [Teknolojiler & Mimari / Technologies & Architecture](#2-teknolojiler--mimari--technologies--architecture)
3. [Servis Detayları / Service Details](#3-servis-detayları--service-details)
4. [Yük Testleri / Load Tests](#4-yük-testleri--load-tests)
5. [Kurulum / Quick Start](#5-kurulum--quick-start)
6. [Projenin Geleceği / Future Work](#6-projenin-geleceği--future-work)

---

## 1. Giriş / Introduction

### 🇹🇷 Türkçe

Bu proje, modern yazılım geliştirme süreçlerinin temelini oluşturan **Mikroservis Mimarisi** ile güvenli ve ölçeklenebilir bir çevrimiçi müzayede platformunun uçtan uca geliştirilmesini kapsamaktadır. Sistemin tüm dış trafiği, merkezi bir **Dispatcher (API Gateway)** üzerinden yönetilmekte; her servis kendi bağımsız MongoDB veritabanına sahip olmakta ve yalnızca iç Docker ağı üzerinden haberleşmektedir.

**Problemin Tanımı:** Geleneksel monolitik yapılarda tek bir servisin çökmesi sistemin tamamını etkiler. Bu proje; her bileşeni bağımsız ölçeklenebilir mikroservislere bölerek, JWT tabanlı merkezi yetkilendirme ve ağ izolasyonu ile güvenli, hata toleranslı bir müzayede platformu inşa etmeyi amaçlamaktadır.

**Amaç:** Dispatcher biriminin Test-Driven Development (TDD) disipliniyle geliştirilmesi; Richardson Olgunluk Modeli Seviye 2 standartlarına uygun RESTful API tasarımı; Docker Compose ile tek komutla ayağa kalkan tam izole bir sistem ortaya koymak.

### 🇬🇧 English

This project covers the end-to-end development of a secure and scalable online auction platform based on **Microservice Architecture**. All external traffic is managed through a central **Dispatcher (API Gateway)**; each service owns its isolated MongoDB database and communicates exclusively over an internal Docker network.

**Problem Statement:** In traditional monolithic architectures, a single service failure brings down the entire system. This project solves this by splitting each component into independently scalable microservices, implementing JWT-based centralized authorization and network isolation.

**Goal:** Develop the Dispatcher using Test-Driven Development (TDD); design RESTful APIs compliant with Richardson Maturity Model Level 2; deliver a fully isolated system that starts with a single `docker-compose up` command.

---

## 2. Teknolojiler & Mimari / Technologies & Architecture

### 2.1 Kullanılan Teknolojiler / Technology Stack

| Katman / Layer | Teknoloji / Technology | Açıklama / Description |
|---|---|---|
| API Gateway | FastAPI + httpx | Merkezi yönlendirme ve JWT doğrulama |
| Auth Service | FastAPI + passlib + python-jose | Kullanıcı kaydı, BCrypt hash, JWT üretimi |
| Item Service | FastAPI + Motor (async) | Ürün CRUD, RMM Level 2 |
| Bid Service | FastAPI + Motor (async) | Teklif oluşturma ve sorgulama |
| GUI Service | Streamlit + Plotly | Yönetim paneli, canlı izleme, yük testi UI |
| Veritabanı | MongoDB (Motor async driver) | Her servise izole NoSQL DB |
| Test | Pytest + FastAPI TestClient | TDD (Red-Green-Refactor) |
| Yük Testi | Locust | Eşzamanlı kullanıcı simülasyonu |
| Konteynerizasyon | Docker + Docker Compose | Tam izole servis orkestrasyonu |

### 2.2 Temel Mimari & Sistem Diyagramı / Core Architecture Diagram

```mermaid
graph TD
    User((İstemci / Browser)) -->|Port: 8000| Disp[Dispatcher Gateway]
    Locust[Locust Test Aracı] -->|Yük Testi :8089| Disp

    subgraph MerkeziYonetim["Merkezi Yönetim (Gateway)"]
        Disp -->|Yetki Doğrulama| JWT{JWT Check}
        JWT -->|Hatalı| E401[401 Unauthorized]
        JWT -->|Geçerli / Public| Route[Yönlendirme Tablosu]
    end

    subgraph MikroservisAg["İzole Mikroservis Ağı (İç Ağ)"]
        Route -->|Auth İşlemleri| AuthS[Auth Service :8002]
        Route -->|Ürün CRUD| ItemS[Item Service :8001]
        Route -->|Teklif Verme| BidS[Bid Service :8003]
    end

    subgraph NoSQLVeri["NoSQL Veri İzolasyonu"]
        AuthS --- DB_User[(MongoDB: users)]
        ItemS --- DB_Auction[(MongoDB: items)]
        BidS --- DB_Bid[(MongoDB: bids)]
    end

    subgraph SunumKatmani["Sunum Katmanı"]
        GUI[Streamlit GUI :8501] -->|API Çağrısı| Disp
    end

    style Disp fill:#f9f,stroke:#333,stroke-width:2px
    style JWT fill:#fff4dd,stroke:#d4a017,stroke-width:2px
    style DB_User fill:#e1f5fe,stroke:#01579b
    style DB_Auction fill:#e1f5fe,stroke:#01579b
    style DB_Bid fill:#e1f5fe,stroke:#01579b
```

### 2.3 Ağ İzolasyonu / Network Isolation

Docker Compose yapılandırmasında yalnızca **Dispatcher (8000)**, **GUI (8501)** ve **Locust (8089)** dış dünyaya açıktır. Tüm mikroservisler (`item_service`, `auth_service`, `bid_service`) sadece iç Docker ağında çalışır; dışarıdan doğrudan erişim **mümkün değildir**.

```mermaid
graph LR
    Internet["🌐 İnternet"] -->|8000| Disp[Dispatcher]
    Internet -->|8501| GUI[Streamlit GUI]
    Internet -->|8089| LocustUI[Locust UI]

    subgraph DockerNetwork["🔒 İç Docker Ağı (Dış Erişim Yok)"]
        Disp --> AuthS[Auth :8002]
        Disp --> ItemS[Item :8001]
        Disp --> BidS[Bid :8003]
        AuthS --> MongoDB[(MongoDB)]
        ItemS --> MongoDB
        BidS --> MongoDB
    end
```

> **Not:** `docker-compose.yml` dosyasında `item_service`, `auth_service` ve `bid_service` için `ports` alanı kasıtlı olarak kaldırılmıştır. Bu sayede söz konusu servisler yalnızca `dispatcher` üzerinden erişilebilir durumdadır.

### 2.4 Richardson Olgunluk Modeli / Richardson Maturity Model (RMM)

Richardson Olgunluk Modeli, REST API'lerinin ne kadar "RESTful" olduğunu 4 seviyede ölçer.

```mermaid
graph TD
    L0["Seviye 0 — Tek URI, tek metot (SOAP benzeri)"]
    L1["Seviye 1 — Kaynaklar URI ile ayrılır"]
    L2["✅ Seviye 2 — HTTP Metotları doğru kullanılır (Bu Proje)"]
    L3["Seviye 3 — HATEOAS (Hypermedia)"]
    L0 --> L1 --> L2 --> L3
    style L2 fill:#c8e6c9,stroke:#2e7d32,stroke-width:2px
```

Bu projede **Seviye 2** tam olarak uygulanmıştır:

| İşlem | URI | HTTP Metodu | Başarı Kodu |
|---|---|---|---|
| Ürün listeleme | `/items` | `GET` | 200 OK |
| Ürün oluşturma | `/items` | `POST` | 201 Created |
| Ürün güncelleme | `/items/{id}` | `PUT` | 200 OK |
| Ürün silme | `/items/{id}` | `DELETE` | 204 No Content |
| Kayıt | `/register` | `POST` | 201 Created |
| Giriş | `/login` | `POST` | 200 OK |
| Teklif verme | `/bids` | `POST` | 201 Created |
| Teklifleri görme | `/bids/{item_id}` | `GET` | 200 OK |

> ❌ Yanlış kullanım örneği: `POST /deleteItem?id=1`
> ✅ Bu projede: `DELETE /items/{item_id}` → `204 No Content`

### 2.5 Sistemin Docker Mimarisi / Docker Compose Architecture

```mermaid
graph TB
    subgraph Compose["docker-compose.yml"]
        direction TB
        mongo[("mongodb\nimage: mongo:latest\nvolume: mongo_data")]
        auth["auth_service\nbuild: ./auth_service\nport: iç ağ"]
        item["item_service\nbuild: ./item_service\nport: iç ağ"]
        bid["bid_service\nbuild: ./bid_service\nport: iç ağ"]
        disp["dispatcher\nbuild: ./dispatcher\nport: 8000:8000"]
        gui["gui_service\nbuild: ./gui_service\nport: 8501:8501"]
        loc["locust\nimage: locustio/locust\nport: 8089:8089"]

        mongo --> auth
        mongo --> item
        mongo --> bid
        auth --> disp
        item --> disp
        bid --> disp
        disp --> gui
        disp --> loc
    end
```

---

## 3. Servis Detayları / Service Details

### 3.1 Dispatcher (API Gateway)

Sistemin tek giriş noktasıdır. Tüm JWT doğrulama ve yönlendirme mantığı burada merkezileştirilmiştir. TDD (Red-Green-Refactor) döngüsüyle geliştirilmiştir.

**Sequence Diyagramı — Korumalı İstek Akışı:**

```mermaid
sequenceDiagram
    participant C as İstemci
    participant D as Dispatcher
    participant S as Mikroservis
    participant DB as MongoDB

    C->>D: POST /items (Authorization: Bearer <token>)
    D->>D: JWT doğrulama (verify_access)
    alt Token Geçersiz
        D-->>C: 401 Unauthorized
    else Token Geçerli
        D->>S: POST /items (iç ağ)
        S->>DB: insert_one(item)
        DB-->>S: inserted_id
        S-->>D: 201 Created + item JSON
        D-->>C: 201 Created + item JSON
    end
```

**Sequence Diyagramı — Login Akışı:**

```mermaid
sequenceDiagram
    participant C as İstemci
    participant D as Dispatcher
    participant A as Auth Service
    participant DB as MongoDB (users)

    C->>D: POST /login {username, password}
    D->>A: POST /token {username, password}
    A->>DB: find_one({username})
    DB-->>A: user belgesi
    A->>A: bcrypt.verify(password, hash)
    alt Doğrulama Başarılı
        A->>A: JWT üret (exp: 30dk)
        A-->>D: {access_token, token_type}
        D-->>C: {access_token, token_type}
    else Hatalı Bilgi
        A-->>D: 401 Unauthorized
        D-->>C: 401 Unauthorized
    end
```

**Sınıf Yapısı / Class Structure:**

```mermaid
classDiagram
    class Dispatcher {
        +SECRET_KEY: str
        +ALGORITHM: str
        +ITEM_SERVICE_URL: str
        +AUTH_SERVICE_URL: str
        +BID_SERVICE_URL: str
        +verify_access(authorization: str) dict
        +proxy_get_items() list
        +proxy_post_items(item: dict) JSONResponse
        +proxy_update_item(item_id: str, item_data: dict) dict
        +proxy_delete_item(item_id: str) Response
        +proxy_register(user: dict) dict
        +proxy_login(user: dict) dict
        +proxy_place_bid(bid_data: dict) JSONResponse
        +proxy_get_bids(item_id: str) list
        +universal_exception_handler(request, exc) JSONResponse
    }
```

**TDD Akış Diyagramı / TDD Flow:**

```mermaid
flowchart LR
    R["🔴 RED\ntest_dispatcher.py yazıldı\n(main.py henüz yok)"]
    G["🟢 GREEN\nmain.py oluşturuldu\ntestler geçti"]
    RF["🔵 REFACTOR\nKod temizlendi\nException handler eklendi"]
    R --> G --> RF --> R
```

### 3.2 Auth Service

Kullanıcı kayıt ve giriş işlemlerini yönetir. Şifreler BCrypt ile hashlenir, başarılı girişte 30 dakika geçerli JWT üretilir.

**Sınıf Yapısı:**

```mermaid
classDiagram
    class AuthService {
        +pwd_context: CryptContext
        +SECRET_KEY: str
        +ALGORITHM: str
        +ACCESS_TOKEN_EXPIRE_MINUTES: int
        +register(user: User) dict
        +login(user: User) dict
    }
    class User {
        +username: str
        +password: str
    }
    AuthService --> User
```

### 3.3 Item Service

Müzayede ürünlerinin CRUD işlemlerini gerçekleştirir. RMM Seviye 2 uyumludur: `PUT` ile güncelleme, `DELETE` ile silme sonrası `204 No Content` döner.

**Sınıf Yapısı:**

```mermaid
classDiagram
    class ItemService {
        +item_collection: AsyncIOMotorCollection
        +get_items() list
        +create_item(item: Item) dict
        +update_item(item_id: str, item_data: Item) dict
        +delete_item(item_id: str) Response
    }
    class Item {
        +name: str
        +description: str
        +starting_price: float
    }
    ItemService --> Item
```

**Akış Diyagramı — Silme İşlemi:**

```mermaid
flowchart TD
    A["DELETE /items/{item_id}"] --> B{ObjectId geçerli mi?}
    B -- Hayır --> C[400 Bad Request]
    B -- Evet --> D[MongoDB delete_one]
    D --> E{Silindi mi?}
    E -- deleted_count == 0 --> F[404 Not Found]
    E -- deleted_count == 1 --> G[204 No Content]
```

### 3.4 Bid Service

Teklif oluşturma ve sorgulama işlemlerini yönetir. `user_id` alanı Dispatcher tarafından JWT payload'ından enjekte edilir; servis doğrudan dışarıya kapalıdır.

**Sınıf Yapısı:**

```mermaid
classDiagram
    class BidService {
        +bid_collection: AsyncIOMotorCollection
        +place_bid(item_id, amount, user_id) dict
        +get_bids(item_id: str) list
    }
    class Bid {
        +item_id: str
        +user_id: str
        +amount: float
        +timestamp: datetime
    }
    BidService --> Bid
```

### 3.5 GUI Service (Streamlit)

Yönetim paneli üç sekme içerir: Ürün Yönetimi, Canlı İzleme ve Yük Testi. Dispatcher üzerinden tüm API çağrılarını yapar; doğrudan mikroservislere erişmez.

**Sekme Yapısı:**

```mermaid
graph TD
    GUI["Streamlit GUI :8501"]
    GUI --> T1["📦 Ürün Yönetimi\nGET/POST/DELETE /items"]
    GUI --> T2["📈 Canlı İzleme\nLatency grafiği + Audit Log"]
    GUI --> T3["🚀 Yük Testi\nEşzamanlı GET simülasyonu"]
    T1 --> D[Dispatcher :8000]
    T2 --> D
    T3 --> D
```

---

## 4. Yük Testleri / Load Tests

### 4.1 Locust Test Senaryosu

`locustfile.py` içinde tanımlanan `AuctionUser` sınıfı, gerçekçi bir kullanıcı davranışını simüle eder:

- `on_start`: Her sanal kullanıcı sisteme login olur ve JWT token alır.
- `@task(3) view_items`: Ağırlık 3 — ürün listeleme (okuma yoğunluklu trafik)
- `@task(1) post_bid`: Ağırlık 1 — rastgele ürüne teklif verme (yazma trafiği)

```mermaid
flowchart LR
    Start["on_start()\nPOST /login\nToken al"] --> Loop["Test Döngüsü"]
    Loop -->|%75 olasılık| VI["view_items()\nGET /items"]
    Loop -->|%25 olasılık| PB["post_bid()\nGET /items → POST /bids"]
    VI --> Loop
    PB --> Loop
```

**Test Konfigürasyonu:**

| Parametre | Değer |
|---|---|
| Hedef URL | `http://dispatcher:8000` |
| Bekleme Süresi | 1–3 saniye (kullanıcı başına) |
| Locust Arayüzü | `http://localhost:8089` |
| Test Senaryoları | 50 / 100 / 200 / 500 eşzamanlı kullanıcı |

### 4.2 GUI Yük Testi (Streamlit Tab 3)

Streamlit arayüzünün 3. sekmesinde yerleşik basit bir yük testi motoru bulunmaktadır. Eşzamanlı kullanıcı sayısı (1–100) ve süre (1–30 saniye) slider ile ayarlanabilir; sonuçlar Plotly grafiğiyle anlık izlenir.

### 4.3 Test Sonuçları / Test Results

#### 🧪 50 Eşzamanlı Kullanıcı / 50 Concurrent Users
<img width="1488" height="900" alt="50 kullanıcı" src="https://github.com/user-attachments/assets/2a18ab9e-2154-4641-aeb8-85312cf0dc82" />



> **Gözlem:** 50 kullanıcıda sistem kararlı çalıştı. ~30 RPS değerine ulaşıldı. p50 yanıt süresi ~100ms ile oldukça düşük seyretti. p95 ise ~2500ms'ye kadar çıktı ancak hata oranı minimumdaydı. Sistem bu yük altında sağlıklı çalışmaktadır.

---

#### 🧪 100 Eşzamanlı Kullanıcı / 100 Concurrent Users

<img width="1488" height="900" alt="100 Kullanıcı" src="https://github.com/user-attachments/assets/4005fb9c-4aa9-4e76-86c2-1a7b2199e20e" />


> **Gözlem:** 100 kullanıcıda RPS ~55'e yükseldi. p50 ~200ms stabil kaldı ancak p95 ~5000ms'ye ulaştı. Yük artışıyla birlikte bazı hata paketleri gözlemlendi. Dispatcher yönlendirme doğruluğunu korudu.

---

#### 🧪 200 Eşzamanlı Kullanıcı / 200 Concurrent Users


<img width="1488" height="900" alt="200 Kullanıcı" src="https://github.com/user-attachments/assets/567cf7a5-a0d2-4fa7-bd00-0b867c037f65" />

> **Gözlem:** 200 kullanıcıda p95 yanıt süresi ~6500ms'ye ulaştı. RPS ~25 seviyesinde dengelendi; sistemin bu noktada darboğaz yaşamaya başladığı gözlemlendi. Hata oranı belirgin şekilde arttı, MongoDB bağlantı havuzu baskı altına girdi.

---

#### 🧪 500 Eşzamanlı Kullanıcı / 500 Concurrent Users


<img width="1488" height="900" alt="500 Kullanıcı" src="https://github.com/user-attachments/assets/562128ae-4823-4aeb-b816-26b3d64b3f55" />

> **Gözlem:** 500 kullanıcıda p95 yanıt süresi ~25.000ms'ye (25 saniye) fırladı. Yüksek hata oranı gözlemlendi. Sistem bu yük seviyesinde belirgin şekilde zorlandı. Gerçek üretim ortamında horizontal scaling (birden fazla Dispatcher instance) ve MongoDB replica set ile bu durum iyileştirilebilir.

---

### 4.4 Ölçekleme & Değerlendirme / Scaling & Evaluation

| Eşzamanlı Kullanıcı | Maks. RPS | p50 Yanıt (ms) | p95 Yanıt (ms) | Hata Durumu |
|---|---|---|---|---|
| 50 | ~30 | ~100 | ~2.500 | ✅ Minimal |
| 100 | ~55 | ~200 | ~5.000 | ⚠️ Az hata |
| 200 | ~25 | ~300 | ~6.500 | ⚠️ Belirgin hata |
| 500 | ~65 | ~400 | ~25.000 | ❌ Yüksek hata |

**Değerlendirme / Evaluation:**

Sistem 50–100 kullanıcı aralığında sağlıklı ve kararlı çalışmaktadır. 200 kullanıcıdan itibaren MongoDB bağlantı havuzu ve async istek kuyruğu darboğaz oluşturmaktadır. 500 kullanıcıda p95 yanıt süresinin 25 saniyeye çıkması, mevcut tek-instance mimarisinin üretim için yetersiz kalacağını göstermektedir. Çözüm olarak Dispatcher'ın yatay ölçeklenmesi ve MongoDB bağlantı havuzu optimizasyonu önerilmektedir.

---

## 5. Kurulum / Quick Start

### Ön Gereksinimler / Prerequisites

- Docker Desktop (v24+)
- Docker Compose (v2+)

### 🚀 Tek Komutla Başlatma / One-Command Start

```bash
git clone <repo-url>
cd b2b-studio-auction
docker-compose up --build
```

### Servis Adresleri / Service Endpoints

| Servis | URL |
|---|---|
| Dispatcher (API Gateway) | `http://localhost:8000` |
| GUI (Yönetim Paneli) | `http://localhost:8501` |
| Locust (Yük Testi) | `http://localhost:8089` |
| API Dokümantasyonu | `http://localhost:8000/docs` |

### Test Kullanıcısı Oluşturma / Create Test User

```bash
# Kullanıcı kayıt
curl -X POST http://localhost:8000/register \
  -H "Content-Type: application/json" \
  -d '{"username": "umut_test", "password": "test123"}'

# Giriş & token al
curl -X POST http://localhost:8000/login \
  -H "Content-Type: application/json" \
  -d '{"username": "umut_test", "password": "test123"}'
```

### Testleri Çalıştırma / Run Tests

```bash
# Dispatcher TDD testleri
cd dispatcher && pytest test_dispatcher.py -v

# Auth Service testleri
cd auth_service && pytest test_auth.py -v

# Item Service testleri
cd item_service && pytest test_items.py -v

# Bid Service testleri
cd bid_service && pytest test_bids.py -v
```

---

## 6. Projenin Geleceği / Future Work

### 🇹🇷 Başarılar & Sınırlılıklar

**Başarılar:**
- Tam mikroservis izolasyonu sağlandı; her servis bağımsız ölçeklenebilir.
- TDD (Red-Green-Refactor) döngüsü Dispatcher için eksiksiz uygulandı.
- RMM Seviye 2 standartları tüm endpoint'lerde karşılandı.
- Docker Compose ile tek komutla tam çalışan sistem kuruldu.
- JWT tabanlı merkezi yetkilendirme ve ağ izolasyonu hayata geçirildi.

**Sınırlılıklar:**
- Token yenileme (refresh token) mekanizması henüz implemente edilmedi.
- Servisler arasında async event-driven iletişim (Kafka/RabbitMQ) bulunmuyor.
- HTTPS/TLS desteği eklenmedi .
- Servis sağlığı için health check endpoint sayısı sınırlı.

### 🇬🇧 Achievements & Limitations

**Achievements:**
- Full microservice isolation achieved; each service is independently scalable.
- TDD (Red-Green-Refactor) cycle fully implemented for the Dispatcher.
- RMM Level 2 standards met across all endpoints.
- Single `docker-compose up` command starts the entire system.
- JWT-based centralized authorization and network isolation implemented.

**Limitations:**
- Refresh token mechanism not yet implemented.
- No async event-driven inter-service communication (Kafka/RabbitMQ).
- HTTPS/TLS support not added ).
- Limited health check endpoints per service.

### 🔮 Olası Geliştirmeler / Future Improvements

```mermaid
graph LR
    NOW["Mevcut Sistem\n(RMM Level 2)"]
    F1["RMM Level 3\n(HATEOAS)"]
    F2["Kafka\nEvent-Driven"]
    F3["Kubernetes\nOrkestrasyonu"]
    F4["Refresh Token\n& OAuth2"]
    F5["CI/CD\nGitHub Actions"]
    NOW --> F1
    NOW --> F2
    NOW --> F3
    NOW --> F4
    NOW --> F5
```

---

<div align="center">

**Bridge to Bridge Studio** — *Art meets Engineering*

*Kocaeli Üniversitesi | Bilişim Sistemleri Mühendisliği | 2025–2026*

</div>
