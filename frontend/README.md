# Resume Intelligence System - Frontend

A modern React TypeScript frontend for the Resume Intelligence System, providing an intuitive interface for AI-powered resume generation, screening, and content creation.

## 🚀 Features

### 🏠 **Dashboard & Overview**
- Real-time system status monitoring
- Usage statistics and performance metrics  
- Interactive feature navigation
- System health indicators

### 📝 **Resume Generation**
- AI-powered resume creation with multiple templates
- Experience level optimization (Entry/Mid/Senior)
- Job description-based tailoring
- ATS-friendly formatting options
- Real-time preview and download

### 🔍 **Resume Screening**
- Upload and analyze resumes against job descriptions
- Section-wise scoring with detailed feedback
- Missing keyword identification
- Improvement suggestions with explanations
- Visual performance metrics

### ✍️ **Content Generation**
- Professional email templates
- Compelling cover letter creation
- LinkedIn message optimization
- Tone control (Professional/Friendly/Formal)
- Context-aware customization

### 📊 **Analytics Dashboard**
- Performance metrics visualization
- Model evaluation tools
- System usage statistics  
- Real-time health monitoring

## 🛠️ Tech Stack

- **Framework**: React 19 + TypeScript
- **Build Tool**: Vite 7
- **Styling**: Tailwind CSS 3 with custom components
- **Routing**: React Router 6
- **HTTP Client**: Axios with interceptors
- **State Management**: React Hooks
- **UI Components**: Custom component library
- **Icons**: Emoji + Custom SVG

## 🚦 Getting Started

### Prerequisites
- Node.js 18+ 
- npm or yarn
- Backend API running on `http://127.0.0.1:8000`

### Installation

1. **Install dependencies**
   ```bash
   npm install
   ```

2. **Start development server**  
   ```bash
   npm run dev
   ```
   
3. **Open browser**
   ```
   http://localhost:3001
   ```

### Build for Production

```bash
# Create optimized build
npm run build

# Preview production build
npm run preview
```

## 🎨 UI/UX Design

### Design System
- **Colors**: Primary blue (#3b82f6), semantic colors for states
- **Typography**: Inter font family, systematic text scales
- **Components**: Consistent spacing (4px grid), rounded corners
- **Animations**: Smooth transitions, loading states
- **Responsive**: Mobile-first design with breakpoints

### Component Library
- `Button`: Multiple variants (primary, secondary, outline, ghost)
- `Input/Textarea`: Consistent form styling with validation
- `Loading`: Animated spinners with contextual messages  
- `Card`: Content containers with consistent styling
- `Layout`: Header navigation + main content + footer

## 🔗 API Integration

### Service Layer
```typescript
// services/api.ts
export const apiService = {
  generateResume: (request: GenerationRequest) => 
    api.post('/api/v1/generate/resume', request),
  
  screenResume: (request: ScreeningRequest) => 
    api.post('/api/v1/screen/resume', request),
  
  generateContent: (request: ContentGenerationRequest) => 
    api.post('/api/v1/generate/content', request),
  
  // ... other endpoints
};
```

### Error Handling
- Axios interceptors for request/response logging
- Consistent error message display
- Loading state management
- Retry mechanisms for failed requests

## 🚀 Deployment

### Production Build
```bash
npm run build
```

### Static Hosting
The built files in `dist/` can be deployed to:
- Vercel, Netlify, AWS S3 + CloudFront, GitHub Pages

### Environment Configuration
Update API base URL for production:
```env
VITE_API_BASE_URL=https://api.yourdomain.com
```

---

**Built with ❤️ using React + TypeScript + Tailwind CSS**
