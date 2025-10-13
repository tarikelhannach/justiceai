# Manual de Compliance Legal - Reino de Marruecos

## 📋 Índice

1. [Marco Legal Marroquí](#marco-legal-marroquí)
2. [Protección de Datos](#protección-de-datos)
3. [Firma Digital](#firma-digital)
4. [Auditoría y Trazabilidad](#auditoría-y-trazabilidad)
5. [Seguridad de la Información](#seguridad-de-la-información)
6. [Accesibilidad](#accesibilidad)
7. [Internacionalización](#internacionalización)
8. [Checklist de Compliance](#checklist-de-compliance)
9. [Certificaciones y Auditorías](#certificaciones-y-auditorías)

---

## 1. Marco Legal Marroquí

### 1.1 Leyes Aplicables

| Ley | Descripción | Aplicación al Sistema |
|-----|-------------|----------------------|
| **Ley 09-08** | Protección de Datos Personales (2009) | Gestión de datos de usuarios, casos y documentos |
| **Ley 53-05** | Intercambio Electrónico de Datos (2007) | Firma digital, documentos electrónicos |
| **Dahir 1-11-91** | Constitución de Marruecos (2011) - Art. 27 | Acceso a información y justicia |
| **Código de Procedimiento Civil** | Procedimientos judiciales | Workflow de casos, plazos, notificaciones |
| **Ley 31-08** | Protección del Consumidor | Derechos de ciudadanos en el sistema |

### 1.2 Autoridades Competentes

| Autoridad | Rol | Contacto |
|-----------|-----|----------|
| **CNDP** (Commission Nationale de Contrôle de la Protection des Données à Caractère Personnel) | Supervisión protección de datos | www.cndp.ma |
| **ANRT** (Agence Nationale de Réglementation des Télécommunications) | Regulación telecomunicaciones y firma digital | www.anrt.ma |
| **Ministerio de Justicia** | Supervisión sistema judicial | www.justice.gov.ma |

---

## 2. Protección de Datos

### 2.1 Cumplimiento Ley 09-08

**Requisitos Implementados:**

✅ **Consentimiento Explícito:**
- Usuarios aceptan términos y condiciones al registrarse
- Consentimiento documentado en base de datos
- Opt-in para comunicaciones no esenciales

✅ **Finalidad del Tratamiento:**
```python
# Propósitos documentados:
- Gestión de casos judiciales
- Administración de usuarios
- Auditoría y compliance
- Firma digital de documentos
- Comunicaciones relacionadas con casos
```

✅ **Minimización de Datos:**
- Solo se recopilan datos necesarios para el propósito judicial
- No se solicitan datos sensibles innecesarios
- Campos opcionales claramente marcados

✅ **Exactitud de Datos:**
- Usuarios pueden actualizar sus datos
- Validación de datos en tiempo real
- Logs de cambios para auditoría

✅ **Limitación de Conservación:**
```python
# Períodos de retención:
CASE_DATA_RETENTION = 2555  # días (7 años - requisito legal)
AUDIT_LOG_RETENTION = 2555  # días (7 años)
USER_DATA_INACTIVE = 365    # días (1 año sin actividad)
TEMP_FILES_RETENTION = 30   # días
```

✅ **Seguridad de Datos:**
- Encriptación en tránsito (TLS 1.3)
- Encriptación en reposo (AES-256)
- Control de acceso RBAC
- Autenticación fuerte (JWT + 2FA opcional)

✅ **Derechos de los Interesados:**
- **Derecho de Acceso**: API `/api/users/me/data`
- **Derecho de Rectificación**: API `/api/users/me/update`
- **Derecho de Supresión**: API `/api/users/me/delete` (anonimización)
- **Derecho de Oposición**: Opt-out de comunicaciones
- **Derecho de Portabilidad**: Exportación JSON/CSV

### 2.2 Notificación a CNDP

**Estado:** ✅ PENDIENTE REGISTRO FORMAL

**Procedimiento:**
1. Completar formulario CNDP: https://www.cndp.ma/declaration/
2. Documentar:
   - Finalidad del tratamiento
   - Categorías de datos
   - Destinatarios de datos
   - Transferencias internacionales (si aplica)
   - Medidas de seguridad
3. Obtener número de registro
4. Publicar en política de privacidad

**Responsable del Tratamiento:**
```
Ministerio de Justicia del Reino de Marruecos
Dirección: [Dirección oficial]
Tel: [Teléfono]
Email: dpo@justice.gov.ma
```

### 2.3 Transferencia Internacional de Datos

**Estado:** ❌ NO APLICABLE (datos en territorio marroquí)

Si fuera necesaria transferencia:
- Solo a países con nivel adecuado de protección
- Cláusulas contractuales tipo aprobadas por CNDP
- Notificación previa a CNDP

---

## 3. Firma Digital

### 3.1 Cumplimiento Ley 53-05

**Requisitos Implementados:**

✅ **Certificados Electrónicos:**
- Integración con HSM certificado
- Soporte PKCS#11 para hardware HSM
- Azure Key Vault para cloud HSM
- Software fallback para desarrollo

✅ **Autoridad de Certificación:**
```python
# Proveedores certificados en Marruecos:
- Barid Al-Maghrib (Poste Maroc)
- MTDS (Maroc Telecommerce)
- Trust Services Maroc
```

✅ **Validez Jurídica:**
- Firma electrónica equivalente a firma manuscrita (Art. 6 Ley 53-05)
- Timestamping para no repudio
- Trazabilidad completa en audit logs

✅ **Tipos de Firma Soportados:**

| Tipo | Descripción | Uso |
|------|-------------|-----|
| **Firma Simple** | Sin certificado | Documentos internos |
| **Firma Avanzada** | Con certificado personal | Documentos oficiales |
| **Firma Cualificada** | HSM + certificado cualificado | Sentencias, actas |

### 3.2 Configuración HSM

**Producción - Hardware HSM:**
```bash
HSM_TYPE=pkcs11
HSM_LIBRARY_PATH=/usr/lib/hsm/libhsm.so
HSM_PIN=[PIN_SEGURO]
HSM_SLOT_ID=0

# Proveedor certificado:
HSM_PROVIDER=thales  # o safenet, gemalto
HSM_CERT_AUTHORITY=barid-al-maghrib
```

**Desarrollo - Software Fallback:**
```bash
HSM_TYPE=software
HSM_KEY_PATH=/secure/keys/
```

### 3.3 Auditoría de Firmas

Todas las firmas digitales se registran:

```sql
-- Tabla audit_logs
INSERT INTO audit_logs (
    action,
    resource_type,
    resource_id,
    user_id,
    details
) VALUES (
    'SIGN_DOCUMENT',
    'Document',
    123,
    user_id,
    '{
        "document_id": 123,
        "signature_type": "qualified",
        "certificate_serial": "ABC123",
        "timestamp": "2024-10-13T14:30:00Z",
        "hsm_provider": "thales",
        "ca": "barid-al-maghrib"
    }'
);
```

---

## 4. Auditoría y Trazabilidad

### 4.1 Requisitos Gubernamentales

✅ **Trazabilidad Completa:**
- Todos los eventos registrados en `audit_logs`
- Retención: 7 años (2555 días)
- Inmutabilidad: Solo inserción, no modificación/borrado
- Integridad: Hash SHA-256 de cada registro

✅ **Eventos Auditados:**

| Categoría | Eventos |
|-----------|---------|
| **Autenticación** | LOGIN, LOGOUT, LOGIN_FAILED, PASSWORD_RESET |
| **Casos** | CREATE_CASE, UPDATE_CASE, DELETE_CASE, ASSIGN_CASE |
| **Documentos** | UPLOAD_DOCUMENT, DOWNLOAD_DOCUMENT, SIGN_DOCUMENT, DELETE_DOCUMENT |
| **Usuarios** | CREATE_USER, UPDATE_USER, DELETE_USER, CHANGE_ROLE |
| **Sistema** | CONFIG_CHANGE, BACKUP, RESTORE, SYSTEM_ERROR |

✅ **Información Registrada:**
```python
{
    "timestamp": "2024-10-13T14:30:00Z",
    "user_id": 123,
    "username": "juan.perez",
    "role": "JUDGE",
    "action": "SIGN_DOCUMENT",
    "resource_type": "Document",
    "resource_id": 456,
    "ip_address": "192.168.1.100",
    "user_agent": "Mozilla/5.0...",
    "details": { ... },
    "result": "SUCCESS"
}
```

### 4.2 Exportación de Auditoría

**Para Inspección Gubernamental:**

```bash
# Exportar logs de período específico
curl -H "Authorization: Bearer $ADMIN_TOKEN" \
     "https://justicia.ma/api/audit/export?format=csv&start_date=2024-01-01&end_date=2024-12-31" \
     > audit_2024.csv

# Exportar todo (7 años)
curl -H "Authorization: Bearer $ADMIN_TOKEN" \
     "https://justicia.ma/api/audit/export?format=json" \
     > audit_completo.json
```

**Formato CSV para Autoridades:**
```csv
timestamp,user,role,action,resource,result,ip,details
2024-10-13 14:30:00,juan.perez,JUDGE,SIGN_DOCUMENT,Document#456,SUCCESS,192.168.1.100,"certificado ABC123"
```

---

## 5. Seguridad de la Información

### 5.1 Clasificación de Datos

| Nivel | Descripción | Ejemplos | Controles |
|-------|-------------|----------|-----------|
| **Público** | Información pública | Leyes, procedimientos generales | Ninguno especial |
| **Interno** | Uso interno gobierno | Estadísticas, reportes | Autenticación |
| **Confidencial** | Datos de casos | Casos, documentos, identidades | RBAC, encriptación |
| **Secreto** | Máxima seguridad | Casos seguridad nacional | RBAC estricto, HSM, auditoría |

### 5.2 Controles de Seguridad Implementados

✅ **Autenticación:**
- JWT con refresh tokens
- Caducidad: 15 minutos (access), 7 días (refresh)
- 2FA opcional (TOTP/SMS)
- Rate limiting: 5 intentos/minuto

✅ **Autorización:**
- RBAC con 5 roles: Admin, Judge, Lawyer, Clerk, Citizen
- Permisos a nivel de campo
- Deny-by-default policy
- Validación en frontend y backend

✅ **Encriptación:**
- TLS 1.3 (tránsito)
- AES-256 (reposo)
- Passwords: bcrypt (12 rounds)
- Secrets: Environment variables

✅ **Protección contra Ataques:**
- XSS: Content Security Policy, sanitización
- CSRF: Tokens, SameSite cookies
- SQL Injection: Prepared statements, ORM
- DDoS: Rate limiting, load balancer

### 5.3 Gestión de Incidentes

**Procedimiento:**

1. **Detección**: Monitoreo 24/7, alertas automáticas
2. **Contención**: Aislar sistema afectado
3. **Investigación**: Logs de auditoría, análisis forense
4. **Remediación**: Parchar vulnerabilidad
5. **Notificación**: 
   - CNDP (si afecta datos personales) - 72 horas
   - Ministerio de Justicia - inmediato
   - Usuarios afectados - según gravedad
6. **Lecciones Aprendidas**: Actualizar procedimientos

---

## 6. Accesibilidad

### 6.1 Cumplimiento WCAG 2.1

**Nivel Objetivo:** AA

✅ **Implementado:**
- Contraste de colores: ratio 4.5:1 mínimo
- Navegación por teclado completa
- ARIA labels en todos los componentes
- Textos alternativos en imágenes
- Formularios con labels explícitos
- Errores de validación claros

✅ **Tecnologías Asistivas:**
- Screen readers (NVDA, JAWS)
- Magnificadores de pantalla
- Navegación por voz

### 6.2 Accesibilidad en Árabe

✅ **RTL (Right-to-Left):**
- Layout automático RTL cuando idioma = árabe
- Fuentes optimizadas para árabe
- OCR con soporte árabe (Tesseract)
- Búsqueda en árabe (Elasticsearch)

---

## 7. Internacionalización

### 7.1 Idiomas Oficiales

**Constitución de Marruecos (Art. 5):**
- **Árabe**: Idioma oficial
- **Amazigh**: Idioma oficial
- **Francés**: Idioma administrativo

**Sistema Implementa:**
- ✅ Árabe (ar) - COMPLETO
- ✅ Francés (fr) - COMPLETO
- ✅ Español (es) - COMPLETO
- ⚠️ Amazigh - PENDIENTE (futuro)

### 7.2 Validación Legal

**Documentos Oficiales:**
- Versión árabe: **Versión oficial con validez legal**
- Versión francesa: Traducción oficial
- Versión española: Traducción de referencia

**Generación de Documentos:**
```python
# Template con idioma
if document.language == "ar":
    template = "templates/ar/sentencia.html"
    is_official = True
elif document.language == "fr":
    template = "templates/fr/jugement.html"
    is_official = True
else:
    template = "templates/es/sentencia.html"
    is_official = False
```

---

## 8. Checklist de Compliance

### 8.1 Pre-Producción

**Obligatorio antes de deployment:**

#### Protección de Datos
- [ ] Registrar tratamiento en CNDP
- [ ] Designar DPO (Data Protection Officer)
- [ ] Publicar política de privacidad (AR/FR/ES)
- [ ] Implementar formularios de consentimiento
- [ ] Configurar períodos de retención
- [ ] Validar derechos de los interesados (acceso, rectificación, supresión)

#### Firma Digital
- [ ] Contratar HSM certificado (Barid Al-Maghrib, MTDS o Trust Services)
- [ ] Obtener certificados cualificados
- [ ] Configurar timestamping
- [ ] Validar firma con autoridad certificadora
- [ ] Documentar procedimientos de firma

#### Auditoría
- [ ] Configurar retención 7 años (2555 días)
- [ ] Validar inmutabilidad de logs
- [ ] Implementar exportación automática
- [ ] Crear procedimiento de auditoría externa
- [ ] Designar responsable de auditoría

#### Seguridad
- [ ] Scan de vulnerabilidades (Nessus, OpenVAS)
- [ ] Penetration testing externo
- [ ] Certificar TLS/SSL
- [ ] Validar encriptación datos en reposo
- [ ] Revisar configuración firewall
- [ ] Implementar IDS/IPS
- [ ] Configurar WAF (Web Application Firewall)

#### Accesibilidad
- [ ] Auditoría WCAG 2.1 AA
- [ ] Testing con screen readers
- [ ] Validar navegación por teclado
- [ ] Verificar contraste de colores
- [ ] Testing con usuarios con discapacidad

#### Internacionalización
- [ ] Validar traducción árabe por traductor jurado
- [ ] Validar traducción francesa por traductor jurado
- [ ] Verificar RTL en árabe
- [ ] Testing con usuarios nativos

#### Backup y Recuperación
- [ ] Configurar backups automáticos diarios
- [ ] Validar restore procedure
- [ ] Configurar replicación geográfica
- [ ] Documentar RTO/RPO
- [ ] Testing de disaster recovery

#### Documentación
- [ ] Manual de usuario (AR/FR/ES)
- [ ] Manual técnico
- [ ] Manual operativo
- [ ] Procedimientos de seguridad
- [ ] Plan de contingencia
- [ ] Política de privacidad

### 8.2 Post-Producción

**Mantenimiento continuo:**

#### Mensual
- [ ] Revisar logs de auditoría
- [ ] Scan de vulnerabilidades
- [ ] Actualizar parches de seguridad
- [ ] Verificar backups
- [ ] Revisar métricas de performance

#### Trimestral
- [ ] Auditoría de accesos
- [ ] Revisión de políticas de seguridad
- [ ] Testing de disaster recovery
- [ ] Actualización de documentación
- [ ] Training de equipo

#### Anual
- [ ] Auditoría externa completa
- [ ] Penetration testing
- [ ] Renovación certificados
- [ ] Revisión compliance CNDP
- [ ] Actualización plan de contingencia

---

## 9. Certificaciones y Auditorías

### 9.1 Certificaciones Requeridas

| Certificación | Estado | Prioridad | Costo Estimado |
|---------------|--------|-----------|----------------|
| **ISO 27001** (Seguridad de Información) | 🟡 En proceso | ALTA | 50,000 MAD |
| **ISO 27017** (Cloud Security) | 🔴 Pendiente | MEDIA | 30,000 MAD |
| **ISO 27018** (Privacy Cloud) | 🔴 Pendiente | MEDIA | 30,000 MAD |
| **FIPS 140-2** (HSM) | 🟢 Certificado | ALTA | Incluido HSM |

### 9.2 Auditorías Programadas

**2025:**
- Q1: Auditoría interna de seguridad
- Q2: Penetration testing externo
- Q3: Auditoría CNDP (protección datos)
- Q4: Auditoría ISO 27001 (pre-certificación)

**2026:**
- Q1: Certificación ISO 27001 oficial
- Q2: Auditoría gubernamental (Ministerio Justicia)
- Q3: Renovación certificados HSM
- Q4: Auditoría compliance anual

### 9.3 Auditor Externo

**Seleccionar auditor certificado:**
- Experiencia en sector público marroquí
- Certificación ISO 27001 Lead Auditor
- Conocimiento de Ley 09-08 (protección datos)
- Conocimiento de Ley 53-05 (firma digital)

**Presupuesto anual:** 200,000 - 300,000 MAD

---

## 10. Responsabilidades

### 10.1 Roles de Compliance

| Rol | Responsabilidad | Contacto |
|-----|----------------|----------|
| **DPO** (Data Protection Officer) | Protección de datos, CNDP | dpo@justice.gov.ma |
| **CISO** (Chief Information Security Officer) | Seguridad de información | ciso@justice.gov.ma |
| **Compliance Officer** | Cumplimiento legal general | compliance@justice.gov.ma |
| **Auditor Interno** | Auditorías internas | audit@justice.gov.ma |
| **Legal Counsel** | Asesoría legal | legal@justice.gov.ma |

### 10.2 Escalación de Incidentes

```
Incidente Detectado
        ↓
¿Afecta datos personales? → Sí → Notificar DPO → CNDP (72h)
        ↓ No
¿Afecta seguridad sistema? → Sí → Notificar CISO → Ministerio
        ↓ No
¿Afecta operación? → Sí → Notificar Ops Manager
        ↓ No
Registrar en audit log
```

---

## 11. Penalizaciones por Incumplimiento

### 11.1 Sanciones Ley 09-08 (Protección Datos)

| Infracción | Sanción |
|------------|---------|
| No declaración a CNDP | 20,000 - 200,000 MAD |
| Tratamiento ilícito de datos | 200,000 - 2,000,000 MAD |
| No atender derechos de interesados | 50,000 - 500,000 MAD |
| Violación de seguridad | 100,000 - 1,000,000 MAD |
| Transferencia ilegal internacional | 500,000 - 5,000,000 MAD |

### 11.2 Sanciones Ley 53-05 (Firma Digital)

| Infracción | Sanción |
|------------|---------|
| Firma falsa o fraudulenta | Penal: 1-5 años prisión |
| Uso indebido de certificado | 50,000 - 500,000 MAD |
| Compromiso de clave privada no reportado | 100,000 - 1,000,000 MAD |

---

## 12. Anexos

### A. Contactos Útiles

**Autoridades:**
- CNDP: +212 537 XXX XXX, contact@cndp.ma
- ANRT: +212 537 XXX XXX, contact@anrt.ma
- Ministerio Justicia: +212 537 XXX XXX

**Proveedores HSM:**
- Barid Al-Maghrib: +212 5XXXX, cps@poste.ma
- MTDS: +212 5XXXX, contact@mtds.com
- Trust Services: +212 5XXXX, info@trustservices.ma

### B. Templates de Documentos

- Política de Privacidad (AR/FR/ES)
- Formulario de Consentimiento
- Solicitud de Acceso a Datos
- Notificación de Incidente CNDP
- Acuerdo de Confidencialidad

### C. Legislación de Referencia

- Ley 09-08: Protección de Datos Personales
- Ley 53-05: Intercambio Electrónico de Datos
- Dahir 1-11-91: Constitución de Marruecos
- Código de Procedimiento Civil
- Código Penal (Arts. relativos a delitos informáticos)

---

**Versión**: 1.0.0  
**Última actualización**: Octubre 2025  
**Sistema Judicial Digital - Reino de Marruecos** 🇲🇦

**IMPORTANTE:** Este documento debe ser revisado y validado por el departamento legal del Ministerio de Justicia antes del deployment en producción.
