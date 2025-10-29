# Operational Manual - Digital Judicial System Morocco

## 📋 Index

1. [Daily Procedures](#daily-procedures)
2. [System Monitoring](#system-monitoring)
3. [User Management](#user-management)
4. [Backups and Restoration](#backups-and-restoration)
5. [Troubleshooting](#troubleshooting)
6. [Maintenance](#maintenance)
7. [Scaling and Performance](#scaling-and-performance)
8. [Security and Compliance](#security-and-compliance)

---

## 1. Daily Procedures

### 1.1 Morning Verification

Each morning, the operations team should:

```bash
# 1. Verify service status
docker-compose ps

# 2. System health check
curl https://justicia.ma/health

# 3. Verify key metrics
docker stats --no-stream

# 4. Review error logs
docker-compose logs --tail=100 | grep ERROR

# 5. Verify nightly backup
ls -lth backups/full/ | head -1
```

**Expected Result:**
- All services in `Up` state
- Health check returns `{"status": "healthy"}`
- CPU < 70%, Memory < 80%
- No critical errors in logs
- Nightly backup completed

### 1.2 Audit Review

Dashboard: `https://justicia.ma/audit`

1. **Access as admin/clerk**
2. **Review previous day statistics:**
   - Total actions
   - Active users
   - Security events
3. **Filter by type:**
   - LOGIN/LOGOUT: Verify normal patterns
   - CREATE_CASE: Validate expected volume
   - ERROR: Investigate any errors
4. **Export daily report** (JSON/CSV)

### 1.3 Backup Verification

```bash
# Verify last backup
cat backups/backup_report_*.txt | tail -n 1

# Integrity test
gunzip -t backups/database/db_backup_*.sql.gz
tar -tzf backups/files/files_backup_*.tar.gz > /dev/null
```

---

## 2. System Monitoring

### 2.1 Monitoring Dashboards

| Dashboard | URL | Credentials | Purpose |
|-----------|-----|--------------|-----------|
| **Grafana** | http://server:3000 | admin / ${GRAFANA_ADMIN_PASSWORD} | General metrics |
| **Flower** | http://server:5555 | - | Celery monitoring |
| **Redis Commander** | http://server:8081 | - | Redis management |
| **ES Head** | http://server:9100 | - | Elasticsearch monitor |

### 2.2 Key Metrics to Monitor

#### Performance
- **Response Time**: < 200ms (p95)
- **Throughput**: > 100 req/s
- **Error Rate**: < 1%

#### Resources
- **CPU**: < 70% average
- **Memory**: < 80% usage
- **Disk**: < 80% usage
- **Network**: < 80% bandwidth

#### Application
- **Active Users**: Monitor peaks
- **Cases Created/day**: Establish baseline
- **Documents Processed/hour**: Validate OCR

### 2.3 Configured Alerts

```bash
# Verify alerts in Slack/Email
# Configured in .env:
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/xxx
ALERT_EMAIL=admin@justicia.ma
```

**Critical Alerts:**
- CPU > 90% for 5 minutes
- Memory > 95%
- Disk > 90%
- Error rate > 5%
- Service down

---

## 3. User Management

### 3.1 Create User

**Frontend:** Admin Dashboard → Users → Create User

**Backend (CLI):**
```bash
docker-compose exec app1 python -c "
from app.models import User
from app.database import SessionLocal

db = SessionLocal()
user = User(
    username='new.user',
    email='user@justicia.ma',
    role='JUDGE',  # ADMIN, JUDGE, LAWYER, CLERK, CITIZEN
    full_name='Full Name'
)
user.set_password('temporary_password')
db.add(user)
db.commit()
print(f'User {user.username} created')
"
```

### 3.2 Reset Password

```bash
docker-compose exec app1 python -c "
from app.models import User
from app.database import SessionLocal

db = SessionLocal()
user = db.query(User).filter(User.username == 'user').first()
user.set_password('new_temporary_password')
db.commit()
print(f'Password for {user.username} reset')
"
```

### 3.3 Change Role

```bash
docker-compose exec app1 python -c "
from app.models import User, UserRole
from app.database import SessionLocal

db = SessionLocal()
user = db.query(User).filter(User.username == 'user').first()
user.role = UserRole.ADMIN
db.commit()
print(f'{user.username} is now {user.role}')
"
```

### 3.4 Deactivate User

```bash
docker-compose exec app1 python -c "
from app.models import User
from app.database import SessionLocal

db = SessionLocal()
user = db.query(User).filter(User.username == 'user').first()
user.is_active = False
db.commit()
print(f'{user.username} deactivated')
"
```

---

## 4. Backups and Restoration

### 4.1 Manual Backup

```bash
# Immediate full backup
./scripts/backup.sh full

# Verify backup
ls -lth backups/full/ | head -1
cat backups/backup_report_*.txt | tail -n 1
```

### 4.2 Automated Backups

**Configured in cron:**
```bash
# View cron jobs
crontab -l

# Expected result:
0 2 * * * cd /path/project && ./scripts/backup.sh full >> logs/backup.log 2>&1
```

**Change schedule:**
```bash
export BACKUP_SCHEDULE="0 3 * * *"  # 3 AM
./scripts/setup-cron.sh
```

### 4.3 Restoration

**⚠️ CRITICAL PROCEDURE - REQUIRES CONFIRMATION**

```bash
# 1. List available backups
ls -lth backups/full/

# 2. Verify backup integrity
gunzip -t backups/database/db_backup_20241013_140000.sql.gz
tar -tzf backups/full/full_backup_20241013_140000.tar.gz

# 3. Execute restoration (REQUIRES MANUAL CONFIRMATION)
./scripts/restore.sh 20241013_140000 full

# Script will ask for confirmation:
# Are you sure you want to continue? (type 'YES' to confirm):
```

### 4.4 Disaster Recovery Procedure

**Scenario: Total server loss**

```bash
# 1. Provision new server (8GB RAM, 4 CPUs)
# 2. Install Docker + Docker Compose

# 3. Clone repository
git clone https://github.com/morocco-gov/sistema-judicial-digital.git
cd sistema-judicial-digital

# 4. Copy backups from secure location
scp -r backup-server:/backups/* ./backups/

# 5. Configure .env
cp .env.example .env
nano .env  # Configure with production values

# 6. Start services
docker-compose up -d

# 7. Restore from latest backup
./scripts/restore.sh [MOST_RECENT_TIMESTAMP] full

# 8. Verify system
curl http://localhost/health
docker-compose ps

# 9. Update DNS if IP changed
# 10. Verify SSL/certificates

# RTO (Recovery Time Objective): < 1 hour
# RPO (Recovery Point Objective): < 1 day
```

---

## 5. Troubleshooting

### 5.1 Application Not Responding

```bash
# 1. Verify container status
docker-compose ps

# 2. View recent logs
docker-compose logs --tail=100 app1

# 3. Verify DB connectivity
docker-compose exec app1 python -c "
from app.database import engine
try:
    engine.connect()
    print('DB OK')
except Exception as e:
    print(f'DB Error: {e}')
"

# 4. Restart application
docker-compose restart app1 app2 app3

# 5. Verify health check
curl http://localhost/health
```

### 5.2 Slow Database

```bash
# 1. View active connections
docker-compose exec db psql -U justicia -d justicia_db -c "
    SELECT count(*) as connections 
    FROM pg_stat_activity 
    WHERE state = 'active';
"

# 2. View slow queries
docker-compose exec db psql -U justicia -d justicia_db -c "
    SELECT pid, now() - pg_stat_activity.query_start AS duration, query 
    FROM pg_stat_activity 
    WHERE state = 'active' 
    ORDER BY duration DESC;
"

# 3. Terminate problematic query
docker-compose exec db psql -U justicia -d justicia_db -c "
    SELECT pg_terminate_backend([PID]);
"

# 4. Vacuum database
docker-compose exec db psql -U justicia -d justicia_db -c "VACUUM ANALYZE;"
```

### 5.3 Redis Out of Memory

```bash
# 1. View memory usage
docker-compose exec redis redis-cli INFO memory

# 2. Clean expired keys
docker-compose exec redis redis-cli FLUSHDB

# 3. Increase maxmemory (temporary)
docker-compose exec redis redis-cli CONFIG SET maxmemory 1gb

# 4. Restart Redis
docker-compose restart redis
```

### 5.4 Celery Workers Not Processing Tasks

```bash
# 1. View worker status
docker-compose logs celery-cpu --tail=50
docker-compose logs celery-io --tail=50

# 2. View task queue
docker-compose exec redis redis-cli LLEN celery

# 3. Purge queue (CAUTION)
docker-compose exec app1 celery -A backend.app.celery.celery purge

# 4. Restart workers
docker-compose restart celery-cpu celery-io celery-hsm
```

### 5.5 OCR Not Working

```bash
# 1. Verify Tesseract installed
docker-compose exec app1 tesseract --version

# 2. Verify languages
docker-compose exec app1 tesseract --list-langs

# Should display: ara, fra, spa

# 3. If language missing, rebuild image
docker-compose build --no-cache app1
docker-compose up -d app1
```

---

## 6. Maintenance

### 6.1 Weekly Maintenance

**Every Sunday at 3 AM:**

```bash
# 1. Full backup
./scripts/backup.sh full

# 2. Vacuum database
docker-compose exec db psql -U justicia -d justicia_db -c "VACUUM FULL ANALYZE;"

# 3. Clean old logs (>30 days)
find ./logs -name "*.log" -mtime +30 -delete

# 4. Clean temp files
docker-compose exec app1 find /app/temp -type f -mtime +7 -delete

# 5. Clean unused Docker images
docker system prune -a -f

# 6. Update Elasticsearch index
curl -X POST "http://localhost:9200/_forcemerge?max_num_segments=1"
```

### 6.2 Monthly Maintenance

**First Sunday of each month:**

```bash
# 1. Review and rotate audit logs (>90 days)
docker-compose exec db psql -U justicia -d justicia_db -c "
    DELETE FROM audit_logs 
    WHERE created_at < NOW() - INTERVAL '90 days';
"

# 2. Update SSL certificates (if expiring)
certbot renew

# 3. Review and update security dependencies
cd backend
pip list --outdated
# Update only security patches

# 4. Offsite backup (upload to S3/Azure)
aws s3 sync ./backups s3://justicia-backups/$(date +%Y%m)/
```

### 6.3 System Updates

```bash
# 1. Backup before updating
./scripts/backup.sh full

# 2. Pull latest version
git pull origin main

# 3. Rebuild images
docker-compose build --no-cache

# 4. Update without downtime (rolling update)
docker-compose up -d --force-recreate --no-deps app1
sleep 30
docker-compose up -d --force-recreate --no-deps app2
sleep 30
docker-compose up -d --force-recreate --no-deps app3

# 5. Verify system
curl http://localhost/health
docker-compose logs --tail=100 | grep ERROR

# 6. If problems, rollback
./scripts/restore.sh [BACKUP_TIMESTAMP] full
```

---

## 7. Scaling and Performance

### 7.1 Horizontal Scaling (Add Instances)

**Edit docker-compose.yml:**

```yaml
  app4:
    build: ./backend
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - SECRET_KEY=${SECRET_KEY}
      - SERVER_ID=app-4
      # ... (copy configuration from app1-3)
```

**Update Nginx (nginx.conf):**

```nginx
upstream backend {
    server app1:8000;
    server app2:8000;
    server app3:8000;
    server app4:8000;  # Add new instance
}
```

**Apply changes:**

```bash
docker-compose up -d app4
docker-compose restart nginx
```

### 7.2 Performance Optimization

**PostgreSQL:**

```bash
# Increase shared_buffers
docker-compose exec db psql -U justicia -d justicia_db -c "
    ALTER SYSTEM SET shared_buffers = '2GB';
    ALTER SYSTEM SET effective_cache_size = '6GB';
    SELECT pg_reload_conf();
"
```

**Redis:**

```bash
# Increase maxmemory
docker-compose exec redis redis-cli CONFIG SET maxmemory 2gb
```

**Elasticsearch:**

```bash
# Increase heap size (edit docker-compose.yml)
ES_JAVA_OPTS=-Xms2g -Xmx2g
```

---

## 8. Security and Compliance

### 8.1 Security Audit

**Monthly:**

```bash
# 1. Review failed login attempts
docker-compose exec db psql -U justicia -d justicia_db -c "
    SELECT user_id, count(*) as attempts 
    FROM audit_logs 
    WHERE action = 'LOGIN' 
      AND details LIKE '%failed%' 
      AND created_at > NOW() - INTERVAL '30 days'
    GROUP BY user_id 
    HAVING count(*) > 10;
"

# 2. Review permission changes
docker-compose exec db psql -U justicia -d justicia_db -c "
    SELECT * FROM audit_logs 
    WHERE action IN ('UPDATE_USER', 'CHANGE_ROLE') 
      AND created_at > NOW() - INTERVAL '30 days'
    ORDER BY created_at DESC;
"

# 3. Export audit report
curl -H "Authorization: Bearer $ADMIN_TOKEN" \
     "https://justicia.ma/api/audit/export?format=csv&start_date=2024-10-01" \
     > audit_report_$(date +%Y%m).csv
```

### 8.2 Compliance Checklist

**Monthly - Verify:**

- [ ] Backups completed and verified (30-day retention)
- [ ] Audit logs intact (2555-day legal retention)
- [ ] SSL certificates valid (>30 days validity)
- [ ] Rate limiting active and functional
- [ ] HSM functional (verify digital signature)
- [ ] Inactive users deactivated (>90 days without login)
- [ ] Expired passwords updated (>90 days)
- [ ] Security vulnerabilities patched
- [ ] Documentation updated
- [ ] Recovery tests performed

---

## 9. Emergency Contacts

### Technical Team

| Role | Name | Phone | Email |
|-----|--------|-----|-------|
| **Lead DevOps** | - | +212 XXX XXX XXX | devops@justicia.ma |
| **DBA** | - | +212 XXX XXX XXX | dba@justicia.ma |
| **Security Officer** | - | +212 XXX XXX XXX | security@justicia.ma |
| **On-Call 24/7** | - | +212 XXX XXX XXX | oncall@justicia.ma |

### Vendors

| Service | Contact | Phone | SLA |
|----------|----------|-----|-----|
| **Hosting** | - | - | 4h response |
| **HSM** | - | - | 2h response |
| **SSL** | - | - | 24h response |

---

## 10. Appendices

### A. Quick Commands

```bash
# Complete health check
./deploy.sh health

# View all logs
docker-compose logs -f

# Resource statistics
docker stats

# Connect to DB
docker-compose exec db psql -U justicia -d justicia_db

# Connect to Redis
docker-compose exec redis redis-cli

# View Celery workers
docker-compose exec app1 celery -A backend.app.celery.celery inspect active
```

### B. Emergency Procedures

**System completely down:**

1. Verify physical server/VM
2. Verify network/connectivity
3. Restart Docker: `systemctl restart docker`
4. Start services: `docker-compose up -d`
5. Verify logs: `docker-compose logs`
6. If persists: Restore from backup

**Security incident:**

1. Isolate affected system
2. Notify Security Officer
3. Capture evidence (logs, dumps)
4. Forensic analysis
5. Remediate vulnerability
6. Restore from clean backup
7. Report to authorities (if applicable)

---

**Version**: 1.0.0  
**Last updated**: October 2025  
**Digital Judicial System - Kingdom of Morocco** 🇲🇦
