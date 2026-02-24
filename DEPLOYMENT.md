# Deployment Guide for MLBB AI Coach

Complete guide for deploying MLBB AI Coach to production.

## Table of Contents

1. [Local Development](#local-development)
2. [Docker Deployment](#docker-deployment)
3. [Cloud Deployment](#cloud-deployment)
4. [SEA Region Optimization](#sea-region-optimization)
5. [Monitoring & Maintenance](#monitoring--maintenance)

---

## Local Development

### Prerequisites
- Python 3.11+
- API keys (Anthropic, Google, Pinecone)

### Steps

```bash
# Clone and setup
git clone <your-repo>
cd Test-AI-Matchmaking

# Setup environment
bash scripts/setup.sh
source venv/bin/activate
pip install -r requirements.txt

# Configure
cp .env.example .env
# Edit .env with your keys

# Ingest data
python scripts/ingest_data.py

# Run server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

---

## Docker Deployment

### Single Container

```bash
# Build image
docker build -t mlbb-coach .

# Run container
docker run -d \
  --name mlbb-coach \
  -p 8000:8000 \
  -e ANTHROPIC_API_KEY=your_key \
  -e GOOGLE_API_KEY=your_key \
  -e PINECONE_API_KEY=your_key \
  mlbb-coach
```

### Docker Compose (Recommended)

```bash
# Create .env file with all required keys
cat > .env << EOF
ANTHROPIC_API_KEY=your_anthropic_key
GOOGLE_API_KEY=your_google_key
PINECONE_API_KEY=your_pinecone_key
PINECONE_ENVIRONMENT=us-east-1
PINECONE_INDEX_NAME=mlbb-coach
POSTGRES_PASSWORD=your_secure_password
EOF

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f api

# Stop services
docker-compose down
```

Services:
- API: http://localhost:8000
- Web: http://localhost
- PostgreSQL: localhost:5432
- Redis: localhost:6379

---

## Cloud Deployment

### AWS Deployment

#### 1. EC2 Setup

```bash
# Launch EC2 instance (Ubuntu 22.04, t3.medium or larger)
# Security groups: Allow ports 80, 443, 22

# SSH into instance
ssh ubuntu@<your-ec2-ip>

# Install Docker
sudo apt update
sudo apt install -y docker.io docker-compose
sudo usermod -aG docker ubuntu

# Clone repository
git clone <your-repo>
cd Test-AI-Matchmaking

# Configure environment
nano .env  # Add your API keys

# Start services
docker-compose up -d
```

#### 2. RDS for PostgreSQL (Optional)

```bash
# Create RDS PostgreSQL instance
# Update DATABASE_URL in .env:
DATABASE_URL=postgresql+asyncpg://user:pass@rds-endpoint:5432/mlbb_coach
```

#### 3. ElastiCache for Redis (Optional)

```bash
# Create ElastiCache Redis cluster
# Update REDIS_HOST in .env:
REDIS_HOST=your-elasticache-endpoint
```

#### 4. Application Load Balancer

- Create ALB pointing to EC2 instance
- Configure SSL certificate
- Set up health checks: `/health`

### Google Cloud Platform (GCP)

#### 1. Cloud Run Deployment

```bash
# Build and push to GCR
gcloud builds submit --tag gcr.io/PROJECT_ID/mlbb-coach

# Deploy to Cloud Run
gcloud run deploy mlbb-coach \
  --image gcr.io/PROJECT_ID/mlbb-coach \
  --platform managed \
  --region asia-southeast1 \
  --allow-unauthenticated \
  --set-env-vars ANTHROPIC_API_KEY=xxx,GOOGLE_API_KEY=xxx
```

#### 2. Cloud SQL + Memorystore

```bash
# Create Cloud SQL PostgreSQL instance
# Create Memorystore Redis instance
# Update connection strings in environment
```

### Azure Deployment

#### 1. Container Instances

```bash
# Create resource group
az group create --name mlbb-coach-rg --location southeastasia

# Create container instance
az container create \
  --resource-group mlbb-coach-rg \
  --name mlbb-coach \
  --image <your-registry>/mlbb-coach:latest \
  --dns-name-label mlbb-coach \
  --ports 8000 \
  --environment-variables \
    ANTHROPIC_API_KEY=xxx \
    GOOGLE_API_KEY=xxx
```

---

## SEA Region Optimization

### 1. Choose SEA Regions

**AWS:**
- Primary: ap-southeast-1 (Singapore)
- Secondary: ap-southeast-3 (Jakarta)

**GCP:**
- Primary: asia-southeast1 (Singapore)
- Secondary: asia-southeast2 (Jakarta)

**Azure:**
- Primary: southeastasia (Singapore)
- Secondary: eastasia (Hong Kong)

### 2. CDN Configuration

```nginx
# CloudFlare configuration
- Enable CDN for static assets
- Set cache rules for frontend
- Configure geo-routing to nearest server

# AWS CloudFront
- Create distribution
- Set origin to ALB
- Enable compression
- Set SEA regions as priority
```

### 3. Pinecone Configuration

```python
# Use Pinecone in GCP us-east-1 or AWS us-east-1
# For SEA, consider self-hosted Weaviate or Qdrant
PINECONE_ENVIRONMENT=us-east-1
```

### 4. Latency Optimization

```yaml
# Enable compression
COMPRESS_RESPONSES=true

# Use HTTP/2
# Enable connection pooling
# Implement response caching
```

---

## Monitoring & Maintenance

### 1. Health Checks

```bash
# Check API health
curl https://your-domain.com/health

# Expected response:
{
  "status": "healthy",
  "services": {
    "llm_providers": true,
    "vector_store": true,
    "api": true
  }
}
```

### 2. Logging

```yaml
# Configure structured logging
LOG_LEVEL=INFO
LOG_FORMAT=json

# Aggregate logs
- Datadog
- CloudWatch
- Stackdriver
- ELK Stack
```

### 3. Monitoring Tools

**Prometheus + Grafana:**

```yaml
# prometheus.yml
scrape_configs:
  - job_name: 'mlbb-coach'
    static_configs:
      - targets: ['api:8000']
```

**Application Performance Monitoring:**
- New Relic
- Datadog APM
- AWS X-Ray
- Google Cloud Trace

### 4. Backup Strategy

```bash
# PostgreSQL backups
# Daily automated backups
pg_dump -h localhost -U mlbb_user mlbb_coach > backup_$(date +%Y%m%d).sql

# Pinecone backups
# Export vector data periodically
python scripts/export_vectors.py
```

### 5. Scaling

**Horizontal Scaling:**

```yaml
# Kubernetes deployment
apiVersion: apps/v1
kind: Deployment
metadata:
  name: mlbb-coach
spec:
  replicas: 3
  selector:
    matchLabels:
      app: mlbb-coach
```

**Auto-scaling:**

```bash
# AWS Auto Scaling
aws autoscaling create-auto-scaling-group \
  --auto-scaling-group-name mlbb-coach-asg \
  --min-size 2 \
  --max-size 10 \
  --desired-capacity 3
```

---

## Security Checklist

- [ ] Use HTTPS/TLS certificates (Let's Encrypt)
- [ ] Set strong SECRET_KEY
- [ ] Enable CORS only for trusted domains
- [ ] Implement rate limiting
- [ ] Add authentication/authorization
- [ ] Encrypt sensitive environment variables
- [ ] Enable firewall rules
- [ ] Regular security updates
- [ ] Monitor for suspicious activity
- [ ] Implement DDoS protection (CloudFlare)

---

## Cost Optimization

### LLM Usage

```python
# Monitor token usage
# Set max tokens per request
# Implement caching for common queries
# Use cheaper models for simple tasks
```

### Infrastructure

- Use spot/preemptible instances for non-critical workloads
- Right-size EC2/VM instances
- Use reserved instances for predictable workloads
- Implement auto-scaling
- Cache static assets on CDN
- Compress responses

### Estimated Costs (Monthly)

**Small Scale (1000 users/day):**
- Compute: $50-100
- Database: $20-50
- LLM API: $100-300
- Vector DB: $70 (Pinecone starter)
- Total: ~$300-500/month

**Medium Scale (10,000 users/day):**
- Compute: $200-400
- Database: $100-200
- LLM API: $1000-2000
- Vector DB: $70-150
- Total: ~$1500-3000/month

---

## Troubleshooting

### API Not Responding

```bash
# Check service status
docker-compose ps

# View logs
docker-compose logs api

# Restart services
docker-compose restart api
```

### High Latency

```bash
# Check response times
curl -w "@curl-format.txt" -o /dev/null -s https://your-domain.com/health

# Monitor database queries
# Check network latency
# Review LLM API response times
```

### Out of Memory

```bash
# Increase container memory
docker-compose.yml:
  api:
    deploy:
      resources:
        limits:
          memory: 2G
```

---

## Post-Deployment

1. **Test endpoints**: Run `python scripts/test_api.py`
2. **Monitor logs**: Check for errors and warnings
3. **Performance testing**: Use Apache Bench or k6
4. **Set up alerts**: Configure notifications for failures
5. **Documentation**: Update API docs and user guides
6. **User feedback**: Implement feedback collection

---

## Support

For deployment issues:
- Check logs first
- Review health endpoint
- Test LLM provider connectivity
- Verify API keys
- Check firewall/security groups
- Review resource usage

---

## Next Steps

1. Set up CI/CD pipeline
2. Implement automated testing
3. Add monitoring dashboards
4. Configure alerting
5. Document runbooks
6. Plan disaster recovery
7. Implement feature flags
8. Add A/B testing capability
