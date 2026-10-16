import streamlit as st
import pandas as pd
import math
import streamlit.components.v1 as components

st.set_page_config(page_title="Kütyo Prefabrik Teklif Programı", layout="wide")

# --- GİZLİLİK AYARLARI (GÖRÜNMEZLİK PELERİNİ + AVCI KOD) ---
st.markdown(
    """
    <style>
    header {visibility: hidden !important; display: none !important;}
    footer {visibility: hidden !important; display: none !important;}
    [data-testid="stToolbar"] {visibility: hidden !important; display: none !important;}
    button[title="View fullscreen"] {visibility: hidden !important; display: none !important;}
    div[class*="viewerBadge"] {visibility: hidden !important; display: none !important;}
    div[class*="styles_viewerBadge"] {visibility: hidden !important; display: none !important;}
    </style>
    """,
    unsafe_allow_html=True
)

components.html(
    """
    <script>
    setInterval(function() {
        try {
            var badges = window.parent.document.querySelectorAll('div[class*="viewerBadge"], [data-testid="stToolbar"], button[title="View fullscreen"]');
            for (var i = 0; i < badges.length; i++) {
                badges[i].style.setProperty('display', 'none', 'important');
            }
        } catch(e) {}
        try {
            var localBadges = document.querySelectorAll('div[class*="viewerBadge"], [data-testid="stToolbar"], button[title="View fullscreen"]');
            for (var j = 0; j < localBadges.length; j++) {
                localBadges[j].style.setProperty('display', 'none', 'important');
            }
        } catch(e) {}
    }, 1000);
    </script>
    """,
    height=0,
    width=0,
)
# ------------------------------------------------

# --- ŞİFRE KORUMASI ---
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    col_kilit1, col_kilit2, col_kilit3 = st.columns([1, 2, 1])
    with col_kilit2:
        st.title("🔒 Kütyo Prefabrik Giriş")
        pwd = st.text_input("Lütfen sistem şifresini girin:", type="password")
        if st.button("Giriş Yap", type="primary"):
            if pwd == "KÜTYO":
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("Hatalı şifre girdiniz!")
    st.stop()

# --- 1. VERİ GİRİŞİ BİRİM FİYATLARI (Baz Fiyatlar) ---
PRICES = {
    "C30": 5252.0, "C40": 5668.0, "C45": 5876.0, "C50": 6084.0,
    "DEMIR": 45.22, "PLAKA": 55.12, "HASIR": 49.86, "HALAT": 47.87,
    "IZOLASYON_OLUK": 750.0, "IZOLASYON_CEPHE": 250.0, "STRAFOR": 525.0,
    "BUHAR": 600.0, "ISLETME": 1200.0, "FINANS": 200.0, "AMORTISMAN": 500.0,
    "PROJE": 350.0, "NAKLIYE": 300.78, "MONTAJ": 1010.75
}

# --- 2. REFERANSLAR ---
REFERENCES = {
    (15.44, 8.5): {"asik": 8, "doseme": 8, "l_kiris": 4, "deprem_kiris": 3, "el": {"AŞIK": {"C50": 0.28, "DEMIR": 29, "HASIR": 7.541499, "HALAT": 13}, "OLUK": {"C40": 0.74, "DEMIR": 61, "PLAKA": 25, "HASIR": 16.767975, "IZ_OLUK": 1}, "MAKAS": {"C40": 3.44, "DEMIR": 489, "PLAKA": 4, "HALAT": 92}, "DÖŞEME PLAĞI": {"C40": 1.71, "DEMIR": 65, "HASIR": 42, "HALAT": 22}, "L KİRİŞİ": {"C30": 1.54, "DEMIR": 274, "PLAKA": 8}, "DEPREM KİRİŞİ": {"C40": 1.20, "DEMIR": 135, "PLAKA": 8}, "VİNÇ KİRİŞİ": {"C40": 1.49, "DEMIR": 330, "PLAKA": 20}}},
    (15.44, 8.0): {"asik": 8, "doseme": 8, "l_kiris": 4, "deprem_kiris": 3, "el": {"AŞIK": {"C50": 0.26, "DEMIR": 28, "HASIR": 7.072674, "HALAT": 12}, "OLUK": {"C40": 0.70, "DEMIR": 58, "PLAKA": 24, "HASIR": 15.950025, "IZ_OLUK": 1}, "MAKAS": {"C40": 3.44, "DEMIR": 487, "PLAKA": 4, "HALAT": 92}, "DÖŞEME PLAĞI": {"C40": 1.71, "DEMIR": 65, "HASIR": 42, "HALAT": 22}, "L KİRİŞİ": {"C30": 1.54, "DEMIR": 274, "PLAKA": 8}, "DEPREM KİRİŞİ": {"C40": 1.13, "DEMIR": 128, "PLAKA": 8}, "VİNÇ KİRİŞİ": {"C40": 1.37, "DEMIR": 319, "PLAKA": 19}}},
    (15.44, 7.5): {"asik": 8, "doseme": 8, "l_kiris": 4, "deprem_kiris": 3, "el": {"AŞIK": {"C50": 0.20, "DEMIR": 26, "HASIR": 6.603849, "HALAT": 12}, "OLUK": {"C40": 0.65, "DEMIR": 45, "PLAKA": 23, "HASIR": 15.132075, "IZ_OLUK": 1}, "MAKAS": {"C40": 3.44, "DEMIR": 487, "PLAKA": 4, "HALAT": 92}, "DÖŞEME PLAĞI": {"C40": 1.51, "DEMIR": 55, "HASIR": 37, "HALAT": 15}, "L KİRİŞİ": {"C30": 1.54, "DEMIR": 255, "PLAKA": 8}, "DEPREM KİRİŞİ": {"C40": 1.05, "DEMIR": 121, "PLAKA": 8}, "VİNÇ KİRİŞİ": {"C40": 1.37, "DEMIR": 319, "PLAKA": 19}}},
    (15.44, 7.0): {"asik": 8, "doseme": 8, "l_kiris": 4, "deprem_kiris": 3, "el": {"AŞIK": {"C40": 0.23, "DEMIR": 25, "HASIR": 6.135024, "HALAT": 11}, "OLUK": {"C30": 0.61, "DEMIR": 43, "PLAKA": 21, "HASIR": 14.314125, "IZ_OLUK": 1}, "MAKAS": {"C40": 3.44, "DEMIR": 456, "PLAKA": 4, "HALAT": 59}, "DÖŞEME PLAĞI": {"C40": 1.41, "DEMIR": 53, "HASIR": 35, "HALAT": 14}, "L KİRİŞİ": {"C30": 1.54, "DEMIR": 255, "PLAKA": 8}, "DEPREM KİRİŞİ": {"C40": 0.98, "DEMIR": 114, "PLAKA": 8}, "VİNÇ KİRİŞİ": {"C40": 1.62, "DEMIR": 267, "PLAKA": 16}}},
    (18.44, 8.5): {"asik": 10, "doseme": 8, "l_kiris": 4, "deprem_kiris": 3, "el": {"AŞIK": {"C50": 0.28, "DEMIR": 29, "HASIR": 7.541499, "HALAT": 13}, "OLUK": {"C40": 0.74, "DEMIR": 61, "PLAKA": 25, "HASIR": 16.767975, "IZ_OLUK": 1}, "MAKAS": {"C40": 4.22, "DEMIR": 580, "PLAKA": 4, "HALAT": 128}, "DÖŞEME PLAĞI": {"C40": 1.71, "DEMIR": 65, "HASIR": 42, "HALAT": 22}, "L KİRİŞİ": {"C30": 1.86, "DEMIR": 319, "PLAKA": 8}, "DEPREM KİRİŞİ": {"C40": 1.20, "DEMIR": 135, "PLAKA": 8}, "VİNÇ KİRİŞİ": {"C40": 1.49, "DEMIR": 330, "PLAKA": 20}}},
    (18.44, 8.0): {"asik": 10, "doseme": 8, "l_kiris": 4, "deprem_kiris": 3, "el": {"AŞIK": {"C45": 0.30, "DEMIR": 28, "HASIR": 7.072674, "HALAT": 12}, "OLUK": {"C40": 0.70, "DEMIR": 58, "PLAKA": 24, "HASIR": 15.950025, "IZ_OLUK": 1}, "MAKAS": {"C40": 4.22, "DEMIR": 580, "PLAKA": 4, "HALAT": 128}, "DÖŞEME PLAĞI": {"C40": 1.71, "DEMIR": 65, "HASIR": 42, "HALAT": 22}, "L KİRİŞİ": {"C30": 1.86, "DEMIR": 319, "PLAKA": 8}, "DEPREM KİRİŞİ": {"C40": 1.20, "DEMIR": 135, "PLAKA": 8}, "VİNÇ KİRİŞİ": {"C40": 1.37, "DEMIR": 319, "PLAKA": 19}}},
    (18.44, 7.5): {"asik": 10, "doseme": 8, "l_kiris": 4, "deprem_kiris": 3, "el": {"AŞIK": {"C45": 0.20, "DEMIR": 27, "HASIR": 6.603849, "HALAT": 12}, "OLUK": {"C40": 0.65, "DEMIR": 55, "PLAKA": 23, "HASIR": 15.132075, "IZ_OLUK": 1}, "MAKAS": {"C40": 4.22, "DEMIR": 567, "PLAKA": 4, "HALAT": 108}, "DÖŞEME PLAĞI": {"C40": 1.51, "DEMIR": 55, "HASIR": 37, "HALAT": 20}, "L KİRİŞİ": {"C30": 1.86, "DEMIR": 1379, "PLAKA": 8}, "DEPREM KİRİŞİ": {"C40": 1.05, "DEMIR": 121, "PLAKA": 8}, "VİNÇ KİRİŞİ": {"C40": 1.25, "DEMIR": 304, "PLAKA": 18}}},
    (18.44, 7.0): {"asik": 10, "doseme": 8, "l_kiris": 4, "deprem_kiris": 3, "el": {"AŞIK": {"C40": 0.23, "DEMIR": 25, "HASIR": 6.135024, "HALAT": 11}, "OLUK": {"C40": 0.61, "DEMIR": 42, "PLAKA": 21, "HASIR": 14.314125, "IZ_OLUK": 1}, "MAKAS": {"C40": 4.22, "DEMIR": 567, "PLAKA": 4, "HALAT": 108}, "DÖŞEME PLAĞI": {"C40": 1.41, "DEMIR": 53, "HASIR": 35, "HALAT": 19}, "L KİRİŞİ": {"C30": 1.86, "DEMIR": 1379, "PLAKA": 8}, "DEPREM KİRİŞİ": {"C40": 0.98, "DEMIR": 114, "PLAKA": 8}, "VİNÇ KİRİŞİ": {"C40": 1.62, "DEMIR": 267, "PLAKA": 16}}},
    (21.44, 8.5): {"asik": 12, "doseme": 9, "l_kiris": 6, "deprem_kiris": 4, "el": {"AŞIK": {"C45": 0.28, "DEMIR": 29, "HASIR": 7.541499, "HALAT": 19}, "OLUK": {"C40": 0.74, "DEMIR": 61, "PLAKA": 25, "HASIR": 16.76798, "IZ_OLUK": 1}, "MAKAS": {"C40": 4.83, "DEMIR": 718, "PLAKA": 4, "HALAT": 170}, "DÖŞEME PLAĞI": {"C40": 1.92, "DEMIR": 52, "HASIR": 45, "HALAT": 22}, "L KİRİŞİ": {"C30": 1.55, "DEMIR": 223, "PLAKA": 8}, "DEPREM KİRİŞİ": {"C40": 1.20, "DEMIR": 135, "PLAKA": 8}, "VİNÇ KİRİŞİ": {"C40": 1.49, "DEMIR": 330, "PLAKA": 20}}},
    (21.44, 8.0): {"asik": 12, "doseme": 9, "l_kiris": 6, "deprem_kiris": 4, "el": {"AŞIK": {"C45": 0.26, "DEMIR": 28, "HASIR": 7.072674, "HALAT": 18}, "OLUK": {"C40": 0.70, "DEMIR": 53, "PLAKA": 24, "HASIR": 15.95003, "IZ_OLUK": 1}, "MAKAS": {"C40": 4.83, "DEMIR": 718, "PLAKA": 4, "HALAT": 170}, "DÖŞEME PLAĞI": {"C40": 1.80, "DEMIR": 51, "HASIR": 43, "HALAT": 21}, "L KİRİŞİ": {"C30": 1.55, "DEMIR": 223, "PLAKA": 8}, "DEPREM KİRİŞİ": {"C40": 1.13, "DEMIR": 128, "PLAKA": 8}, "VİNÇ KİRİŞİ": {"C40": 1.37, "DEMIR": 319, "PLAKA": 19}}},
    (21.44, 7.5): {"asik": 12, "doseme": 9, "l_kiris": 6, "deprem_kiris": 4, "el": {"AŞIK": {"C45": 0.24, "DEMIR": 27, "HASIR": 6.603849, "HALAT": 18}, "OLUK": {"C40": 0.65, "DEMIR": 50, "PLAKA": 23, "HASIR": 15.13208, "IZ_OLUK": 1}, "MAKAS": {"C40": 4.83, "DEMIR": 689, "PLAKA": 4, "HALAT": 148}, "DÖŞEME PLAĞI": {"C40": 1.80, "DEMIR": 51, "HASIR": 43, "HALAT": 21}, "L KİRİŞİ": {"C30": 1.55, "DEMIR": 223, "PLAKA": 8}, "DEPREM KİRİŞİ": {"C40": 1.13, "DEMIR": 121, "PLAKA": 8}, "VİNÇ KİRİŞİ": {"C40": 1.25, "DEMIR": 304, "PLAKA": 18}}},
    (21.44, 7.0): {"asik": 12, "doseme": 9, "l_kiris": 6, "deprem_kiris": 4, "el": {"AŞIK": {"C45": 0.23, "DEMIR": 25, "HASIR": 6.135024, "HALAT": 15}, "OLUK": {"C40": 0.61, "DEMIR": 42, "PLAKA": 21, "HASIR": 14.31413, "IZ_OLUK": 1}, "MAKAS": {"C40": 4.83, "DEMIR": 688, "PLAKA": 4, "HALAT": 125}, "DÖŞEME PLAĞI": {"C40": 1.80, "DEMIR": 51, "HASIR": 43, "HALAT": 21}, "L KİRİŞİ": {"C30": 1.55, "DEMIR": 223, "PLAKA": 8}, "DEPREM KİRİŞİ": {"C40": 1.13, "DEMIR": 121, "PLAKA": 8}, "VİNÇ KİRİŞİ": {"C40": 1.62, "DEMIR": 267, "PLAKA": 16}}},
    (23.44, 8.5): {"asik": 12, "doseme": 9, "l_kiris": 6, "deprem_kiris": 4, "el": {"AŞIK": {"C50": 0.30, "DEMIR": 29, "HASIR": 7.541499, "HALAT": 19}, "OLUK": {"C40": 0.74, "DEMIR": 61, "PLAKA": 25, "HASIR": 16.76798, "IZ_OLUK": 1}, "MAKAS": {"C40": 5.37, "DEMIR": 801, "PLAKA": 4, "HALAT": 211}, "DÖŞEME PLAĞI": {"C40": 1.92, "DEMIR": 52, "HASIR": 45, "HALAT": 22}, "L KİRİŞİ": {"C30": 1.74, "DEMIR": 275, "PLAKA": 8}, "DEPREM KİRİŞİ": {"C40": 1.20, "DEMIR": 135, "PLAKA": 8}, "VİNÇ KİRİŞİ": {"C40": 1.49, "DEMIR": 330, "PLAKA": 20}}},
    (23.44, 8.0): {"asik": 12, "doseme": 9, "l_kiris": 6, "deprem_kiris": 4, "el": {"AŞIK": {"C45": 0.26, "DEMIR": 28, "HASIR": 7.072674, "HALAT": 18}, "OLUK": {"C40": 0.70, "DEMIR": 53, "PLAKA": 24, "HASIR": 15.95003, "IZ_OLUK": 1}, "MAKAS": {"C40": 5.37, "DEMIR": 832, "PLAKA": 4, "HALAT": 186}, "DÖŞEME PLAĞI": {"C40": 1.84, "DEMIR": 51, "HASIR": 44, "HALAT": 21}, "L KİRİŞİ": {"C30": 1.74, "DEMIR": 262, "PLAKA": 8}, "DEPREM KİRİŞİ": {"C40": 1.13, "DEMIR": 128, "PLAKA": 8}, "VİNÇ KİRİŞİ": {"C40": 1.37, "DEMIR": 319, "PLAKA": 19}}},
    (23.44, 7.5): {"asik": 12, "doseme": 9, "l_kiris": 6, "deprem_kiris": 4, "el": {"AŞIK": {"C45": 0.24, "DEMIR": 27, "HASIR": 6.603849, "HALAT": 15}, "OLUK": {"C40": 0.65, "DEMIR": 50, "PLAKA": 23, "HASIR": 15.13208, "IZ_OLUK": 1}, "MAKAS": {"C40": 5.37, "DEMIR": 816, "PLAKA": 4, "HALAT": 161}, "DÖŞEME PLAĞI": {"C40": 1.73, "DEMIR": 50, "HASIR": 41, "HALAT": 20}, "L KİRİŞİ": {"C30": 1.74, "DEMIR": 255, "PLAKA": 8}, "DEPREM KİRİŞİ": {"C40": 1.05, "DEMIR": 115, "PLAKA": 8}, "VİNÇ KİRİŞİ": {"C40": 1.25, "DEMIR": 304, "PLAKA": 18}}},
    (23.44, 7.0): {"asik": 12, "doseme": 9, "l_kiris": 6, "deprem_kiris": 4, "el": {"AŞIK": {"C45": 0.23, "DEMIR": 25, "HASIR": 6.135024, "HALAT": 15}, "OLUK": {"C40": 0.63, "DEMIR": 42, "PLAKA": 21, "HASIR": 14.31413, "IZ_OLUK": 1}, "MAKAS": {"C40": 5.37, "DEMIR": 762, "PLAKA": 4, "HALAT": 161}, "DÖŞEME PLAĞI": {"C40": 1.61, "DEMIR": 49, "HASIR": 39, "HALAT": 19}, "L KİRİŞİ": {"C30": 1.74, "DEMIR": 255, "PLAKA": 8}, "DEPREM KİRİŞİ": {"C40": 0.98, "DEMIR": 108, "PLAKA": 8}, "VİNÇ KİRİŞİ": {"C40": 1.62, "DEMIR": 267, "PLAKA": 16}}},
    (25.44, 8.5): {"asik": 14, "doseme": 10, "l_kiris": 6, "deprem_kiris": 4, "el": {"AŞIK": {"C50": 0.30, "DEMIR": 29, "HASIR": 7.541499, "HALAT": 19}, "OLUK": {"C40": 0.74, "DEMIR": 61, "PLAKA": 25, "HASIR": 16.76798, "IZ_OLUK": 1}, "MAKAS": {"C40": 5.90, "DEMIR": 956, "PLAKA": 4, "HALAT": 283}, "DÖŞEME PLAĞI": {"C40": 1.92, "DEMIR": 52, "HASIR": 47, "HALAT": 22}, "L KİRİŞİ": {"C30": 1.78, "DEMIR": 298, "PLAKA": 8}, "DEPREM KİRİŞİ": {"C40": 1.20, "DEMIR": 135, "PLAKA": 8}, "VİNÇ KİRİŞİ": {"C40": 1.49, "DEMIR": 330, "PLAKA": 20}}},
    (25.44, 8.0): {"asik": 14, "doseme": 10, "l_kiris": 6, "deprem_kiris": 4, "el": {"AŞIK": {"C45": 0.26, "DEMIR": 28, "HASIR": 7.072674, "HALAT": 18}, "OLUK": {"C40": 0.70, "DEMIR": 53, "PLAKA": 24, "HASIR": 15.95003, "IZ_OLUK": 1}, "MAKAS": {"C40": 5.90, "DEMIR": 905, "PLAKA": 4, "HALAT": 255}, "DÖŞEME PLAĞI": {"C40": 1.84, "DEMIR": 51, "HASIR": 44, "HALAT": 21}, "L KİRİŞİ": {"C30": 1.78, "DEMIR": 298, "PLAKA": 8}, "DEPREM KİRİŞİ": {"C40": 1.13, "DEMIR": 128, "PLAKA": 8}, "VİNÇ KİRİŞİ": {"C40": 1.37, "DEMIR": 319, "PLAKA": 19}}},
    (25.44, 7.5): {"asik": 14, "doseme": 10, "l_kiris": 6, "deprem_kiris": 4, "el": {"AŞIK": {"C45": 0.24, "DEMIR": 27, "HASIR": 6.603849, "HALAT": 15}, "OLUK": {"C40": 0.65, "DEMIR": 50, "PLAKA": 23, "HASIR": 15.13208, "IZ_OLUK": 1}, "MAKAS": {"C40": 5.90, "DEMIR": 1023, "PLAKA": 4, "HALAT": 201}, "DÖŞEME PLAĞI": {"C40": 1.73, "DEMIR": 50, "HASIR": 41, "HALAT": 20}, "L KİRİŞİ": {"C30": 1.78, "DEMIR": 269, "PLAKA": 8}, "DEPREM KİRİŞİ": {"C40": 1.05, "DEMIR": 115, "PLAKA": 8}, "VİNÇ KİRİŞİ": {"C40": 1.25, "DEMIR": 304, "PLAKA": 18}}},
    (25.44, 7.0): {"asik": 14, "doseme": 10, "l_kiris": 6, "deprem_kiris": 4, "el": {"AŞIK": {"C45": 0.23, "DEMIR": 25, "HASIR": 6.135024, "HALAT": 15}, "OLUK": {"C40": 0.61, "DEMIR": 42, "PLAKA": 21, "HASIR": 14.31413, "IZ_OLUK": 1}, "MAKAS": {"C40": 5.90, "DEMIR": 1070, "PLAKA": 4, "HALAT": 174}, "DÖŞEME PLAĞI": {"C40": 1.61, "DEMIR": 48, "HASIR": 39, "HALAT": 19}, "L KİRİŞİ": {"C30": 1.74, "DEMIR": 255, "PLAKA": 8}, "DEPREM KİRİŞİ": {"C40": 0.98, "DEMIR": 108, "PLAKA": 8}, "VİNÇ KİRİŞİ": {"C40": 1.62, "DEMIR": 267, "PLAKA": 16}}},
    (28.44, 8.5): {"asik": 14, "doseme": 10, "l_kiris": 6, "deprem_kiris": 4, "el": {"AŞIK": {"C50": 0.30, "DEMIR": 29, "HASIR": 7.541499, "HALAT": 19}, "OLUK": {"C40": 0.74, "DEMIR": 61, "PLAKA": 25, "HASIR": 16.76798, "IZ_OLUK": 1}, "MAKAS": {"C40": 7.40, "DEMIR": 1420, "PLAKA": 4, "HALAT": 220}, "DÖŞEME PLAĞI": {"C40": 1.96, "DEMIR": 52, "HASIR": 47, "HALAT": 22}, "L KİRİŞİ": {"C30": 2.11, "DEMIR": 378, "PLAKA": 8}, "DEPREM KİRİŞİ": {"C40": 1.20, "DEMIR": 135, "PLAKA": 8}, "VİNÇ KİRİŞİ": {"C40": 1.49, "DEMIR": 381, "PLAKA": 20}}},
    (28.44, 8.0): {"asik": 14, "doseme": 10, "l_kiris": 6, "deprem_kiris": 4, "el": {"AŞIK": {"C50": 0.28, "DEMIR": 28, "HASIR": 7.072674, "HALAT": 18}, "OLUK": {"C40": 0.70, "DEMIR": 58, "PLAKA": 24, "HASIR": 15.95003, "IZ_OLUK": 1}, "MAKAS": {"C40": 7.40, "DEMIR": 1304, "PLAKA": 4, "HALAT": 220}, "DÖŞEME PLAĞI": {"C40": 1.84, "DEMIR": 51, "HASIR": 44, "HALAT": 21}, "L KİRİŞİ": {"C30": 2.11, "DEMIR": 378, "PLAKA": 8}, "DEPREM KİRİŞİ": {"C40": 1.13, "DEMIR": 128, "PLAKA": 8}, "VİNÇ KİRİŞİ": {"C40": 1.37, "DEMIR": 369, "PLAKA": 19}}},
    (28.44, 7.5): {"asik": 14, "doseme": 10, "l_kiris": 6, "deprem_kiris": 4, "el": {"AŞIK": {"C50": 0.24, "DEMIR": 27, "HASIR": 6.603849, "HALAT": 15}, "OLUK": {"C40": 0.65, "DEMIR": 45, "PLAKA": 23, "HASIR": 15.13208, "IZ_OLUK": 1}, "MAKAS": {"C40": 7.40, "DEMIR": 1313, "PLAKA": 4, "HALAT": 190}, "DÖŞEME PLAĞI": {"C40": 1.73, "DEMIR": 55, "HASIR": 41, "HALAT": 15}, "L KİRİŞİ": {"C30": 2.11, "DEMIR": 378, "PLAKA": 8}, "DEPREM KİRİŞİ": {"C40": 1.05, "DEMIR": 121, "PLAKA": 8}, "VİNÇ KİRİŞİ": {"C40": 1.25, "DEMIR": 354, "PLAKA": 18}}},
    (28.44, 7.0): {"asik": 14, "doseme": 10, "l_kiris": 6, "deprem_kiris": 4, "el": {"AŞIK": {"C50": 0.20, "DEMIR": 27, "HASIR": 6.135024, "HALAT": 8}, "OLUK": {"C40": 0.61, "DEMIR": 42, "PLAKA": 21, "HASIR": 14.31413, "IZ_OLUK": 1}, "MAKAS": {"C40": 7.40, "DEMIR": 1227, "PLAKA": 4, "HALAT": 190}, "DÖŞEME PLAĞI": {"C40": 1.61, "DEMIR": 54, "HASIR": 39, "HALAT": 14}, "L KİRİŞİ": {"C30": 2.11, "DEMIR": 378, "PLAKA": 8}, "DEPREM KİRİŞİ": {"C40": 0.98, "DEMIR": 114, "PLAKA": 8}, "VİNÇ KİRİŞİ": {"C40": 1.62, "DEMIR": 317, "PLAKA": 16}}}
}

def get_reference(makas, oluk):
    search_makas = min(makas, 28.44)
    valid_refs = [(m, o) for (m, o) in REFERENCES.keys() if m >= search_makas and o >= oluk]
    if not valid_refs:
        st.error("Girdiğiniz ebatlar maksimum referans limitlerini aşıyor!")
        return None
    valid_refs.sort(key=lambda x: (x[0], x[1]))
    return valid_refs[0]

# --- ARAYÜZ ---
st.title("🏗️ Kütyo Prefabrik Kapsamlı Teklif ve Maliyet Yazılımı")
st.markdown("**Yazılım Geliştirici:** Y. İnş. Müh. Umut Doğuş Kaçmaz")

st.markdown(
    "<div style='position: fixed; bottom: 10px; right: 15px; font-size: 11px; color: gray; opacity: 0.6; z-index: 999;'>Kaçmaz Prefabrik</div>", 
    unsafe_allow_html=True
)

col1, col2, col3 = st.columns(3)
with col1:
    st.subheader("Geometri & Boyut")
    m_mesafe = st.number_input("Makas Yönü Aks Mesafesi (m) (1 adet makas boyu)", min_value=1.0, max_value=28.0, value=15.0)
    o_mesafe = st.number_input("Oluk Yönü Aks Mesafesi (m) (1 adet oluk boyu)", value=8.0)
    h_bina = st.number_input("Bina Yüksekliği (m)", value=8.0)
    st.markdown("---")
    bina_eni = st.number_input("Bina Eni (m)", value=20.0)
    bina_boyu = st.number_input("Bina Boyu (m)", value=40.0)

with col2:
    st.subheader("Bina Hol Düzeni")
    m_hol = st.number_input("Makas Yönü Hol Sayısı", min_value=1, value=2, step=1)
    o_aks = st.number_input("Oluk Yönü Aks Arası Sayısı", min_value=1, value=5, step=1)

with col3:
    st.subheader("Opsiyonlar & Finans")
    is_arakat = st.radio("Tek aksta arakat olsun mu?", ("Hayır", "Evet")) == "Evet"
    is_vinc = st.radio("Vinç Yükü Var mı? (12ton'a kadar)", ("Hayır", "Evet")) == "Evet"
    is_cephe = st.radio("Cephe Paneli Olsun mu?", ("Evet", "Hayır")) == "Evet"
    st.markdown("---")
    dolar_kuru = st.number_input("Güncel Dolar Kuru (TL)", value=49.30, step=0.10)
    st.info("Hesaplamalara %2 zam uygulanmış olup, Dolar kuruna endekslidir.")

if st.button("Metraj ve Fiyat Çıkar", type="primary"):
    ref_key = get_reference(m_mesafe, o_mesafe)
    
    if ref_key:
        ref = REFERENCES[ref_key]
        
        baz_dolar = 49.30
        artis_carpani = 1.02 * (dolar_kuru / baz_dolar)
        CURRENT_PRICES = {k: v * artis_carpani for k, v in PRICES.items()}
        
        cephe_m2 = 0.0
        if is_cephe:
            cevre = 2 * (bina_eni + bina_boyu)
            brut_cephe = cevre * (h_bina + 0.20)
            pencere_kapı_firesi = (cevre * 1.0) + (5.0 * 4.0)
            cephe_m2 = max(0, brut_cephe - pencere_kapı_firesi)
        
        if h_bina <= 8.0:
            cx, cy = 0.45, 0.45
        elif h_bina <= 10.0:
            cx, cy = 0.55, 0.55
        else:
            cx, cy = 0.60, 0.60
            
        kenar_m3_tek = (cx * cy * (h_bina + (2 * cy) + 0.35)) + 0.045
        orta_m3_tek = (cx * cy * (h_bina + (2 * cy) + 0.35))
        ruzgar_m3_tek = (cx * cy * (h_bina + (2 * cy) + 0.15))
        
        gercek_aks_sayisi = o_aks + 1 
        
        if m_mesafe <= 17.0:
            ruzgar_adet = 2 * m_hol
        else:
            ruzgar_adet = 4 * m_hol
            
        kenar_adet = gercek_aks_sayisi * 2
        orta_adet = (m_hol - 1) * gercek_aks_sayisi
        
        if is_arakat and gercek_aks_sayisi > 2:
            if m_mesafe <= 18:
                ruzgar_adet += 2 * m_hol
            elif 18 < m_mesafe <= 28: 
                ruzgar_adet += 3 * m_hol
        
        toplam_kenar_m3 = kenar_adet * kenar_m3_tek
        toplam_orta_m3 = orta_adet * orta_m3_tek
        toplam_ruzgar_m3 = ruzgar_adet * ruzgar_m3_tek
        
        kolonlar_total_m3 = toplam_kenar_m3 + toplam_orta_m3 + toplam_ruzgar_m3
        kolonlar_total_demir = kolonlar_total_m3 * 220 
        
        oluk_adet = (m_hol + 1) * o_aks
        makas_adet = m_hol * gercek_aks_sayisi
        asik_adet = ref["asik"] * o_aks * m_hol
        
        eleman_adetleri = {"AŞIK": asik_adet, "OLUK": oluk_adet, "MAKAS": makas_adet}
        
        if is_arakat:
            eleman_adetleri["DÖŞEME PLAĞI"] = (9 if m_mesafe <= 20.0 else 10) * m_hol
            eleman_adetleri["L KİRİŞİ"] = 6 * m_hol
            eleman_adetleri["DEPREM KİRİŞİ"] = 4 * m_hol
            
        if is_vinc:
            eleman_adetleri["VİNÇ KİRİŞİ"] = m_hol * o_aks * 2
            
        metraj_list = []
        metraj_list.append({
            "ELEMAN": f"KOLONLAR ({int(cx*100)}x{int(cy*100)})", "ADET": kenar_adet + orta_adet + ruzgar_adet,
            "C30 (m3)": kolonlar_total_m3, "C40 (m3)": 0.0, "C45 (m3)": 0.0, "C50 (m3)": 0.0,
            "DEMİR (kg)": kolonlar_total_demir, "PLAKA (kg)": 0.0, "HASIR (kg)": 0.0, "HALAT (kg)": 0.0, 
            "İZ_OLUK": 0.0, "İZ_CEPHE": 0.0, "STRAFOR (m3)": 0.0
        })
        
        for el_name, adet in eleman_adetleri.items():
            props = ref["el"].get(el_name, {})
            metraj_list.append({
                "ELEMAN": el_name, "ADET": adet,
                "C30 (m3)": props.get("C30", 0) * adet, "C40 (m3)": props.get("C40", 0) * adet,
                "C45 (m3)": props.get("C45", 0) * adet, "C50 (m3)": props.get("C50", 0) * adet,
                "DEMİR (kg)": props.get("DEMIR", 0) * adet, "PLAKA (kg)": props.get("PLAKA", 0) * adet,
                "HASIR (kg)": props.get("HASIR", 0) * adet, "HALAT (kg)": props.get("HALAT", 0) * adet,
                "İZ_OLUK": props.get("IZ_OLUK", 0) * adet, "İZ_CEPHE": props.get("IZOLASYON_CEPHE", 0) * adet,
                "STRAFOR (m3)": props.get("STRAFOR", 0) * adet
            })

        if is_cephe:
            metraj_list.append({
                "ELEMAN": "CEPHE PANELİ (m²)", "ADET": cephe_m2,
                "C30 (m3)": 0.087 * cephe_m2, "C40 (m3)": 0.0, "C45 (m3)": 0.0, "C50 (m3)": 0.0,
                "DEMİR (kg)": 0.53 * cephe_m2, "PLAKA (kg)": 1.00 * cephe_m2, "HASIR (kg)": 4.67 * cephe_m2,
                "HALAT (kg)": 0.0, "İZ_OLUK": 0.0, "İZ_CEPHE": 1.50 * cephe_m2, "STRAFOR (m3)": 0.04 * cephe_m2
            })
            
        df = pd.DataFrame(metraj_list)
        
        toplam_beton_m3 = df["C30 (m3)"].sum() + df["C40 (m3)"].sum() + df["C45 (m3)"].sum() + df["C50 (m3)"].sum()
        toplam_tonaj = toplam_beton_m3 * 2.5 
        
        df["TOPLAM MALİYET (TL)"] = 0.0
        genel_toplam = 0.0
        for idx, row in df.iterrows():
            maliyet = (
                (row["C30 (m3)"] * CURRENT_PRICES["C30"]) + (row["C40 (m3)"] * CURRENT_PRICES["C40"]) +
                (row["C45 (m3)"] * CURRENT_PRICES["C45"]) + (row["C50 (m3)"] * CURRENT_PRICES["C50"]) +
                (row["DEMİR (kg)"] * CURRENT_PRICES["DEMIR"]) + (row["PLAKA (kg)"] * CURRENT_PRICES["PLAKA"]) +
                (row["HASIR (kg)"] * CURRENT_PRICES["HASIR"]) + (row["HALAT (kg)"] * CURRENT_PRICES["HALAT"]) +
                (row["İZ_OLUK"] * CURRENT_PRICES["IZOLASYON_OLUK"]) + (row["İZ_CEPHE"] * CURRENT_PRICES["IZOLASYON_CEPHE"]) +
                (row["STRAFOR (m3)"] * CURRENT_PRICES["STRAFOR"])
            )
            df.at[idx, "TOPLAM MALİYET (TL)"] = maliyet
            genel_toplam += maliyet
            
        buhar_gideri = toplam_beton_m3 * CURRENT_PRICES["BUHAR"]
        isletme_gideri = toplam_beton_m3 * CURRENT_PRICES["ISLETME"]
        finans_gideri = toplam_beton_m3 * CURRENT_PRICES["FINANS"]
        amortisman = toplam_beton_m3 * CURRENT_PRICES["AMORTISMAN"]
        proje_hizmeti = toplam_beton_m3 * CURRENT_PRICES["PROJE"]
        
        makas_ilave_nakliye = makas_adet * 15000.0 * artis_carpani
        nakliye = (toplam_tonaj * CURRENT_PRICES["NAKLIYE"]) + makas_ilave_nakliye
        montaj = toplam_tonaj * CURRENT_PRICES["MONTAJ"]
        
        ekstra_giderler_toplami = buhar_gideri + isletme_gideri + finans_gideri + amortisman + proje_hizmeti + nakliye + montaj
        
        st.markdown("### Eleman Bazlı Metraj ve Fiyat")
        st.dataframe(df.style.format(precision=2), use_container_width=True)
        
        if is_cephe:
            st.info(f"**Not:** Cephe Paneli alanından ({cephe_m2:.2f} m²) 1 m bant pencere ve 1 adet 4x5 kapı düşülmüştür.")
        
        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown("#### ⚙️ Şantiye ve Operasyon Maliyetleri")
            st.write(f"- Toplam Beton Hacmi: **{toplam_beton_m3:.2f} m³**")
            st.write(f"- Toplam Hesaplanan Tonaj: **{toplam_tonaj:.2f} Ton**")
            st.write(f"- Nakliye Maliyeti: ₺ {nakliye:,.2f} *(Makas ilave dâhil)*")
            st.write(f"- Montaj Maliyeti: ₺ {montaj:,.2f}")
            
        with col_b:
            st.markdown("#### 💰 FİNAL TEKLİF ÖZETİ")
            st.success(f"Elemanların Malzeme Maliyeti: ₺ {genel_toplam:,.2f}")
            st.warning(f"Operasyon ve Nakliye Toplamı: ₺ {ekstra_giderler_toplami:,.2f}")
            st.error(f"GENEL TOPLAM TEKLİF BEDELİ: ₺ {(genel_toplam + ekstra_giderler_toplami):,.2f}")

        # --- GÜÇLENDİRİLMİŞ TÜRKÇE PDF OLUŞTURMA BÖLÜMÜ ---
        try:
            from fpdf import FPDF
            import base64
            import os
            import urllib.request
            
            # Google'dan Roboto Fontlarını Otomatik İndir
            font_reg = "Roboto-Regular.ttf"
            font_bold = "Roboto-Bold.ttf"
            
            if not os.path.exists(font_reg):
                urllib.request.urlretrieve("https://raw.githubusercontent.com/googlefonts/roboto/main/src/hinted/Roboto-Regular.ttf", font_reg)
            if not os.path.exists(font_bold):
                urllib.request.urlretrieve("https://raw.githubusercontent.com/googlefonts/roboto/main/src/hinted/Roboto-Bold.ttf", font_bold)
            
            total_maliyet = genel_toplam + ekstra_giderler_toplami
            musteri_fiyat = total_maliyet * 1.25  # %25 Kar Marjı
            
            # --- 1. PDF: İÇ KULLANIM (Maliyet Analizi) ---
            pdf1 = FPDF(orientation='L', unit='mm', format='A4')
            pdf1.set_auto_page_break(auto=True, margin=10) 
            pdf1.add_page()
            
            # Fontları PDF'e Tanıt
            if os.path.exists(font_reg) and os.path.exists(font_bold):
                pdf1.add_font("Roboto", "", font_reg)
                pdf1.add_font("Roboto", "B", font_bold)
                pdf1.set_font("Roboto", "B", 15)
            else:
                pdf1.set_font("Arial", "B", 15)
                
            pdf1.cell(0, 8, "KÜTYO PREFABRİK İÇ MALİYET RAPORU", ln=True, align="C")
            pdf1.ln(3)
            
            if os.path.exists(font_reg):
                pdf1.set_font("Roboto", "B", 10)
            else:
                pdf1.set_font("Arial", "B", 10)
            pdf1.cell(0, 5, "1. PROJE BİLGİLERİ", ln=True)
            
            if os.path.exists(font_reg):
                pdf1.set_font("Roboto", "", 9)
            else:
                pdf1.set_font("Arial", "", 9)
                
            pdf1.cell(0, 5, f"Makas Yönü: {m_mesafe}m | Oluk Yönü: {o_mesafe}m | Bina Yüksekliği: {h_bina}m | Bina Eni: {bina_eni}m | Bina Boyu: {bina_boyu}m", ln=True)
            pdf1.cell(0, 5, f"Hol Sayısı: {m_hol} | Oluk Aks Arası: {o_aks} | Arakat: {'Evet' if is_arakat else 'Hayır'} | Vinç: {'Evet' if is_vinc else 'Hayır'} | Cephe Paneli: {'Evet' if is_cephe else 'Hayır'}", ln=True)
            pdf1.ln(3)
            
            if os.path.exists(font_bold):
                pdf1.set_font("Roboto", "B", 10)
            else:
                pdf1.set_font("Arial", "B", 10)
                
            pdf1.cell(0, 5, "2. METRAJ VE MALİYET TABLOSU", ln=True)
            
            cols = ["ELEMAN", "MİKTAR", "C30", "C40", "C45", "C50", "DEMİR", "PLK.", "HSR.", "HLT.", "İZL.O", "İZL.C", "STRFR", "TOPLAM(TL)"]
            col_widths = [40, 14, 13, 13, 13, 13, 15, 12, 14, 12, 12, 12, 14, 25]
            
            pdf1.set_fill_color(220, 230, 241) 
            if os.path.exists(font_bold):
                pdf1.set_font("Roboto", "B", 7)
            else:
                pdf1.set_font("Arial", "B", 7)
                
            for i, col in enumerate(cols):
                pdf1.cell(col_widths[i], 5, col, border=1, align="C", fill=True)
            pdf1.ln()
            
            if os.path.exists(font_reg):
                pdf1.set_font("Roboto", "", 7)
            else:
                pdf1.set_font("Arial", "", 7)
                
            for idx, row in df.iterrows():
                el_name = str(row['ELEMAN'])
                pdf1.cell(col_widths[0], 5, el_name, border=1)
                adet_str = f"{row['ADET']:.2f}" if isinstance(row['ADET'], float) and not row['ADET'].is_integer() else str(int(row['ADET']))
                pdf1.cell(col_widths[1], 5, adet_str, border=1, align="C")
                pdf1.cell(col_widths[2], 5, f"{row['C30 (m3)']:.2f}", border=1, align="C")
                pdf1.cell(col_widths[3], 5, f"{row['C40 (m3)']:.2f}", border=1, align="C")
                pdf1.cell(col_widths[4], 5, f"{row['C45 (m3)']:.2f}", border=1, align="C")
                pdf1.cell(col_widths[5], 5, f"{row['C50 (m3)']:.2f}", border=1, align="C")
                pdf1.cell(col_widths[6], 5, f"{row['DEMİR (kg)']:.2f}", border=1, align="C")
                pdf1.cell(col_widths[7], 5, f"{row['PLAKA (kg)']:.2f}", border=1, align="C")
                pdf1.cell(col_widths[8], 5, f"{row['HASIR (kg)']:.2f}", border=1, align="C")
                pdf1.cell(col_widths[9], 5, f"{row['HALAT (kg)']:.2f}", border=1, align="C")
                pdf1.cell(col_widths[10], 5, f"{row['İZ_OLUK']:.0f}", border=1, align="C")
                pdf1.cell(col_widths[11], 5, f"{row['İZ_CEPHE']:.1f}", border=1, align="C")
                pdf1.cell(col_widths[12], 5, f"{row['STRAFOR (m3)']:.2f}", border=1, align="C")
                pdf1.cell(col_widths[13], 5, f"{row['TOPLAM MALİYET (TL)']:,.2f}", border=1, align="R")
                pdf1.ln()
                
            pdf1.ln(3)
            
            if os.path.exists(font_bold):
                pdf1.set_font("Roboto", "B", 10)
            else:
                pdf1.set_font("Arial", "B", 10)
            pdf1.cell(0, 5, "3. ŞANTİYE VE OPERASYON MALİYETLERİ", ln=True)
            
            if os.path.exists(font_reg):
                pdf1.set_font("Roboto", "", 9)
            else:
                pdf1.set_font("Arial", "", 9)
            pdf1.cell(0, 5, f"Toplam Beton Hacmi: {toplam_beton_m3:.2f} m3 | Toplam Tonaj: {toplam_tonaj:.2f} Ton", ln=True)
            pdf1.cell(0, 5, f"Malzeme Maliyeti: {genel_toplam:,.2f} TL | Operasyon ve Nakliye Toplamı: {ekstra_giderler_toplami:,.2f} TL", ln=True)
            pdf1.ln(2)
            
            if os.path.exists(font_bold):
                pdf1.set_font("Roboto", "B", 11)
            else:
                pdf1.set_font("Arial", "B", 11)
            pdf1.set_fill_color(255, 255, 204) 
            pdf1.cell(0, 7, f"GENEL TOPLAM MALİYET BEDELİ: {total_maliyet:,.2f} TL", ln=True, fill=True)
            
            out1 = pdf1.output(dest='S')
            b64_1 = base64.b64encode(out1.encode('latin-1') if isinstance(out1, str) else bytes(out1)).decode()
            
            # --- 2. PDF: MÜŞTERİ TEKLİF DOSYASI (Kurumsal, Tek Sayfa, %25 Kârlı) ---
            pdf2 = FPDF(orientation='P', unit='mm', format='A4')
            pdf2.set_auto_page_break(auto=True, margin=15)
            pdf2.add_page()
            
            if os.path.exists(font_reg) and os.path.exists(font_bold):
                pdf2.add_font("Roboto", "", font_reg)
                pdf2.add_font("Roboto", "B", font_bold)
                pdf2.set_font("Roboto", "B", 16)
            else:
                pdf2.set_font("Arial", "B", 16)
                
            pdf2.cell(0, 10, "KÜTYO PREFABRİK TEKLİF FORMU", ln=True, align="C")
            pdf2.ln(5)
            
            corp1 = "KÜTYO PREFABRİK: Geleceği Birlikte İnşa Ediyoruz\nKütahya 30 Ağustos Organize Sanayi Bölgesi'nde yer alan modern üretim tesisimiz ve güçlü kurumsal kimliğimizle, betonarme prefabrik yapı sektöründe yenilikçi, güvenilir ve kalıcı çözümler üretiyoruz. Kütahya başta olmak üzere çevre illere sunduğumuz anahtar teslim hizmetlerle, sanayicimizin, üreticimizin ve yatırımcımızın yapısal ihtiyaçlarını en üst mühendislik standartlarında karşılıyoruz."
            corp2 = "Sektörel Tecrübe ve Uzman Yönetim\nUzun yıllara dayanan köklü sektör tecrübemiz, vizyoner ve dinamik yönetim kadromuzla birleşerek KÜTYO Prefabrik'in sarsılmaz temelini oluşturmaktadır. Projelerimizin her aşamasında kalite disiplininden ödün vermeyen uzman ekibimiz; mimari tasarımdan üretime, lojistikten şantiye montajına kadar tüm süreçleri kusursuz bir koordinasyonla yönetmektedir. Kurumsal yapımız; şeffaflık, iş güvenliği, sürdürülebilirlik ve projeleri zamanında teslim etme prensipleri üzerine inşa edilmiştir."
            corp3 = "İleri Teknoloji ve Yönetmeliklere Tam Uyum\nYapı güvenliğini her şeyin üstünde tutan çalışma anlayışımızla, üretim hatlarımızda sektördeki en güncel kalıp sistemlerini ve ileri teknolojileri kullanıyoruz. İnşa ettiğimiz tüm betonarme prefabrik yapılar; güncel deprem yönetmeliklerine, yapı denetim standartlarına ve uluslararası kalite normlarına harfiyen uygun olarak tasarlanmakta ve üretilmektedir."
            corp4 = "Anahtar Teslim Proje Çözümlerimiz\nMüşterilerimizin işletme kapasitelerine ve sektörel ihtiyaçlarına özel, fonksiyonel, geniş açıklıklı ve yüksek dayanımlı anahtar teslim betonarme prefabrik yapılar inşa ediyoruz. Uzmanlık alanımıza giren yapılar:\n- Sanayi ve Üretim Tesisleri: Modern fabrikalar ve işlevsel sanayi dükkanları.\n- Depolama ve Lojistik: Yüksek tonajlı taşıma ve depolama kapasitesine sahip lojistik merkezleri.\n- Tarım ve Hayvancılık Yapıları: İklimlendirme ve hijyen standartlarına uyumlu besihaneler.\n- Ticari ve Sosyal Alanlar: Kapalı pazar yerleri ve spor tesisleri.\n\nKÜTYO Prefabrik olarak; inşaat süreçlerindeki hızı, ekonomik çözümleri ve sarsılmaz güvenliği bir araya getiren gücümüzle bölge ekonomisine değer katmaya ve iş ortaklarımızın geleceğini inşa etmeye devam ediyoruz."
            
            if os.path.exists(font_reg):
                pdf2.set_font("Roboto", "", 10)
            else:
                pdf2.set_font("Arial", "", 10)
                
            pdf2.multi_cell(0, 5, corp1)
            pdf2.ln(3)
            pdf2.multi_cell(0, 5, corp2)
            pdf2.ln(3)
            pdf2.multi_cell(0, 5, corp3)
            pdf2.ln(3)
            pdf2.multi_cell(0, 5, corp4)
            pdf2.ln(8)
            
            if os.path.exists(font_bold):
                pdf2.set_font("Roboto", "B", 12)
            else:
                pdf2.set_font("Arial", "B", 12)
                
            pdf2.cell(0, 6, "PROJE BİLGİLERİ VE TEKLİF DETAYI", ln=True, border='B')
            pdf2.ln(3)
            
            bina_m2 = bina_eni * bina_boyu
            arakat_m2 = bina_eni * o_mesafe if is_arakat else 0.0
            
            if os.path.exists(font_reg):
                pdf2.set_font("Roboto", "", 11)
            else:
                pdf2.set_font("Arial", "", 11)
                
            pdf2.cell(50, 6, "Bina Taban Alanı:", 0, 0)
            pdf2.cell(0, 6, f"{bina_m2:,.2f} m²", 0, 1)
            pdf2.cell(50, 6, "Bina Yüksekliği:", 0, 0)
            pdf2.cell(0, 6, f"{h_bina} m", 0, 1)
            pdf2.cell(50, 6, "Arakat:", 0, 0)
            pdf2.cell(0, 6, f"Var ({arakat_m2:,.2f} m²)" if is_arakat else "Yok", 0, 1)
            pdf2.cell(50, 6, "Vinç Yükü:", 0, 0)
            pdf2.cell(0, 6, "Var (12 tona kadar)" if is_vinc else "Yok", 0, 1)
            pdf2.cell(50, 6, "Cephe Paneli:", 0, 0)
            pdf2.cell(0, 6, "Var" if is_cephe else "Yok", 0, 1)
            pdf2.ln(5)
            
            if os.path.exists(font_bold):
                pdf2.set_font("Roboto", "B", 14)
            else:
                pdf2.set_font("Arial", "B", 14)
                
            pdf2.set_fill_color(240, 240, 240)
            pdf2.cell(0, 10, f"ANAHTAR TESLİM TOPLAM BEDEL: {musteri_fiyat:,.2f} TL + KDV", ln=True, align="C", fill=True)
            pdf2.ln(8)
            
            if os.path.exists(font_reg):
                pdf2.set_font("Roboto", "", 10)
            else:
                pdf2.set_font("Arial", "I", 10)
                
            closing = "Teklifimizi memnuniyetle karşılamanızı umar, projelerinizde çözüm ortağınız olmaktan gurur duyarız. Değerli işbirliğiniz için teşekkür ederiz."
            pdf2.multi_cell(0, 5, closing, align="C")
            
            out2 = pdf2.output(dest='S')
            b64_2 = base64.b64encode(out2.encode('latin-1') if isinstance(out2, str) else bytes(out2)).decode()
            
            # Butonları yan yana yerleştirme
            st.markdown("<br>", unsafe_allow_html=True)
            col_btn1, col_btn2 = st.columns(2)
            with col_btn1:
                href1 = f'<div style="text-align: center;"><a href="data:application/pdf;base64,{b64_1}" download="Kutyo_Maliyet_Analizi.pdf" target="_blank" style="display: inline-block; padding: 12px 24px; background-color: #ff4b4b; color: white; text-decoration: none; border-radius: 5px; font-weight: bold; font-size: 15px;">📥 Maliyet PDF (İç Kullanım)</a></div>'
                st.markdown(href1, unsafe_allow_html=True)
            with col_btn2:
                href2 = f'<div style="text-align: center;"><a href="data:application/pdf;base64,{b64_2}" download="Kutyo_Musteri_Teklifi.pdf" target="_blank" style="display: inline-block; padding: 12px 24px; background-color: #007bff; color: white; text-decoration: none; border-radius: 5px; font-weight: bold; font-size: 15px;">📄 Müşteri Teklif PDF (%25 Kârlı)</a></div>'
                st.markdown(href2, unsafe_allow_html=True)
                
        except ImportError:
            st.error("Lütfen terminale `pip install fpdf2` yazın veya requirements.txt dosyanızı güncelleyin.")
