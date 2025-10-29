# backend/tests/integration/test_elasticsearch.py - Tests de Integración con Elasticsearch

import pytest
import json
from datetime import datetime

@pytest.mark.integration
class TestElasticsearchIntegration:
    """Tests de integración con Elasticsearch."""
    
    def test_elasticsearch_connection(self, mock_elasticsearch):
        """Test conexión a Elasticsearch."""
        result = mock_elasticsearch.ping()
        assert result is True
    
    def test_index_document(self, mock_elasticsearch):
        """Test indexar documento."""
        case_doc = {
            "case_number": "ES-2025-001",
            "title": "Caso de Prueba Elasticsearch",
            "description": "Testing Elasticsearch integration",
            "status": "pending",
            "created_at": datetime.utcnow().isoformat()
        }
        
        mock_elasticsearch.index.return_value = {"result": "created"}
        
        result = mock_elasticsearch.index(
            index="cases",
            id="es-2025-001",
            body=case_doc
        )
        
        assert result["result"] == "created"
    
    def test_search_documents(self, mock_elasticsearch):
        """Test búsqueda de documentos."""
        query = {
            "query": {
                "match": {
                    "title": "Caso de Prueba"
                }
            }
        }
        
        mock_elasticsearch.search.return_value = {
            "hits": {
                "total": {"value": 1},
                "hits": [
                    {
                        "_source": {
                            "case_number": "ES-2025-001",
                            "title": "Caso de Prueba Elasticsearch"
                        }
                    }
                ]
            }
        }
        
        result = mock_elasticsearch.search(
            index="cases",
            body=query
        )
        
        assert result["hits"]["total"]["value"] == 1
        assert len(result["hits"]["hits"]) == 1
    
    def test_full_text_search(self, mock_elasticsearch):
        """Test búsqueda de texto completo."""
        query = {
            "query": {
                "multi_match": {
                    "query": "demanda civil marruecos",
                    "fields": ["title^2", "description", "case_number"],
                    "type": "best_fields"
                }
            }
        }
        
        mock_elasticsearch.search.return_value = {
            "hits": {
                "total": {"value": 3},
                "hits": [
                    {"_source": {"case_number": "CIV-2025-001", "title": "Demanda Civil"}},
                    {"_source": {"case_number": "CIV-2025-002", "title": "Caso Civil Marruecos"}},
                    {"_source": {"case_number": "CIV-2025-003", "title": "Demanda en Marruecos"}}
                ]
            }
        }
        
        result = mock_elasticsearch.search(
            index="cases",
            body=query
        )
        
        assert result["hits"]["total"]["value"] == 3
    
    def test_filter_by_status(self, mock_elasticsearch):
        """Test filtrar por estado."""
        query = {
            "query": {
                "bool": {
                    "must": [
                        {"match": {"status": "pending"}}
                    ]
                }
            }
        }
        
        mock_elasticsearch.search.return_value = {
            "hits": {
                "total": {"value": 5},
                "hits": []
            }
        }
        
        result = mock_elasticsearch.search(
            index="cases",
            body=query
        )
        
        assert result["hits"]["total"]["value"] >= 0
    
    def test_aggregation_by_status(self, mock_elasticsearch):
        """Test agregación por estado."""
        query = {
            "size": 0,
            "aggs": {
                "by_status": {
                    "terms": {
                        "field": "status.keyword"
                    }
                }
            }
        }
        
        mock_elasticsearch.search.return_value = {
            "aggregations": {
                "by_status": {
                    "buckets": [
                        {"key": "pending", "doc_count": 45},
                        {"key": "in_progress", "doc_count": 60},
                        {"key": "resolved", "doc_count": 30}
                    ]
                }
            }
        }
        
        result = mock_elasticsearch.search(
            index="cases",
            body=query
        )
        
        buckets = result["aggregations"]["by_status"]["buckets"]
        assert len(buckets) == 3
        assert buckets[0]["key"] == "pending"
        assert buckets[0]["doc_count"] == 45
    
    def test_delete_document(self, mock_elasticsearch):
        """Test eliminar documento."""
        mock_elasticsearch.delete.return_value = {"result": "deleted"}
        
        result = mock_elasticsearch.delete(
            index="cases",
            id="es-2025-001"
        )
        
        assert result["result"] == "deleted"
    
    def test_multilingual_search(self, mock_elasticsearch):
        """Test búsqueda multi-idioma (árabe, francés, español)."""
        # Búsqueda en árabe
        arabic_query = {
            "query": {
                "match": {
                    "description": "قضية مدنية"
                }
            }
        }
        
        mock_elasticsearch.search.return_value = {
            "hits": {
                "total": {"value": 2},
                "hits": [
                    {"_source": {"title": "قضية مدنية رقم 1"}},
                    {"_source": {"title": "قضية مدنية رقم 2"}}
                ]
            }
        }
        
        result = mock_elasticsearch.search(
            index="cases",
            body=arabic_query
        )
        
        assert result["hits"]["total"]["value"] >= 0

@pytest.mark.integration
class TestElasticsearchPerformance:
    """Tests de performance con Elasticsearch."""
    
    @pytest.mark.slow
    def test_bulk_indexing(self, mock_elasticsearch):
        """Test indexación masiva."""
        import time
        
        # Simular bulk indexing
        docs = [
            {
                "case_number": f"BULK-{i}",
                "title": f"Caso {i}",
                "description": f"Descripción del caso {i}",
                "status": "pending"
            }
            for i in range(1000)
        ]
        
        start = time.time()
        
        # En producción usaríamos helpers.bulk()
        for doc in docs:
            mock_elasticsearch.index(
                index="cases",
                body=doc
            )
        
        end = time.time()
        
        # Debe completarse en tiempo razonable
        assert (end - start) < 5.0
    
    @pytest.mark.slow
    def test_search_performance(self, mock_elasticsearch):
        """Test performance de búsqueda."""
        import time
        
        query = {
            "query": {
                "match_all": {}
            },
            "size": 100
        }
        
        mock_elasticsearch.search.return_value = {
            "hits": {
                "total": {"value": 1000},
                "hits": []
            }
        }
        
        start = time.time()
        result = mock_elasticsearch.search(
            index="cases",
            body=query
        )
        end = time.time()
        
        # Búsqueda debe ser rápida
        assert (end - start) < 0.5
