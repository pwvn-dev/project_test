from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.fernet import Fernet
import base64
import os
import json

def derive_key(password: str, salt: bytes):
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100_000)
    return base64.urlsafe_b64encode(kdf.derive(password.encode()))

def encrypt_license(data_dict, password):
    salt = os.urandom(16)
    key = derive_key(password, salt)
    f = Fernet(key)
    license_json = json.dumps(data_dict).encode()
    token = f.encrypt(license_json)
    return base64.b64encode(salt + token).decode('utf-8')

if __name__ == "__main__":
    # Thông tin license mẫu
    license_data = {
        "user": "testuser",
        "expiry": "2025-09-10",    # ngày hết hạn 10/09/2025
        "max_devices": 3
    }
    password = "strongpassword"  # Mật khẩu bạn sẽ nhập ở GUI để check
    token = encrypt_license(license_data, password)
    os.makedirs("license", exist_ok=True)
    with open("license/license.lic", "w", encoding="utf-8") as f:
        f.write(token)
    print("Đã tạo file license/license.lic!")
