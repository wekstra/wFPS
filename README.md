# wFPS - Üstün FPS Optimizasyon Aracı

![wFPS](https://img.shields.io/badge/wFPS-FPS%20Booster-blue?style=for-the-badge)
![Durum](https://img.shields.io/badge/Status-Active-success?style=for-the-badge)

## Genel Bakış

**wFPS**, oyun performansını artırmak için modern bir web panosunu güçlü bir yerel sistem aracısıyla birleştiren hibrit bir FPS (Saniye Başına Kare) optimizasyon platformudur. Platform, gerçek zamanlı sistem izleme, akıllı süreç yönetimi ve özelleştirilebilir oyun profilleri sunar.

## Mimari

### 🌐 Web Kontrol Paneli (React + FastAPI + MongoDB)
- **Ön Uç**: Tailwind CSS ve Shadcn UI bileşenleriyle React 19
- **Arka Uç**: Eşzamansız MongoDB ile FastAPI
- **Veritabanı**: Kullanıcı verileri, profiller ve telemetri için MongoDB

### 💻 Yerel Aracı (Python)
- Sistem düzeyinde erişimle kullanıcının bilgisayarında çalışır
- REST API aracılığıyla arka uçla iletişim kurar
- Gerçek sistem optimizasyonlarını gerçekleştirir

## Temel Özellikler

### ⚡ Gerçek Zamanlı Sistem İzleme
- CPU kullanım takibi
- RAM kullanımı ve kullanılabilirliği
- Sistem sıcaklığı izleme (Windows)
- Aktif oyun algılama

### 🎮 Oyun İşlem Öncelik Yönetimi
İşlem öncelik seviyelerini ayarlayın:
- Düşük
- Normalin Altında
- Normal
- Normalin Üstünde
- Yüksek
- Gerçek Zamanlı

### 🧹 RAM/Bellek Optimizasyonu
- Bekleme belleğini temizleyin
- Oyun için kaynakları serbest bırakın
- Otomatik bellek yönetimi

### 🚫 Arka Plan İşlem Yönetimi
- Kaynak yoğun uygulamaları otomatik olarak sonlandırın
- Temel uygulamalar için beyaz liste desteği
- Korunan sistem işlemlerine asla dokunulmaz

### 📊 Özel Oyun Profilleri
- Oyun başına optimizasyon ayarlarını kaydedin
- Hızlı profil değiştirme
- Kalıcı profil depolama

### 🔄 Tek Tıkla Hızlandırma Modu
Tek tıklamayla anında optimizasyon

## Hızlı Başlangıç

### 1. Web Panosuna Erişim
wFPS web panosu zaten çalışıyor ve dağıtım URL'nizden erişilebilir.

### 2. Kaydolun / Giriş Yapın
Panoya erişmek için bir hesap oluşturun veya giriş yapın.

### 3. Yerel Aracıyı İndirin ve Çalıştırın
```bash
cd agent
pip install psutil requests
python wfps_agent.py
```

İstendiğinde panodan kimlik doğrulama belirtecinizi girin.

### 4. Optimizasyona Başlayın!
- Sisteminizi gerçek zamanlı olarak izleyin
- Anında performans artışı için Hızlı Güçlendirme'yi kullanın
- Favori oyunlarınız için özel profiller oluşturun

## Kurulum (Geliştirme)

### Arka Uç Kurulumu
```bash
cd backend
pip install -r requirements.txt
uvicorn server:app --reload --port 8001
```

### Ön Uç Kurulumu
```bash
cd frontend
yarn install
yarn start
```

### Yerel Aracı Kurulumu
Ayrıntılı talimatlar için [Agent README](./agent/README.md) dosyasına bakın.

## Kullanım Kılavuzu

### Oyun Profili Oluşturma

1. Kontrol panelinde "Profil Oluştur"a tıklayın.
2. Profil ayrıntılarını girin:
- **Ad**: ör. "CS:GO Optimizasyonu"
- **İşlem Adları**: ör. csgo.exe (isteğe bağlı)
- **Öncelik Düzeyi**: Yüksek veya Gerçek Zamanlı
- **Belleği Temizle**: En iyi performans için etkinleştirin
- **Arka Plan Uygulamalarını Sonlandır**: Kaynakları serbest bırakmak için etkinleştirin
- **Beyaz Liste**: Çalışmaya devam etmek istediğiniz uygulamaları ekleyin (ör. discord.exe)
3. "Profil Oluştur"a tıklayın.

### Profil Uygulama

1. Bilgisayarınızda yerel aracının çalıştığından emin olun.
2. Kaydedilmiş herhangi bir profilde "Profili Uygula"ya tıklayın.
3. Aracı, optimizasyonları gerçekleştirecektir.
4. Sonuçları kontrol panelinde gerçek zamanlı olarak izleyin.

### Hızlı Güçlendirme

Profil olmadan anında optimizasyon için:
1. Yerel aracının çalıştığından emin olun.
2. Kontrol panelinde "Boost'u Başlat"
3. Genel optimizasyonlar hemen uygulanacaktır
4. Geri almak için "Boost'u Durdur"a tıklayın

## API Belgeleri

### Kimlik Doğrulama Uç Noktaları
- `POST /api/auth/register` - Yeni kullanıcı kaydet
- `POST /api/auth/login` - Kullanıcı girişi yap

### Profil Yönetimi
- `GET /api/profiles` - Tüm profilleri listele
- `POST /api/profiles` - Profil oluştur
- `GET /api/profiles/{id}` - Belirli bir profili al
- `PUT /api/profiles/{id}` - Profili güncelle
- `DELETE /api/profiles/{id}` - Profili sil

### Telemetri
- `POST /api/telemetry` - Sistem metriklerini gönder
- `GET /api/telemetry/latest` - En son verileri al telemetri
- `GET /api/telemetry/history` - Telemetri geçmişini al

### Boost Komutları
- `POST /api/boost/command` - Boost komutu oluştur
- `GET /api/boost/commands/pending` - Bekleyen komutları al
- `PUT /api/boost/command/{id}/status` - Komut durumunu güncelle

## Teknoloji Yığını

### Ön Uç
- Modern kancalarla React 19
- Stil için Tailwind CSS
- Shadcn kullanıcı arayüzü bileşenleri
- Lucide React simgeleri
- API çağrıları için Axios
- Bildirimler için Sonner

### Arka Uç
- Eşzamansız destekli FastAPI
- Motor (eşzamansız MongoDB sürücüsü)
- ​​JWT kimlik doğrulaması
- BCrypt parola karma işlemi
- Pydantic doğrulaması

### Yerel Aracı
- Sistem izleme için PSUtil
- API iletişimi istekleri
- Platformlar arası destek

## Proje Yapısı

```
wfps/
├── backend/
│ ├── server.py # Tüm rotaları içeren FastAPI uygulaması
│ ├── requirements.txt # Python bağımlılıkları
│ └── .env # Arka uç ortam yapılandırması
├── frontend/
│ ├── src/
│ │ ├── App.js # Rotalı ana uygulama
│ │ ├── App.css # Genel stiller
│ │ ├── pages/
│ │ │ ├── Auth.jsx # Giriş Yap/Kayıt Ol
