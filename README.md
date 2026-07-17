# İşletme Bulucu (Giriş Panelli)

## Kurulum

```bash
python -m pip install -r requirements.txt
```

## Çalıştırma

```bash
python -m streamlit run app.py
```

## Varsayılan Giriş Bilgileri

İlk çalıştırmada otomatik olarak `users.json` dosyası oluşturulur ve şu hesaplar tanımlanır:

| Kullanıcı Adı | Şifre         | Rol   |
|---------------|---------------|-------|
| admin         | admin123      | admin |
| kullanici     | kullanici123  | user  |

**Önemli: İlk girişten sonra bu şifreleri değiştir** (admin panelinden yeni kullanıcı
ekleyip eskilerini silerek, veya `users.json` dosyasını elle düzenleyerek).

## Kredi Sistemi

- Her yeni kullanıcı (ilk çalıştırmadaki varsayılanlar dahil) **20 kredi** ile başlar.
- **1 arama = 1 kredi**. Kredisi 0 olan kullanıcı arama yapamaz, önce kredi satın alması gerekir.
- Kullanıcılar ana sayfadaki **"💳 Kredi Satın Al"** bölümünden bir paket seçer, ardından
  **WhatsApp** veya **telefon** (`auth.py` içindeki `ODEME_TELEFON`) üzerinden satıcıyla iletişime
  geçip ödemesini yapar.
  - Ödemeyi yaptıktan sonra **"Ödemeyi Yaptım, Talebi Gönder"** butonuna basarak talebini kayda
    geçirir — bu talep "onay bekliyor" durumunda `odeme_talepleri.csv` dosyasına yazılır.
  - Admin, ödemenin gerçekten alındığını doğruladıktan sonra **Yönetici Paneli → Ödeme Talepleri**
    sekmesinden talebi **Onayla**r; krediler otomatik olarak kullanıcının hesabına eklenir ve
    onaylı ödeme `odemeler.csv`'ye kaydedilir. Talep hatalıysa/ödeme alınmadıysa **Reddet**
    ile silinebilir.
  - Bu akış gerçek bir ödeme altyapısı (iyzico, Stripe, PayTR vb.) gerektirmez; küçük ölçekli,
    "WhatsApp'tan onaylaşarak satış" modeline uygundur. İleride otomatik ödeme almak istersen
    bu sağlayıcılardan birinin API anahtarlarını entegre edebilirsin.

## Admin Paneli

`admin` rolüyle giriş yaptığında ana sayfada "🛠️ Yönetici Paneli" bölümü açılır:

- **Kullanıcılar** sekmesi: yeni kullanıcı ekleme, mevcut kullanıcıları silme, her kullanıcının
  kredisini ➕/➖ butonlarıyla hızlıca değiştirme veya tam bir değere ayarlama
- **Arama Geçmişi** sekmesi: kimin ne zaman ne aradığının kaydı
- **Ödeme Geçmişi** sekmesi: onaylanmış ödemelerin kaydı
- **Ödeme Talepleri** sekmesi: WhatsApp/telefonla bildirilen, onay bekleyen kredi taleplerini
  görüp tek tıkla **Onayla**yabilir veya **Reddet**ebilirsin

Normal kullanıcılar (`role: user`) bu paneli göremez, sadece arama yapabilir ve kredi satın alabilir.

## Dosyalar

- `app.py` — ana uygulama
- `auth.py` — giriş/kullanıcı/kredi yönetimi mantığı
- `users.json` — kullanıcı listesi (ilk çalıştırmada otomatik oluşur, şifreler hash'lenmiş halde, krediler bu dosyada saklanır)
- `arama_gecmisi.csv` — arama logları (otomatik oluşur)
- `odeme_talepleri.csv` — onay bekleyen ödeme talepleri (otomatik oluşur)
- `odemeler.csv` — admin tarafından onaylanmış ödeme logları (otomatik oluşur)

`users.json` ve `arama_gecmisi.csv` dosyalarını başka bir bilgisayara taşırsan
kullanıcı/geçmiş bilgileri de taşınır — silersen sıfırdan başlar.
