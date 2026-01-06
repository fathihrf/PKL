# 📸 Sistem Image Processing Monitor HTC-2

Sistem otomatis untuk membaca nilai **suhu** dan **kelembapan** dari foto monitor HTC-2 menggunakan **OpenCV** dan **Tesseract OCR**.

---

## ✨ Fitur

- ✅ **Preprocessing Otomatis** - Enhance kualitas gambar untuk OCR optimal
- ✅ **ROI Detection** - Deteksi area tampilan digital otomatis atau manual
- ✅ **OCR Ekstraksi** - Baca nilai suhu dan kelembapan dengan Tesseract
- ✅ **Validasi Hasil** - Verifikasi range nilai yang masuk akal
- ✅ **Batch Processing** - Proses multiple gambar sekaligus
- ✅ **Debug Output** - Simpan gambar intermediate untuk troubleshooting
- ✅ **Export CSV** - Hasil pembacaan tersimpan dalam format CSV

---

## 🚀 Quick Start

### 1. Install Dependencies

```bash
# Install Tesseract OCR
brew install tesseract  # macOS
# atau download dari https://github.com/UB-Mannheim/tesseract/wiki (Windows)

# Install Python packages
pip install -r requirements.txt
```

### 2. Setup ROI (Pertama Kali)

```python
# Edit main.py
setup_mode = True
image_path = "foto_monitor.jpg"

# Jalankan
python main.py

# Pilih area suhu dan kelembapan di window yang muncul
# Koordinat tersimpan di roi_config.txt
```

### 3. Proses Gambar

```python
# Edit main.py
setup_mode = False
image_path = "foto_monitor.jpg"

# Jalankan
python main.py
```

**Output:**
```
======================================================================
HASIL PEMBACAAN
======================================================================
Suhu        : 25.3°C
Kelembapan  : 65.2%
Status      : VALID ✓
======================================================================
```

---

## 📁 Struktur File

```
Image Proccess PKL/
├── main.py                    # Script utama
├── requirements.txt           # Python dependencies
├── README.md                  # File ini
├── CARA_PENGGUNAAN.md        # Panduan lengkap penggunaan
├── PERSIAPAN_DATASET.md      # Panduan persiapan dataset
│
├── roi_config.txt            # Koordinat ROI (auto-generated)
│
├── dataset/                  # (optional) Dataset untuk testing
│   ├── training/
│   ├── validation/
│   └── labels/
│
└── debug_output/             # (auto-generated) Debug images
    ├── original_*.jpg
    ├── processed_*.jpg
    ├── temp_roi_*.jpg
    └── humidity_roi_*.jpg
```

---

## 📖 Dokumentasi Lengkap

- **[CARA_PENGGUNAAN.md](CARA_PENGGUNAAN.md)** - Panduan penggunaan lengkap
  - Instalasi step-by-step
  - Setup ROI
  - Penggunaan dasar & lanjutan
  - Troubleshooting

- **[PERSIAPAN_DATASET.md](PERSIAPAN_DATASET.md)** - Panduan dataset
  - Cara mengambil foto yang baik
  - Struktur folder dataset
  - Membuat ground truth labels
  - Testing & evaluasi akurasi

---

## 🛠️ Requirements

- **Python** 3.7+
- **Tesseract OCR** 4.0+
- **OpenCV** 4.8+
- **Pytesseract** 0.3.10+
- **NumPy** 1.24+
- **Pillow** 10.0+

---

## 💡 Tips Pengambilan Foto

✓ **BAIK:**
- Pencahayaan merata
- Fokus tajam pada display
- Sudut tegak lurus (90°)
- Jarak 20-30 cm
- Tidak ada glare/pantulan

✗ **HINDARI:**
- Flash langsung
- Foto blur/out of focus
- Sudut terlalu miring
- Pencahayaan gelap
- Refleksi dari jendela

---

## 🔧 Troubleshooting Cepat

### OCR tidak akurat?
1. Aktifkan `save_debug=True`
2. Periksa gambar di folder `debug_output/`
3. Re-setup ROI jika perlu
4. Improve kualitas foto

### Tesseract not found?
```bash
# macOS
brew install tesseract

# Windows - edit main.py:
monitor = HTC2Monitor(tesseract_path=r'C:\Program Files\Tesseract-OCR\tesseract.exe')
```

### Nilai tidak valid?
- Periksa warning messages
- Verifikasi foto secara manual
- Check range suhu: -40°C to 80°C
- Check range kelembapan: 0-100%

---

## 📊 Contoh Penggunaan

### Single Image
```python
from main import HTC2Monitor, load_roi_coordinates

monitor = HTC2Monitor()
roi = load_roi_coordinates()
result = monitor.process_image("foto.jpg", roi_coords=roi)

print(f"Suhu: {result['temperature']}°C")
print(f"Kelembapan: {result['humidity']}%")
```

### Batch Processing
```python
from main import batch_process_images

results = batch_process_images("dataset/training")
# Hasil tersimpan di CSV
```

---

## 📝 License

Free to use for educational and research purposes.

---

## 👨‍💻 Author

**GitHub Copilot**  
Created: January 6, 2026

---

## 🙏 Acknowledgments

- OpenCV - Computer Vision Library
- Tesseract OCR - Google's OCR Engine
- Python Community

---

**Selamat Menggunakan! 🎉**

Untuk panduan lengkap, lihat [CARA_PENGGUNAAN.md](CARA_PENGGUNAAN.md)
