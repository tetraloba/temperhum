TEMPerHUM から 温湿度を取得するPythonスクリプト
Windows環境でのみ動作確認済み。


[lsusb](https://libusb.info)のWindows用をDLして`libusb-1.0.29.7z\VS2022\MS64\dll\libusb-1.0.dll`を`C:\Windows\System32\libusb-1.0.dll`に置く。

`pip install -r requirements.txt`

`python.exe pyusb.py`

