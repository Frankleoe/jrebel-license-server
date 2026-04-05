# -*- coding: utf-8 -*-
"""
JRebel 签名器模块
"""
import base64
import logging

logger = logging.getLogger(__name__)

# JRebel 私钥
JREBEL_PRIVATE_KEY_BASE64 = (
    "MIICXAIBAAKBgQDQ93CP6SjEneDizCF1P/MaBGf582voNNFcu8oMhgdTZ/N6qa6O"
    "7XJDr1FSCyaDdKSsPCdxPK7Y4Usq/fOPas2kCgYcRS/iebrtPEFZ/7TLfk39HLuT"
    "Ejzo0/CNvjVsgWeh9BYznFaxFDLx7fLKqCQ6w1OKScnsdqwjpaXwXqiulwIDAQAB"
    "AoGATOQvvBSMVsTNQkbgrNcqKdGjPNrwQtJkk13aO/95ZJxkgCc9vwPqPrOdFbZa"
    "ppZeHa5IyScOI2nLEfe+DnC7V80K2dBtaIQjOeZQt5HoTRG4EHQaWoDh27BWuJoi"
    "p5WMrOd+1qfkOtZoRjNcHl86LIAh/+3vxYyebkug4UHNGPkCQQD+N4ZUkhKNQW7m"
    "pxX6eecitmOdN7Yt0YH9UmxPiW1LyCEbLwduMR2tfyGfrbZALiGzlKJize38shGC"
    "1qYSMvZFAkEA0m6psWWiTUWtaOKMxkTkcUdigalZ9xFSEl6jXFB94AD+dlPS3J5g"
    "NzTEmbPLc14VIWJFkO+UOrpl77w5uF2dKwJAaMpslhnsicvKMkv31FtBut5iK6GW"
    "eEafhdPfD94/bnidpP362yJl8Gmya4cI1GXvwH3pfj8S9hJVA5EFvgTB3QJBAJP1"
    "O1uAGp46X7Nfl5vQ1M7RYnHIoXkWtJ417Kb78YWPLVwFlD2LHhuy/okT4fk8LZ9L"
    "eZ5u1cp1RTdLIUqAiAECQC46OwOm87L35yaVfpUIjqg/1gsNwNsj8HvtXdF/9d30"
    "JIM3GwdytCvNRLqP35Ciogb9AO8ke8L6zY83nxPbClM="
)

SERVER_RANDOMNESS = "H2ulzLlh7E0="


class JRebelSigner:
    def __init__(self):
        self.private_key = None
        self._load_private_key()

    def _load_private_key(self):
        try:
            from cryptography.hazmat.primitives import serialization
            from cryptography.hazmat.backends import default_backend
            key_bytes = base64.b64decode(JREBEL_PRIVATE_KEY_BASE64)
            self.private_key = serialization.load_der_private_key(
                key_bytes, password=None, backend=default_backend()
            )
            logger.info("JRebel 私钥加载成功")
        except Exception as e:
            logger.error(f"加载私钥失败: {e}")
            self.private_key = None

    def sign(self, data: str) -> str:
        if self.private_key is None:
            return ""
        try:
            from cryptography.hazmat.primitives import hashes
            from cryptography.hazmat.primitives.asymmetric import padding
            signature = self.private_key.sign(
                data.encode("utf-8"),
                padding.PKCS1v15(),
                hashes.SHA1()
            )
            return base64.b64encode(signature).decode()
        except Exception as e:
            logger.error(f"签名失败: {e}")
            return ""

    def create_lease_signature(self, client_randomness: str, guid: str,
                               offline: bool, valid_from: str = "null",
                               valid_until: str = "null") -> str:
        if offline:
            sign_data = f"{client_randomness};{SERVER_RANDOMNESS};{guid};true;{valid_from};{valid_until}"
        else:
            sign_data = f"{client_randomness};{SERVER_RANDOMNESS};{guid};false"
        logger.info(f"签名数据: {sign_data}")
        return self.sign(sign_data)


signer = JRebelSigner()
