# Deployment Guide - Vercel

This guide will help you deploy the Resume Intelligence System to Vercel as a serverless application.

## 📋 Prerequisites

1. **Vercel Account**: Sign up at [vercel.com](https://vercel.com)
2. **Git Repository**: Push your code to GitHub, GitLab, or Bitbucket
3. **Vercel CLI** (optional): `npm i -g vercel`

## 🚀 Deployment Steps

### Method 1: Vercel Dashboard (Recommended)

1. **Push to Git**
   ```bash
   git init
   git add .
   git commit -m "Initial commit: Ready for Vercel deployment"
   git branch -M main
   git remote add origin <your-git-repo-url>
   git push -u origin main
   ```

2. **Import to Vercel**
   - Go to [vercel.com/new](https://vercel.com/new)
   - Import your Git repository
   - Vercel will auto-detect the configuration

3. **Configure Project**
   - **Framework Preset**: Vite
   - **Root Directory**: `./` (leave as is)
   - **Build Command**: `cd frontend && npm run build`
   - **Output Directory**: `frontend/dist`
   - **Install Command**: `cd frontend && npm install`

4. **Environment Variables** (Optional)
   Add in Vercel Dashboard under Settings → Environment Variables:
   ```
   VITE_API_URL=/api
   NODE_ENV=production
   ```

5. **Deploy**
   - Click "Deploy"
   - Wait for build to complete
   - Your app will be live at `https://your-app.vercel.app`

### Method 2: Vercel CLI

```bash
# Install Vercel CLI
npm i -g vercel

# Login to Vercel
vercel login

# Deploy from project root
vercel

# Follow the prompts:
# - Set up and deploy? Yes
# - Which scope? (your account)
# - Link to existing project? No
# - Project name? resume-intelligence-system
# - Directory? ./
# - Override settings? No

# Production deployment
vercel --prod
```

## 📁 Project Structure for Vercel

```
├── api/                    # Serverless functions
│   ├── index.py           # Main API entry point
│   └── requirements.txt   # Python dependencies
├── frontend/              # React app
│   ├── dist/             # Built files (auto-generated)
│   ├── src/              # Source code
│   └── package.json      # Frontend dependencies
├── src/                   # Backend Python code
├── vercel.json           # Vercel configuration
└── .vercelignore         # Files to ignore during deployment
```

## ⚙️ Configuration Files

### `vercel.json`
Main configuration file that defines:
- Build steps for frontend and backend
- Routing rules (API routes and static files)
- Serverless function settings
- Environment variables

### `api/index.py`
Entry point for serverless API functions. All API routes from FastAPI are automatically converted to serverless functions.

### `frontend/.env.production`
Production environment variables used during build:
```
VITE_API_URL=/api
```

## 🔧 Post-Deployment Configuration

### Custom Domain (Optional)
1. Go to Project Settings → Domains
2. Add your custom domain
3. Configure DNS records as shown

### Environment Variables
Add any sensitive variables in Vercel Dashboard:
- Go to Settings → Environment Variables
- Add variables (they won't be exposed to client)

### Automatic Deployments
- Every push to `main` branch triggers production deployment
- Pull requests get preview deployments automatically

## 🐛 Troubleshooting

### Build Failures

**Frontend Build Issues:**
```bash
# Test build locally
cd frontend
npm run build
```

**Python Dependencies:**
- Check `api/requirements.txt` has all dependencies
- Vercel uses Python 3.9 by default
- Large dependencies may need optimization

### API Routes Not Working

1. Check `vercel.json` routing configuration
2. Verify API base URL in frontend: `VITE_API_URL=/api`
3. Check Vercel function logs in dashboard

### Cold Starts
Serverless functions may have cold start delays (1-3 seconds). This is normal for free tier.

## 📊 Performance Optimization

1. **Frontend**
   - Code splitting is automatic with Vite
   - Use lazy loading for routes
   - Optimize images and assets

2. **Backend**
   - Minimize serverless function size
   - Use edge functions for faster response
   - Cache frequently accessed data

3. **ML Models**
   - Consider using smaller models
   - Lazy load heavy dependencies
   - Use external ML API services for large models

## 🔒 Security

1. **Environment Variables**: Never commit sensitive data
2. **CORS**: Configure properly in `src/api/main.py`
3. **Rate Limiting**: Add rate limiting for API endpoints
4. **Authentication**: Implement auth for sensitive endpoints

## 💰 Pricing Considerations

**Vercel Free Tier Includes:**
- 100 GB bandwidth
- Unlimited deployments
- 100 GB-hours serverless function execution
- 6000 build minutes

**Upgrade if you need:**
- More bandwidth
- Longer function execution time
- More build minutes
- Team collaboration features

## 📈 Monitoring

1. **Vercel Analytics**
   - Enable in Project Settings
   - Track Web Vitals and performance

2. **Function Logs**
   - View in Vercel Dashboard
   - Real-time log streaming
   - Error tracking

3. **Deployment Notifications**
   - Set up in Integrations
   - Slack, Discord, or email notifications

## 🔄 Updates and Redeployment

```bash
# Make changes to code
git add .
git commit -m "Update: description"
git push

# Vercel automatically redeploys
# Check deployment status in dashboard
```

## 📚 Additional Resources

- [Vercel Documentation](https://vercel.com/docs)
- [Vercel Python Runtime](https://vercel.com/docs/functions/serverless-functions/runtimes/python)
- [Vite Deployment Guide](https://vitejs.dev/guide/static-deploy.html)

---

**Your app will be live at:** `https://your-project-name.vercel.app`

For custom domains, configure in Vercel Dashboard → Settings → Domains
