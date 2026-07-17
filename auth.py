import json
import hashlib
import os
from datetime import datetime

USERS_FILE = "users.json"
LOG_FILE = "arama_gecmisi.csv"
PAYMENTS_FILE = "odemeler.csv"
PAYMENT_REQUESTS_FILE = "odeme_talepleri.csv"

BASLANGIC_KREDISI = 20
ARAMA_MALIYETI = 1

# Kredi satışı için iletişim numarası (WhatsApp / arama)
ODEME_TELEFON = "05461156134"


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def load_users() -> dict:
    if not os.path.exists(USERS_FILE):
        default_users = {
            "admin": {"password": hash_password("admin123"), "role": "admin", "credits": BASLANGIC_KREDISI},
            "kullanici": {"password": hash_password("kullanici123"), "role": "user", "credits": BASLANGIC_KREDISI},
        }
        save_users(default_users)
        return default_users

    with open(USERS_FILE, "r", encoding="utf-8") as f:
        users = json.load(f)

    # Geriye dönük uyumluluk: eski kayıtlarda "credits" alanı yoksa ekle
    changed = False
    for uname, info in users.items():
        if "credits" not in info:
            info["credits"] = BASLANGIC_KREDISI
            changed = True
    if changed:
        save_users(users)

    return users


def save_users(users: dict):
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False, indent=2)


def verify_login(username: str, password: str):
    users = load_users()
    user = users.get(username)
    if user and user["password"] == hash_password(password):
        return user["role"]
    return None


def add_user(username: str, password: str, role: str = "user") -> bool:
    users = load_users()
    if username in users:
        return False
    users[username] = {
        "password": hash_password(password),
        "role": role,
        "credits": BASLANGIC_KREDISI,
    }
    save_users(users)
    return True


def delete_user(username: str) -> bool:
    users = load_users()
    if username not in users or username == "admin":
        return False
    del users[username]
    save_users(users)
    return True


def get_credits(username: str) -> int:
    users = load_users()
    user = users.get(username)
    if not user:
        return 0
    return int(user.get("credits", 0))


def has_enough_credits(username: str, amount: int = ARAMA_MALIYETI) -> bool:
    return get_credits(username) >= amount


def deduct_credits(username: str, amount: int = ARAMA_MALIYETI) -> bool:
    """Kullanıcının kredisini düşürür. Yetersizse False döner ve hiçbir şey değiştirmez."""
    users = load_users()
    user = users.get(username)
    if not user or int(user.get("credits", 0)) < amount:
        return False
    user["credits"] = int(user.get("credits", 0)) - amount
    save_users(users)
    return True


def add_credits(username: str, amount: int) -> bool:
    """Kullanıcının kredisini artırır (admin paneli veya ödeme sonrası)."""
    users = load_users()
    user = users.get(username)
    if not user:
        return False
    user["credits"] = int(user.get("credits", 0)) + int(amount)
    save_users(users)
    return True


def set_credits(username: str, amount: int) -> bool:
    """Kullanıcının kredisini doğrudan belirli bir değere ayarlar (admin paneli)."""
    users = load_users()
    user = users.get(username)
    if not user:
        return False
    user["credits"] = max(0, int(amount))
    save_users(users)
    return True


def log_search(username: str, query_desc: str, result_count: int):
    is_new = not os.path.exists(LOG_FILE)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        if is_new:
            f.write("Zaman,Kullanıcı,Arama,Sonuç Sayısı\n")
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        safe_query = query_desc.replace(",", ";")
        f.write(f"{timestamp},{username},{safe_query},{result_count}\n")


def read_log():
    if not os.path.exists(LOG_FILE):
        return []
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        lines = f.read().splitlines()
    return lines


def log_payment(username: str, package_name: str, amount_try: float, credits_added: int):
    is_new = not os.path.exists(PAYMENTS_FILE)
    with open(PAYMENTS_FILE, "a", encoding="utf-8") as f:
        if is_new:
            f.write("Zaman,Kullanıcı,Paket,Tutar (TL),Eklenen Kredi\n")
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"{timestamp},{username},{package_name},{amount_try:.2f},{credits_added}\n")


def read_payments():
    if not os.path.exists(PAYMENTS_FILE):
        return []
    with open(PAYMENTS_FILE, "r", encoding="utf-8") as f:
        lines = f.read().splitlines()
    return lines


# ---------------------------------------------------------------------------
# ÖDEME TALEPLERİ (WhatsApp / telefon üzerinden bildirilen, onay bekleyen
# kredi satın alma talepleri). Kullanıcı "Talep Gönder" dediğinde buraya
# düşer; admin ödemeyi elden/havale/WhatsApp üzerinden aldığını
# doğruladıktan sonra panelden onaylayınca krediler hesaba geçer.
# ---------------------------------------------------------------------------
def _read_payment_request_rows():
    if not os.path.exists(PAYMENT_REQUESTS_FILE):
        return []
    with open(PAYMENT_REQUESTS_FILE, "r", encoding="utf-8") as f:
        lines = f.read().splitlines()
    if len(lines) <= 1:
        return []
    rows = []
    for line in lines[1:]:
        parts = line.split(",")
        if len(parts) < 6:
            continue
        rows.append({
            "id": parts[0],
            "zaman": parts[1],
            "kullanici": parts[2],
            "paket": parts[3],
            "tutar": parts[4],
            "kredi": parts[5],
        })
    return rows


def _write_payment_request_rows(rows: list):
    with open(PAYMENT_REQUESTS_FILE, "w", encoding="utf-8") as f:
        f.write("ID,Zaman,Kullanıcı,Paket,Tutar (TL),Talep Edilen Kredi\n")
        for r in rows:
            f.write(f"{r['id']},{r['zaman']},{r['kullanici']},{r['paket']},{r['tutar']},{r['kredi']}\n")


def log_payment_request(username: str, package_name: str, amount_try: float, credits_requested: int) -> str:
    """Yeni bir ödeme talebi kaydeder (onay bekliyor). Talebin id'sini döner."""
    rows = _read_payment_request_rows()
    req_id = datetime.now().strftime("%Y%m%d%H%M%S%f")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    rows.append({
        "id": req_id,
        "zaman": timestamp,
        "kullanici": username,
        "paket": package_name,
        "tutar": f"{amount_try:.2f}",
        "kredi": str(credits_requested),
    })
    _write_payment_request_rows(rows)
    return req_id


def read_payment_requests() -> list:
    """Onay bekleyen tüm talepleri döner (liste of dict)."""
    return _read_payment_request_rows()


def approve_payment_request(req_id: str) -> bool:
    """Talebi onaylar: kullanıcıya kredi ekler, onaylı ödeme geçmişine yazar,
    talebi bekleyenler listesinden kaldırır."""
    rows = _read_payment_request_rows()
    target = next((r for r in rows if r["id"] == req_id), None)
    if target is None:
        return False

    added = add_credits(target["kullanici"], int(target["kredi"]))
    if not added:
        return False

    log_payment(target["kullanici"], target["paket"], float(target["tutar"]), int(target["kredi"]))

    remaining = [r for r in rows if r["id"] != req_id]
    _write_payment_request_rows(remaining)
    return True


def reject_payment_request(req_id: str) -> bool:
    """Talebi (ödeme alınmadıysa/iptal edildiyse) listeden siler, kredi eklemez."""
    rows = _read_payment_request_rows()
    remaining = [r for r in rows if r["id"] != req_id]
    if len(remaining) == len(rows):
        return False
    _write_payment_request_rows(remaining)
    return True
