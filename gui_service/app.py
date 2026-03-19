import streamlit as st
import httpx
import pandas as pd
import plotly.express as px
import asyncio
import time
from datetime import datetime
import os


# --- KONFİGÜRASYON ---
GATEWAY_URL = os.getenv("GATEWAY_URL", "http://localhost:8000")
st.set_page_config(page_title="B2B Studio Auction Admin", layout="wide")

# Session State Hazırlığı
if "token" not in st.session_state: st.session_state.token = None
if "logs" not in st.session_state: st.session_state.logs = []
if "metrics" not in st.session_state: st.session_state.metrics = pd.DataFrame(columns=["timestamp", "latency", "status"])

# --- YARDIMCI FONKSİYONLAR ---
def add_log(method, path, status):
    new_log = {
        "Zaman": datetime.now().strftime("%H:%M:%S"),
        "Metot": method,
        "Yol": path,
        "Durum": status
    }
    st.session_state.logs.insert(0, new_log)
    if len(st.session_state.logs) > 20: st.session_state.logs.pop()

async def run_load_test(users, seconds):
    """Basit bir yük testi motoru"""
    start_time = time.time()
    results = []
    headers = {"Authorization": f"Bearer {st.session_state.token}"}
    
    while time.time() - start_time < seconds:
        tasks = []
        async with httpx.AsyncClient() as client:
            for _ in range(users):
                tasks.append(client.get(f"{GATEWAY_URL}/items")) # Yükü GET ile simüle ediyoruz
            responses = await asyncio.gather(*tasks, return_exceptions=True)
            for r in responses:
                if isinstance(r, httpx.Response):
                    results.append({"timestamp": datetime.now(), "latency": r.elapsed.total_seconds() * 1000, "status": r.status_code})
    return pd.DataFrame(results)

# --- ARAYÜZ BAŞLIĞI ---
st.title("🎨 Bridge to Bridge Studio | Mikroservis Yönetim Paneli")
st.markdown(f"**Durum:** {'🟢 Bağlı' if st.session_state.token else '🔴 Oturum Kapalı'}")

# --- SIDEBAR (Giriş & Sağlık) ---
with st.sidebar:
    st.header("🔐 Yetkilendirme")
    if not st.session_state.token:
        user = st.text_input("Kullanıcı")
        pw = st.text_input("Şifre", type="password")
        if st.button("Giriş Yap"):
            resp = httpx.post(f"{GATEWAY_URL}/login", json={"username": user, "password": pw})
            if resp.status_code == 200:
                st.session_state.token = resp.json().get("access_token")
                st.rerun()
            else: st.error("Hatalı giriş!")
    else:
        if st.button("Çıkış Yap"):
            st.session_state.token = None
            st.rerun()

    st.markdown("---")
    st.header("🚦 Servis Sağlığı")
    try:
        health = httpx.get(f"{GATEWAY_URL}/items", timeout=1.0)
        st.success("Dispatcher & Items: ONLINE")
    except: st.error("Sistem Erişilemez!")

# --- ANA PANEL (TABLI YAPI) ---
tab1, tab2, tab3 = st.tabs(["📦 Ürün Yönetimi", "📈 Canlı İzleme (Grafana Style)", "🚀 Yük Testi"])

with tab1:
    col_add, col_list = st.columns([1, 2])
    
    with col_add:
        st.subheader("Yeni Eser Ekle")
        with st.form("add_item_form"):
            n = st.text_input("Eser Adı")
            d = st.text_area("Açıklama")
            p = st.number_input("Fiyat", min_value=0.0)
            if st.form_submit_button("Sisteme Gönder"):
                h = {"Authorization": f"Bearer {st.session_state.token}"}
                r = httpx.post(f"{GATEWAY_URL}/items", json={"name":n, "description":d, "starting_price":p}, headers=h)
                if r.status_code == 201: 
                    st.success("Eklendi!"); add_log("POST", "/items", 201); time.sleep(1); st.rerun()
                else: st.error("Yetki hatası!")

    with col_list:
        st.subheader("Mevcut Ürünler (RMM Level 2)")
        items_resp = httpx.get(f"{GATEWAY_URL}/items")
        if items_resp.status_code == 200:
            df_items = pd.DataFrame(items_resp.json())
            if not df_items.empty:
                st.dataframe(df_items[["_id", "name", "starting_price"]], use_container_width=True)
                
                # SİLME İŞLEMİ (DELETE - RMM L2)
                target_id = st.selectbox("İşlem Yapılacak ID", df_items["_id"].tolist())
                if st.button("🗑️ Seçili Eseri Sil (DELETE)"):
                    h = {"Authorization": f"Bearer {st.session_state.token}"}
                    r = httpx.delete(f"{GATEWAY_URL}/items/{target_id}", headers=h)
                    if r.status_code == 204:
                        st.warning(f"{target_id} silindi!"); add_log("DELETE", f"/items/{target_id}", 204); time.sleep(1); st.rerun()
            else: st.info("Eser bulunamadı.")

with tab2:
    st.subheader("Dispatcher Trafik Analizi")
    if not st.session_state.metrics.empty:
        fig = px.line(st.session_state.metrics, x="timestamp", y="latency", title="İstek Gecikme Süresi (ms)")
        st.plotly_chart(fig, use_container_width=True)
    
    st.subheader("📋 Audit Log (Detaylı Trafik Tablosu)")
    st.table(st.session_state.logs)

with tab3:
    st.subheader("Sistem Stres Testi")
    st.write("Aynı anda birden fazla kullanıcı ile Dispatcher'ı zorlayalım.")
    u_count = st.slider("Eşzamanlı Kullanıcı Sayısı", 1, 100, 10)
    s_count = st.slider("Süre (Saniye)", 1, 30, 5)
    
    if st.button("🔥 TESTİ BAŞLAT"):
        if not st.session_state.token:
            st.error("Test için önce giriş yapmalısınız!")
        else:
            with st.spinner("Yük oluşturuluyor..."):
                test_results = asyncio.run(run_load_test(u_count, s_count))
                st.session_state.metrics = pd.concat([st.session_state.metrics, test_results])
                st.success(f"Test Tamamlandı! Toplam {len(test_results)} istek gönderildi.")
                st.rerun()