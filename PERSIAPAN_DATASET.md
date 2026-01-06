# PANDUAN PERSIAPAN DATASET UNTUK TRAINING

## 📋 Overview
Panduan ini menjelaskan cara mempersiapkan dataset foto monitor HTC-2 untuk meningkatkan akurasi sistem image processing dan OCR.

---

## 🎯 Tujuan Dataset

Dataset yang baik akan membantu:
1. **Kalibrasi ROI** - Menentukan posisi optimal area pembacaan
2. **Testing & Validasi** - Memastikan sistem bekerja dengan baik
3. **Fine-tuning** - Mengoptimalkan parameter preprocessing
4. **Training Custom OCR** (opsional) - Jika Tesseract standar kurang akurat

---

## 📸 1. PENGAMBILAN FOTO

### A. Peralatan yang Dibutuhkan
- **Kamera/Smartphone** dengan resolusi minimal 5MP
- **Tripod/Stand** untuk stabilitas (sangat direkomendasikan)
- **Pencahayaan** yang konsisten dan cukup

### B. Spesifikasi Foto yang Ideal

```
✓ Resolusi      : Minimal 1920x1080 px (Full HD)
✓ Format        : JPG atau PNG
✓ Fokus         : Tajam pada angka display
✓ Angle         : Tegak lurus terhadap monitor (90°)
✓ Jarak         : 20-30 cm dari display
✓ Pencahayaan   : Merata, tidak ada glare/pantulan
✓ Orientasi     : Landscape atau portrait (konsisten)
```

### C. Kondisi Pengambilan Foto

**BAIK ✓**
- Cahaya merata dari atas/samping
- Display terlihat jelas tanpa bayangan
- Angka kontras dengan background
- Tidak ada refleksi dari flash/jendela
- Focus tajam pada display digital

**HINDARI ✗**
- Flash langsung ke display (glare)
- Pencahayaan terlalu gelap/terang
- Sudut miring >15°
- Display blur/out of focus
- Bayangan menutupi angka

---

## 📁 2. STRUKTUR FOLDER DATASET

### Organisasi yang Disarankan:

```
Image Proccess PKL/
├── dataset/
│   ├── training/              # Data untuk testing dan kalibrasi
│   │   ├── IMG_001.jpg       # Foto dengan kondisi ideal
│   │   ├── IMG_002.jpg       # Foto dengan pencahayaan berbeda
│   │   ├── IMG_003.jpg       # Foto dengan jarak berbeda
│   │   └── ...
│   │
│   ├── validation/            # Data untuk validasi akhir
│   │   ├── VAL_001.jpg
│   │   └── ...
│   │
│   └── labels/                # Ground truth (nilai sebenarnya)
│       └── labels.csv         # File CSV dengan nilai aktual
│
├── output/                    # Hasil processing
│   ├── debug_output/          # Gambar debug
│   └── results/               # File hasil CSV
│
├── main.py                    # Script utama
└── roi_config.txt             # Konfigurasi ROI
```

---

## 📊 3. PEMBUATAN LABELS (Ground Truth)

### File: dataset/labels/labels.csv

Buat file CSV yang berisi nilai aktual dari setiap foto:

```csv
filename,temperature,humidity,notes
IMG_001.jpg,25.3,65.2,Kondisi normal
IMG_002.jpg,26.8,68.5,Pencahayaan rendah
IMG_003.jpg,24.5,70.1,Sudut sedikit miring
IMG_004.jpg,27.2,62.3,Jarak dekat
IMG_005.jpg,25.9,66.8,Kondisi ideal
```

**Kolom:**
- `filename`: Nama file foto
- `temperature`: Nilai suhu aktual (baca manual dari display)
- `humidity`: Nilai kelembapan aktual
- `notes`: Catatan kondisi foto (opsional)

---

## 🔢 4. JUMLAH DATASET YANG DIREKOMENDASIKAN

### Minimum untuk Testing Dasar:
- **20-30 foto** dengan berbagai kondisi

### Ideal untuk Sistem Robust:
- **100-200 foto** mencakup:
  - 40% kondisi ideal
  - 30% variasi pencahayaan
  - 20% variasi jarak/angle
  - 10% edge cases (kondisi ekstrem)

### Variasi yang Harus Dicakup:

1. **Rentang Nilai**
   - Suhu: 15°C - 35°C (atau sesuai range penggunaan)
   - Kelembapan: 40% - 90%

2. **Kondisi Pencahayaan**
   - Terang (siang hari)
   - Normal (lampu ruangan)
   - Redup (pencahayaan minimal)

3. **Posisi Kamera**
   - Frontal (ideal)
   - Sedikit miring kiri/kanan (±10°)
   - Sedikit dari atas/bawah (±10°)

4. **Jarak Pengambilan**
   - Dekat (15-20 cm)
   - Normal (20-30 cm)
   - Jauh (30-40 cm)

---

## 🛠️ 5. KALIBRASI ROI (Region of Interest)

### Langkah-langkah Setup ROI:

1. **Siapkan 1 Foto Referensi Terbaik**
   - Kualitas ideal
   - Display terlihat jelas
   - Pencahayaan merata

2. **Jalankan Mode Setup**
   ```python
   # Di main.py, ubah:
   setup_mode = True
   image_path = "dataset/training/IMG_001.jpg"
   ```

3. **Pilih Area ROI**
   - Jalankan script: `python main.py`
   - Window akan muncul untuk memilih area SUHU
   - Klik dan drag untuk membuat kotak seleksi
   - Tekan ENTER setelah selesai
   - Ulangi untuk area KELEMBAPAN

4. **Koordinat Tersimpan**
   - File `roi_config.txt` akan dibuat otomatis
   - Koordinat ini akan digunakan untuk semua foto berikutnya

### Tips Memilih ROI:
- ✓ Pilih area yang **hanya berisi angka**
- ✓ Beri sedikit margin di sekeliling angka
- ✓ Hindari menyertakan simbol °C atau %
- ✓ Pastikan tidak ada background yang mengganggu

---

## 🧪 6. TESTING DATASET

### A. Test Single Image

```python
from main import HTC2Monitor

monitor = HTC2Monitor()

# Test 1 gambar
result = monitor.process_image(
    "dataset/training/IMG_001.jpg",
    roi_coords=None,  # atau load dari file
    save_debug=True
)

print(f"Suhu: {result['temperature']}°C")
print(f"Kelembapan: {result['humidity']}%")
print(f"Valid: {result['valid']}")
```

### B. Test Batch (Multiple Images)

```python
from main import batch_process_images, load_roi_coordinates

# Load ROI yang sudah di-setup
roi_coords = load_roi_coordinates()

# Proses semua gambar di folder
results = batch_process_images(
    "dataset/training",
    roi_coords=roi_coords
)

# Hasil tersimpan di CSV
```

### C. Evaluasi Akurasi

```python
import pandas as pd

# Load hasil dan ground truth
results_df = pd.read_csv("results_20260106_120000.csv")
labels_df = pd.read_csv("dataset/labels/labels.csv")

# Merge data
merged = results_df.merge(labels_df, on='filename')

# Hitung akurasi
temp_accuracy = (merged['temperature_x'] == merged['temperature_y']).mean()
humidity_accuracy = (merged['humidity_x'] == merged['humidity_y']).mean()

print(f"Akurasi Suhu: {temp_accuracy * 100:.2f}%")
print(f"Akurasi Kelembapan: {humidity_accuracy * 100:.2f}%")
```

---

## 📝 7. TIPS MENGUMPULKAN DATASET

### Do's ✓
1. **Konsistensi** - Gunakan posisi kamera yang sama
2. **Label Langsung** - Catat nilai aktual segera setelah foto
3. **Dokumentasi** - Catat kondisi pengambilan foto
4. **Backup** - Simpan salinan dataset di tempat terpisah
5. **Verifikasi** - Cek setiap foto untuk memastikan kualitas

### Don'ts ✗
1. **Jangan** gunakan foto blur atau out of focus
2. **Jangan** mengubah resolusi foto setelah diambil
3. **Jangan** crop foto secara manual
4. **Jangan** edit foto (brightness, contrast, dll)
5. **Jangan** gunakan screenshot - gunakan foto langsung

---

## 🎓 8. ADVANCED: CUSTOM OCR TRAINING (OPSIONAL)

Jika Tesseract OCR standar kurang akurat, Anda bisa training custom:

### Tools yang Dibutuhkan:
- **Tesseract Training Tools**
- **jTessBoxEditor** untuk labeling
- **Dataset minimal 100 gambar** karakter individual

### Langkah Singkat:
1. Extract karakter individual dari display
2. Label setiap karakter menggunakan Box files
3. Generate training data (.traineddata)
4. Replace Tesseract default model

**Note**: Ini advanced dan biasanya tidak diperlukan untuk digit recognition.

---

## ✅ CHECKLIST PERSIAPAN

Sebelum mulai production:

- [ ] Minimal 20 foto training terkumpul
- [ ] Semua foto memiliki kualitas baik (focus, lighting, angle)
- [ ] File labels.csv sudah dibuat dengan ground truth
- [ ] ROI sudah dikalibrasi dan tersimpan di roi_config.txt
- [ ] Testing menunjukkan akurasi >90% pada dataset training
- [ ] Script dapat memproses batch images tanpa error
- [ ] Debug output berfungsi untuk troubleshooting
- [ ] Dokumentasi kondisi pengambilan foto lengkap

---

## 🚀 NEXT STEPS

Setelah dataset siap:
1. Run batch testing untuk evaluasi
2. Fine-tune parameters jika akurasi kurang
3. Deploy untuk penggunaan real-time
4. Monitor dan update dataset secara berkala
5. Dokumentasikan edge cases yang ditemukan

---

## 📞 TROUBLESHOOTING

### Problem: Akurasi OCR Rendah (<80%)
**Solusi:**
- Periksa kualitas foto (focus, lighting)
- Re-kalibrasi ROI
- Adjust preprocessing parameters
- Tambah dataset dengan variasi lebih banyak

### Problem: ROI Tidak Konsisten
**Solusi:**
- Gunakan tripod untuk posisi kamera tetap
- Setup ROI dengan foto yang lebih representative
- Pertimbangkan auto-detection algorithm

### Problem: Gagal Detect Angka
**Solusi:**
- Periksa contrast gambar
- Adjust threshold di preprocessing
- Pastikan ROI hanya berisi angka
- Coba OCR config berbeda (--psm 6, 7, 8)

---

**Dibuat oleh:** GitHub Copilot  
**Tanggal:** January 6, 2026  
**Versi:** 1.0
