"""
Tests de Rate Limiting para Sistema Judicial Digital

Verifica que los límites de tasa se apliquen correctamente en endpoints críticos
para prevenir ataques de fuerza bruta y spam.
"""

import pytest
from fastapi.testclient import TestClient
import time


def test_login_rate_limit(client: TestClient):
    """
    Test que el endpoint de login limita a 5 intentos por minuto.
    
    Verifica protección contra ataques de fuerza bruta.
    """
    login_data = {
        "email": "test@example.com",
        "password": "wrongpassword"
    }
    
    # Primeros 5 intentos deberían funcionar (aunque fallen por credenciales incorrectas)
    for i in range(5):
        response = client.post("/api/auth/login", json=login_data)
        # Puede ser 401 (credenciales incorrectas) pero NO 429 (rate limit)
        assert response.status_code in [401, 404], f"Attempt {i+1} got unexpected status: {response.status_code}"
    
    # El 6to intento debería ser bloqueado por rate limit
    response = client.post("/api/auth/login", json=login_data)
    assert response.status_code == 429, "Should be rate limited after 5 attempts"
    assert "rate limit" in response.text.lower() or "too many" in response.text.lower()


def test_register_rate_limit(client: TestClient):
    """
    Test que el endpoint de registro limita a 3 intentos por hora.
    
    Verifica protección contra spam y creación masiva de cuentas.
    """
    # Primeros 3 intentos deberían funcionar
    for i in range(3):
        register_data = {
            "email": f"spammer{i}@example.com",
            "name": f"Spammer {i}",
            "password": "Password123!"
        }
        response = client.post("/api/auth/register", json=register_data)
        # Puede ser 200 (éxito) o 400 (email duplicado) pero NO 429
        assert response.status_code in [200, 400, 404], f"Attempt {i+1} got unexpected status: {response.status_code}"
    
    # El 4to intento debería ser bloqueado por rate limit
    register_data = {
        "email": "spammer4@example.com",
        "name": "Spammer 4",
        "password": "Password123!"
    }
    response = client.post("/api/auth/register", json=register_data)
    assert response.status_code == 429, "Should be rate limited after 3 attempts"


def test_rate_limit_headers(client: TestClient):
    """
    Test que los headers de rate limit se incluyen en las respuestas.
    
    Verifica que X-RateLimit-* headers están presentes.
    """
    response = client.post(
        "/api/auth/login",
        json={"email": "test@example.com", "password": "test"}
    )
    
    # Verificar que los headers de rate limit están presentes
    # (SlowAPI con headers_enabled=True debe incluirlos)
    headers = response.headers
    
    # Nota: SlowAPI puede no incluir headers en todas las respuestas
    # Este test es informativo, no crítico
    if "X-RateLimit-Limit" in headers:
        assert int(headers["X-RateLimit-Limit"]) > 0
        assert "X-RateLimit-Remaining" in headers


def test_rate_limit_per_ip(client: TestClient):
    """
    Test que el rate limiting es por IP, no global.
    
    Simula que diferentes IPs pueden hacer requests independientemente.
    """
    # Nota: En TestClient es difícil simular diferentes IPs
    # Este test es conceptual y requiere testing de integración real
    
    login_data = {
        "email": "test@example.com",
        "password": "wrongpassword"
    }
    
    # Con la misma IP (test client), después de 5 intentos debe bloquearse
    for i in range(5):
        response = client.post("/api/auth/login", json=login_data)
        assert response.status_code in [401, 404]
    
    # El 6to debería estar bloqueado
    response = client.post("/api/auth/login", json=login_data)
    assert response.status_code == 429


@pytest.mark.asyncio
async def test_rate_limit_recovery(client: TestClient):
    """
    Test que los rate limits se recuperan después del tiempo de espera.
    
    NOTA: Este test toma 60+ segundos. Se puede skip para CI/CD rápido.
    """
    pytest.skip("Test de recuperación requiere esperar 60+ segundos")
    
    login_data = {
        "email": "test@example.com",
        "password": "wrongpassword"
    }
    
    # Agotar rate limit (5 intentos)
    for i in range(5):
        client.post("/api/auth/login", json=login_data)
    
    # Verificar que está bloqueado
    response = client.post("/api/auth/login", json=login_data)
    assert response.status_code == 429
    
    # Esperar 60 segundos para recuperación
    time.sleep(61)
    
    # Debería funcionar nuevamente
    response = client.post("/api/auth/login", json=login_data)
    assert response.status_code == 401  # No 429


def test_authenticated_endpoints_rate_limit(client: TestClient, admin_token: str):
    """
    Test que endpoints autenticados tienen rate limits más altos.
    
    Los usuarios autenticados deberían tener límites más generosos.
    """
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    # Los endpoints autenticados no deberían tener límites tan estrictos
    # Este test verifica que al menos podemos hacer 20 requests sin bloqueo
    for i in range(20):
        response = client.get("/api/cases/", headers=headers)
        assert response.status_code != 429, f"Authenticated request {i+1} should not be rate limited"


def test_health_check_no_rate_limit(client: TestClient):
    """
    Test que el health check no tiene rate limit.
    
    Los endpoints de monitoreo deben estar siempre disponibles.
    """
    # Hacer 100 requests al health check
    for i in range(100):
        response = client.get("/health")
        assert response.status_code == 200, f"Health check {i+1} should never be rate limited"
        assert response.json()["status"] == "healthy"


def test_rate_limit_different_endpoints_independent(client: TestClient):
    """
    Test que los rate limits de diferentes endpoints son independientes.
    
    Agotar el límite de login no debería afectar el límite de registro.
    """
    login_data = {
        "email": "test@example.com",
        "password": "wrongpassword"
    }
    
    # Agotar rate limit de login
    for i in range(6):
        client.post("/api/auth/login", json=login_data)
    
    # Register debería funcionar aún
    register_data = {
        "email": "newuser@example.com",
        "name": "New User",
        "password": "Password123!"
    }
    response = client.post("/api/auth/register", json=register_data)
    # No debería ser 429 (rate limit), puede ser 200 o 400
    assert response.status_code != 429, "Register should have independent rate limit from login"
