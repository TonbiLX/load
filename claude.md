# Container Load Visualizer - Proje Notları

## Proje Özeti
PyQt5 + matplotlib tabanlı konteyner yükleme görselleştirme aracı. 2D ve 3D olmak üzere iki ayrı implementasyon var (`Load_2D/` ve `Load_3D/`). Kullanıcı ürün boyutlarını girer, uygulama konteynere yerleştirip 3D olarak gösterir.

## Mimari
- **Load_2D/**: 2D zemin planı algoritması, 3D görselleştirme `Poly3DCollection` ile
- **Load_3D/**: Gerçek 3D yerleştirme, corner-point algoritması, `bar3d` ile görselleştirme
- Her iki modül: `main.py` (giriş noktası), `data_processing.py` (iş mantığı + QThread), `visualization.py` (matplotlib canvas), `utils.py` (yardımcı fonksiyonlar)

## Kritik Mimari Kararlar

### Thread Güvenliği
- `LoadThread.run()` içinden **asla** GUI widget'larına erişilmemeli
- Load_2D: Tablo verileri `start_loading()`'da toplanıp thread'e parametre olarak geçiriliyor. `result_plot()` ana thread'de `finished` sinyali ile çağrılıyor (güvenli)
- Load_3D: Tüm sonuçlar `result_ready = pyqtSignal(object)` ile dict olarak ana thread'e gönderiliyor. `display_results()` slotu GUI güncellemelerini yapıyor

### 3D Yerleştirme Algoritması
- Eski: `np.zeros((length, width, height), dtype=bool)` — 40' konteyner için ~67 MB, O(n³) tarama
- Yeni: Corner-point algoritması — yerleştirilen kutuların köşe noktaları takip ediliyor, AABB çarpışma kontrolü. Çok daha hızlı ve bellek dostu

### Renk Atama
- Renkler `df['Ürün Adı'].unique()` üzerinden döngü öncesinde atanmalı
- `plt.get_cmap('tab10')(idx % 10)` ile tutarlı renk

## Bilinen Sınırlamalar
- Load_2D algoritması yüksekliği yok sayar (sadece zemin planı), ürünler üst üste istiflenemez
- Konteyner türleri sabit kodlanmış (20', 40', Kamyon)
- Maksimum 10 farklı ürün rengi (tab10 colormap)

## Dosya Yapısı
```
Load_2D/
  main.py              — ContainerLoadingApp (QMainWindow), giriş noktası
  data_processing.py   — LoadThread (QThread), 2D bin packing
  visualization.py     — create_canvas(), draw_prism()
  utils.py             — paste_data(), clear_layout()

Load_3D/
  main.py              — Sadece import + QApplication başlatma
  data_processing.py   — ContainerLoadingApp + LoadThread (her ikisi bu dosyada)
  visualization.py     — create_canvas()
  utils.py             — paste_data(), clear_layout()
```

## Önceden Düzeltilen Hatalar (referans)
1. **Thread safety ihlalleri** — Load_3D'de worker thread'den GUI erişimi kaldırıldı
2. **Devasa bellek tüketimi** — 3D boolean array yerine corner-point algoritması
3. **Yanlış total_items** — `len(df) * sum` yerine sadece `sum`
4. **Güvensiz astype** — `pd.to_numeric(errors='coerce')` kullanıldı
5. **Renk atama hatası** — Renkler ürün bazında önceden atanıyor
6. **Ağırlık limiti kontrolü** — Her iki versiyona eklendi
7. **Eşzamanlı thread koruması** — `isRunning()` kontrolü + buton devre dışı
8. **Progress bar sıfırlanmıyor** — Her yüklemede reset
9. **Nested layout bellek sızıntısı** — Rekürsif `clear_layout`
10. **Göreceli resim yolları** — `__file__` tabanlı mutlak yol
11. **paste_data seçim pozisyonu** — `selectedIndexes()` ile başlangıç
12. **Kullanılmayan bağımlılıklar** — openpyxl, requests kaldırıldı
13. **Kullanılmayan importlar** — pandas (utils), plt (3D visualization)
14. **README dizin adı** — `load_2D` → `Load_2D`
15. **.gitignore** — Oluşturuldu

## Geliştirme Notları
- Python 3.11+, Poetry ile bağımlılık yönetimi
- `poetry run python Load_2D/main.py` veya `poetry run python Load_3D/main.py` ile çalıştırılır
- Tablo verisi Ctrl+V ile Excel/spreadsheet'ten yapıştırılabilir
