# 🔗 FastAPI URL Shortener with Advanced Analytics

A production-ready URL shortener API built with FastAPI, featuring comprehensive analytics, user authentication, and enterprise-grade security.

## ✨ Features

### 🔐 Authentication & Security
- User registration and login with JWT tokens
- Password hashing with bcrypt
- OAuth2 compatible authentication
- Profile management and password changes
- Security headers and CORS protection

### 🔗 Link Management
- Create short links (authenticated or anonymous)
- Custom aliases for branded short URLs
- Edit and update existing links
- Delete individual or bulk links
- View all user's links with pagination

### 📊 Advanced Analytics
- **Real-time click tracking** with detailed insights
- **Device analytics**: Browser, OS, device type/brand detection
- **Geographic analytics**: Country, city, timezone, ISP tracking
- **Unique visitor detection** with session tracking
- **Time-based analytics**: Hourly, daily, weekly patterns
- **Export functionality**: JSON and CSV export
- **Analytics dashboard** for overview statistics

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- pip (Python package manager)

### Installation

1. **Clone the repository**
```bash
git clone <your-repo-url>
cd myapp
```

2. **Create virtual environment**
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables**
Create a `.env` file:
```env
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///./test.db
ENVIRONMENT=development
ALLOWED_ORIGINS=["http://localhost:3000", "http://127.0.0.1:8000"]
```

5. **Run database migrations**
```bash
# Basic database setup (if needed)
python -c "from database import engine; import models; models.Base.metadata.create_all(bind=engine)"

# Advanced analytics migration
python migrate_analytics_advanced.py
```

6. **Start the server**
```bash
uvicorn main:app --reload
```

The API will be available at `http://127.0.0.1:8000`

## 📖 API Documentation

### Interactive Documentation
- **Swagger UI**: http://127.0.0.1:8000/docs
- **ReDoc**: http://127.0.0.1:8000/redoc

### Authentication Endpoints
```
POST /auth/register          # Create new account
POST /auth/login             # User login
POST /auth/token             # OAuth2 token endpoint
POST /auth/refresh           # Refresh access token
```

### Link Management Endpoints
```
POST /links/create           # Create short link
GET  /links/my-links         # Get user's links
PUT  /links/{link_id}        # Update link
DELETE /links/{link_id}      # Delete link
DELETE /links/bulk-delete    # Delete multiple links
```

### Analytics Endpoints
```
GET /analytics/dashboard                    # User dashboard overview
GET /analytics/{link_id}/overview          # Complete link analytics
GET /analytics/{link_id}/devices           # Device & browser stats
GET /analytics/{link_id}/geography         # Geographic distribution
GET /analytics/{link_id}/timeline          # Time-based analytics
GET /analytics/{link_id}/clicks            # Raw click data
GET /analytics/{link_id}/export            # Export data (JSON/CSV)
```

### Profile Management
```
GET  /profile/me             # Get user profile
PUT  /profile/update         # Update profile
POST /profile/change-password # Change password
```

## 💡 Usage Examples

### Creating a Short Link
```bash
curl -X POST "http://127.0.0.1:8000/links/create" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://www.example.com",
    "alias": "my-link"
  }'
```

### Getting Analytics
```bash
curl -X GET "http://127.0.0.1:8000/analytics/1/overview" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## 🏗️ Project Structure

```
myapp/
├── analytics/              # Analytics module
│   ├── __init__.py
│   ├── models.py          # LinkClick model
│   ├── parser.py          # User agent & IP parsing
│   ├── tracker.py         # Click tracking service
│   └── routes.py          # Analytics API endpoints
├── routes/                # API route modules
│   ├── auth.py           # Authentication routes
│   ├── links.py          # Link management routes
│   └── profile.py        # User profile routes
├── main.py               # FastAPI application
├── models.py             # Database models
├── schemas.py            # Pydantic schemas
├── database.py           # Database configuration
├── auth.py              # Authentication utilities
├── config.py            # Application settings
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

## 📊 Analytics Features

### Device Detection
- **Browsers**: Chrome, Firefox, Safari, Edge + versions
- **Operating Systems**: Windows, macOS, iOS, Android, Linux
- **Device Types**: Desktop, Mobile, Tablet
- **Device Brands**: Apple, Samsung, Google, etc.

### Geographic Analytics
- **Location**: Country, city, region detection
- **Network**: ISP and timezone information
- **Privacy**: IP address masking for compliance

### Behavioral Tracking
- **Unique Visitors**: Advanced fingerprinting
- **Session Tracking**: Multiple clicks per visitor
- **Referrer Analysis**: Traffic source identification
- **Bot Detection**: Automated traffic filtering

## 🔧 Configuration

### Environment Variables
- `SECRET_KEY`: JWT signing key
- `DATABASE_URL`: Database connection string
- `ENVIRONMENT`: development/production
- `ALLOWED_ORIGINS`: CORS allowed origins

### Database
- Default: SQLite (for development)
- Production: PostgreSQL/MySQL supported
- Automatic migrations included

## 🚀 Deployment

### Docker (Recommended)
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Production Considerations
- Use PostgreSQL for production database
- Set up environment variables securely
- Configure proper CORS origins
- Use HTTPS with SSL certificates
- Set up monitoring and logging

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-feature`)
3. Commit your changes (`git commit -am 'Add new feature'`)
4. Push to the branch (`git push origin feature/new-feature`)
5. Create a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Create an issue in the GitHub repository
- Check the API documentation at `/docs`
- Review the analytics dashboard for usage insights

## 🔮 Roadmap

- [ ] QR code generation for links
- [ ] Custom domains support
- [ ] Link expiration dates
- [ ] Password-protected links
- [ ] Team collaboration features
- [ ] Advanced reporting and insights
- [ ] Webhook notifications
- [ ] API rate limiting enhancements

---

**Built with ❤️ using FastAPI, SQLAlchemy, and modern Python practices.**
