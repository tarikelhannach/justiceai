# backend/app/monitoring/performance_monitor.py - Monitor de Performance

import time
import psutil
import logging
import asyncio
from typing import Dict, Any, List
from datetime import datetime, timedelta
from collections import deque
import redis
import json

from ..config import settings

logger = logging.getLogger(__name__)

class PerformanceMonitor:
    """
    Monitor de performance en tiempo real
    Rastrea métricas del sistema y aplicación
    """
    
    def __init__(self):
        self.redis_client = redis.from_url(settings.redis_url)
        self.metrics_history = deque(maxlen=1000)  # Últimas 1000 métricas
        self.alert_thresholds = {
            "cpu_percent": 80.0,
            "memory_percent": 85.0,
            "disk_percent": 90.0,
            "response_time": 2.0,  # segundos
            "error_rate": 5.0  # porcentaje
        }
        self.is_monitoring = False
        self.monitor_task = None
    
    async def start_monitoring(self, interval: int = 30):
        """Iniciar monitoreo continuo"""
        try:
            if self.is_monitoring:
                logger.warning("Performance monitoring already running")
                return
            
            self.is_monitoring = True
            self.monitor_task = asyncio.create_task(
                self._monitoring_loop(interval)
            )
            
            logger.info("Performance monitoring started")
            
        except Exception as e:
            logger.error(f"Error starting performance monitoring: {e}")
            self.is_monitoring = False
    
    async def stop_monitoring(self):
        """Detener monitoreo"""
        try:
            self.is_monitoring = False
            if self.monitor_task:
                self.monitor_task.cancel()
                try:
                    await self.monitor_task
                except asyncio.CancelledError:
                    pass
            
            logger.info("Performance monitoring stopped")
            
        except Exception as e:
            logger.error(f"Error stopping performance monitoring: {e}")
    
    async def _monitoring_loop(self, interval: int):
        """Loop principal de monitoreo"""
        while self.is_monitoring:
            try:
                # Recopilar métricas
                metrics = await self._collect_metrics()
                
                # Guardar métricas
                await self._store_metrics(metrics)
                
                # Verificar alertas
                await self._check_alerts(metrics)
                
                # Esperar intervalo
                await asyncio.sleep(interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(interval)
    
    async def _collect_metrics(self) -> Dict[str, Any]:
        """Recopilar métricas del sistema"""
        try:
            # Métricas del sistema
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Métricas de red
            net_io = psutil.net_io_counters()
            
            # Métricas de procesos
            process = psutil.Process()
            process_memory = process.memory_info()
            process_cpu = process.cpu_percent()
            
            # Métricas de base de datos (si está disponible)
            db_metrics = await self._get_database_metrics()
            
            # Métricas de Redis
            redis_metrics = await self._get_redis_metrics()
            
            # Métricas de aplicación
            app_metrics = await self._get_application_metrics()
            
            return {
                "timestamp": datetime.utcnow().isoformat(),
                "system": {
                    "cpu_percent": cpu_percent,
                    "memory_percent": memory.percent,
                    "memory_used_gb": memory.used / (1024**3),
                    "memory_available_gb": memory.available / (1024**3),
                    "disk_percent": disk.percent,
                    "disk_used_gb": disk.used / (1024**3),
                    "disk_free_gb": disk.free / (1024**3),
                    "load_average": psutil.getloadavg()[0] if hasattr(psutil, 'getloadavg') else 0,
                    "uptime_seconds": time.time() - psutil.boot_time()
                },
                "network": {
                    "bytes_sent": net_io.bytes_sent,
                    "bytes_recv": net_io.bytes_recv,
                    "packets_sent": net_io.packets_sent,
                    "packets_recv": net_io.packets_recv
                },
                "process": {
                    "cpu_percent": process_cpu,
                    "memory_rss_mb": process_memory.rss / (1024**2),
                    "memory_vms_mb": process_memory.vms / (1024**2),
                    "num_threads": process.num_threads(),
                    "num_fds": process.num_fds() if hasattr(process, 'num_fds') else 0
                },
                "database": db_metrics,
                "redis": redis_metrics,
                "application": app_metrics
            }
            
        except Exception as e:
            logger.error(f"Error collecting metrics: {e}")
            return {"timestamp": datetime.utcnow().isoformat(), "error": str(e)}
    
    async def _get_database_metrics(self) -> Dict[str, Any]:
        """Obtener métricas de base de datos"""
        try:
            # Aquí se implementaría la conexión a la base de datos
            # para obtener métricas específicas
            return {
                "connections": 0,
                "active_queries": 0,
                "slow_queries": 0,
                "cache_hit_ratio": 0.0
            }
        except Exception as e:
            logger.error(f"Error getting database metrics: {e}")
            return {}
    
    async def _get_redis_metrics(self) -> Dict[str, Any]:
        """Obtener métricas de Redis"""
        try:
            info = self.redis_client.info()
            return {
                "used_memory_mb": info.get("used_memory", 0) / (1024**2),
                "connected_clients": info.get("connected_clients", 0),
                "keyspace_hits": info.get("keyspace_hits", 0),
                "keyspace_misses": info.get("keyspace_misses", 0),
                "evicted_keys": info.get("evicted_keys", 0),
                "expired_keys": info.get("expired_keys", 0)
            }
        except Exception as e:
            logger.error(f"Error getting Redis metrics: {e}")
            return {}
    
    async def _get_application_metrics(self) -> Dict[str, Any]:
        """Obtener métricas de aplicación"""
        try:
            # Métricas de requests (si están disponibles)
            return {
                "requests_per_second": 0,
                "average_response_time": 0.0,
                "error_rate": 0.0,
                "active_connections": 0
            }
        except Exception as e:
            logger.error(f"Error getting application metrics: {e}")
            return {}
    
    async def _store_metrics(self, metrics: Dict[str, Any]):
        """Guardar métricas en Redis"""
        try:
            # Agregar a historial en memoria
            self.metrics_history.append(metrics)
            
            # Guardar en Redis para persistencia
            timestamp = metrics["timestamp"]
            self.redis_client.setex(
                f"metrics:{timestamp}",
                3600,  # 1 hora
                json.dumps(metrics)
            )
            
            # Mantener solo últimas 100 métricas en Redis
            await self._cleanup_old_metrics()
            
        except Exception as e:
            logger.error(f"Error storing metrics: {e}")
    
    async def _cleanup_old_metrics(self):
        """Limpiar métricas antiguas"""
        try:
            # Obtener todas las claves de métricas
            metric_keys = self.redis_client.keys("metrics:*")
            
            if len(metric_keys) > 100:
                # Ordenar por timestamp y eliminar las más antiguas
                metric_keys.sort()
                keys_to_delete = metric_keys[:-100]
                
                if keys_to_delete:
                    self.redis_client.delete(*keys_to_delete)
                    
        except Exception as e:
            logger.error(f"Error cleaning up old metrics: {e}")
    
    async def _check_alerts(self, metrics: Dict[str, Any]):
        """Verificar alertas basadas en métricas"""
        try:
            alerts = []
            
            # Verificar CPU
            cpu_percent = metrics.get("system", {}).get("cpu_percent", 0)
            if cpu_percent > self.alert_thresholds["cpu_percent"]:
                alerts.append({
                    "type": "cpu_high",
                    "message": f"CPU usage is {cpu_percent:.1f}%",
                    "value": cpu_percent,
                    "threshold": self.alert_thresholds["cpu_percent"]
                })
            
            # Verificar memoria
            memory_percent = metrics.get("system", {}).get("memory_percent", 0)
            if memory_percent > self.alert_thresholds["memory_percent"]:
                alerts.append({
                    "type": "memory_high",
                    "message": f"Memory usage is {memory_percent:.1f}%",
                    "value": memory_percent,
                    "threshold": self.alert_thresholds["memory_percent"]
                })
            
            # Verificar disco
            disk_percent = metrics.get("system", {}).get("disk_percent", 0)
            if disk_percent > self.alert_thresholds["disk_percent"]:
                alerts.append({
                    "type": "disk_high",
                    "message": f"Disk usage is {disk_percent:.1f}%",
                    "value": disk_percent,
                    "threshold": self.alert_thresholds["disk_percent"]
                })
            
            # Enviar alertas si las hay
            if alerts:
                await self._send_alerts(alerts)
                
        except Exception as e:
            logger.error(f"Error checking alerts: {e}")
    
    async def _send_alerts(self, alerts: List[Dict[str, Any]]):
        """Enviar alertas"""
        try:
            for alert in alerts:
                # Log de alerta
                logger.warning(f"ALERT: {alert['message']}")
                
                # Guardar en Redis para procesamiento
                alert_data = {
                    "timestamp": datetime.utcnow().isoformat(),
                    "alert": alert
                }
                
                self.redis_client.lpush(
                    "alerts:queue",
                    json.dumps(alert_data)
                )
                
        except Exception as e:
            logger.error(f"Error sending alerts: {e}")
    
    async def get_metrics_summary(self, hours: int = 1) -> Dict[str, Any]:
        """Obtener resumen de métricas"""
        try:
            # Obtener métricas de las últimas N horas
            cutoff_time = datetime.utcnow() - timedelta(hours=hours)
            
            recent_metrics = [
                m for m in self.metrics_history
                if datetime.fromisoformat(m["timestamp"]) > cutoff_time
            ]
            
            if not recent_metrics:
                return {"error": "No metrics available"}
            
            # Calcular promedios
            cpu_values = [m.get("system", {}).get("cpu_percent", 0) for m in recent_metrics]
            memory_values = [m.get("system", {}).get("memory_percent", 0) for m in recent_metrics]
            disk_values = [m.get("system", {}).get("disk_percent", 0) for m in recent_metrics]
            
            return {
                "period_hours": hours,
                "sample_count": len(recent_metrics),
                "averages": {
                    "cpu_percent": sum(cpu_values) / len(cpu_values) if cpu_values else 0,
                    "memory_percent": sum(memory_values) / len(memory_values) if memory_values else 0,
                    "disk_percent": sum(disk_values) / len(disk_values) if disk_values else 0
                },
                "maximums": {
                    "cpu_percent": max(cpu_values) if cpu_values else 0,
                    "memory_percent": max(memory_values) if memory_values else 0,
                    "disk_percent": max(disk_values) if disk_values else 0
                },
                "current": recent_metrics[-1] if recent_metrics else {}
            }
            
        except Exception as e:
            logger.error(f"Error getting metrics summary: {e}")
            return {"error": str(e)}
    
    def get_current_metrics(self) -> Dict[str, Any]:
        """Obtener métricas actuales"""
        try:
            if self.metrics_history:
                return self.metrics_history[-1]
            else:
                return {"error": "No metrics available"}
        except Exception as e:
            logger.error(f"Error getting current metrics: {e}")
            return {"error": str(e)}
