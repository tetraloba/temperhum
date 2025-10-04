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
基本的にはsudoが必要。  
venvを使っている場合は`sudo .venv/bin/python get_temper_hum.py`のように実行する。  

#### 一般ユーザ(非ルートユーザ)でも実行できるようにする
(想定: 非ルートユーザでcronを使って定期実行をしたい場合など)  
udevルールを編集して一般ユーザがTEMPerHUMにアクセスできるようにする。  
```/etc/udev/rules.d/99-temperhum.rules
SUBSYSTEM=="usb", ATTR{idVendor}=="3553", ATTR{idProduct}=="a001", MODE="0666", GROUP="plugdev"
```
```
sudo udevadm control --reload-rules
sudo udevadm trigger
```

