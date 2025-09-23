## temperhum
TEMPerHUM(3553:a001) から 温湿度を取得するPythonスクリプト  
Windows11とLinux(Ubuntu 24.04.3 LTS)で動作確認済み。

### 使用方法 (Windows)
[lsusb](https://libusb.info)のWindows用をDLして`libusb-1.0.29.7z\VS2022\MS64\dll\libusb-1.0.dll`を`C:\Windows\System32\libusb-1.0.dll`に置く。
```
pip install -r requirements.txt
python.exe get_temper_hum.py
```

### 使用方法 (Linux)
```
pip install -r requirements.txt
python get_temper_hum.py
```
