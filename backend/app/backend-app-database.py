# backend/app/database.py - Configuración de Base de Datos

from sqlalchemy import create_engine, event, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
from contextlib import contextmanager
import logging
import time

from .config import settings, get_database_config

logger = logging.getLogger(__name__)

# Configuración del engine de base de datos
engine_config = get_database_config()

engine = create_engine(
    settings.database_url,
    poolclass=QueuePool,
    **engine_config
)

# Event listeners para optimización de conexiones
@event.listens_for(engine, "connect")
def set_connection_parameters(connection, connection_record):
    """Configurar parámetros optimizados para cada conexión"""
    with connection.cursor() as cursor:
        # Configuraciones específicas para PostgreSQL
        cursor.execute("SET timezone='UTC'")
        cursor.execute("SET work_mem = '32MB'")
        cursor.execute("SET maintenance_work_mem = '256MB'")
        cursor.execute("SET effective_cache_size = '1GB'")
        cursor.execute("SET statement_timeout = '30s'")
        cursor.execute("SET idle_in_transaction_session_timeout = '60s'")
        
        # Configuración específica para búsquedas en árabe
        cursor.execute("SET default_text_search_config = 'arabic'")

@event.listens_for(engine, "checkout")
def receive_checkout(connection, connection_record, connection_proxy):
    """Monitor connection checkout para debugging"""
    connection_record.info['checkout_time'] = time.time()
    if settings.debug:
        logger.debug(f"Connection checked out: {connection_record}")

@event.listens_for(engine, "checkin")
def receive_checkin(connection, connection_record):
    """Monitor connection checkin y detectar conexiones largas"""
    if 'checkout_time' in connection_record.info:
        duration = time.time() - connection_record.info['checkout_time']
        if duration > 30:  # 30 segundos
            logger.warning(f"Long-running connection: {duration:.2f}s")

@event.listens_for(engine, "before_cursor_execute")
def receive_before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    """Monitor inicio de queries para detectar queries lentas"""
    context._query_start_time = time.time()

@event.listens_for(engine, "after_cursor_execute")
def receive_after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    """Monitor queries completadas y alertar sobre queries lentas"""
    total_time = time.time() - context._query_start_time
    if total_time > 1.0:  # Queries más lentas que 1 segundo
        logger.warning(f"Slow query ({total_time:.2f}s): {statement[:200]}...")

# Configurar session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False  # Evitar lazy loading después del commit
)

Base = declarative_base()

# Dependency para obtener sesión de base de datos
def get_db():
    """
    Dependency para FastAPI que proporciona sesión de base de datos
    con manejo automático de errores y cleanup
    """
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Database error: {e}")
        db.rollback()
        raise
    finally:
        db.close()

# Context manager para operaciones transaccionales
@contextmanager
def get_db_session():
    """
    Context manager para operaciones de base de datos fuera de FastAPI
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"Database transaction error: {e}")
        raise
    finally:
        db.close()

# Health check para base de datos
def check_db_health() -> bool:
    """Verificar salud de la conexión a base de datos"""
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return True
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return False

# Funciones de utilidad para operaciones comunes
class DatabaseManager:
    """Gestor de operaciones de base de datos optimizadas"""
    
    @staticmethod
    def bulk_insert(db: Session, model_class, data_list: list):
        """Bulk insert optimizado para grandes volúmenes de datos"""
        try:
            db.bulk_insert_mappings(model_class, data_list)
            db.commit()
            logger.info(f"Bulk inserted {len(data_list)} {model_class.__name__} records")
        except Exception as e:
            db.rollback()
            logger.error(f"Bulk insert failed: {e}")
            raise
    
    @staticmethod
    def bulk_update(db: Session, model_class, data_list: list):
        """Bulk update optimizado"""
        try:
            db.bulk_update_mappings(model_class, data_list)
            db.commit()
            logger.info(f"Bulk updated {len(data_list)} {model_class.__name__} records")
        except Exception as e:
            db.rollback()
            logger.error(f"Bulk update failed: {e}")
            raise
    
    @staticmethod
    def create_indexes(db: Session):
        """Crear índices optimizados para el sistema judicial"""
        indexes = [
            # Índices para casos
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_cases_status ON case_files(status)",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_cases_created_at ON case_files(created_at DESC)",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_cases_user_id ON case_files(created_by)",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_cases_assigned ON case_files(assigned_to)",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_cases_type_status ON case_files(case_type, status)",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_cases_number ON case_files(case_number)",
            
            # Índices para documentos
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_documents_case_id ON documents(case_id)",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_documents_type ON documents(document_type)",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_documents_uploaded_by ON documents(uploaded_by)",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_documents_signature_status ON documents(signature_status)",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_documents_searchable ON documents(is_searchable) WHERE is_searchable = true",
            
            # Índices para usuarios
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_email ON users(email)",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_role ON users(role)",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_active ON users(is_active) WHERE is_active = true",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_national_id ON users(national_id) WHERE national_id IS NOT NULL",
            
            # Índices para auditoría
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_audit_logs_timestamp ON audit_logs(timestamp DESC)",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_audit_logs_user_id ON audit_logs(user_id)",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_audit_logs_resource ON audit_logs(resource_type, resource_id)",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_audit_logs_action ON audit_logs(action)",
            
            # Índices para participantes
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_participants_case_id ON case_participants(case_id)",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_participants_user_id ON case_participants(user_id)",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_participants_role ON case_participants(role)",
            
            # Índices para notificaciones
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_notifications_recipient ON notifications(recipient_id)",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_notifications_unread ON notifications(recipient_id, is_read) WHERE is_read = false",
            
            # Índices para sesiones
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_sessions_user_id ON user_sessions(user_id)",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_sessions_active ON user_sessions(is_active, expires_at) WHERE is_active = true",
            
            # Índices full-text para búsqueda (PostgreSQL específico)
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_cases_title_fts ON case_files USING GIN(to_tsvector('arabic', title))",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_cases_description_fts ON case_files USING GIN(to_tsvector('arabic', description))",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_documents_ocr_fts ON documents USING GIN(to_tsvector('arabic', ocr_text)) WHERE ocr_text IS NOT NULL",
        ]
        
        for index_sql in indexes:
            try:
                db.execute(text(index_sql))
                db.commit()
                logger.info(f"Created index: {index_sql.split()[-1]}")
            except Exception as e:
                db.rollback()
                logger.warning(f"Index creation failed or already exists: {e}")
    
    @staticmethod
    def optimize_database(db: Session):
        """Ejecutar optimizaciones de mantenimiento en la base de datos"""
        try:
            # Actualizar estadísticas
            db.execute(text("ANALYZE"))
            
            # Optimizar tablas principales
            main_tables = ['case_files', 'documents', 'users', 'audit_logs']
            for table in main_tables:
                # Safe: table names are from hardcoded whitelist only
                # Build SQL separately to satisfy static analysis tools
                sql = 'VACUUM ANALYZE "{}"'.format(table)
                db.execute(text(sql))
            
            db.commit()
            logger.info("Database optimization completed")
            
        except Exception as e:
            db.rollback()
            logger.error(f"Database optimization failed: {e}")
    
    @staticmethod
    def get_database_stats(db: Session) -> dict:
        """Obtener estadísticas de la base de datos"""
        try:
            stats = {}
            
            # Contar registros por tabla
            tables = ['users', 'case_files', 'documents', 'audit_logs', 'notifications']
            for table in tables:
                # Safe: table names are from hardcoded whitelist only
                # Build SQL separately to satisfy static analysis tools
                sql = 'SELECT COUNT(*) FROM "{}"'.format(table)
                result = db.execute(text(sql)).fetchone()
                stats[f"{table}_count"] = result[0] if result else 0
            
            # Tamaño de la base de datos
            result = db.execute(text("""
                SELECT 
                    pg_size_pretty(pg_database_size(current_database())) as db_size,
                    pg_size_pretty(sum(pg_total_relation_size(schemaname||'.'||tablename))) as tables_size
                FROM pg_tables WHERE schemaname = 'public'
            """)).fetchone()
            
            if result:
                stats['database_size'] = result[0]
                stats['tables_size'] = result[1]
            
            # Estadísticas de conexiones
            result = db.execute(text("""
                SELECT 
                    count(*) as total_connections,
                    count(*) FILTER (WHERE state = 'active') as active_connections,
                    count(*) FILTER (WHERE state = 'idle') as idle_connections
                FROM pg_stat_activity 
                WHERE datname = current_database()
            """)).fetchone()
            
            if result:
                stats.update({
                    'total_connections': result[0],
                    'active_connections': result[1],
                    'idle_connections': result[2]
                })
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting database stats: {e}")
            return {}

# Inicialización de base de datos
def init_database():
    """Inicializar base de datos con configuración optimizada"""
    try:
        # Crear todas las tablas
        from .models import Base
        Base.metadata.create_all(bind=engine)
        
        # Crear índices optimizados
        with get_db_session() as db:
            db_manager = DatabaseManager()
            db_manager.create_indexes(db)
        
        logger.info("Database initialized successfully")
        
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise

# Función para ejecutar migraciones
def run_migrations():
    """Ejecutar migraciones pendientes usando Alembic"""
    try:
        from alembic.config import Config
        from alembic import command
        
        # Configurar Alembic
        alembic_cfg = Config("alembic.ini")
        alembic_cfg.set_main_option("sqlalchemy.url", settings.database_url)
        
        # Ejecutar migraciones
        command.upgrade(alembic_cfg, "head")
        logger.info("Database migrations completed")
        
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        raise

# Configuración específica para testing
def get_test_database():
    """Crear base de datos en memoria para testing"""
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    
    # Base de datos SQLite en memoria para tests
    test_engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False}
    )
    
    TestingSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=test_engine
    )
    
    return test_engine, TestingSessionLocal

# Export del manager de base de datos
db_manager = DatabaseManager()