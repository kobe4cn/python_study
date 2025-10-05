"""
JWT令牌管理
生成、验证和解析JWT令牌
"""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status
import logging

from api.config import settings

logger = logging.getLogger(__name__)

# 密码加密上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_access_token(
    data: Dict[str, Any], expires_delta: Optional[timedelta] = None
) -> str:
    """
    创建访问令牌

    Args:
        data: 要编码的数据
        expires_delta: 过期时间增量

    Returns:
        编码后的JWT令牌
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.access_token_expire_minutes
        )

    to_encode.update({"exp": expire, "iat": datetime.utcnow(), "type": "access"})

    try:
        encoded_jwt = jwt.encode(
            to_encode, settings.secret_key, algorithm=settings.algorithm
        )
        logger.debug(f"创建访问令牌成功: {data.get('sub', 'unknown')}")
        return encoded_jwt
    except Exception as e:
        logger.error(f"创建访问令牌失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="令牌创建失败"
        )


def create_refresh_token(
    data: Dict[str, Any], expires_delta: Optional[timedelta] = None
) -> str:
    """
    创建刷新令牌

    Args:
        data: 要编码的数据
        expires_delta: 过期时间增量

    Returns:
        编码后的JWT令牌
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=settings.refresh_token_expire_days)

    to_encode.update({"exp": expire, "iat": datetime.utcnow(), "type": "refresh"})

    try:
        encoded_jwt = jwt.encode(
            to_encode, settings.secret_key, algorithm=settings.algorithm
        )
        logger.debug(f"创建刷新令牌成功: {data.get('sub', 'unknown')}")
        return encoded_jwt
    except Exception as e:
        logger.error(f"创建刷新令牌失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="令牌创建失败"
        )


def verify_token(token: str, token_type: str = "access") -> Dict[str, Any]:
    """
    验证JWT令牌

    Args:
        token: JWT令牌
        token_type: 令牌类型 (access/refresh)

    Returns:
        解码后的令牌数据

    Raises:
        HTTPException: 令牌无效或过期
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无法验证凭据",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token, settings.secret_key, algorithms=[settings.algorithm]
        )

        # 验证令牌类型
        if payload.get("type") != token_type:
            logger.warning(
                f"令牌类型不匹配: 期望 {token_type}, 实际 {payload.get('type')}"
            )
            raise credentials_exception

        # 检查过期时间
        exp = payload.get("exp")
        if exp is None:
            raise credentials_exception

        if datetime.fromtimestamp(exp) < datetime.utcnow():
            logger.warning("令牌已过期")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="令牌已过期",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return payload

    except JWTError as e:
        logger.error(f"JWT解码失败: {e}")
        raise credentials_exception


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    验证密码

    Args:
        plain_password: 明文密码
        hashed_password: 哈希密码

    Returns:
        密码是否匹配
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    获取密码哈希

    Args:
        password: 明文密码

    Returns:
        哈希后的密码
    """
    return pwd_context.hash(password)


# 示例用户数据库（生产环境应使用真实数据库）
FAKE_USERS_DB = {
    "admin": {
        "username": "admin",
        "full_name": "管理员",
        "email": "admin@example.com",
        "hashed_password": get_password_hash("admin123"),
        "disabled": False,
    },
    "user": {
        "username": "user",
        "full_name": "普通用户",
        "email": "user@example.com",
        "hashed_password": get_password_hash("user123"),
        "disabled": False,
    },
}


def authenticate_user(username: str, password: str) -> Optional[Dict[str, Any]]:
    """
    认证用户

    Args:
        username: 用户名
        password: 密码

    Returns:
        用户信息或None
    """
    user = FAKE_USERS_DB.get(username)
    if not user:
        return None
    if not verify_password(password, user["hashed_password"]):  # type: ignore
        return None
    return user


if __name__ == "__main__":
    # 测试令牌创建和验证
    test_data = {"sub": "test_user", "role": "admin"}

    # 创建访问令牌
    access_token = create_access_token(test_data)
    print(f"访问令牌: {access_token}")

    # 验证令牌
    payload = verify_token(access_token, "access")
    print(f"令牌数据: {payload}")

    # 创建刷新令牌
    refresh_token = create_refresh_token(test_data)
    print(f"刷新令牌: {refresh_token}")
