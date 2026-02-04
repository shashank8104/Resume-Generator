# Resume Intelligence System

A production-grade ML-driven resume intelligence system that provides end-to-end resume analysis, generation, and screening capabilities.

## 🚀 Features

- **Resume Generation**: AI-powered ATS-friendly resume creation with template selection
- **LaTeX Resume Generation**: Professional LaTeX resume templates with customization
- **Resume Screening**: ML-based candidate matching with explainable AI
- **Content Generation**: Professional emails, cover letters, and LinkedIn prompts
- **Skill Gap Analysis**: Detailed feedback on missing competencies
- **Analytics Dashboard**: Performance metrics and insights

## 🏗️ Architecture

```
Frontend (React/TypeScript) ↔ Backend API (FastAPI/Python) ↔ ML Pipeline (scikit-learn/BERT)
```

## 🛠️ Tech Stack

### Backend
- **Framework**: FastAPI
- **ML/NLP**: scikit-learn, sentence-transformers, NLTK
- **Data**: Pandas, NumPy
- **Database**: JSON-based storage with metadata management

### Frontend
- **Framework**: React 19 with TypeScript
- **Styling**: Tailwind CSS
- **Build Tool**: Vite
- **Routing**: React Router v6

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- npm or yarn

### Installation

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

## 📁 Project Structure

```
├── src/                    # Backend Python code
│   ├── api/               # FastAPI endpoints and middleware
│   ├── data/              # Data management and synthetic generation
│   ├── models/            # Pydantic schemas and data models
│   ├── generation/        # Resume and content generation
│   ├── screening/         # ML-based resume screening
│   ├── explainability/    # AI explainability engine
│   ├── evaluation/        # Model evaluation and metrics
│   └── utils/             # Shared utilities and helpers
├── frontend/              # React TypeScript frontend
│   ├── src/
│   │   ├── components/    # Reusable React components
│   │   ├── pages/         # Application pages/routes
│   │   ├── services/      # API service layer
│   │   └── types/         # TypeScript type definitions
│   └── public/            # Static assets
├── data/                  # Data storage and templates
├── configs/               # Configuration files
└── logs/                  # Application logs
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

## 🧪 Testing

```bash
# Run backend tests
python test_system.py

# Build frontend (checks for compilation errors)
cd frontend && npm run build
```

## 🚀 Deployment

### Production Build
```bash
# Frontend production build
cd frontend && npm run build

# Backend with production server
pip install gunicorn
gunicorn -w 4 -k uvicorn.workers.UvicornWorker src.api.main:app
```

## 📊 Key Design Principles

- **ML-First Architecture**: Production-ready ML pipelines
- **Explainable AI**: All decisions are interpretable
- **Modular Design**: Clean separation of concerns
- **Type Safety**: Full TypeScript frontend, Pydantic backend
- **Production Ready**: Comprehensive logging, error handling, validation

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

---

**Built with ❤️ using modern ML and web technologies**