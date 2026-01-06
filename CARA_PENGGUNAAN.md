# 🚀 CARA PENGGUNAAN SISTEM IMAGE PROCESSING HTC-2

## 📋 Daftar Isi
1. [Instalasi](#instalasi)
2. [Setup Awal](#setup-awal)
3. [Penggunaan Dasar](#penggunaan-dasar)
4. [Mode Lanjutan](#mode-lanjutan)
5. [Troubleshooting](#troubleshooting)

---

## 🔧 1. INSTALASI

### A. Install Python
Pastikan Python 3.7+ sudah terinstall:
```bash
python --version
# atau
python3 --version
```

### B. Install Tesseract OCR

**macOS:**
```bash
brew install tesseract
```

**Windows:**
1. Download installer dari: https://github.com/UB-Mannheim/tesseract/wiki
2. Install ke `C:\Program Files\Tesseract-OCR\`
3. Tambahkan ke PATH environment variable

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install tesseract-ocr
```

### C. Install Python Libraries

Buat virtual environment (recommended):
```bash
# Buat virtual environment
python -m venv venv

# Activate (macOS/Linux)
source venv/bin/activate

# Activate (Windows)
venv\Scripts\activate
```

Install dependencies:
```bash
pip install opencv-python
pip install pytesseract
pip install numpy
pip install Pillow
```

Atau gunakan requirements.txt (jika tersedia):
```bash
pip install -r requirements.txt
```

### D. Verifikasi Instalasi

```bash
# Test Tesseract
tesseract --version

# Test Python
python -c "import cv2; import pytesseract; print('OK')"
```

---

## 🎬 2. SETUP AWAL

### A. Siapkan Foto Monitor HTC-2

1. **Ambil Foto** monitor HTC-2 Anda
   - Pastikan display terlihat jelas
   - Pencahayaan merata
   - Fokus tajam
   - Sudut tegak lurus

2. **Simpan Foto** di folder yang sama dengan `main.py`
   - Rename menjadi `sample_htc2.jpg` atau
   - Catat nama file untuk digunakan nanti

### B. Konfigurasi Path Tesseract (Khusus Windows)

Edit file `main.py`:
```python
# Cari baris ini di bagian bawah:
if __name__ == "__main__":
    # Untuk Windows, uncomment dan sesuaikan path:
    monitor = HTC2Monitor(tesseract_path=r'C:\Program Files\Tesseract-OCR\tesseract.exe')
```

Uncomment dan sesuaikan path jika perlu.

### C. Setup ROI (Region of Interest) - **PENTING!**

**Langkah pertama kali menggunakan sistem:**

1. **Edit main.py** - ubah mode setup:
```python
# Cari baris ini:
setup_mode = False  # Ubah ke True

# Ganti path gambar:
image_path = "sample_htc2.jpg"  # Sesuaikan nama file Anda
```

2. **Jalankan Script**:
```bash
python main.py
```

3. **Pilih Area ROI**:
   - Window akan muncul dengan judul "Pilih Area Suhu"
   - **Klik dan drag** untuk membuat kotak di sekeliling angka SUHU
   - Tekan **ENTER** jika sudah selesai
   - Window kedua akan muncul untuk "Pilih Area Kelembapan"
   - **Klik dan drag** untuk membuat kotak di sekeliling angka KELEMBAPAN
   - Tekan **ENTER**

4. **Koordinat ROI Tersimpan**:
   - File `roi_config.txt` akan dibuat otomatis
   - Berisi koordinat untuk digunakan nanti

### Tips Memilih ROI:
```
✓ Pilih HANYA area angka
✓ Beri margin kecil (2-3px) di sekeliling
✓ HINDARI simbol °C atau %
✓ Pastikan kotak pas dengan display angka
```

---

## 💻 3. PENGGUNAAN DASAR

### A. Proses Single Image

Setelah setup ROI selesai:

1. **Edit main.py** - ubah kembali ke mode processing:
```python
setup_mode = False  # Pastikan False untuk processing
image_path = "sample_htc2.jpg"  # Path ke foto yang akan diproses
```

2. **Jalankan Script**:
```bash
python main.py
```

3. **Lihat Hasil**:
```
======================================================================
HASIL PEMBACAAN
======================================================================
Suhu        : 25.3°C
Kelembapan  : 65.2%
Status      : VALID ✓
======================================================================
```

### B. Debug Output

Jika ingin melihat proses detail:

```python
result = monitor.process_image(
    image_path, 
    roi_coords=roi_coords,
    save_debug=True  # Aktifkan debug
)
```

Debug images akan tersimpan di folder `debug_output/`:
- `original_*.jpg` - Gambar asli
- `processed_*.jpg` - Gambar setelah preprocessing
- `temp_roi_*.jpg` - ROI area suhu
- `humidity_roi_*.jpg` - ROI area kelembapan

### C. Proses Tanpa ROI Tersimpan

Jika tidak ada file `roi_config.txt`:

```python
# Sistem akan auto-detect ROI
result = monitor.process_image(
    "sample_htc2.jpg",
    roi_coords=None,  # Auto-detect
    save_debug=True
)
```

**Note**: Auto-detect kurang akurat, setup manual ROI direkomendasikan.

---

## 🔥 4. MODE LANJUTAN

### A. Batch Processing (Multiple Images)

Proses banyak gambar sekaligus:

1. **Siapkan Folder** dengan foto-foto:
```
dataset/
├── IMG_001.jpg
├── IMG_002.jpg
├── IMG_003.jpg
└── ...
```

2. **Jalankan Batch Processing**:
```python
from main import batch_process_images, load_roi_coordinates

# Load ROI
roi_coords = load_roi_coordinates()

# Proses semua gambar
results = batch_process_images(
    "dataset/training",  # Folder gambar
    roi_coords=roi_coords
)
```

3. **Hasil** tersimpan di file CSV:
```
results_20260106_120000.csv
```

Format CSV:
```csv
timestamp,filename,temperature,humidity,valid
2026-01-06 12:00:01,IMG_001.jpg,25.3,65.2,True
2026-01-06 12:00:02,IMG_002.jpg,26.8,68.5,True
```

### B. Custom ROI untuk Tiap Gambar

Jika posisi kamera berbeda-beda:

```python
from main import HTC2Monitor

monitor = HTC2Monitor()

# Define ROI manual untuk gambar tertentu
custom_roi = {
    'temperature': (100, 50, 200, 80),  # (x, y, width, height)
    'humidity': (100, 150, 200, 80)
}

result = monitor.process_image(
    "foto_posisi_beda.jpg",
    roi_coords=custom_roi,
    save_debug=True
)
```

### C. Adjust OCR Configuration

Jika pembacaan kurang akurat, coba config berbeda:

```python
# Edit di main.py - method extract_numbers_ocr()

# Config 1: Single line (default)
config = '--psm 7 digits'

# Config 2: Single word
config = '--psm 8 digits'

# Config 3: Single uniform block
config = '--psm 6 digits'

# Config 4: Tanpa whitelist (baca semua karakter)
config = '--psm 7'
```

### D. Adjust Preprocessing Parameters

Fine-tune preprocessing untuk kondisi foto berbeda:

```python
# Edit di main.py - method preprocess_image()

# CLAHE parameters
clahe = cv2.createCLAHE(
    clipLimit=3.0,      # Tingkatkan untuk kontras lebih tinggi
    tileGridSize=(8,8)
)

# Denoising strength
denoised = cv2.fastNlMeansDenoising(
    enhanced, None, 
    h=15,           # Tingkatkan untuk noise reduction lebih kuat
    templateWindowSize=7, 
    searchWindowSize=21
)

# Adaptive threshold
binary = cv2.adaptiveThreshold(
    denoised, 255, 
    cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
    cv2.THRESH_BINARY, 
    blockSize=15,   # Tingkatkan untuk area yang lebih besar
    C=2
)
```

### E. Real-time Monitoring (Webcam/IP Camera)

Untuk monitoring real-time:

```python
import cv2
from main import HTC2Monitor

monitor = HTC2Monitor()
roi_coords = load_roi_coordinates()

# Buka webcam atau IP camera
cap = cv2.VideoCapture(0)  # 0 untuk webcam default
# atau untuk IP camera:
# cap = cv2.VideoCapture("http://192.168.1.100:8080/video")

while True:
    ret, frame = cap.read()
    if not ret:
        break
    
    # Simpan frame sementara
    cv2.imwrite("temp_frame.jpg", frame)
    
    # Proses frame
    try:
        result = monitor.process_image(
            "temp_frame.jpg",
            roi_coords=roi_coords
        )
        
        # Tampilkan hasil di frame
        if result['temperature'] and result['humidity']:
            text = f"Temp: {result['temperature']}C | Humidity: {result['humidity']}%"
            cv2.putText(frame, text, (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    except:
        pass
    
    # Tampilkan frame
    cv2.imshow('HTC-2 Monitor', frame)
    
    # Tekan 'q' untuk keluar
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
```

---

## 🧪 5. CONTOH PENGGUNAAN KUSTOM

### Script Minimal

```python
from main import HTC2Monitor, load_roi_coordinates

# Initialize
monitor = HTC2Monitor()

# Load ROI
roi = load_roi_coordinates()

# Process
result = monitor.process_image("foto.jpg", roi_coords=roi)

# Output
if result['valid']:
    print(f"{result['temperature']}°C, {result['humidity']}%")
else:
    print("Gagal membaca")
```

### Integration dengan Database

```python
import sqlite3
from datetime import datetime
from main import HTC2Monitor, load_roi_coordinates

# Setup database
conn = sqlite3.connect('sensor_data.db')
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS readings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT,
        temperature REAL,
        humidity REAL,
        valid BOOLEAN
    )
''')

# Process image
monitor = HTC2Monitor()
roi = load_roi_coordinates()
result = monitor.process_image("foto.jpg", roi_coords=roi)

# Save to database
cursor.execute('''
    INSERT INTO readings (timestamp, temperature, humidity, valid)
    VALUES (?, ?, ?, ?)
''', (
    datetime.now().isoformat(),
    result['temperature'],
    result['humidity'],
    result['valid']
))

conn.commit()
conn.close()
```

### API Endpoint (Flask)

```python
from flask import Flask, request, jsonify
from main import HTC2Monitor, load_roi_coordinates
import os

app = Flask(__name__)
monitor = HTC2Monitor()
roi = load_roi_coordinates()

@app.route('/upload', methods=['POST'])
def upload_image():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    filepath = os.path.join('uploads', file.filename)
    file.save(filepath)
    
    # Process
    result = monitor.process_image(filepath, roi_coords=roi)
    
    # Clean up
    os.remove(filepath)
    
    return jsonify(result)

if __name__ == '__main__':
    os.makedirs('uploads', exist_ok=True)
    app.run(debug=True, port=5000)
```

---

## ⚠️ 6. TROUBLESHOOTING

### Problem 1: "pytesseract.pytesseract.TesseractNotFoundError"

**Penyebab**: Tesseract tidak terinstall atau tidak ditemukan

**Solusi**:
```bash
# macOS
brew install tesseract

# Windows - Set path di main.py:
monitor = HTC2Monitor(tesseract_path=r'C:\Program Files\Tesseract-OCR\tesseract.exe')

# Verify
tesseract --version
```

### Problem 2: "cv2.error: OpenCV(4.x.x) ... image is empty"

**Penyebab**: File gambar tidak ditemukan atau corrupt

**Solusi**:
```python
# Check file exists
import os
if not os.path.exists("sample_htc2.jpg"):
    print("File tidak ditemukan!")
    
# Check file valid
img = cv2.imread("sample_htc2.jpg")
if img is None:
    print("File corrupt atau format tidak didukung")
```

### Problem 3: OCR Membaca Angka Salah

**Penyebab**: Kualitas foto kurang baik, ROI tidak tepat, atau preprocessing kurang optimal

**Solusi**:
1. **Periksa Debug Output**:
```python
result = monitor.process_image("foto.jpg", save_debug=True)
# Check file di debug_output/
```

2. **Re-setup ROI**:
```python
setup_mode = True  # Reset ROI
```

3. **Improve Foto Quality**:
   - Gunakan pencahayaan lebih baik
   - Focus lebih tajam
   - Jarak lebih dekat ke display

4. **Adjust Preprocessing**:
   - Tingkatkan CLAHE clipLimit
   - Adjust threshold parameters

### Problem 4: "Gagal membaca nilai suhu/kelembapan"

**Penyebab**: OCR tidak mengenali angka

**Solusi**:
```python
# Coba OCR config berbeda
# Edit method extract_numbers_ocr():

# Try PSM 6
config = '--psm 6 digits'

# Try PSM 8  
config = '--psm 8 digits'

# Try tanpa whitelist
config = '--psm 7'
```

### Problem 5: Nilai di Luar Range Normal

**Penyebab**: OCR salah baca atau monitor menampilkan error

**Solusi**:
- Check warnings di output
- Verifikasi manual nilai di foto
- Periksa apakah monitor berfungsi normal

---

## 📊 7. BEST PRACTICES

### ✓ Do's
1. **Setup ROI dengan hati-hati** - Akurasi bergantung pada ROI yang tepat
2. **Gunakan pencahayaan konsisten** - Hasil lebih stabil
3. **Simpan debug output** - Untuk troubleshooting
4. **Validasi hasil** - Cross-check dengan pembacaan manual
5. **Backup roi_config.txt** - Jangan sampai hilang

### ✗ Don'ts
1. **Jangan** skip setup ROI - Auto-detect kurang akurat
2. **Jangan** gunakan foto blur - OCR akan gagal
3. **Jangan** ubah posisi monitor/kamera - ROI jadi tidak valid
4. **Jangan** edit foto manual - Gunakan preprocessing otomatis
5. **Jangan** ignore warnings - Periksa dan fix masalahnya

---

## 📞 SUPPORT

Jika masih ada masalah:
1. Periksa debug output di folder `debug_output/`
2. Verifikasi semua dependencies terinstall
3. Test dengan foto berkualitas baik terlebih dahulu
4. Dokumentasikan error message untuk troubleshooting

---

**Happy Processing! 🎉**

Dibuat oleh: GitHub Copilot  
Tanggal: January 6, 2026  
Versi: 1.0
