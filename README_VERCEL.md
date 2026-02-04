# Resume Intelligence System

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/yourusername/resume-intelligence-system)

A production-grade ML-driven resume intelligence system that provides end-to-end resume analysis, generation, and screening capabilities. **Now serverless and ready for Vercel deployment!**

## 🚀 Features

- **Resume Generation**: AI-powered ATS-friendly resume creation with template selection
- **LaTeX Resume Generation**: Professional LaTeX resume templates with customization
- **Resume Screening**: ML-based candidate matching with explainable AI
- **Content Generation**: Professional emails, cover letters, and LinkedIn prompts
- **Skill Gap Analysis**: Detailed feedback on missing competencies
- **Analytics Dashboard**: Performance metrics and insights
- **Serverless Architecture**: Zero-config deployment to Vercel

## 🏗️ Architecture

```
Frontend (React/TypeScript/Vite) → Serverless API (FastAPI/Python) → ML Pipeline (scikit-learn/BERT)
                                   ↓
                              Vercel Edge Network
```

## 🛠️ Tech Stack

### Frontend
- **Framework**: React 19 with TypeScript
- **Styling**: Tailwind CSS
- **Build Tool**: Vite
- **Routing**: React Router v6
- **Deployment**: Vercel

### Backend
- **Framework**: FastAPI (Serverless Functions)
- **ML/NLP**: scikit-learn, sentence-transformers, NLTK
- **Data**: Pandas, NumPy
- **Deployment**: Vercel Python Runtime

## 🚀 Quick Start

### Local Development

1. **Clone the repository**
```bash
git clone <your-repo-url>
cd resume-intelligence-system
```

2. **Backend Setup**
```bash
# Install Python dependencies
pip install -r requirements.txt

# Start the API server
python -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000
```

3. **Frontend Setup**
```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

4. **Access the Application**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

## ☁️ Deploy to Vercel

### One-Click Deploy

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/yourusername/resume-intelligence-system)

### Manual Deployment

1. **Push to Git**
```bash
git init
git add .
git commit -m "Initial commit"
git push -u origin main
```

2. **Import to Vercel**
   - Go to [vercel.com/new](https://vercel.com/new)
   - Import your repository
   - Vercel auto-detects configuration
   - Click "Deploy"

3. **Done!** Your app is live at `https://your-app.vercel.app`

For detailed deployment instructions, see [DEPLOYMENT.md](DEPLOYMENT.md)

## 📁 Project Structure

```
├── api/                    # Serverless API functions
│   ├── index.py           # API entry point
│   └── requirements.txt   # Python dependencies
├── src/                    # Backend Python code
│   ├── api/               # FastAPI endpoints
│   ├── models/            # Data models
│   ├── generation/        # Resume generation
│   ├── screening/         # ML screening
│   └── utils/             # Utilities
├── frontend/              # React application
│   ├── src/
│   │   ├── components/    # React components
│   │   ├── pages/         # Application pages
│   │   ├── services/      # API services
│   │   └── types/         # TypeScript types
│   └── dist/              # Build output
├── data/                  # Data storage
├── configs/               # Configuration
├── vercel.json           # Vercel configuration
└── DEPLOYMENT.md         # Deployment guide
```

## 🔧 Configuration

### Environment Variables

Create `.env.local` files for local development:

**Root `.env`:**
```bash
# Copy from .env.example
cp .env.example .env
```

**Frontend `.env.development`:**
```bash
VITE_API_URL=http://localhost:8000
```

**Frontend `.env.production`:**
```bash
VITE_API_URL=/api
```

### Vercel Environment Variables

Set in Vercel Dashboard → Settings → Environment Variables:
```
VITE_API_URL=/api
NODE_ENV=production
```

## 🔧 API Endpoints

### Core Features
- `POST /api/v1/generate/resume` - Generate tailored resume
- `POST /api/v1/generate/resume/latex` - Generate LaTeX resume
- `POST /api/v1/screen/resume` - Screen resume against job
- `POST /api/v1/generate/content` - Generate emails/cover letters

### Utilities
- `GET /health` - Health check
- `GET /api/v1/data/stats` - Data statistics
- `POST /api/v1/data/generate` - Generate synthetic data

Full API documentation available at `/docs` when running

## 🧪 Testing

```bash
# Run backend tests
python test_system.py

# Build frontend (checks for compilation errors)
cd frontend && npm run build

# Test serverless deployment locally
vercel dev
```

## 📊 Key Features

- ✅ **Serverless Architecture** - Zero server management
- ✅ **Auto-scaling** - Handles traffic spikes automatically
- ✅ **Global CDN** - Fast loading worldwide
- ✅ **CI/CD** - Automatic deployments on git push
- ✅ **Preview Deployments** - Every PR gets a preview URL
- ✅ **Environment Variables** - Secure configuration management
- ✅ **TypeScript** - Full type safety
- ✅ **ML/AI Integration** - Advanced resume intelligence

## 🚀 Performance

- **Frontend**: Optimized Vite build with code splitting
- **Backend**: Serverless functions with auto-scaling
- **ML Models**: Lazy-loaded for optimal cold start performance
- **CDN**: Global edge network for fast delivery

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙋‍♂️ Support

For questions and support, please open an issue in the GitHub repository.

## 📚 Documentation

- [Deployment Guide](DEPLOYMENT.md) - Complete Vercel deployment instructions
- [API Documentation](http://localhost:8000/docs) - Interactive API docs (when running locally)
- [Contributing Guidelines](CONTRIBUTING.md) - How to contribute

---

**Built with ❤️ using modern serverless architecture and ML technologies**

**Live Demo**: [https://your-app.vercel.app](https://your-app.vercel.app)
