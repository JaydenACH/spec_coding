# Respond IO Alternate Interface

A modern, real-time customer communication platform that integrates with Respond.IO to provide enhanced team collaboration and customer management capabilities.

## 🎯 Project Overview

This application serves as an alternative interface to Respond.IO, providing:
- **Role-based access control** (Basic User, Manager, System Admin)
- **Real-time customer messaging** via Respond.IO integration
- **Internal team communication** with @tagging and comments
- **Customer assignment workflow** for managers
- **File sharing capabilities** between team and customers
- **Mobile-responsive design** for on-the-go access

## 🏗️ Architecture

- **Frontend**: Next.js 14 with TypeScript, Tailwind CSS, and Zustand for state management
- **Backend**: Django 4.2 with Django REST Framework
- **Database**: PostgreSQL 15 with Redis for caching and sessions
- **Real-time**: WebSocket connections for live messaging
- **Integration**: Respond.IO API for customer communication
- **Deployment**: Docker containers with Caddy reverse proxy

## 📁 Project Structure

```
respond-io-alternate/
├── frontend/                 # Next.js application
│   ├── src/
│   │   ├── app/             # App router pages
│   │   ├── components/      # Reusable UI components
│   │   ├── hooks/           # Custom React hooks
│   │   ├── lib/             # Utility functions
│   │   ├── store/           # Zustand state management
│   │   └── types/           # TypeScript type definitions
│   ├── public/              # Static assets
│   └── package.json
├── backend/                 # Django application
│   ├── core/                # Django project settings
│   ├── apps/                # Django applications
│   │   ├── authentication/ # User auth and roles
│   │   ├── customers/       # Customer management
│   │   ├── messaging/       # Chat and comments
│   │   ├── files/           # File handling
│   │   └── notifications/   # Notification system
│   ├── requirements.txt
│   └── manage.py
├── docker/                  # Docker configuration
│   ├── frontend.Dockerfile
│   ├── backend.Dockerfile
│   └── nginx.conf
├── docker-compose.yml       # Development environment
├── docker-compose.prod.yml  # Production environment
└── docs/                    # Documentation
    ├── api/                 # API documentation
    ├── deployment/          # Deployment guides
    └── user-guide/          # User documentation
```

## 🚀 Quick Start

### Prerequisites

- **Docker & Docker Compose** (recommended)
- **Node.js 18+** and **Python 3.11+** (for local development)
- **PostgreSQL 15+** and **Redis 6+** (if running without Docker)

### Development Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd respond-io-alternate
   ```

2. **Environment Configuration**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Start with Docker (Recommended)**
   ```bash
   docker-compose up --build
   ```

4. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - Admin Panel: http://localhost:8000/admin

### Manual Setup (Alternative)

#### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

#### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
# Database Configuration
POSTGRES_DB=respond_io_db
POSTGRES_USER=respond_user
POSTGRES_PASSWORD=your_secure_password
DATABASE_URL=postgresql://respond_user:your_secure_password@localhost:5432/respond_io_db

# Redis Configuration
REDIS_URL=redis://localhost:6379/0

# Django Configuration
SECRET_KEY=your_super_secret_django_key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Respond.IO Integration
RESPOND_IO_API_URL=https://api.respond.io/v2
RESPOND_IO_API_TOKEN=your_respond_io_token
RESPOND_IO_WEBHOOK_SECRET=your_webhook_secret

# File Storage
MEDIA_ROOT=/app/media
MAX_FILE_SIZE=5242880  # 5MB in bytes

# Security
SESSION_EXPIRE_HOURS=8
PASSWORD_MIN_LENGTH=8

# Frontend Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000/api
NEXT_PUBLIC_WS_URL=ws://localhost:8000/ws
```

## 📖 Development

### Database Management

```bash
# Create and apply migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Load sample data
python manage.py loaddata fixtures/sample_data.json
```

### API Documentation

- **Development**: http://localhost:8000/api/docs/
- **Redoc**: http://localhost:8000/api/redoc/

### Testing

```bash
# Backend tests
cd backend
python manage.py test

# Frontend tests
cd frontend
npm run test

# End-to-end tests
npm run test:e2e
```

## 🚢 Deployment

### Production Deployment

1. **Prepare environment**
   ```bash
   cp .env.example .env.production
   # Configure production values
   ```

2. **Build and deploy**
   ```bash
   docker-compose -f docker-compose.prod.yml up --build -d
   ```

3. **Initialize database**
   ```bash
   docker-compose -f docker-compose.prod.yml exec backend python manage.py migrate
   docker-compose -f docker-compose.prod.yml exec backend python manage.py createsuperuser
   ```

### Respond.IO Webhook Configuration

Configure your Respond.IO webhook to point to:
```
https://your-domain.com/api/webhooks/respond-io/message
```

## 🔐 Security

- **HTTPS enforcement** in production
- **JWT token authentication** with refresh mechanism
- **Role-based access control** for all endpoints
- **Input validation and sanitization**
- **File upload security** with type and size validation
- **Rate limiting** on API endpoints

## 📋 User Roles

### Basic User (Salesperson)
- View assigned customers only
- Chat with assigned customers
- Add internal comments and tag colleagues
- Upload/download files in conversations

### Manager
- View all customers and assignments
- Assign/reassign customers to salespersons
- Access all conversations for monitoring
- All Basic User permissions

### System Admin
- User account management
- System configuration
- Full system access and monitoring
- All Manager permissions

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📞 Support

For support and questions:
- Check the [documentation](docs/)
- Create an issue in the repository
- Contact the development team

## 🗓️ Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history and updates. 