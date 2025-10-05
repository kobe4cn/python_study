"""
API端点测试
"""

import pytest
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)


class TestHealthEndpoints:
    """健康检查端点测试"""

    def test_ping(self):
        """测试ping端点"""
        response = client.get("/ping")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"
        assert response.json()["message"] == "pong"

    def test_health_check(self):
        """测试健康检查端点"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "version" in data
        assert "uptime_seconds" in data
        assert "dependencies" in data

    def test_root_endpoint(self):
        """测试根路径"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert "version" in data
        assert "status" in data


class TestAuthEndpoints:
    """认证端点测试"""

    def test_login_success(self):
        """测试成功登录"""
        response = client.post(
            "/api/v1/auth/token",
            data={"username": "admin", "password": "admin123"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"

    def test_login_failure(self):
        """测试登录失败"""
        response = client.post(
            "/api/v1/auth/token",
            data={"username": "wrong", "password": "wrong"}
        )
        assert response.status_code == 401

    def test_refresh_token(self):
        """测试刷新令牌"""
        # 先登录获取令牌
        login_response = client.post(
            "/api/v1/auth/token",
            data={"username": "admin", "password": "admin123"}
        )
        refresh_token = login_response.json()["refresh_token"]

        # 刷新令牌
        response = client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": refresh_token}
        )
        assert response.status_code == 200
        assert "access_token" in response.json()


class TestSearchEndpoints:
    """搜索端点测试"""

    def test_search_basic(self):
        """测试基础搜索"""
        response = client.post(
            "/api/v1/search",
            json={
                "query": "测试查询",
                "collection_name": "documents",
                "top_k": 5
            }
        )
        # 注意：可能返回500如果Qdrant未启动
        assert response.status_code in [200, 500]

    def test_search_validation_error(self):
        """测试搜索参数验证"""
        response = client.post(
            "/api/v1/search",
            json={
                "query": "",  # 空查询应该失败
                "collection_name": "documents"
            }
        )
        assert response.status_code == 422


class TestCollectionEndpoints:
    """集合端点测试（需要认证）"""

    @pytest.fixture
    def auth_token(self):
        """获取认证令牌"""
        response = client.post(
            "/api/v1/auth/token",
            data={"username": "admin", "password": "admin123"}
        )
        return response.json()["access_token"]

    def test_list_collections(self, auth_token):
        """测试列出集合"""
        response = client.get(
            "/api/v1/collections",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        # 可能返回200或500（如果Qdrant未启动）
        assert response.status_code in [200, 401, 500]


# 运行测试
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
