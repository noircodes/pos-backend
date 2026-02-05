# Render Deployment Guide

This guide explains how to deploy the POS Backend to Render using either Docker or native Python deployment.

## Prerequisites

- Render account (free tier available)
- MongoDB Atlas account (free tier available)
- GitHub repository with this code
- Git installed locally

## Environment Variables

Set these in the Render dashboard or your `render.yaml`:

| Variable | Description | Example |
|-----------|-------------|----------|
| `MONGO_URI` | MongoDB connection string | `mongodb+srv://user:pass@cluster.mongodb.net/db?retryWrites=true&w=majority` |
| `MONGO_DB` | Database name | `pos` |
| `JWT_SECRET_KEY` | Secret key for JWT tokens | Generate with: `openssl rand -hex 32` |
| `PYTHON_VERSION` | Python version (optional) | `3.13` |

### Generating MongoDB URI

1. Go to [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
2. Create a free cluster
3. Click "Connect" → "Connect your application"
4. Choose "Drivers" → "Python"
5. Copy the connection string
6. Replace `<password>` with your database password
7. Use as `MONGO_URI`

### Generating JWT Secret Key

```bash
# On Linux/Mac
openssl rand -hex 32

# On Windows (Git Bash or PowerShell)
openssl rand -hex 32
```

---

## Option A: Docker Deployment (Recommended)

Docker deployment provides better consistency and reliability.

### Steps:

1. **Push to GitHub**
   ```bash
   git add .
   git commit -m "Add Render deployment files"
   git push origin main
   ```

2. **Connect Render to GitHub**
   - Go to [dashboard.render.com](https://dashboard.render.com)
   - Click "New+" → "Web Service"
   - Connect your GitHub account
   - Select this repository
   - Select `main` branch

3. **Configure Docker Build**
   - Build & Deploy settings
   - Runtime: **Docker**
   - Build context: `/`
   - Dockerfile path: `./Dockerfile`

4. **Set Environment Variables**
   - Add all variables from the table above
   - Never commit secrets to Git!

5. **Deploy**
   - Click "Create Web Service"
   - Wait for build and deployment (~3-5 minutes)
   - Your app will be available at `https://pos-backend.onrender.com`

### Advantages:
- ✅ Consistent environment
- ✅ Faster builds (cached layers)
- ✅ Better isolation
- ✅ Production-ready

---

## Option B: Native Python Deployment

Simpler setup with less control over the environment.

### Steps:

1. **Push to GitHub** (same as above)

2. **Connect Render to GitHub** (same as above)

3. **Configure Python Build**
   - Build & Deploy settings
   - Runtime: **Python 3**
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`

4. **Set Environment Variables** (same as above)

5. **Deploy**
   - Click "Create Web Service"
   - Wait for deployment (~5-7 minutes)

### Advantages:
- ✅ Simpler setup
- ✅ Faster initial deployment
- ✅ Render manages Python environment

---

## Using `render.yaml`

The included `render.yaml` file auto-configures most settings:

```bash
# Render will automatically detect and use this file
# No manual configuration needed after connecting GitHub
```

If `render.yaml` doesn't work, manually configure using the steps above.

---

## Post-Deployment

### Verify Health Check

```bash
curl https://your-app.onrender.com/health
# Should return: {"status":"ok"}
```

### Access API Documentation

Open: `https://your-app.onrender.com/docs`

### Test Authentication

```bash
# Register
curl -X POST https://your-app.onrender.com/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"test","email":"test@example.com","password":"secret"}'

# Login
curl -X POST https://your-app.onrender.com/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=test&password=secret"
```

---

## Monitoring & Logs

### View Logs
- Go to [dashboard.render.com](https://dashboard.render.com)
- Select your service
- Click "Logs" tab

### Metrics
- Response time
- CPU usage
- Memory usage
- Request count

---

## Troubleshooting

### Build Failures

**Problem**: Build fails during `pip install`
```bash
# Check requirements.txt
pip install -r requirements.txt --dry-run
```

**Problem**: Module not found
```bash
# Add missing module to requirements.txt
echo "module-name" >> requirements.txt
```

### Runtime Errors

**Problem**: MongoDB connection refused
```
# Check MONGO_URI is correct
# Verify MongoDB Atlas whitelist includes Render IP (0.0.0.0/0)
```

**Problem**: JWT decode error
```
# Regenerate JWT_SECRET_KEY in Render dashboard
# Redeploy to apply new key
```

### Health Check Failing

**Problem**: `/health` endpoint returns error
```bash
# Check main.py has health endpoint
# Verify port 8000 is exposed
# Review logs for startup errors
```

### Slow Performance

**Problem**: Response time > 500ms
- Consider upgrading to paid Render plan
- Add Redis for caching
- Optimize MongoDB queries
- Enable database indexes (run `scripts/create_indexes.py`)

---

## CI/CD Integration

### Auto-deploy on Push

With `render.yaml`, Render auto-deploys when you push to `main`:

```bash
git add .
git commit -m "Fix bug"
git push origin main  # Triggers automatic deploy
```

### Manual Deploy

In Render dashboard:
- Select service
- Click "Manual Deploy"
- Choose branch and commit
- Click "Deploy"

---

## Scaling

### From Free to Paid

1. Go to service settings
2. Click "Scale"
3. Choose plan and instance type

### Horizontal Scaling

Add more instances for higher traffic:
```yaml
# In render.yaml
numInstances: 3
```

---

## Security Best Practices

1. **Never commit secrets** to Git
2. **Use strong passwords** for MongoDB
3. **Enable SSL** (automatic on Render)
4. **Set CORS** origins appropriately
5. **Rotate secrets** regularly
6. **Monitor logs** for suspicious activity

---

## Cost Estimation

### Free Tier
- 1 instance, 512MB RAM
- 750 hours/month
- 0.1 CPU credits
- Good for: Development, testing, low traffic

### Paid Tier (Basic)
- $7/month per instance
- More CPU, RAM, bandwidth
- Good for: Production, moderate traffic

---

## Support

- Render Docs: [docs.render.com](https://docs.render.com)
- MongoDB Atlas: [docs.atlas.mongodb.com](https://docs.atlas.mongodb.com)
- Issues: Create in [GitHub Issues](https://github.com/noircodes/pos-backend/issues)

---

## Quick Reference

| Task | Command |
|-------|---------|
| Local test | `python start.py` |
| Docker build | `docker build -t pos-backend .` |
| Docker run | `docker run -p 8000:8000 pos-backend` |
| View logs | Render Dashboard → Logs |
| Redeploy | Render Dashboard → Manual Deploy |
| Scale | Render Dashboard → Scale |

---

**Happy Deploying! 🚀**