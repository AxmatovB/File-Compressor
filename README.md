# 🎬 Max Video Compressor

Max Video Compressor – bu **GPU (videokarta) orqali** videolarni juda tez va yuqori sifatda (H.265 kodek) siqish uchun mo'ljallangan qulay desktop dasturi. Dastur to'liq Python va Tkinter yordamida yozilgan bo'lib, foydalanuvchi kompyuterida alohida dasturlar o'rnatishni talab qilmaydi (chunki barcha kerakli fayllar .exe ichiga joylangan).

![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)
![FFmpeg](https://img.shields.io/badge/FFmpeg-Included-green.svg)
![Tkinter](https://img.shields.io/badge/GUI-Tkinter-lightgrey.svg)

---

## 🌟 Asosiy Imkoniyatlari

- **Tezkor GPU Siqish**: Odatdagi protsessorga (CPU) qaraganda 5-10 barobar tezroq ishlaydi. 
  Quyidagi videokartalarni avtomatik taniydi va qo'llab-quvvatlaydi:
  - 🟩 **NVIDIA** (NVENC)
  - 🟥 **AMD** (AMF)
  - 🟦 **Intel** (QSV)
  - ⬜ **CPU** (Agar videokarta topilmasa, libx265 orqali CPU ishlatiladi)
- **H.265 (HEVC) Kodek**: Video sifatini yo'qotmagan holda fayl hajmini 80-90% gacha tejaydi.
- **Ommaviy Siqish (Batch Processing)**: Bitta jildni (papkani) ko'rsatsangiz, uning ichidagi barcha videolarni o'zi topib birma-bir siqib chiqadi.
- **Avtomatik Joylashuv**: Dastur kompyuterning `Desktop` (Ish stoli) qismida bugungi sana bilan papka ochadi va barcha tayyor videolarni o'sha yerga saqlaydi.
- **Jarayonni Boshqarish**: Siqish jarayoni ketayotganda istalgan paytda **bekor qilish (❌)** tugmasini bosib to'xtatishingiz mumkin. Chala qolgan fayllar avtomatik tozalanadi.
- **Mustaqil (Standalone) Dastur**: Hech nima o'rnatish shart emas. Bitta dona `Max_Video_Compressor.exe` fayli bilan dasturni xohlagan kompyuterda ochib ishlatish mumkin!

---

## 🖥 Dasturni Qanday Ishlatish Kerak?

Dastur interfeysi juda sodda va tushunarli. Uni ishlatish uchun quyidagi qadamlarni bajaring:

1. **Dasturni ishga tushiring**: `Max_Video_Compressor.exe` faylini ikki marta bosib oching.
2. **Videokartani tanlang**: 
   - Dastur tepasidagi ro'yxatdan o'zingizning kompyuteringizda bor bo'lgan GPU ni tanlang (Masalan: *NVIDIA GPU*). 
   - Agar qaysi biriligini bilmasangiz, shunchaki harakat qilib ko'ring yoki *CPU Processor* ni tanlang.
3. **Fayl yoki Papka yuklang**:
   - 🎬 **Video yuklash**: Agar bitta donagina videoni siqmoqchi bo'lsangiz, shu tugmani bosing va videoni tanlang.
   - 📁 **Jild yuklash**: Agar sizda ko'plab videolar bo'lsa, ularni bitta papkaga soling va shu tugmani bosib papkani tanlang. Dastur ichidagi barcha videolarni o'zi kompress qiladi.
4. **Kuting**: Dastur pastida foiz (0% dan 100% gacha) va qolgan vaqt ko'rsatiladi. 
5. **Tayyor!**: 100% bo'lganidan so'ng, videolaringiz sizning Ish stolingiz (Desktop) da bugungi sana yozilgan papkada tayyor bo'ladi.

---

## 🛠 Dasturchilar uchun qo'llanma (Source Code)

Agar kodingizni o'zgartirmoqchi yoki uni qanday yig'ishni bilmoqchi bo'lsangiz, quyidagilarni o'qing:

### Talablar (Prerequisites)
Kodni to'g'ridan to'g'ri Pycharm yoki VS Code'da ishlatish uchun kompyuteringizda quyidagilar bo'lishi shart:
1. Python 3.7 yoki undan yuqori versiya.
2. `ffmpeg.exe` va `ffprobe.exe` fayllari ushbu loyiha bilan bir xil papkada bo'lishi kerak. 

### Kodni ishga tushirish:
```bash
python main.py
```

### Kodni yangi `.exe` (dastur) ko'rinishiga keltirish:
Kodingizga o'zgartirish kiritib, uni barchada ishlaydigan `.exe` fayl qilmoqchi bo'lsangiz terminalda quyidagi buyruqni bering. Bu buyruq o'z ichiga FFmpeg fayllarini ham qamrab oladi, natijada bitta katta fayl yaratiladi:

```bash
pip install pyinstaller

pyinstaller --onefile --windowed --icon=compress_setting_repair_tools_zipper_icon_265700.ico --add-binary "ffmpeg.exe;." --add-binary "ffprobe.exe;." --name="Max_Video_Compressor" main.py
```
*(Yig'ilgan EXE fayli `dist` nomli papka ichida paydo bo'ladi).*

---

## ⚙️ Sozlamalarni o'zgartirish

Sifatni o'zgartirish uchun `main.py` ichiga kiring va quyidagi qatorni toping:
```python
QUALITY = 30 
```
Bu qiymat qancha past bo'lsa, sifati shuncha yaxshi, lekin xotiradan katta joy oladi. Qancha baland bo'lsa shuncha yomon sifat, lekin xotiradan juda kam joy oladi. Tavsiya etilgan oraliq: **25 - 35**.

---

## 📄 Litsenziya

Ushbu loyiha ochiq manbali kod (Open Source) hisoblanib, MIT litsenziyasi asosida taqdim etiladi.
