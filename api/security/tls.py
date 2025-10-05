"""
TLS/SSL配置
HTTPS证书管理和配置
"""

from __future__ import annotations

import ssl
from typing import Optional, Dict, Any
from pathlib import Path
import logging

from api.config import settings

logger = logging.getLogger(__name__)


def create_ssl_context() -> Optional[ssl.SSLContext]:
    """
    创建SSL上下文

    Returns:
        SSL上下文或None（如果未启用HTTPS）
    """
    if not settings.use_https:
        logger.info("HTTPS未启用")
        return None

    if not settings.ssl_certfile or not settings.ssl_keyfile:
        logger.error("启用HTTPS但未提供证书文件")
        raise ValueError("启用HTTPS时必须提供ssl_certfile和ssl_keyfile")

    # 检查证书文件是否存在
    cert_path = Path(settings.ssl_certfile)
    key_path = Path(settings.ssl_keyfile)

    if not cert_path.exists():
        raise FileNotFoundError(f"证书文件不存在: {cert_path}")

    if not key_path.exists():
        raise FileNotFoundError(f"密钥文件不存在: {key_path}")

    # 创建SSL上下文
    try:
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)

        # 加载证书和密钥
        context.load_cert_chain(certfile=str(cert_path), keyfile=str(key_path))

        # 如果提供了CA证书
        if settings.ssl_ca_certs:
            ca_path = Path(settings.ssl_ca_certs)
            if ca_path.exists():
                context.load_verify_locations(cafile=str(ca_path))
            else:
                logger.warning(f"CA证书文件不存在: {ca_path}")

        # 设置证书验证要求
        context.verify_mode = ssl.VerifyMode(settings.ssl_cert_reqs)

        # 推荐的安全设置
        context.minimum_version = ssl.TLSVersion.TLSv1_2
        context.set_ciphers(
            "ECDHE+AESGCM:ECDHE+CHACHA20:DHE+AESGCM:DHE+CHACHA20:!aNULL:!MD5:!DSS"
        )

        logger.info(f"SSL上下文创建成功 - 证书: {cert_path}, 密钥: {key_path}")
        return context

    except Exception as e:
        logger.error(f"SSL上下文创建失败: {e}")
        raise


def get_uvicorn_ssl_config() -> Dict[str, Any]:
    """
    获取Uvicorn的SSL配置

    Returns:
        SSL配置字典
    """
    if not settings.use_https:
        return {}

    if not settings.ssl_certfile or not settings.ssl_keyfile:
        raise ValueError("启用HTTPS时必须提供ssl_certfile和ssl_keyfile")

    config = {
        "ssl_certfile": settings.ssl_certfile,
        "ssl_keyfile": settings.ssl_keyfile,
    }

    if settings.ssl_ca_certs:
        config["ssl_ca_certs"] = settings.ssl_ca_certs

    if settings.ssl_cert_reqs:
        config["ssl_cert_reqs"] = str(settings.ssl_cert_reqs)

    logger.info("Uvicorn SSL配置已生成")
    return config


def generate_self_signed_cert(
    cert_file: str = "cert.pem", key_file: str = "key.pem", days_valid: int = 365
) -> None:
    """
    生成自签名证书（仅用于开发环境）

    Args:
        cert_file: 证书文件路径
        key_file: 密钥文件路径
        days_valid: 证书有效期（天）

    Warning:
        自签名证书仅用于开发和测试，生产环境应使用正式CA签发的证书
    """
    try:
        from cryptography import x509
        from cryptography.x509.oid import NameOID
        from cryptography.hazmat.primitives import hashes
        from cryptography.hazmat.primitives.asymmetric import rsa
        from cryptography.hazmat.primitives import serialization
        from datetime import datetime, timedelta

        logger.warning("⚠️  正在生成自签名证书 - 仅用于开发环境！")

        # 生成私钥
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
        )

        # 创建证书
        subject = issuer = x509.Name(
            [
                x509.NameAttribute(NameOID.COUNTRY_NAME, "CN"),
                x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "Beijing"),
                x509.NameAttribute(NameOID.LOCALITY_NAME, "Beijing"),
                x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Document API"),
                x509.NameAttribute(NameOID.COMMON_NAME, "localhost"),
            ]
        )

        cert = (
            x509.CertificateBuilder()
            .subject_name(subject)
            .issuer_name(issuer)
            .public_key(private_key.public_key())
            .serial_number(x509.random_serial_number())
            .not_valid_before(datetime.utcnow())
            .not_valid_after(datetime.utcnow() + timedelta(days=days_valid))
            .add_extension(
                x509.SubjectAlternativeName(
                    [
                        x509.DNSName("localhost"),
                        x509.DNSName("127.0.0.1"),
                    ]
                ),
                critical=False,
            )
            .sign(private_key, hashes.SHA256())
        )

        # 保存私钥
        with open(key_file, "wb") as f:
            f.write(
                private_key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.TraditionalOpenSSL,
                    encryption_algorithm=serialization.NoEncryption(),
                )
            )

        # 保存证书
        with open(cert_file, "wb") as f:
            f.write(cert.public_bytes(serialization.Encoding.PEM))

        logger.info(
            f"自签名证书已生成: {cert_file}, {key_file} (有效期: {days_valid}天)"
        )

    except ImportError:
        logger.error("需要安装cryptography库才能生成自签名证书")
        raise
    except Exception as e:
        logger.error(f"生成自签名证书失败: {e}")
        raise


# 证书验证辅助函数
def verify_certificate(cert_file: str, key_file: str) -> bool:
    """
    验证证书和密钥是否匹配

    Args:
        cert_file: 证书文件路径
        key_file: 密钥文件路径

    Returns:
        是否匹配
    """
    try:
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context.load_cert_chain(certfile=cert_file, keyfile=key_file)
        logger.info("证书和密钥验证成功")
        return True
    except Exception as e:
        logger.error(f"证书验证失败: {e}")
        return False


if __name__ == "__main__":
    # 测试生成自签名证书
    generate_self_signed_cert("test_cert.pem", "test_key.pem")
    verify_certificate("test_cert.pem", "test_key.pem")
