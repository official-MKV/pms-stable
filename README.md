# NIGCOMSAT Performance Management System (PMS)

A comprehensive performance management platform for Nigerian Communications Satellite Limited (NIGCOMSAT) to streamline goal setting, task management, performance reviews, and organizational analytics.

## 🚀 Features

### Phase 1: Foundation & Authentication (COMPLETED)
- ✅ SuperAdmin-driven system initialization
- ✅ JWT-based authentication system
- ✅ Dynamic role and permission management
- ✅ User management with invitation system
- ✅ Real-time WebSocket communication
- ✅ Redis caching and session management

### Upcoming Phases
- **Phase 2**: Organizational structure builder, task management system
- **Phase 3**: Goal management, performance reviews, analytics dashboard

## 🏗️ Technology Stack

### Backend
- **FastAPI** - Modern Python web framework
- **SQLAlchemy** - Python SQL toolkit and ORM
- **PostgreSQL 15** - Primary database
- **Redis** - Caching and WebSocket support
- **JWT** - Authentication tokens
- **WebSockets** - Real-time communication

### Frontend
- **Next.js 14+** - React framework with App Router
- **shadcn/ui** - Modern UI components
- **TailwindCSS** - Utility-first CSS framework
- **TanStack Query** - Data fetching and caching
- **React Hook Form** - Form management

### Infrastructure
- **Docker & Docker Compose** - Containerization
- **Nginx** - Reverse proxy and load balancer
- **Windows Server 2019** - Target deployment platform

## 🛠️ Development Setup

### Prerequisites
- Docker Desktop with Windows containers support
- Git for version control
- A code editor (VS Code recommended)

### Quick Start

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd PMS
   ```

2. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Start the development environment**
   ```bash
   docker-compose up -d
   ```

4. **Initialize the database and create SuperAdmin**
   - Navigate to http://localhost:3000
   - Click "Create SuperAdmin Account"
   - Fill in the required information
   - This creates the first user with full system access

### Development URLs
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **RedisInsight**: http://localhost:8001
- **Nginx (Production)**: http://localhost:80

### Database Commands

**Backup Database**
```bash
docker exec pms_postgres pg_dump -U pms_user pms_db > backup.sql
```

**Restore Database**
```bash
cat backup.sql | docker exec -i pms_postgres psql -U pms_user -d pms_db
```

**Access Database Console**
```bash
docker exec -it pms_postgres psql -U pms_user -d pms_db
```

### Backend Development

**Install dependencies locally (for IDE support)**
```bash
cd backend
pip install -r requirements.txt
```

**Run backend in development mode**
```bash
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Database migrations**
```bash
# Generate migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head
```

### Frontend Development

**Install dependencies**
```bash
cd frontend
npm install
```

**Run frontend in development mode**
```bash
cd frontend
npm run dev
```

**Build for production**
```bash
cd frontend
npm run build
```

## 🔒 Initial SuperAdmin Setup

The system is designed with a SuperAdmin-first approach:

1. **First User**: The first registered user automatically becomes SuperAdmin
2. **Full Control**: SuperAdmin has complete system access and configuration rights
3. **System Configuration**: SuperAdmin must configure organizational structure before adding other users
4. **Role Creation**: SuperAdmin creates all custom roles and assigns permissions

### SuperAdmin Responsibilities
- Configure organizational nomenclature and structure
- Create and manage custom roles
- Set up permission frameworks
- Invite and manage users
- Configure system-wide settings

## 📡 WebSocket Communication

The system includes real-time features via WebSocket:

### Connection
```javascript
const ws = new WebSocket(`ws://localhost:8000/api/ws/ws/${token}`)
```

### Message Types
- `ping/pong` - Connection health check
- `presence_update` - User online/offline status
- `task_assigned` - Real-time task notifications
- `chat_message` - Group communication
- `notification` - System notifications

## 🔐 Authentication & Permissions

### JWT Token Structure
- **Access Token**: Short-lived (30 minutes default)
- **Scopes**: User permissions and roles
- **Claims**: User ID, username, superuser status

### Permission System
- **Granular Permissions**: Feature-specific access control
- **Role-Based**: Group permissions into roles
- **Scope-Based**: Department, directorate, or global access
- **Dynamic**: SuperAdmin can create custom permissions

### Default Permission Categories
- `users:*` - User management
- `roles:*` - Role management
- `tasks:*` - Task management
- `goals:*` - Goal management
- `system:*` - System configuration

## 🏢 Organizational Structure

The system supports flexible organizational hierarchies:

- **Configurable Levels**: 2-5 levels deep
- **Custom Nomenclature**: Define your own terms (Directorate, Department, Unit, etc.)
- **Leadership Roles**: Assign heads to organizational units
- **Permission Inheritance**: Roles can be scoped to organizational levels

## 📊 Monitoring & Logging

### Application Logs
- Request/response logging via middleware
- WebSocket connection tracking
- Authentication attempts
- Error tracking

### Health Checks
- **Backend**: `/health` endpoint
- **Database**: Connection status
- **Redis**: Cache connectivity
- **WebSocket**: Connection count

## 🚀 Deployment

### Development Deployment
```bash
docker-compose up -d
```

### Production Deployment
1. Update environment variables in `.env`
2. Configure SSL certificates in `ssl/` directory
3. Update Nginx configuration for your domain
4. Start with production compose file

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DB_PASSWORD` | PostgreSQL password | `pms_secure_password` |
| `JWT_SECRET_KEY` | JWT signing key | Generate secure key |
| `CORS_ALLOWED_ORIGINS` | Frontend URLs | `http://localhost:3000` |
| `DEBUG` | Debug mode | `False` |

## 🧪 Testing

### Backend Tests
```bash
cd backend
pytest
```

### Frontend Tests
```bash
cd frontend
npm test
```

### API Testing
Use the built-in documentation at http://localhost:8000/docs

## 📈 Performance Optimization

### Caching Strategy
- **Redis**: Session data, user permissions
- **Query Caching**: Frequently accessed data
- **WebSocket State**: Connection management

### Database Optimization
- **Indexes**: On frequently queried columns
- **Connection Pooling**: SQLAlchemy connection management
- **Query Optimization**: Efficient joins and filters

## 🔧 Troubleshooting

### Common Issues

**Container won't start**
```bash
docker-compose logs [service-name]
```

**Database connection errors**
- Check PostgreSQL container status
- Verify connection string in environment

**Frontend can't reach API**
- Verify CORS settings
- Check network connectivity between containers

**WebSocket connection fails**
- Verify JWT token is valid
- Check WebSocket URL configuration

### Reset Development Environment
```bash
docker-compose down -v
docker-compose up -d
```

## 📞 Support

For technical support and questions:
- Check the troubleshooting section above
- Review Docker container logs
- Verify environment configuration

## 🚧 Roadmap

### Phase 2 (Next)
- Organizational structure builder
- Advanced task management
- Goal setting and tracking
- Performance review system

### Phase 3 (Future)
- Analytics dashboard
- Reporting system
- Mobile application
- Advanced integrations