# -*- coding: utf-8 -*-
"""
JetBrains IDE 签名器模块
使用 MD5withRSA 签名
"""
import base64
import hashlib
import logging

logger = logging.getLogger(__name__)

# JetBrains 私钥
JETBRAINS_PRIVATE_KEY_BASE64 = (
    "MIIBOgIBAAJBALecq3BwAI4YJZwhJ+snnDFj3lF3DMqNPorV6y5ZKXCiCMqj8OeO"
    "mxk4YZW9aaV9ckl/zlAOI0mpB3pDT+Xlj2sCAwEAAQJAW6/aVD05qbsZHMvZuS2A"
    "a5FpNNj0BDlf38hOtkhDzz/hkYb+EBYLLvldhgsD0OvRNy8yhz7EjaUqLCB0juIN"
    "4QIhAOeCQp+NXxfBmfdG/S+XbRUAdv8iHBl+F6O2wr5fA2jzAiEAywlDfGIl6acn"
    "akPrmJE0IL8qvuO3FtsHBrpkUuOnXakCIQCqdr+XvADI/UThTuQepuErFayJMBSA"
    "sNe3NFsw0cUxAQIgGA5n7ZPfdBi3BdM4VeJWb87WrLlkVxPqeDSbcGrCyMkCIFSs"
    "5JyXvFTreWt7IQjDssrKDRIPmALdNjvfETwlNJyY"
)


class JetBrainsSigner:
    def __init__(self):
        self.private_key = None
        self._load_private_key()

    def _load_private_key(self):
        try:
            from cryptography.hazmat.primitives.serialization import load_der_private_key
            from cryptography.hazmat.backends import default_backend
            key_bytes = base64.b64decode(JETBRAINS_PRIVATE_KEY_BASE64)
            self.private_key = load_der_private_key(
                key_bytes, password=None, backend=default_backend()
            )
            logger.info("JetBrains 私钥加载成功")
        except Exception as e:
            logger.error(f"加载 JetBrains 私钥失败: {e}")
            self.private_key = None

    def sign(self, content: str) -> str:
        if self.private_key is None:
            # Fallback to MD5 hash
            return hashlib.md5(content.encode()).hexdigest()
        try:
            from cryptography.hazmat.primitives import hashes
            from cryptography.hazmat.primitives.asymmetric import padding
            signature = self.private_key.sign(
                content.encode("utf-8"),
                padding.PKCS1v15(),
                hashes.MD5()
            )
            return signature.hex()
        except Exception as e:
            logger.error(f"JetBrains 签名失败: {e}")
            return hashlib.md5(content.encode()).hexdigest()


jetbrains_signer = JetBrainsSigner()
