# Legal Compliance Manual - Kingdom of Morocco

## 📋 Index

1. [Moroccan Legal Framework](#moroccan-legal-framework)
2. [Data Protection](#data-protection)
3. [Digital Signature](#digital-signature)
4. [Audit and Traceability](#audit-and-traceability)
5. [Information Security](#information-security)
6. [Accessibility](#accessibility)
7. [Internationalization](#internationalization)
8. [Compliance Checklist](#compliance-checklist)
9. [Certifications and Audits](#certifications-and-audits)

---

## 1. Moroccan Legal Framework

### 1.1 Applicable Laws

| Law | Description | Application to System |
|-----|-------------|----------------------|
| **Law 09-08** | Personal Data Protection (2009) | User, case, and document data management |
| **Law 53-05** | Electronic Data Exchange (2007) | Digital signature, electronic documents |
| **Dahir 1-11-91** | Constitution of Morocco (2011) - Art. 27 | Access to information and justice |
| **Civil Procedure Code** | Judicial procedures | Case workflow, deadlines, notifications |
| **Law 31-08** | Consumer Protection | Citizen rights in the system |

### 1.2 Competent Authorities

| Authority | Role | Contact |
|-----------|-----|----------|
| **CNDP** (Commission Nationale de Contrôle de la Protection des Données à Caractère Personnel) | Data protection supervision | www.cndp.ma |
| **ANRT** (Agence Nationale de Réglementation des Télécommunications) | Telecommunications and digital signature regulation | www.anrt.ma |
| **Ministry of Justice** | Judicial system supervision | www.justice.gov.ma |

---

## 2. Data Protection

### 2.1 Law 09-08 Compliance

**Implemented Requirements:**

✅ **Explicit Consent:**
- Users accept terms and conditions upon registration
- Consent documented in database
- Opt-in for non-essential communications

✅ **Purpose of Processing:**
```python
# Documented purposes:
- Judicial case management
- User administration
- Audit and compliance
- Digital document signing
- Case-related communications
```

✅ **Data Minimization:**
- Only data necessary for judicial purpose collected
- No unnecessary sensitive data requested
- Optional fields clearly marked

✅ **Data Accuracy:**
- Users can update their data
- Real-time data validation
- Change logs for audit

✅ **Retention Limitation:**
```python
# Retention periods:
CASE_DATA_RETENTION = 2555  # days (7 years - legal requirement)
AUDIT_LOG_RETENTION = 2555  # days (7 years)
USER_DATA_INACTIVE = 365    # days (1 year without activity)
TEMP_FILES_RETENTION = 30   # days
```

✅ **Data Security:**
- Encryption in transit (TLS 1.3)
- Encryption at rest (AES-256)
- RBAC access control
- Strong authentication (JWT + optional 2FA)

✅ **Data Subject Rights:**
- **Right of Access**: API `/api/users/me/data`
- **Right to Rectification**: API `/api/users/me/update`
- **Right to Erasure**: API `/api/users/me/delete` (anonymization)
- **Right to Object**: Communication opt-out
- **Right to Portability**: JSON/CSV export

### 2.2 CNDP Notification

**Status:** ✅ PENDING FORMAL REGISTRATION

**Procedure:**
1. Complete CNDP form: https://www.cndp.ma/declaration/
2. Document:
   - Processing purpose
   - Data categories
   - Data recipients
   - International transfers (if applicable)
   - Security measures
3. Obtain registration number
4. Publish in privacy policy

**Data Controller:**
```
Ministry of Justice of the Kingdom of Morocco
Address: [Official address]
Phone: [Phone]
Email: dpo@justice.gov.ma
```

### 2.3 International Data Transfer

**Status:** ❌ NOT APPLICABLE (data in Moroccan territory)

If transfer necessary:
- Only to countries with adequate protection level
- Standard contractual clauses approved by CNDP
- Prior notification to CNDP

---

## 3. Digital Signature

### 3.1 Law 53-05 Compliance

**Implemented Requirements:**

✅ **Electronic Certificates:**
- Certified HSM integration
- PKCS#11 support for hardware HSM
- Azure Key Vault for cloud HSM
- Software fallback for development

✅ **Certification Authority:**
```python
# Certified providers in Morocco:
- Barid Al-Maghrib (Poste Maroc)
- MTDS (Maroc Telecommerce)
- Trust Services Maroc
```

✅ **Legal Validity:**
- Electronic signature equivalent to handwritten signature (Art. 6 Law 53-05)
- Timestamping for non-repudiation
- Complete traceability in audit logs

✅ **Supported Signature Types:**

| Type | Description | Use |
|------|-------------|-----|
| **Simple Signature** | Without certificate | Internal documents |
| **Advanced Signature** | With personal certificate | Official documents |
| **Qualified Signature** | HSM + qualified certificate | Judgments, minutes |

### 3.2 HSM Configuration

**Production - Hardware HSM:**
```bash
HSM_TYPE=pkcs11
HSM_LIBRARY_PATH=/usr/lib/hsm/libhsm.so
HSM_PIN=[SECURE_PIN]
HSM_SLOT_ID=0

# Certified provider:
HSM_PROVIDER=thales  # or safenet, gemalto
HSM_CERT_AUTHORITY=barid-al-maghrib
```

**Development - Software Fallback:**
```bash
HSM_TYPE=software
HSM_KEY_PATH=/secure/keys/
```

### 3.3 Signature Audit

All digital signatures are logged:

```sql
-- audit_logs table
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

## 4. Audit and Traceability

### 4.1 Government Requirements

✅ **Complete Traceability:**
- All events logged in `audit_logs`
- Retention: 7 years (2555 days)
- Immutability: Insert only, no modification/deletion
- Integrity: SHA-256 hash of each record

✅ **Audited Events:**

| Category | Events |
|-----------|---------|
| **Authentication** | LOGIN, LOGOUT, LOGIN_FAILED, PASSWORD_RESET |
| **Cases** | CREATE_CASE, UPDATE_CASE, DELETE_CASE, ASSIGN_CASE |
| **Documents** | UPLOAD_DOCUMENT, DOWNLOAD_DOCUMENT, SIGN_DOCUMENT, DELETE_DOCUMENT |
| **Users** | CREATE_USER, UPDATE_USER, DELETE_USER, CHANGE_ROLE |
| **System** | CONFIG_CHANGE, BACKUP, RESTORE, SYSTEM_ERROR |

✅ **Logged Information:**
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

### 4.2 Audit Export

**For Government Inspection:**

```bash
# Export logs from specific period
curl -H "Authorization: Bearer $ADMIN_TOKEN" \
     "https://justicia.ma/api/audit/export?format=csv&start_date=2024-01-01&end_date=2024-12-31" \
     > audit_2024.csv

# Export all (7 years)
curl -H "Authorization: Bearer $ADMIN_TOKEN" \
     "https://justicia.ma/api/audit/export?format=json" \
     > audit_complete.json
```

**CSV Format for Authorities:**
```csv
timestamp,user,role,action,resource,result,ip,details
2024-10-13 14:30:00,juan.perez,JUDGE,SIGN_DOCUMENT,Document#456,SUCCESS,192.168.1.100,"certificate ABC123"
```

---

## 5. Information Security

### 5.1 Data Classification

| Level | Description | Examples | Controls |
|-------|-------------|----------|-----------|
| **Public** | Public information | Laws, general procedures | None special |
| **Internal** | Government internal use | Statistics, reports | Authentication |
| **Confidential** | Case data | Cases, documents, identities | RBAC, encryption |
| **Secret** | Maximum security | National security cases | Strict RBAC, HSM, audit |

### 5.2 Implemented Security Controls

✅ **Authentication:**
- JWT with refresh tokens
- Expiration: 15 minutes (access), 7 days (refresh)
- Optional 2FA (TOTP/SMS)
- Rate limiting: 5 attempts/minute

✅ **Authorization:**
- RBAC with 5 roles: Admin, Judge, Lawyer, Clerk, Citizen
- Field-level permissions
- Deny-by-default policy
- Frontend and backend validation

✅ **Encryption:**
- TLS 1.3 (transit)
- AES-256 (rest)
- Passwords: bcrypt (12 rounds)
- Secrets: Environment variables

✅ **Attack Protection:**
- XSS: Content Security Policy, sanitization
- CSRF: Tokens, SameSite cookies
- SQL Injection: Prepared statements, ORM
- DDoS: Rate limiting, load balancer

### 5.3 Incident Management

**Procedure:**

1. **Detection**: 24/7 monitoring, automatic alerts
2. **Containment**: Isolate affected system
3. **Investigation**: Audit logs, forensic analysis
4. **Remediation**: Patch vulnerability
5. **Notification**: 
   - CNDP (if affects personal data) - 72 hours
   - Ministry of Justice - immediate
   - Affected users - according to severity
6. **Lessons Learned**: Update procedures

---

## 6. Accessibility

### 6.1 WCAG 2.1 Compliance

**Target Level:** AA

✅ **Implemented:**
- Color contrast: 4.5:1 minimum ratio
- Complete keyboard navigation
- ARIA labels on all components
- Alternative text on images
- Forms with explicit labels
- Clear validation errors

✅ **Assistive Technologies:**
- Screen readers (NVDA, JAWS)
- Screen magnifiers
- Voice navigation

### 6.2 Accessibility in Arabic

✅ **RTL (Right-to-Left):**
- Automatic RTL layout when language = Arabic
- Fonts optimized for Arabic
- OCR with Arabic support (Tesseract)
- Arabic search (Elasticsearch)

---

## 7. Internationalization

### 7.1 Official Languages

**Constitution of Morocco (Art. 5):**
- **Arabic**: Official language
- **Amazigh**: Official language
- **French**: Administrative language

**System Implements:**
- ✅ Arabic (ar) - COMPLETE
- ✅ French (fr) - COMPLETE
- ✅ Spanish (es) - COMPLETE
- ⚠️ Amazigh - PENDING (future)

### 7.2 Legal Validation

**Official Documents:**
- Arabic version: **Official version with legal validity**
- French version: Official translation
- Spanish version: Reference translation

**Document Generation:**
```python
# Template with language
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

## 8. Compliance Checklist

### 8.1 Pre-Production

**Mandatory before deployment:**

#### Data Protection
- [ ] Register processing with CNDP
- [ ] Designate DPO (Data Protection Officer)
- [ ] Publish privacy policy (AR/FR/ES)
- [ ] Implement consent forms
- [ ] Configure retention periods
- [ ] Validate data subject rights (access, rectification, erasure)

#### Digital Signature
- [ ] Contract certified HSM (Barid Al-Maghrib, MTDS or Trust Services)
- [ ] Obtain qualified certificates
- [ ] Configure timestamping
- [ ] Validate signature with certification authority
- [ ] Document signature procedures

#### Audit
- [ ] Configure 7-year retention (2555 days)
- [ ] Validate log immutability
- [ ] Implement automatic export
- [ ] Create external audit procedure
- [ ] Designate audit officer

#### Security
- [ ] Vulnerability scan (Nessus, OpenVAS)
- [ ] External penetration testing
- [ ] Certify TLS/SSL
- [ ] Validate data-at-rest encryption
- [ ] Review firewall configuration
- [ ] Implement IDS/IPS
- [ ] Configure WAF (Web Application Firewall)

#### Accessibility
- [ ] WCAG 2.1 AA audit
- [ ] Testing with screen readers
- [ ] Validate keyboard navigation
- [ ] Verify color contrast
- [ ] Testing with disabled users

#### Internationalization
- [ ] Validate Arabic translation by sworn translator
- [ ] Validate French translation by sworn translator
- [ ] Verify RTL in Arabic
- [ ] Testing with native users

#### Backup and Recovery
- [ ] Configure daily automated backups
- [ ] Validate restore procedure
- [ ] Configure geographic replication
- [ ] Document RTO/RPO
- [ ] Disaster recovery testing

#### Documentation
- [ ] User manual (AR/FR/ES)
- [ ] Technical manual
- [ ] Operational manual
- [ ] Security procedures
- [ ] Contingency plan
- [ ] Privacy policy

### 8.2 Post-Production

**Continuous maintenance:**

#### Monthly
- [ ] Review audit logs
- [ ] Vulnerability scan
- [ ] Update security patches
- [ ] Verify backups
- [ ] Review performance metrics

#### Quarterly
- [ ] Access audit
- [ ] Security policy review
- [ ] Disaster recovery testing
- [ ] Documentation update
- [ ] Team training

#### Annual
- [ ] Complete external audit
- [ ] Penetration testing
- [ ] Certificate renewal
- [ ] CNDP compliance review
- [ ] Contingency plan update

---

## 9. Certifications and Audits

### 9.1 Required Certifications

| Certification | Status | Priority | Estimated Cost |
|---------------|--------|-----------|----------------|
| **ISO 27001** (Information Security) | 🟡 In process | HIGH | 50,000 MAD |
| **ISO 27017** (Cloud Security) | 🔴 Pending | MEDIUM | 30,000 MAD |
| **ISO 27018** (Privacy Cloud) | 🔴 Pending | MEDIUM | 30,000 MAD |
| **FIPS 140-2** (HSM) | 🟢 Certified | HIGH | Included HSM |

### 9.2 Scheduled Audits

**2025:**
- Q1: Internal security audit
- Q2: External penetration testing
- Q3: CNDP audit (data protection)
- Q4: ISO 27001 audit (pre-certification)

**2026:**
- Q1: Official ISO 27001 certification
- Q2: Government audit (Ministry of Justice)
- Q3: HSM certificate renewal
- Q4: Annual compliance audit

### 9.3 External Auditor

**Select certified auditor:**
- Experience in Moroccan public sector
- ISO 27001 Lead Auditor certification
- Knowledge of Law 09-08 (data protection)
- Knowledge of Law 53-05 (digital signature)

**Annual budget:** 200,000 - 300,000 MAD

---

## 10. Responsibilities

### 10.1 Compliance Roles

| Role | Responsibility | Contact |
|-----|----------------|----------|
| **DPO** (Data Protection Officer) | Data protection, CNDP | dpo@justice.gov.ma |
| **CISO** (Chief Information Security Officer) | Information security | ciso@justice.gov.ma |
| **Compliance Officer** | General legal compliance | compliance@justice.gov.ma |
| **Internal Auditor** | Internal audits | audit@justice.gov.ma |
| **Legal Counsel** | Legal advice | legal@justice.gov.ma |

### 10.2 Incident Escalation

```
Incident Detected
        ↓
Affects personal data? → Yes → Notify DPO → CNDP (72h)
        ↓ No
Affects system security? → Yes → Notify CISO → Ministry
        ↓ No
Affects operation? → Yes → Notify Ops Manager
        ↓ No
Log in audit log
```

---

## 11. Non-Compliance Penalties

### 11.1 Law 09-08 Sanctions (Data Protection)

| Infraction | Sanction |
|------------|---------|
| No declaration to CNDP | 20,000 - 200,000 MAD |
| Unlawful data processing | 200,000 - 2,000,000 MAD |
| Not attending to data subject rights | 50,000 - 500,000 MAD |
| Security breach | 100,000 - 1,000,000 MAD |
| Illegal international transfer | 500,000 - 5,000,000 MAD |

### 11.2 Law 53-05 Sanctions (Digital Signature)

| Infraction | Sanction |
|------------|---------|
| False or fraudulent signature | Criminal: 1-5 years prison |
| Improper use of certificate | 50,000 - 500,000 MAD |
| Unreported private key compromise | 100,000 - 1,000,000 MAD |

---

## 12. Annexes

### A. Useful Contacts

**Authorities:**
- CNDP: +212 537 XXX XXX, contact@cndp.ma
- ANRT: +212 537 XXX XXX, contact@anrt.ma
- Ministry of Justice: +212 537 XXX XXX

**HSM Providers:**
- Barid Al-Maghrib: +212 5XXXX, cps@poste.ma
- MTDS: +212 5XXXX, contact@mtds.com
- Trust Services: +212 5XXXX, info@trustservices.ma

### B. Document Templates

- Privacy Policy (AR/FR/ES)
- Consent Form
- Data Access Request
- CNDP Incident Notification
- Confidentiality Agreement

### C. Reference Legislation

- Law 09-08: Personal Data Protection
- Law 53-05: Electronic Data Exchange
- Dahir 1-11-91: Constitution of Morocco
- Civil Procedure Code
- Criminal Code (Arts. related to computer crimes)

---

**Version**: 1.0.0  
**Last updated**: October 2025  
**Digital Judicial System - Kingdom of Morocco** 🇲🇦

**IMPORTANT:** This document must be reviewed and validated by the Ministry of Justice legal department before production deployment.
