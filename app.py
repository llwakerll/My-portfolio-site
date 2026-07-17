import streamlit as st
import requests
import pandas as pd
import io
import time

from auth import (
    verify_login, load_users, add_user, delete_user,
    log_search, read_log,
    get_credits, has_enough_credits, deduct_credits, add_credits, set_credits,
    log_payment, read_payments,
    log_payment_request, read_payment_requests, approve_payment_request, reject_payment_request,
    validate_username, validate_password, username_exists,
    ARAMA_MALIYETI, ODEME_TELEFON, BASLANGIC_KREDISI,
)

st.set_page_config(page_title="İşletme Bulucu", page_icon="📍", layout="wide")

# ---------------------------------------------------------------------------
# STİL (modern, canlı, profesyonel tema)
# ---------------------------------------------------------------------------
st.markdown("""
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap" rel="stylesheet">
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header[data-testid="stHeader"] {background: transparent;}

    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    .stApp {
        background:
            radial-gradient(circle at 8% 8%, rgba(37, 99, 235, 0.10) 0%, transparent 40%),
            radial-gradient(circle at 92% 92%, rgba(124, 58, 237, 0.08) 0%, transparent 40%),
            linear-gradient(180deg, #f6f8fc 0%, #eef1f8 100%);
    }

    h1, h2, h3, h4, p, label, span, div {
        color: #0f172a;
    }

    /* --- Ana başlık / navbar --- */
    .app-navbar {
        display: flex;
        align-items: center;
        justify-content: space-between;
        background: linear-gradient(120deg, #1d4ed8 0%, #4338ca 100%);
        border-radius: 18px;
        padding: 1.3rem 1.8rem;
        margin-bottom: 1.6rem;
        box-shadow: 0 12px 28px rgba(29, 78, 216, 0.25);
    }
    .app-navbar .brand {
        font-size: 1.5rem;
        font-weight: 800;
        color: #ffffff;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    .app-navbar .tagline {
        color: #dbeafe;
        font-size: 0.85rem;
        font-weight: 500;
        margin-top: 0.15rem;
    }

    /* --- Giriş / Kayıt ekranı --- */
    .auth-wrapper {
        max-width: 460px;
        margin: 2.2rem auto 0 auto;
    }
    .auth-hero {
        text-align: center;
        margin-bottom: 1.6rem;
    }
    .auth-hero .logo-circle {
        width: 64px;
        height: 64px;
        border-radius: 20px;
        background: linear-gradient(135deg, #2563eb, #7c3aed);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.9rem;
        margin: 0 auto 0.9rem auto;
        box-shadow: 0 10px 24px rgba(37, 99, 235, 0.35);
    }
    .auth-hero h1 {
        font-size: 1.7rem;
        font-weight: 800;
        margin-bottom: 0.2rem;
        background: linear-gradient(120deg, #1e293b, #4338ca);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .auth-hero p {
        color: #64748b;
        font-size: 0.92rem;
    }

    .login-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 18px;
        padding: 2.2rem 2.2rem 1.6rem 2.2rem;
        box-shadow: 0 14px 32px rgba(15, 23, 42, 0.09);
        animation: fadeUp 0.35s ease-out;
    }

    @keyframes fadeUp {
        from { opacity: 0; transform: translateY(8px); }
        to { opacity: 1; transform: translateY(0); }
    }

    .feature-strip {
        display: flex;
        justify-content: center;
        gap: 1.6rem;
        margin-top: 1.6rem;
        flex-wrap: wrap;
    }
    .feature-pill {
        display: flex;
        align-items: center;
        gap: 0.4rem;
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 999px;
        padding: 0.4rem 0.9rem;
        font-size: 0.8rem;
        font-weight: 600;
        color: #334155;
        box-shadow: 0 2px 8px rgba(15, 23, 42, 0.05);
    }

    div[data-testid="stMetric"] {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 14px;
        padding: 1rem;
        box-shadow: 0 4px 14px rgba(15, 23, 42, 0.06);
        transition: transform 0.15s ease;
    }
    div[data-testid="stMetric"]:hover {
        transform: translateY(-2px);
    }

    section[data-testid="stSidebar"] {
        background: #ffffff;
        border-right: 1px solid #e2e8f0;
    }

    .stButton > button {
        border-radius: 10px;
        font-weight: 700;
        transition: all 0.15s ease;
    }
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 6px 14px rgba(15, 23, 42, 0.12);
    }
    .stButton > button[kind="primary"] {
        background: linear-gradient(120deg, #2563eb, #4338ca);
        border-color: #2563eb;
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 4px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px 8px 0 0;
        font-weight: 600;
    }

    .role-badge {
        display: inline-block;
        padding: 2px 10px;
        border-radius: 999px;
        font-size: 0.75rem;
        font-weight: 700;
    }
    .role-admin { background: #ede9fe; color: #6d28d9; }
    .role-user { background: #d1fae5; color: #047857; }

    .credit-badge {
        display: inline-block;
        padding: 4px 14px;
        border-radius: 999px;
        font-size: 0.85rem;
        font-weight: 700;
        background: #fef9c3;
        color: #854d0e;
        border: 1px solid #fde68a;
    }

    .navbar-credit-badge {
        display: inline-block;
        padding: 6px 16px;
        border-radius: 999px;
        font-size: 0.85rem;
        font-weight: 700;
        background: rgba(255,255,255,0.15);
        color: #ffffff;
        border: 1px solid rgba(255,255,255,0.35);
    }

    .pricing-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 16px;
        padding: 1.5rem 1.2rem;
        text-align: center;
        box-shadow: 0 4px 16px rgba(15, 23, 42, 0.06);
        position: relative;
        transition: transform 0.15s ease, box-shadow 0.15s ease;
    }
    .pricing-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 12px 26px rgba(37, 99, 235, 0.14);
    }
    .pricing-card.popular {
        border: 2px solid #2563eb;
    }
    .pricing-card .badge-popular {
        position: absolute;
        top: -12px;
        left: 50%;
        transform: translateX(-50%);
        background: linear-gradient(120deg, #2563eb, #7c3aed);
        color: #fff;
        font-size: 0.7rem;
        font-weight: 800;
        padding: 3px 12px;
        border-radius: 999px;
        white-space: nowrap;
    }
    .pricing-card h3 {
        margin: 0.2rem 0;
        color: #2563eb;
    }
    .pricing-card .fiyat {
        font-size: 1.7rem;
        font-weight: 800;
        color: #1e293b;
    }
    .pricing-card .aciklama {
        color: #64748b;
        font-size: 0.85rem;
        margin-bottom: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 0.04em;
    }

    .contact-card {
        background: linear-gradient(120deg, #f0fdf4, #ecfdf5);
        border: 1px solid #bbf7d0;
        border-radius: 16px;
        padding: 1.5rem;
        margin-top: 1rem;
    }
    .contact-phone {
        font-size: 1.4rem;
        font-weight: 800;
        color: #15803d;
        letter-spacing: 0.5px;
    }
    a.whatsapp-btn {
        display: inline-block;
        background: #25D366;
        color: #ffffff !important;
        font-weight: 700;
        padding: 0.65rem 1.3rem;
        border-radius: 8px;
        text-decoration: none;
        margin-top: 0.6rem;
        transition: transform 0.15s ease;
    }
    a.whatsapp-btn:hover { transform: translateY(-1px); }
    a.call-btn {
        display: inline-block;
        background: #2563eb;
        color: #ffffff !important;
        font-weight: 700;
        padding: 0.65rem 1.3rem;
        border-radius: 8px;
        text-decoration: none;
        margin-top: 0.6rem;
        margin-left: 0.5rem;
        transition: transform 0.15s ease;
    }
    a.call-btn:hover { transform: translateY(-1px); }
    .pending-badge {
        display: inline-block;
        padding: 2px 10px;
        border-radius: 999px;
        font-size: 0.75rem;
        font-weight: 700;
        background: #fef3c7;
        color: #92400e;
    }

    .section-title {
        font-size: 1.15rem;
        font-weight: 800;
        margin: 0.2rem 0 0.6rem 0;
        display: flex;
        align-items: center;
        gap: 0.4rem;
    }
</style>
""", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# ARAMA MANTIĞI (OpenStreetMap)
# ---------------------------------------------------------------------------
NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
OVERPASS_URL = "https://overpass-api.de/api/interpreter"
HEADERS = {"User-Agent": "IsletmeBulucuApp/1.0 (kisisel kullanim)"}

KATEGORILER = {
    "Kuaför / Berber": [("shop", "hairdresser")],
    "Restoran": [("amenity", "restaurant")],
    "Kafe": [("amenity", "cafe")],
    "Diş Kliniği": [("amenity", "dentist")],
    "Eczane": [("amenity", "pharmacy")],
    "Market": [("shop", "supermarket"), ("shop", "convenience")],
    "Otel / Konaklama": [("tourism", "hotel"), ("tourism", "guest_house")],
    "Mobilyacı": [("shop", "furniture")],
    "Oto Tamirci": [("shop", "car_repair")],
    "Bar / Pub": [("amenity", "bar"), ("amenity", "pub")],
    "Banka": [("amenity", "bank")],
    "Spor Salonu": [("leisure", "fitness_centre")],
    "Avukat": [("office", "lawyer")],
    "Emlakçı": [("office", "estate_agent")],
    "Güzellik Salonu": [("shop", "beauty")],
    "Fırın / Pastane": [("shop", "bakery")],
    "Elektronik Mağazası": [("shop", "electronics")],
    "Giyim Mağazası": [("shop", "clothes")],
    "Özel etiket (ileri seviye)": [],
}

# Kredi paketleri: (görünen isim, kredi miktarı, fiyat TL)
KREDI_PAKETLERI = [
    {"ad": "Başlangıç", "kredi": 20, "fiyat": 49.0},
    {"ad": "Standart", "kredi": 60, "fiyat": 129.0},
    {"ad": "Pro", "kredi": 150, "fiyat": 249.0},
]


def geocode_location(location: str):
    params = {"q": location, "format": "json", "limit": 1}
    resp = requests.get(NOMINATIM_URL, params=params, headers=HEADERS, timeout=15)
    resp.raise_for_status()
    results = resp.json()
    if not results:
        return None
    bbox = results[0]["boundingbox"]
    south, north, west, east = map(float, bbox)
    return south, west, north, east, results[0].get("display_name", location)


def build_overpass_query(tag_pairs, bbox, custom_tag=None, custom_value=None):
    south, west, north, east = bbox
    filters = []
    if custom_tag:
        pairs = [(custom_tag, custom_value)] if custom_value else [(custom_tag, None)]
    else:
        pairs = tag_pairs

    for tag, value in pairs:
        tag_filter = f'["{tag}"="{value}"]' if value else f'["{tag}"]'
        for kind in ("node", "way", "relation"):
            filters.append(f'{kind}{tag_filter}({south},{west},{north},{east});')

    return f"""
    [out:json][timeout:60];
    (
      {' '.join(filters)}
    );
    out center tags;
    """


def run_overpass(query: str):
    resp = requests.post(OVERPASS_URL, data={"data": query}, headers=HEADERS, timeout=90)
    resp.raise_for_status()
    return resp.json().get("elements", [])


def elements_to_dataframe(elements: list) -> pd.DataFrame:
    rows = []
    seen = set()
    for el in elements:
        tags = el.get("tags", {})
        name = tags.get("name")
        if not name:
            continue

        if el["type"] == "node":
            lat, lon = el.get("lat"), el.get("lon")
        else:
            center = el.get("center", {})
            lat, lon = center.get("lat"), center.get("lon")

        key = (name, lat, lon)
        if key in seen:
            continue
        seen.add(key)

        phone = tags.get("contact:phone") or tags.get("phone") or ""
        website = tags.get("contact:website") or tags.get("website") or ""
        address_parts = [
            tags.get("addr:street", ""),
            tags.get("addr:housenumber", ""),
            tags.get("addr:district", ""),
            tags.get("addr:city", ""),
        ]
        address = " ".join(p for p in address_parts if p).strip()
        maps_link = f"https://www.google.com/maps?q={lat},{lon}" if lat and lon else ""

        rows.append({
            "İşletme Adı": name,
            "Telefon": phone,
            "Website": website,
            "Adres": address,
            "Enlem": lat,
            "Boylam": lon,
            "Harita Linki": maps_link,
        })
    return pd.DataFrame(rows)


def to_excel_bytes(df: pd.DataFrame) -> bytes:
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="İşletmeler")
        worksheet = writer.sheets["İşletmeler"]
        for i, col in enumerate(df.columns):
            max_len = max(df[col].astype(str).map(len).max(), len(col)) + 2
            worksheet.set_column(i, i, min(max_len, 50))
    return buffer.getvalue()


# ---------------------------------------------------------------------------
# GİRİŞ / KAYIT EKRANI
# ---------------------------------------------------------------------------
def show_login():
    st.markdown('<div class="auth-wrapper">', unsafe_allow_html=True)

    st.markdown("""
    <div class="auth-hero">
        <div class="logo-circle">📍</div>
        <h1>İşletme Bulucu</h1>
        <p>Türkiye genelinde saniyeler içinde işletme verisi bul, dışa aktar, büyüt.</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="login-card">', unsafe_allow_html=True)

    tab_login, tab_register = st.tabs(["🔐 Giriş Yap", "✨ Kayıt Ol"])

    with tab_login:
        st.markdown("<div style='height:0.4rem'></div>", unsafe_allow_html=True)
        username = st.text_input("Kullanıcı Adı", key="login_user", placeholder="kullanici_adi")
        password = st.text_input("Şifre", type="password", key="login_pass", placeholder="••••••••")

        if st.button("Giriş Yap", use_container_width=True, type="primary", key="login_btn"):
            if not username or not password:
                st.error("Lütfen kullanıcı adı ve şifreni gir.")
            else:
                role = verify_login(username, password)
                if role:
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.session_state.role = role
                    st.rerun()
                else:
                    st.error("Kullanıcı adı veya şifre hatalı.")

    with tab_register:
        st.markdown("<div style='height:0.4rem'></div>", unsafe_allow_html=True)
        st.caption(f"Kayıt olduğunda hesabına otomatik olarak **{BASLANGIC_KREDISI} kredi** tanımlanır — ilk aramaların bizden. 🎉")

        new_username = st.text_input("Kullanıcı Adı", key="reg_user", placeholder="en az 3 karakter")
        new_password = st.text_input("Şifre", type="password", key="reg_pass", placeholder="en az 6 karakter")
        new_password2 = st.text_input("Şifre (Tekrar)", type="password", key="reg_pass2", placeholder="şifreni tekrar gir")

        if st.button("Hesap Oluştur", use_container_width=True, type="primary", key="register_btn"):
            uname_err = validate_username(new_username)
            pass_err = validate_password(new_password)

            if uname_err:
                st.error(uname_err)
            elif pass_err:
                st.error(pass_err)
            elif new_password != new_password2:
                st.error("Şifreler birbiriyle uyuşmuyor.")
            elif username_exists(new_username.strip()):
                st.error("Bu kullanıcı adı zaten alınmış, başka bir tane dene.")
            else:
                created = add_user(new_username.strip(), new_password, role="user")
                if created:
                    st.success("Hesabın oluşturuldu! Şimdi giriş yapabilirsin. 🎉")
                    st.balloons()
                else:
                    st.error("Hesap oluşturulamadı, lütfen tekrar dene.")

    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="feature-strip">
        <div class="feature-pill">🗺️ OpenStreetMap verisi</div>
        <div class="feature-pill">⚡ Saniyeler içinde sonuç</div>
        <div class="feature-pill">⬇️ Excel / CSV dışa aktarım</div>
        <div class="feature-pill">🔒 Güvenli giriş</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# YÖNETİCİ PANELİ
# ---------------------------------------------------------------------------
def show_admin_panel():
    st.subheader("🛠️ Yönetici Paneli")

    tab1, tab2, tab3, tab4 = st.tabs(["Kullanıcılar", "Arama Geçmişi", "Ödeme Geçmişi", "Ödeme Talepleri"])

    with tab1:
        users = load_users()
        st.write("**Mevcut Kullanıcılar**")
        for uname, info in users.items():
            c1, c2, c3, c4 = st.columns([2.5, 1.5, 1.8, 2.2])
            c1.write(uname)
            badge_class = "role-admin" if info["role"] == "admin" else "role-user"
            c2.markdown(f'<span class="role-badge {badge_class}">{info["role"]}</span>', unsafe_allow_html=True)
            c3.markdown(f'<span class="credit-badge">💳 {info.get("credits", 0)} kredi</span>', unsafe_allow_html=True)
            with c4:
                sub1, sub2, sub3 = st.columns(3)
                if sub1.button("➖", key=f"minus_{uname}", help="5 kredi azalt"):
                    set_credits(uname, max(0, int(info.get("credits", 0)) - 5))
                    st.rerun()
                if sub2.button("➕", key=f"plus_{uname}", help="5 kredi ekle"):
                    add_credits(uname, 5)
                    st.rerun()
                if uname != "admin":
                    if sub3.button("🗑️", key=f"del_{uname}", help="Kullanıcıyı sil"):
                        delete_user(uname)
                        st.rerun()

        st.markdown("---")
        st.write("**Kredi Elle Ayarla**")
        cc1, cc2, cc3 = st.columns([2, 1.5, 1])
        secilen_kullanici = cc1.selectbox("Kullanıcı", list(users.keys()), key="admin_credit_user")
        yeni_kredi = cc2.number_input("Yeni kredi miktarı", min_value=0, value=int(users[secilen_kullanici].get("credits", 0)), step=1)
        if cc3.button("Kaydet", use_container_width=True):
            set_credits(secilen_kullanici, yeni_kredi)
            st.success(f"'{secilen_kullanici}' kullanıcısının kredisi {yeni_kredi} olarak ayarlandı.")
            st.rerun()

        st.markdown("---")
        st.write("**Yeni Kullanıcı Ekle**")
        with st.form("new_user_form", clear_on_submit=True):
            new_username = st.text_input("Kullanıcı adı")
            new_password = st.text_input("Şifre", type="password")
            new_role = st.selectbox("Rol", ["user", "admin"])
            submitted = st.form_submit_button("Ekle")
            if submitted:
                if not new_username or not new_password:
                    st.error("Kullanıcı adı ve şifre boş olamaz.")
                elif add_user(new_username, new_password, new_role):
                    st.success(f"'{new_username}' eklendi ve 20 kredi ile başlatıldı.")
                    st.rerun()
                else:
                    st.error("Bu kullanıcı adı zaten var.")

    with tab2:
        log_lines = read_log()
        if len(log_lines) <= 1:
            st.info("Henüz kayıtlı arama geçmişi yok.")
        else:
            header = log_lines[0].split(",")
            rows = [line.split(",") for line in log_lines[1:]]
            log_df = pd.DataFrame(rows, columns=header)
            st.dataframe(log_df, use_container_width=True, hide_index=True)

    with tab3:
        pay_lines = read_payments()
        if len(pay_lines) <= 1:
            st.info("Henüz kayıtlı ödeme yok.")
        else:
            header = pay_lines[0].split(",")
            rows = [line.split(",") for line in pay_lines[1:]]
            pay_df = pd.DataFrame(rows, columns=header)
            st.dataframe(pay_df, use_container_width=True, hide_index=True)

    with tab4:
        st.caption(
            "Kullanıcılar WhatsApp/telefon üzerinden ödeme yaptığını bildirdiğinde talepler burada listelenir. "
            "Ödemeyi aldığını doğruladıktan sonra 'Onayla' butonuna bas — krediler otomatik eklenir."
        )
        talepler = read_payment_requests()
        if not talepler:
            st.info("Bekleyen ödeme talebi yok.")
        else:
            for r in talepler:
                c1, c2, c3, c4, c5 = st.columns([2, 1.6, 1.4, 1.6, 2])
                c1.write(f"**{r['kullanici']}**")
                c2.write(r["paket"])
                c3.write(f"{r['kredi']} kredi")
                c4.write(f"{r['tutar']} TL")
                with c5:
                    a1, a2 = st.columns(2)
                    if a1.button("✅ Onayla", key=f"approve_{r['id']}", use_container_width=True):
                        if approve_payment_request(r["id"]):
                            st.success(f"{r['kullanici']} için {r['kredi']} kredi eklendi.")
                            st.rerun()
                        else:
                            st.error("Talep onaylanamadı.")
                    if a2.button("❌ Reddet", key=f"reject_{r['id']}", use_container_width=True):
                        reject_payment_request(r["id"])
                        st.rerun()
                st.caption(f"Talep zamanı: {r['zaman']}")
                st.markdown("---")


# ---------------------------------------------------------------------------
# ÖDEME / KREDİ YÜKLEME
# ---------------------------------------------------------------------------
def _whatsapp_link(paket, username):
    # 0546 115 61 34 -> 905461156134 (Türkiye ülke kodu + başındaki 0 atılır)
    numara = "90" + ODEME_TELEFON.strip().lstrip("0")
    mesaj = (
        f"Merhaba, İşletme Bulucu uygulamasında '{paket['ad']}' paketini "
        f"({paket['kredi']} kredi - {paket['fiyat']:.2f} TL) satın almak istiyorum. "
        f"Kullanıcı adım: {username}"
    )
    from urllib.parse import quote
    return f"https://wa.me/{numara}?text={quote(mesaj)}"


def show_payment_section():
    st.subheader("💳 Kredi Satın Al")
    st.caption(
        "Kredi satın almak için aşağıdan bir paket seç, ardından WhatsApp/telefon ile bize ulaş. "
        "Ödemen onaylandıktan sonra krediler hesabına tanımlanır."
    )

    cols = st.columns(len(KREDI_PAKETLERI))
    for i, (col, paket) in enumerate(zip(cols, KREDI_PAKETLERI)):
        with col:
            is_popular = (i == 1 and len(KREDI_PAKETLERI) >= 2)
            card_class = "pricing-card popular" if is_popular else "pricing-card"
            badge_html = '<div class="badge-popular">⭐ En Popüler</div>' if is_popular else ""
            st.markdown(f"""
            <div class="{card_class}">
                {badge_html}
                <div class="aciklama">{paket['ad']} Paket</div>
                <h3>{paket['kredi']} kredi</h3>
                <div class="fiyat">{paket['fiyat']:.2f} TL</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button(f"Bu Paketi Seç ({paket['ad']})", key=f"buy_{paket['ad']}", use_container_width=True):
                st.session_state.secilen_paket = paket
                st.session_state.odeme_adimi = "iletisim"
                st.rerun()

    if st.session_state.get("odeme_adimi") == "iletisim":
        paket = st.session_state.secilen_paket
        st.markdown("---")
        st.write(f"**{paket['ad']} paket** seçildi — {paket['kredi']} kredi — {paket['fiyat']:.2f} TL")

        telefon_okunabilir = ODEME_TELEFON
        wa_link = _whatsapp_link(paket, st.session_state.username)
        tel_link = f"tel:+90{ODEME_TELEFON.lstrip('0')}"

        st.markdown(f"""
        <div class="contact-card">
            <div>Ödeme yapmak / bilgi almak için bize ulaş:</div>
            <div class="contact-phone">📞 {telefon_okunabilir}</div>
            <a class="whatsapp-btn" href="{wa_link}" target="_blank">💬 WhatsApp'tan Yaz</a>
            <a class="call-btn" href="{tel_link}">📲 Hemen Ara</a>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("")
        st.caption(
            "Ödemeni yaptıktan sonra aşağıdaki butona basarak talebini kayda geçir — "
            "yöneticimiz ödemeni onayladığında krediler otomatik olarak hesabına eklenecek."
        )
        if st.button("✅ Ödemeyi Yaptım, Talebi Gönder", type="primary", use_container_width=True):
            log_payment_request(st.session_state.username, paket["ad"], paket["fiyat"], paket["kredi"])
            st.session_state.odeme_adimi = None
            st.success(
                f"Talebin alındı! {paket['kredi']} kredi, ödemen onaylandığında hesabına eklenecek. "
                "Onay durumunu buradan takip edebilirsin."
            )
            st.rerun()

    # Kullanıcının kendi bekleyen talepleri
    kendi_talepler = [r for r in read_payment_requests() if r["kullanici"] == st.session_state.username]
    if kendi_talepler:
        st.markdown("---")
        st.write("**Bekleyen Talebin**")
        for r in kendi_talepler:
            st.markdown(
                f'<span class="pending-badge">⏳ Onay bekliyor</span> &nbsp; '
                f'{r["paket"]} paket — {r["kredi"]} kredi — {r["tutar"]} TL &nbsp; '
                f'<span style="color:#94a3b8;font-size:0.8rem;">({r["zaman"]})</span>',
                unsafe_allow_html=True,
            )


# ---------------------------------------------------------------------------
# ANA UYGULAMA (giriş yapıldıktan sonra)
# ---------------------------------------------------------------------------
def show_main_app():
    with st.sidebar:
        st.markdown(f"👤 **{st.session_state.username}**")
        badge_class = "role-admin" if st.session_state.role == "admin" else "role-user"
        st.markdown(f'<span class="role-badge {badge_class}">{st.session_state.role}</span>', unsafe_allow_html=True)

        guncel_kredi = get_credits(st.session_state.username)
        st.markdown(f'<div style="margin-top:0.6rem;"><span class="credit-badge">💳 {guncel_kredi} kredi</span></div>', unsafe_allow_html=True)
        st.caption(f"Her arama {ARAMA_MALIYETI} kredi düşer.")

        st.markdown("---")

        if st.button("Çıkış Yap", use_container_width=True):
            for key in ("logged_in", "username", "role", "df", "odeme_adimi", "secilen_paket"):
                st.session_state.pop(key, None)
            st.rerun()

        st.markdown("---")
        st.header("Arama Ayarları")
        kategori = st.selectbox("İşletme kategorisi", list(KATEGORILER.keys()))

        custom_tag = None
        custom_value = None
        if kategori == "Özel etiket (ileri seviye)":
            st.markdown("[OSM etiketleri için tıkla](https://wiki.openstreetmap.org/wiki/Map_features)")
            custom_tag = st.text_input("Etiket (örn: shop)", value="shop")
            custom_value = st.text_input("Değer (örn: bookstore)", value="")

    guncel_kredi_nav = get_credits(st.session_state.username)
    st.markdown(f"""
    <div class="app-navbar">
        <div>
            <div class="brand">📍 İşletme Bulucu</div>
            <div class="tagline">OpenStreetMap verileriyle çalışır — API key veya kart bilgisi gerekmez.</div>
        </div>
        <div class="navbar-right" style="display:flex; align-items:center; gap:0.7rem;">
            <span class="navbar-credit-badge">💳 {guncel_kredi_nav} kredi</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if st.session_state.role == "admin":
        with st.expander("🛠️ Yönetici Paneli", expanded=False):
            show_admin_panel()

    with st.expander("💳 Kredi Satın Al", expanded=False):
        show_payment_section()

    location = st.text_input(
        "Nerede aramak istersin?",
        placeholder="Örn: Kadıköy İstanbul, Çankaya Ankara, Konak İzmir"
    )

    col1, col2 = st.columns([1, 5])
    with col1:
        search_clicked = st.button("🔍 Ara", type="primary", use_container_width=True)

    if "df" not in st.session_state:
        st.session_state.df = None

    if search_clicked:
        if not location:
            st.error("Lütfen bir konum yaz (örn: 'Kadıköy İstanbul').")
        elif kategori == "Özel etiket (ileri seviye)" and not custom_tag:
            st.error("Lütfen bir OSM etiketi gir (örn: 'shop').")
        elif not has_enough_credits(st.session_state.username, ARAMA_MALIYETI):
            st.error("Kredin yetersiz. Aramaya devam etmek için lütfen kredi satın al.")
        else:
            with st.spinner("Konum bulunuyor..."):
                try:
                    geo = geocode_location(location)
                except Exception as e:
                    st.error(f"Konum bulunurken hata oluştu: {e}")
                    geo = None

            if geo is None:
                st.warning("Bu konum bulunamadı. Daha genel bir isim dene.")
                st.session_state.df = None
            else:
                south, west, north, east, display_name = geo
                st.info(f"Aranan bölge: {display_name}")

                with st.spinner("İşletmeler aranıyor, bu 10-30 saniye sürebilir..."):
                    try:
                        query = build_overpass_query(
                            KATEGORILER[kategori], (south, west, north, east),
                            custom_tag, custom_value
                        )
                        elements = run_overpass(query)
                        df = elements_to_dataframe(elements)

                        if df.empty:
                            st.warning("Sonuç bulunamadı. Farklı bir kategori veya bölge dene.")
                            st.session_state.df = None
                        else:
                            deduct_credits(st.session_state.username, ARAMA_MALIYETI)
                            st.session_state.df = df
                            kalan_kredi = get_credits(st.session_state.username)
                            st.success(f"{len(df)} işletme bulundu. (Kalan kredi: {kalan_kredi})")
                            log_search(st.session_state.username, f"{kategori} - {location}", len(df))
                    except Exception as e:
                        st.error(f"Arama sırasında hata oluştu: {e}")
                        st.session_state.df = None

    if st.session_state.df is not None:
        df = st.session_state.df

        m1, m2, m3 = st.columns(3)
        m1.metric("Toplam İşletme", len(df))
        m2.metric("Telefonu Olan", int((df["Telefon"] != "").sum()))
        m3.metric("Websitesi Olan", int((df["Website"] != "").sum()))

        st.dataframe(
            df,
            use_container_width=True,
            column_config={
                "Harita Linki": st.column_config.LinkColumn("Harita Linki"),
                "Website": st.column_config.LinkColumn("Website"),
            },
            hide_index=True,
        )

        c1, c2 = st.columns(2)
        with c1:
            st.download_button(
                "⬇️ Excel olarak indir (.xlsx)",
                data=to_excel_bytes(df),
                file_name="isletmeler.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
            )
        with c2:
            st.download_button(
                "⬇️ CSV olarak indir (.csv)",
                data=df.to_csv(index=False).encode("utf-8-sig"),
                file_name="isletmeler.csv",
                mime="text/csv",
                use_container_width=True,
            )


# ---------------------------------------------------------------------------
# GİRİŞ NOKTASI
# ---------------------------------------------------------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    show_login()
else:
    show_main_app()
