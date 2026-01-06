import cv2
import numpy as np
import pytesseract
from PIL import Image
import re
import os
from datetime import datetime

class HTC2Monitor:
    """Class untuk memproses gambar monitor HTC-2 dan mengekstrak nilai suhu & kelembapan"""
    
    def __init__(self, tesseract_path=None):
        r"""
        Inisialisasi HTC2Monitor
        
        Args:
            tesseract_path: Path ke tesseract executable (untuk Windows)
                          Contoh: r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        """
        if tesseract_path:
            pytesseract.pytesseract.tesseract_cmd = tesseract_path
    
    # ========== 1. PREPROCESSING GAMBAR ==========
    def preprocess_image(self, image_path):
        """
        Preprocessing gambar untuk meningkatkan kualitas OCR
        
        Args:
            image_path: Path ke file gambar
            
        Returns:
            tuple: (original_image, preprocessed_image)
        """
        # Baca gambar
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError(f"Tidak dapat membaca gambar: {image_path}")
        
        # Simpan gambar original
        original = img.copy()
        
        # Konversi ke grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Tingkatkan kontras menggunakan CLAHE
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        enhanced = clahe.apply(gray)
        
        # Denoising untuk mengurangi noise
        denoised = cv2.fastNlMeansDenoising(enhanced, None, 10, 7, 21)
        
        # Adaptive thresholding untuk binarization
        binary = cv2.adaptiveThreshold(
            denoised, 255, 
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv2.THRESH_BINARY, 
            11, 2
        )
        
        # Morphological operations untuk cleanup
        kernel = np.ones((2,2), np.uint8)
        processed = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
        processed = cv2.morphologyEx(processed, cv2.MORPH_OPEN, kernel)
        
        return original, processed
    
    # ========== 2. DETEKSI ROI (Region of Interest) ==========
    def detect_roi(self, image, display_coords=None):
        """
        Deteksi area tampilan digital (ROI) pada monitor
        
        Args:
            image: Gambar yang sudah dipreprocess
            display_coords: Koordinat manual ROI jika diketahui
                          Format: (x, y, width, height)
                          
        Returns:
            dict: Dictionary berisi ROI untuk suhu dan kelembapan
        """
        if display_coords:
            # Gunakan koordinat manual
            x, y, w, h = display_coords
            roi = image[y:y+h, x:x+w]
            
            # Split menjadi area suhu dan kelembapan
            # Asumsi: suhu di bagian atas, kelembapan di bawah
            height = roi.shape[0]
            temp_roi = roi[0:height//2, :]
            humidity_roi = roi[height//2:height, :]
        else:
            # Auto-detect menggunakan contour detection
            # Deteksi kontur untuk menemukan area display
            contours, _ = cv2.findContours(
                image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
            )
            
            # Cari kontur dengan area terbesar (kemungkinan display)
            if contours:
                largest_contour = max(contours, key=cv2.contourArea)
                x, y, w, h = cv2.boundingRect(largest_contour)
                roi = image[y:y+h, x:x+w]
                
                # Split menjadi area suhu dan kelembapan
                height = roi.shape[0]
                temp_roi = roi[0:height//2, :]
                humidity_roi = roi[height//2:height, :]
            else:
                # Fallback: gunakan seluruh gambar
                height = image.shape[0]
                temp_roi = image[0:height//2, :]
                humidity_roi = image[height//2:height, :]
        
        return {
            'temperature_roi': temp_roi,
            'humidity_roi': humidity_roi
        }
    
    def manual_roi_selection(self, image_path):
        """
        Memungkinkan user untuk memilih ROI secara manual
        
        Args:
            image_path: Path ke gambar
            
        Returns:
            tuple: (temp_coords, humidity_coords)
        """
        img = cv2.imread(image_path)
        
        print("Pilih area SUHU (Temperature)")
        print("Klik dan drag untuk memilih area, tekan ENTER jika selesai, ESC untuk cancel")
        temp_roi = cv2.selectROI("Pilih Area Suhu", img, False)
        cv2.destroyAllWindows()
        
        print("Pilih area KELEMBAPAN (Humidity)")
        print("Klik dan drag untuk memilih area, tekan ENTER jika selesai, ESC untuk cancel")
        humidity_roi = cv2.selectROI("Pilih Area Kelembapan", img, False)
        cv2.destroyAllWindows()
        
        return temp_roi, humidity_roi
    
    # ========== 3. OCR UNTUK EKSTRAKSI ANGKA ==========
    def extract_numbers_ocr(self, roi_image, config='--psm 7 digits'):
        """
        Ekstraksi angka dari ROI menggunakan Tesseract OCR
        
        Args:
            roi_image: ROI yang berisi angka
            config: Konfigurasi Tesseract
                   --psm 7: Single line
                   --psm 8: Single word
                   --psm 6: Uniform block
                   digits: Hanya deteksi angka
                   
        Returns:
            str: Text hasil OCR
        """
        # Resize untuk meningkatkan akurasi OCR
        scale_factor = 3
        height, width = roi_image.shape[:2]
        resized = cv2.resize(
            roi_image, 
            (width * scale_factor, height * scale_factor),
            interpolation=cv2.INTER_CUBIC
        )
        
        # OCR menggunakan pytesseract
        custom_config = config
        text = pytesseract.image_to_string(resized, config=custom_config)
        
        return text.strip()
    
    # ========== 4. PARSING DAN VALIDASI HASIL ==========
    def parse_reading(self, text):
        """
        Parse hasil OCR untuk mendapatkan nilai numerik
        
        Args:
            text: Text hasil OCR
            
        Returns:
            float: Nilai numerik, atau None jika parsing gagal
        """
        # Bersihkan text
        cleaned = text.strip()
        
        # Ekstrak angka menggunakan regex
        # Pattern untuk angka dengan atau tanpa desimal
        pattern = r'[-+]?\d*\.?\d+'
        matches = re.findall(pattern, cleaned)
        
        if matches:
            try:
                # Ambil angka pertama yang ditemukan
                value = float(matches[0])
                return value
            except ValueError:
                return None
        
        return None
    
    def validate_reading(self, temperature, humidity):
        """
        Validasi hasil pembacaan suhu dan kelembapan
        
        Args:
            temperature: Nilai suhu (Celsius)
            humidity: Nilai kelembapan (%)
            
        Returns:
            dict: Hasil validasi dengan flag valid/invalid
        """
        result = {
            'temperature': temperature,
            'humidity': humidity,
            'valid': False,
            'warnings': []
        }
        
        # Validasi suhu (range normal: -40°C to 80°C untuk HTC-2)
        if temperature is not None:
            if -40 <= temperature <= 80:
                result['temp_valid'] = True
            else:
                result['temp_valid'] = False
                result['warnings'].append(f"Suhu {temperature}°C di luar range normal (-40 to 80°C)")
        else:
            result['temp_valid'] = False
            result['warnings'].append("Gagal membaca nilai suhu")
        
        # Validasi kelembapan (range: 0-100%)
        if humidity is not None:
            if 0 <= humidity <= 100:
                result['humidity_valid'] = True
            else:
                result['humidity_valid'] = False
                result['warnings'].append(f"Kelembapan {humidity}% di luar range normal (0-100%)")
        else:
            result['humidity_valid'] = False
            result['warnings'].append("Gagal membaca nilai kelembapan")
        
        # Overall valid jika kedua pembacaan valid
        result['valid'] = result['temp_valid'] and result['humidity_valid']
        
        return result
    
    # ========== FUNGSI UTAMA UNTUK PROSES LENGKAP ==========
    def process_image(self, image_path, roi_coords=None, save_debug=False):
        """
        Proses lengkap dari gambar ke hasil pembacaan
        
        Args:
            image_path: Path ke gambar monitor
            roi_coords: Dictionary dengan 'temperature' dan 'humidity' ROI coords
                       Format: {'temperature': (x,y,w,h), 'humidity': (x,y,w,h)}
            save_debug: Simpan gambar debug untuk troubleshooting
            
        Returns:
            dict: Hasil pembacaan dengan validasi
        """
        print(f"Memproses gambar: {image_path}")
        
        # 1. Preprocessing
        print("1. Preprocessing gambar...")
        original, processed = self.preprocess_image(image_path)
        
        # 2. Deteksi ROI
        print("2. Mendeteksi Region of Interest...")
        if roi_coords:
            # Gunakan koordinat manual
            temp_roi = processed[
                roi_coords['temperature'][1]:roi_coords['temperature'][1]+roi_coords['temperature'][3],
                roi_coords['temperature'][0]:roi_coords['temperature'][0]+roi_coords['temperature'][2]
            ]
            humidity_roi = processed[
                roi_coords['humidity'][1]:roi_coords['humidity'][1]+roi_coords['humidity'][3],
                roi_coords['humidity'][0]:roi_coords['humidity'][0]+roi_coords['humidity'][2]
            ]
            rois = {
                'temperature_roi': temp_roi,
                'humidity_roi': humidity_roi
            }
        else:
            rois = self.detect_roi(processed)
        
        # 3. OCR Ekstraksi
        print("3. Melakukan OCR untuk ekstraksi angka...")
        temp_text = self.extract_numbers_ocr(rois['temperature_roi'])
        humidity_text = self.extract_numbers_ocr(rois['humidity_roi'])
        
        print(f"   - Teks suhu: '{temp_text}'")
        print(f"   - Teks kelembapan: '{humidity_text}'")
        
        # 4. Parsing hasil
        print("4. Parsing hasil OCR...")
        temperature = self.parse_reading(temp_text)
        humidity = self.parse_reading(humidity_text)
        
        # 5. Validasi
        print("5. Validasi hasil...")
        result = self.validate_reading(temperature, humidity)
        
        # Simpan debug images jika diminta
        if save_debug:
            debug_dir = "debug_output"
            os.makedirs(debug_dir, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            cv2.imwrite(f"{debug_dir}/original_{timestamp}.jpg", original)
            cv2.imwrite(f"{debug_dir}/processed_{timestamp}.jpg", processed)
            cv2.imwrite(f"{debug_dir}/temp_roi_{timestamp}.jpg", rois['temperature_roi'])
            cv2.imwrite(f"{debug_dir}/humidity_roi_{timestamp}.jpg", rois['humidity_roi'])
            print(f"   Debug images disimpan di folder '{debug_dir}'")
        
        return result


# ========== FUNGSI UTILITY ==========
def save_roi_coordinates(temp_coords, humidity_coords, filename="roi_config.txt"):
    """
    Simpan koordinat ROI ke file untuk digunakan kembali
    
    Args:
        temp_coords: Koordinat ROI suhu (x, y, w, h)
        humidity_coords: Koordinat ROI kelembapan (x, y, w, h)
        filename: Nama file untuk menyimpan koordinat
    """
    with open(filename, 'w') as f:
        f.write(f"temperature={temp_coords[0]},{temp_coords[1]},{temp_coords[2]},{temp_coords[3]}\n")
        f.write(f"humidity={humidity_coords[0]},{humidity_coords[1]},{humidity_coords[2]},{humidity_coords[3]}\n")
    print(f"Koordinat ROI disimpan ke {filename}")


def load_roi_coordinates(filename="roi_config.txt"):
    """
    Load koordinat ROI dari file
    
    Args:
        filename: Nama file konfigurasi
        
    Returns:
        dict: Dictionary berisi koordinat ROI
    """
    roi_coords = {}
    with open(filename, 'r') as f:
        for line in f:
            key, values = line.strip().split('=')
            coords = tuple(map(int, values.split(',')))
            roi_coords[key] = coords
    return roi_coords


# ========== CONTOH PENGGUNAAN ==========
if __name__ == "__main__":
    # Inisialisasi monitor processor
    # Untuk Windows, uncomment dan sesuaikan path tesseract:
    # monitor = HTC2Monitor(tesseract_path=r'C:\Program Files\Tesseract-OCR\tesseract.exe')
    
    monitor = HTC2Monitor()
    
    print("="*70)
    print("SISTEM IMAGE PROCESSING MONITOR HTC-2")
    print("="*70)
    print()
    
    # ===== MODE 1: Setup ROI pertama kali =====
    setup_mode = False  # Ubah ke True jika pertama kali setup
    
    if setup_mode:
        print("MODE SETUP: Pilih area ROI")
        print("-" * 70)
        image_path = "sample_htc2.jpg"  # Ganti dengan path gambar Anda
        
        # Pilih ROI secara manual
        temp_coords, humidity_coords = monitor.manual_roi_selection(image_path)
        
        # Simpan koordinat untuk digunakan kembali
        save_roi_coordinates(temp_coords, humidity_coords)
        print("Setup selesai! ROI telah disimpan.")
    
    # ===== MODE 2: Proses gambar dengan ROI yang sudah disimpan =====
    else:
        print("MODE PROCESSING: Membaca nilai dari gambar")
        print("-" * 70)
        
        # Path ke gambar yang akan diproses
        image_path = "sample_htc2.jpg"  # Ganti dengan path gambar Anda
        
        # Cek apakah file gambar ada
        if not os.path.exists(image_path):
            print(f"ERROR: File '{image_path}' tidak ditemukan!")
            print("Silakan:")
            print("1. Letakkan foto monitor HTC-2 di folder yang sama dengan script ini")
            print("2. Rename file menjadi 'sample_htc2.jpg' atau")
            print("3. Ubah variabel 'image_path' dengan nama file Anda")
        else:
            # Load ROI coordinates jika sudah pernah setup
            try:
                roi_coords = load_roi_coordinates()
                print("Menggunakan ROI yang sudah disimpan")
            except FileNotFoundError:
                print("ROI belum di-setup, menggunakan auto-detect")
                roi_coords = None
            
            # Proses gambar
            result = monitor.process_image(
                image_path, 
                roi_coords=roi_coords,
                save_debug=True  # Simpan debug images
            )
            
            # Tampilkan hasil
            print()
            print("="*70)
            print("HASIL PEMBACAAN")
            print("="*70)
            print(f"Suhu        : {result['temperature']}°C" if result['temperature'] else "Suhu        : Gagal dibaca")
            print(f"Kelembapan  : {result['humidity']}%" if result['humidity'] else "Kelembapan  : Gagal dibaca")
            print(f"Status      : {'VALID ✓' if result['valid'] else 'INVALID ✗'}")
            
            if result['warnings']:
                print("\nPERINGATAN:")
                for warning in result['warnings']:
                    print(f"  - {warning}")
            
            print("="*70)


# ========== CONTOH BATCH PROCESSING ==========
def batch_process_images(image_folder, roi_coords=None):
    """
    Proses multiple gambar dalam satu folder
    
    Args:
        image_folder: Path ke folder berisi gambar
        roi_coords: Koordinat ROI (optional)
    """
    monitor = HTC2Monitor()
    
    # List semua file gambar
    image_extensions = ['.jpg', '.jpeg', '.png', '.bmp']
    image_files = [
        f for f in os.listdir(image_folder) 
        if os.path.splitext(f)[1].lower() in image_extensions
    ]
    
    results = []
    
    for img_file in image_files:
        img_path = os.path.join(image_folder, img_file)
        print(f"\nMemproses: {img_file}")
        
        try:
            result = monitor.process_image(img_path, roi_coords)
            result['filename'] = img_file
            result['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            results.append(result)
        except Exception as e:
            print(f"Error memproses {img_file}: {str(e)}")
    
    # Simpan hasil ke CSV
    import csv
    output_file = f"results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    
    with open(output_file, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['timestamp', 'filename', 'temperature', 'humidity', 'valid'])
        writer.writeheader()
        for result in results:
            writer.writerow({
                'timestamp': result['timestamp'],
                'filename': result['filename'],
                'temperature': result['temperature'],
                'humidity': result['humidity'],
                'valid': result['valid']
            })
    
    print(f"\nHasil batch processing disimpan ke: {output_file}")
    return results
