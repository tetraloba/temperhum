from logging import getLogger, FileHandler, DEBUG, INFO, WARN, ERROR
import time
from datetime import datetime
from platform import system
import usb.core
import usb.util

# USBデバイスのベンダーIDとプロダクトID
VENDOR_ID = 0x3553
PRODUCT_ID = 0xa001

# HIDレポートのペイロードサイズ
REPORT_SIZE = 8

# ログ出力設定
logger = getLogger(__name__)
logger.setLevel(DEBUG)
# ch = StreamHandler()
ch = FileHandler("temperhum.err.log")
ch.setLevel(WARN)
logger.addHandler(ch)

# 繰り返し設定
REPEAT_NUM = 1
REPEAT_INTERVAL = 3 # [s]

def find_temphum_device():
    """
    TEMPerHUMデバイスを検索し、返す
    """
    dev = usb.core.find(idVendor=VENDOR_ID, idProduct=PRODUCT_ID)
    if dev is None:
        raise ValueError('Device not found')
    return dev

def parse_data(raw_data):
    """
    生のバイト列を解析して温度と湿度を計算
    """
    if len(raw_data) < 8:
        return None, None

    # 生の温度データは3バイト目と4バイト目
    temp_raw = raw_data[2] * 256 + raw_data[3]
    # 生の湿度データは5バイト目と6バイト目
    humidity_raw = raw_data[4] * 256 + raw_data[5]

    # 100で割って実際の温度と湿度を計算
    temperature = temp_raw / 100.0
    humidity = humidity_raw / 100.0

    return temperature, humidity

def hex_str(raw_data):
    res = ""
    for r in raw_data:
        res += hex(r)[2:]
    return res

def main():
    try:
        # 1. デバイスを検索
        dev = find_temphum_device()
        logger.info("Device found.")

        # 2. デバイスの設定
        cfg = dev.get_active_configuration()
        intf = None
        ep_out = None
        ep_in = None

        # すべてのインターフェースをループして、適切なエンドポイントを見つける
        for interface in cfg:
            ep_out = usb.util.find_descriptor(
                interface,
                custom_match=lambda e: (e.bEndpointAddress & 0x80) == 0 # OUT方向 (LSBが0)
            )
            ep_in = usb.util.find_descriptor(
                interface,
                custom_match=lambda e: (e.bEndpointAddress & 0x80) == 0x80 # IN方向 (LSBが1)
            )
            if ep_out and ep_in:
                intf = interface
                break
        if not intf:
            raise RuntimeError("Endpoints not found on any interface.")

        logger.info(f"Endpoints found on Interface: {intf.bInterfaceNumber}. Commencing data transfer.")

        # 2. デバイスの設定 (手動)
        # dev.set_configuration()
        # intf = dev[0][(1,0)]
        # ep_out = intf[1]
        # ep_in = intf[0]

        logger.info("== intf =="); logger.info(intf)
        logger.info("== ep_out =="); logger.info(ep_out)
        logger.info("== ep_in =="); logger.info(ep_in)

        if not ep_out or not ep_in:
            raise RuntimeError("Endpoints not found with hardcoded values.")

        # 3. カーネルドライバの切り離し(Windowsでは不要)
        if system() == 'Linux':
            logger.info("OS: Linux. Checking for kernel driver...")
            try:
                if dev.is_kernel_driver_active(intf.bInterfaceNumber):
                    logger.info("Detaching kernel driver.")
                    dev.detach_kernel_driver(intf.bInterfaceNumber)
            except usb.core.USBError as e:
                logger.error(f"Failed to detach kernel driver: {e}")
        else:
            logger.info("OS: Not Linux. Skipping kernel driver detachment.\nIf Windows, you need to install 'libusb-1.0.dll'.")

        # 4. モデル名・ファームウェアバージョンの取得 (必須でない)
        # パケットキャプチャから特定した「モデル名・ファームウェアバージョンを要求する」コマンド
        # command_for_data = [0x01, 0x86, 0xff, 0x01, 0x00, 0x00, 0x00, 0x00]
        # logger.info(f"Sending command: {hex_str(command_for_data)}")
        # ep_out.write(command_for_data)

        # logger.info("Waiting for data...")
        # raw_data = ep_in.read(REPORT_SIZE)
        # if raw_data:
        #     logger.info(f"Received raw data: {hex_str(raw_data)}")

        # logger.info("Waiting for data...")
        # raw_data = ep_in.read(REPORT_SIZE)
        # if raw_data:
        #     logger.info(f"Received raw data: {hex_str(raw_data)}")

        # パケットキャプチャから特定した「温湿度データを要求する」コマンド
        command_for_data = [0x01, 0x80, 0x33, 0x01, 0x00, 0x00, 0x00, 0x00]
        for i in range(REPEAT_NUM):
            logger.info(f"Sending command: {hex_str(command_for_data)}")
            ep_out.write(command_for_data)

            # 5. データを読み取る
            logger.info("Waiting for data...")
            raw_data = ep_in.read(REPORT_SIZE)

            if raw_data:
                logger.info(f"Received raw data: {hex_str(raw_data)}")
                timestamp = datetime.now().isoformat(timespec="seconds")
                temperature, humidity = parse_data(raw_data)
                if temperature is not None and humidity is not None:
                    print(f"{timestamp},{temperature},{humidity}")
                else:
                    logger.error("Failed to parse data.")
            else:
                logger.error("No data received.")
            if i < REPEAT_NUM - 1:
                time.sleep(REPEAT_INTERVAL)

    except usb.core.USBError as ex:
        logger.error(f"USB Error: {ex}")
    except ValueError as ex:
        logger.error(f"Error: {ex}")
    except RuntimeError as ex:
        logger.error(f"Runtime Error: {ex}")
    except Exception as ex:
        logger.error(f"An unexpected error occurred: {ex}")
    finally:
        # デバイスを閉じる
        if 'dev' in locals() and dev:
            usb.util.dispose_resources(dev)
            logger.info("Resources disposed.")

if __name__ == "__main__":
    main()
