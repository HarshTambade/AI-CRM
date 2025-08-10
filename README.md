# AI-Powered CRM System

A comprehensive Customer Relationship Management system enhanced with Artificial Intelligence capabilities, built to run efficiently on systems with limited resources (8GB RAM, CPU-only).

## 🚀 Features

### Core CRM Features
- **Contact Management**: Complete customer profiles with interaction history
- **Lead Management**: Lead tracking, scoring, and conversion pipeline
- **Sales Pipeline**: Visual sales funnel with stage management
- **Task Management**: Automated task creation and reminders
- **Email Integration**: Email tracking and automated responses
- **Reporting & Analytics**: Real-time dashboards and insights
- **Role-Based Access Control**: Multi-level user permissions
- **Mobile Responsive**: Works on all devices

### AI-Powered Features
- **Predictive Lead Scoring**: AI ranks leads based on behavior patterns
- **Sales Forecasting**: Revenue prediction using historical data
- **Smart Email Suggestions**: AI-generated email responses and follow-ups
- **Sentiment Analysis**: Analyze customer communication tone
- **Churn Prediction**: Identify customers likely to leave
- **Next Best Action**: AI recommendations for sales reps
- **Duplicate Detection**: Automatic customer record merging
- **Voice-to-Text**: Call transcription and analysis
- **Smart Data Entry**: Auto-completion using AI

## 🛠️ Technology Stack

### Backend
- **Python 3.9+**: Core application logic
- **FastAPI**: High-performance web framework
- **SQLAlchemy**: Database ORM
- **PostgreSQL/SQLite**: Database (SQLite for development)
- **Pydantic**: Data validation

### AI/ML Stack
- **Hugging Face Transformers**: Free pre-trained models
- **Sentence Transformers**: Text embeddings
- **Scikit-learn**: Traditional ML models
- **NLTK**: Natural language processing
- **Pandas/NumPy**: Data manipulation

### Frontend
- **React 18**: Modern UI framework
- **TypeScript**: Type safety
- **Tailwind CSS**: Utility-first styling
- **React Query**: Data fetching and caching
- **React Hook Form**: Form management

### Infrastructure
- **Docker**: Containerization
- **SQLite**: Lightweight database for development
- **JWT**: Authentication
- **Redis**: Caching (optional)

## 📋 System Requirements

### Minimum Requirements
- **RAM**: 8GB
- **Storage**: 20GB SSD
- **CPU**: Multi-core processor
- **OS**: Windows 10/11, macOS, or Linux

### Recommended Requirements
- **RAM**: 16GB
- **Storage**: 50GB SSD
- **CPU**: 4+ cores
- **Internet**: For downloading AI models

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Node.js 18+
- Git

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd ai-crm
```

2. **Backend Setup**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. **Frontend Setup**
```bash
cd frontend
npm install
```

4. **Environment Configuration**
```bash
# Copy environment files
cp .env.example .env
# Edit .env with your configuration
```

5. **Database Setup**
```bash
cd backend
python manage.py init_db
```

6. **Start the Application**
```bash
# Terminal 1 - Backend
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2 - Frontend
cd frontend
npm run dev
```

7. **Access the Application**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## 🏗️ Project Structure

```
ai-crm/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── models/
│   │   ├── services/
│   │   ├── ai/
│   │   └── utils/
│   ├── requirements.txt
│   └── main.py
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── hooks/
│   │   ├── services/
│   │   └── utils/
│   ├── package.json
│   └── tailwind.config.js
├── docs/
├── tests/
└── README.md
```

## 🔐 Role-Based Access Control

### User Roles
1. **Super Admin**: Full system access
2. **Admin**: User management and system configuration
3. **Manager**: Team oversight and reporting
4. **Sales Rep**: Lead and opportunity management
5. **Support Agent**: Customer service and ticket management
6. **Viewer**: Read-only access to assigned data

### Permissions Matrix
| Feature | Super Admin | Admin | Manager | Sales Rep | Support | Viewer |
|---------|-------------|-------|---------|-----------|---------|--------|
| User Management | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |
| System Settings | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |
| Team Management | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ |
| Lead Management | ✅ | ✅ | ✅ | ✅ | ❌ | 👁️ |
| Sales Pipeline | ✅ | ✅ | ✅ | ✅ | ❌ | 👁️ |
| Customer Data | ✅ | ✅ | ✅ | ✅ | ✅ | 👁️ |
| Reports | ✅ | ✅ | ✅ | 👁️ | 👁️ | 👁️ |
| AI Features | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ |

## 🤖 AI Models Used

### Free Hugging Face Models
- **Lead Scoring**: `sentence-transformers/all-MiniLM-L6-v2`
- **Sentiment Analysis**: `cardiffnlp/twitter-roberta-base-sentiment-latest`
- **Text Generation**: `microsoft/DialoGPT-medium`
- **Named Entity Recognition**: `dslim/bert-base-NER`
- **Text Classification**: `distilbert-base-uncased`

### Model Optimization
- **Quantization**: 8-bit quantization for reduced memory usage
- **Model Caching**: Local caching to avoid repeated downloads
- **Batch Processing**: Efficient batch operations
- **Memory Management**: Automatic garbage collection

## 📊 Key Features Deep Dive

### 1. Predictive Lead Scoring
- Analyzes lead behavior patterns
- Considers engagement history, demographics, and interactions
- Provides confidence scores for conversion likelihood
- Updates scores in real-time

### 2. Sales Forecasting
- Time-series analysis of historical data
- Seasonal trend detection
- Pipeline velocity calculations
- Revenue prediction with confidence intervals

### 3. Smart Email Suggestions
- Context-aware response generation
- Tone matching based on customer history
- Follow-up timing recommendations
- Template suggestions based on deal stage

### 4. Sentiment Analysis
- Real-time communication analysis
- Customer satisfaction tracking
- Escalation triggers for negative sentiment
- Trend analysis over time

### 5. Churn Prediction
- Behavioral pattern analysis
- Usage decline detection
- Risk scoring algorithms
- Proactive retention strategies

## 🔧 Configuration

### Environment Variables
```bash
# Database
DATABASE_URL=sqlite:///./ai_crm.db

# Security
SECRET_KEY=your-secret-key
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# AI Models
HUGGINGFACE_CACHE_DIR=./models
MODEL_DEVICE=cpu

# Email
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# Redis (Optional)
REDIS_URL=redis://localhost:6379
```

## 🧪 Testing

### Backend Tests
```bash
cd backend
pytest tests/
```

### Frontend Tests
```bash
cd frontend
npm test
```

### AI Model Tests
```bash
cd backend
python -m pytest tests/test_ai/
```

## 📈 Performance Optimization

### Memory Management
- Model lazy loading
- Automatic garbage collection
- Memory-efficient data processing
- Batch size optimization

### Response Time
- Model caching
- Database query optimization
- API response compression
- Frontend code splitting

## 🔒 Security Features

- **JWT Authentication**: Secure token-based auth
- **Password Hashing**: bcrypt encryption
- **Input Validation**: Comprehensive data validation
- **SQL Injection Protection**: Parameterized queries
- **XSS Protection**: Content Security Policy
- **Rate Limiting**: API request throttling
- **Audit Logging**: Complete action tracking

## 🚀 Deployment

### Docker Deployment
```bash
# Build and run with Docker
docker-compose up --build
```

### Production Setup
1. Use PostgreSQL instead of SQLite
2. Configure Redis for caching
3. Set up proper SSL certificates
4. Configure backup strategies
5. Set up monitoring and logging

## 📚 API Documentation

Comprehensive API documentation is available at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Create an issue on GitHub
- Check the documentation
- Review the troubleshooting guide

## 🔄 Updates and Maintenance

- Regular model updates from Hugging Face
- Security patches and updates
- Performance optimizations
- Feature enhancements

---

**Built with ❤️ for efficient AI-powered customer relationship management**
