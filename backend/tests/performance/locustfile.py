from locust import HttpUser, task, between, constant_throughput
from locust.env import Environment
from locust.stats import stats_printer, stats_history
from locust.log import setup_logging
import json
import random
import time

setup_logging("INFO", None)


class JudicialSystemUser(HttpUser):
    wait_time = between(1, 3)
    
    def on_start(self):
        self.login()
    
    def login(self):
        roles = ["ADMIN", "JUDGE", "LAWYER", "CLERK", "CITIZEN"]
        role = random.choice(roles)
        
        credentials = {
            "username": f"test_{role.lower()}_{random.randint(1, 100)}",
            "password": "Test123!@#"
        }
        
        response = self.client.post(
            "/api/auth/login",
            json=credentials,
            catch_response=True
        )
        
        if response.status_code == 200:
            data = response.json()
            self.token = data.get("access_token", "")
            self.headers = {"Authorization": f"Bearer {self.token}"}
            response.success()
        else:
            response.failure(f"Login failed: {response.status_code}")
    
    @task(10)
    def view_dashboard(self):
        self.client.get(
            "/api/dashboard",
            headers=self.headers,
            name="/api/dashboard"
        )
    
    @task(8)
    def list_cases(self):
        params = {
            "skip": random.randint(0, 100),
            "limit": 20
        }
        self.client.get(
            "/api/cases",
            params=params,
            headers=self.headers,
            name="/api/cases"
        )
    
    @task(5)
    def search_cases(self):
        search_terms = ["Juan", "Smith", "2024", "Penal", "Civil"]
        params = {"q": random.choice(search_terms)}
        
        self.client.get(
            "/api/cases/search",
            params=params,
            headers=self.headers,
            name="/api/cases/search"
        )
    
    @task(3)
    def view_case_detail(self):
        case_id = random.randint(1, 1000)
        self.client.get(
            f"/api/cases/{case_id}",
            headers=self.headers,
            name="/api/cases/[id]"
        )
    
    @task(2)
    def create_case(self):
        case_data = {
            "title": f"Caso Test {random.randint(1, 10000)}",
            "description": "Descripción de caso de prueba para testing de carga",
            "case_type": random.choice(["CIVIL", "PENAL", "LABORAL", "FAMILIAR"]),
            "status": "ABIERTO",
            "priority": random.choice(["BAJA", "MEDIA", "ALTA"])
        }
        
        self.client.post(
            "/api/cases",
            json=case_data,
            headers=self.headers,
            name="/api/cases [POST]"
        )
    
    @task(4)
    def view_documents(self):
        self.client.get(
            "/api/documents",
            headers=self.headers,
            name="/api/documents"
        )
    
    @task(3)
    def view_audit_logs(self):
        params = {
            "skip": 0,
            "limit": 50
        }
        self.client.get(
            "/api/audit/logs",
            params=params,
            headers=self.headers,
            name="/api/audit/logs"
        )
    
    @task(1)
    def health_check(self):
        self.client.get("/health", name="/health")


class AdminUser(HttpUser):
    wait_time = between(2, 5)
    
    def on_start(self):
        credentials = {
            "username": "admin",
            "password": "admin123"
        }
        
        response = self.client.post("/api/auth/login", json=credentials)
        if response.status_code == 200:
            data = response.json()
            self.token = data.get("access_token", "")
            self.headers = {"Authorization": f"Bearer {self.token}"}
    
    @task(5)
    def view_audit_dashboard(self):
        self.client.get(
            "/api/audit/stats",
            headers=self.headers,
            name="/api/audit/stats"
        )
    
    @task(3)
    def export_audit_logs(self):
        params = {"format": random.choice(["json", "csv"])}
        self.client.get(
            "/api/audit/export",
            params=params,
            headers=self.headers,
            name="/api/audit/export"
        )
    
    @task(2)
    def manage_users(self):
        self.client.get(
            "/api/users",
            headers=self.headers,
            name="/api/users"
        )


class JudgeUser(HttpUser):
    wait_time = between(3, 6)
    
    def on_start(self):
        credentials = {
            "username": "judge1",
            "password": "judge123"
        }
        
        response = self.client.post("/api/auth/login", json=credentials)
        if response.status_code == 200:
            data = response.json()
            self.token = data.get("access_token", "")
            self.headers = {"Authorization": f"Bearer {self.token}"}
    
    @task(10)
    def view_assigned_cases(self):
        params = {"assigned_to_me": True}
        self.client.get(
            "/api/cases",
            params=params,
            headers=self.headers,
            name="/api/cases [assigned]"
        )
    
    @task(5)
    def update_case_status(self):
        case_id = random.randint(1, 100)
        update_data = {
            "status": random.choice(["EN_PROCESO", "RESUELTO", "ARCHIVADO"])
        }
        
        self.client.put(
            f"/api/cases/{case_id}",
            json=update_data,
            headers=self.headers,
            name="/api/cases/[id] [PUT]"
        )
    
    @task(3)
    def sign_document(self):
        doc_id = random.randint(1, 500)
        self.client.post(
            f"/api/documents/{doc_id}/sign",
            headers=self.headers,
            name="/api/documents/[id]/sign"
        )


class LawyerUser(HttpUser):
    wait_time = between(2, 4)
    
    def on_start(self):
        credentials = {
            "username": f"lawyer{random.randint(1, 50)}",
            "password": "lawyer123"
        }
        
        response = self.client.post("/api/auth/login", json=credentials)
        if response.status_code == 200:
            data = response.json()
            self.token = data.get("access_token", "")
            self.headers = {"Authorization": f"Bearer {self.token}"}
    
    @task(8)
    def view_client_cases(self):
        self.client.get(
            "/api/cases",
            headers=self.headers,
            name="/api/cases [lawyer]"
        )
    
    @task(5)
    def upload_document(self):
        files = {
            'file': ('test_document.pdf', b'PDF content here', 'application/pdf')
        }
        data = {
            'case_id': random.randint(1, 100),
            'document_type': random.choice(['EVIDENCE', 'MOTION', 'BRIEF'])
        }
        
        self.client.post(
            "/api/documents/upload",
            files=files,
            data=data,
            headers=self.headers,
            name="/api/documents/upload"
        )
    
    @task(3)
    def view_case_documents(self):
        case_id = random.randint(1, 100)
        self.client.get(
            f"/api/cases/{case_id}/documents",
            headers=self.headers,
            name="/api/cases/[id]/documents"
        )
