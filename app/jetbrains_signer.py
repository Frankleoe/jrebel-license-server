# -*- coding: utf-8 -*-
"""
JetBrains IDE 签名器模块
使用 SHA256withRSA 签名（Base64 编码）
修复: 原 512-bit 密钥太弱，升级为 2048-bit；MD5→SHA256；hex→Base64
"""
import base64
import logging

logger = logging.getLogger(__name__)

# JetBrains 私钥（2048-bit RSA，2026-04-11 重新生成）
JETBRAINS_PRIVATE_KEY_BASE64 = (
    "MIIEvAIBADANBgkqhkiG9w0BAQEFAASCBKYwggSiAgEAAoIBAQDUeaLUeAUtgcgH"
    "oShjYdWXgnPs19s4sitbrdMeQWZbrIZ+GxYyJ3MzwUKMIg696sB/pE9RPdxvfwVE"
    "3vAsWQQXBrBfwcdNyZlzB8PQmeIStI9SS2tHlTM1h1O8xzaaJYEgvQclLgfHIgxX"
    "aScjSgyLKBD8Dnotf36sKOi4Y61f6m2I6vREqntMZO21QhKTXG7wx+v7nWlQ+Ms7"
    "I2gf3G42ElAnXP9EdrqZaiYxcavsuecIlEcCUW22oXiERvrmt3armdClFg7bkFxk"
    "o5CXKRS1QNG1cYXRa+JE3A3H9bGtY/jyYUj1yFZh3A/OZdKtYCai04P/DZpY6Tpr"
    "1+Y4U98nAgMBAAECggEATxcT+HjQnJbhqY1gplXFlwc1NaVH8fvITfEPVATOIDPB"
    "QHG+ul6a8Fnw9o665BDdJOY5rCkVw98JTBCcYDWmYxfXUV2lXZw8ZWgviJevYn0Z"
    "mG2Aen3cOQGttuiEt65cOZ6DaWCP/pz68RKwQd+PecEpSVnuOr9pnJYBwpk/8SJ5"
    "eC8I7H56yG/Q5UsBQuuT//ZP56FXbrY3MMX6QWm7E6FuUsnFVTFJJUtx3CKPOT0b"
    "p+6J2wxfsA8DO1P/+w8HPvrwjMHpXxh+0CxR3I6ZLP4FU+O2q2NQU8hE05M0g8Q+"
    "HUEsAz2Mj0wVrWPjeFRKqTBrj3dS3Eha2UelMwolEQKBgQDxAZ1PPyvl6VMofjK8"
    "SGSPe6upTkgjH08flNvXc6KfBfcS6VUdiLi/T1dxi8589K+e+RkPan0M7v3itmBr"
    "Xtsxzqn0OuiGnTPPlFdnsDfxs1N6N/1wZr/e6nc0+OdP+dqOnMvoT/CA/jkktw0E"
    "+2EklG8kCyX9J34pIRINHNHqTwKBgQDhsZ7AUjjWe1tMSsdymzeafvtfsYcxenaI"
    "1Kk7Z8C+9eFwYzW6hJGkHtefgZC4iUiTH5EGnJS5eF7uQRcfmgEe3UVUJLlaL4Dk"
    "PgVYoUHb6lBL38q3Q4z26ADqxq6CCJJjkiwu7wL0js/wChObmvmSgB09Kp8WPrOJ"
    "k95Yr41/qQKBgCblXM8aYepUMtCZNXT/tgMWMYk8khXhCrMNIkHubrN9kfeiYtNG"
    "apKtqm4v4x51mxZsG2hKhm4c8CqzxnHtuDCcqv84tqhrHJ6G0Whxn0XJ7FIQUT3f"
    "x12ht6V7+lEFAQn9MkeHB0i6Pty3EknYjEAMGLfXeMUXp5vZs4EcQqCvAoGAcVyc"
    "FpG2BtVTGFD/OSuJlEpvzLMI6utOGpBmqHYGtGQgZikO1a680KjFOVME9AvQrkVO"
    "vPltInO5iwaarL7YDT6rEgaYKxptLTeRy+DDich5qIKx+bcuWN5Th5lgEeRoUyca"
    "lkBrRZduDm2hR6lh7hn3lb+QxMWdvF7PcdBLzHECgYAJeFJhatTkkcsFf6+hAo/x"
    "F/z+t8xSjP5qsnFdCrqxzLZb6E1OgKylc2xcs2LcVyxNe/u9HWH0z9lqQS6yPgmi"
    "kEii2/fjelJ2UhE6nUAcKPFLMtS3+CXJQYFVb1pnVxMFUaUqAnB21zyBzhIEX/5A"
    "3SxAz/jp0UJq7l+xaF80Kg=="
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
            logger.info(f"JetBrains 私钥加载成功 ({self.private_key.key_size} bits)")
        except Exception as e:
            logger.error(f"加载 JetBrains 私钥失败: {e}")
            self.private_key = None

    def sign(self, content: str) -> str:
        if self.private_key is None:
            logger.warning("JetBrains 私钥未加载，跳过签名")
            return ""
        try:
            from cryptography.hazmat.primitives import hashes
            from cryptography.hazmat.primitives.asymmetric import padding
            signature = self.private_key.sign(
                content.encode("utf-8"),
                padding.PKCS1v15(),
                hashes.SHA256()
            )
            b64 = base64.b64encode(signature).decode()
            logger.info(f"JetBrains 签名成功: {len(signature)} bytes, b64_len={len(b64)}")
            return b64
        except Exception as e:
            logger.error(f"JetBrains 签名失败: {e}")
            return ""


jetbrains_signer = JetBrainsSigner()
