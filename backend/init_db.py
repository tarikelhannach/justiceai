#!/usr/bin/env python3
"""
Script para inicializar la base de datos y crear datos de demo
"""
import sys
import os
from passlib.context import CryptContext

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.app.database import engine
from backend.app.models import Base, User, Case, Document, AuditLog, UserRole, CaseStatus
from backend.app.database import SessionLocal

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def init_database():
    """Crear todas las tablas"""
    print("Creando tablas en la base de datos...")
    Base.metadata.create_all(bind=engine)
    print("✅ Tablas creadas exitosamente")

def create_demo_data():
    """Crear datos de demostración"""
    db = SessionLocal()
    
    try:
        # Verificar si ya existen usuarios
        existing_user = db.query(User).first()
        if existing_user:
            print("⚠️  Los datos de demo ya existen, saltando...")
            return
        
        print("Creando datos de demostración...")
        
        # Crear usuarios (contraseñas acortadas para evitar límite de bcrypt)
        admin = User(
            email="admin@justicia.ma",
            name="Administrador del Sistema",
            hashed_password=pwd_context.hash("admin123"[:72]),
            role=UserRole.ADMIN,
            is_active=True,
            is_verified=True
        )
        
        judge = User(
            email="juez@justicia.ma",
            name="Juez Mohamed Al-Fassi",
            hashed_password=pwd_context.hash("juez123"[:72]),
            role=UserRole.JUDGE,
            is_active=True,
            is_verified=True
        )
        
        lawyer = User(
            email="abogado@justicia.ma",
            name="Abogado Fatima Zahra",
            hashed_password=pwd_context.hash("abogado123"[:72]),
            role=UserRole.LAWYER,
            is_active=True,
            is_verified=True
        )
        
        clerk = User(
            email="secretario@justicia.ma",
            name="Secretario Ahmed Ben",
            hashed_password=pwd_context.hash("secretario123"[:72]),
            role=UserRole.CLERK,
            is_active=True,
            is_verified=True
        )
        
        db.add_all([admin, judge, lawyer, clerk])
        db.commit()
        
        # Crear casos de ejemplo
        cases = [
            Case(
                case_number="MAR-2025-001",
                title="Caso de Propiedad Comercial",
                description="Disputa sobre derechos de propiedad comercial en Casablanca",
                status=CaseStatus.IN_PROGRESS,
                owner_id=lawyer.id,
                assigned_judge_id=judge.id
            ),
            Case(
                case_number="MAR-2025-002",
                title="Caso Laboral - Despido Improcedente",
                description="Reclamación por despido improcedente en empresa de Rabat",
                status=CaseStatus.PENDING,
                owner_id=lawyer.id
            ),
            Case(
                case_number="MAR-2025-003",
                title="Caso de Herencia Familiar",
                description="División de herencia familiar en Marrakech",
                status=CaseStatus.RESOLVED,
                owner_id=lawyer.id,
                assigned_judge_id=judge.id
            ),
        ]
        
        db.add_all(cases)
        db.commit()
        
        # Crear logs de auditoría
        audit_logs = [
            AuditLog(
                user_id=admin.id,
                action="login",
                resource_type="auth",
                status="success",
                ip_address="192.168.1.1"
            ),
            AuditLog(
                user_id=judge.id,
                action="update_case",
                resource_type="case",
                resource_id=1,
                status="success",
                ip_address="192.168.1.2"
            ),
            AuditLog(
                user_id=lawyer.id,
                action="create_case",
                resource_type="case",
                resource_id=2,
                status="success",
                ip_address="192.168.1.3"
            ),
        ]
        
        db.add_all(audit_logs)
        db.commit()
        
        print("✅ Datos de demostración creados exitosamente")
        print("\n📊 Usuarios creados:")
        print("   - admin@justicia.ma (contraseña: admin123)")
        print("   - juez@justicia.ma (contraseña: juez123)")
        print("   - abogado@justicia.ma (contraseña: abogado123)")
        print("   - secretario@justicia.ma (contraseña: secretario123)")
        print(f"\n📋 Casos creados: {len(cases)}")
        
    except Exception as e:
        print(f"❌ Error creando datos de demo: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    init_database()
    create_demo_data()
    print("\n✅ Base de datos inicializada correctamente")
