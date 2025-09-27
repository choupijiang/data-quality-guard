# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Frontend Development
```bash
cd frontend
npm install        # Install dependencies
npm run dev        # Start development server on http://localhost:5173
npm run build      # Build for production
npm run lint       # Run ESLint
npm run type-check # Run TypeScript type checking
npm run test:unit  # Run unit tests with Vitest
npm run format     # Format code with Prettier
```

### Backend Development
```bash
cd backend
pip install -r requirements.txt  # Install Python dependencies
python main.py                   # Start FastAPI development server 
```

### Quick Start Scripts
```bash
# Start both frontend and backend in development
./dev-start.sh                   # Launch both services simultaneously

# Quick start with minimal dependencies
./start.sh                       # Use simple_main.py with minimal setup

# Database management (SQLite for development)
sqlite3 backend/dq.db            # Access the SQLite database directly
```

## Architecture Overview

This is a full-stack database quality inspection system (DQ系统) for monitoring database data quality through automated SQL comparisons.

### Core Domain Model
The system inspects database quality by running comparison tasks:
- **Data Sources**: MySQL, ClickHouse, StarRocks database connections (enum: DataSourceType)
- **Inspection Tasks**: Compare actual vs expected values using SQL queries with cron scheduling
- **Task Execution**: Results stored in InspectionResults with pass/fail status and error handling
- **Alerting**: Failed task notifications and visual status indicators (green for success, red for failure)

### Backend Architecture (FastAPI)
- **Models**: SQLAlchemy ORM models in `backend/app/models/models.py` - User, DataSource, InspectionTask, InspectionResult
- **Schemas**: Pydantic validation schemas in `backend/app/schemas/schemas.py`
- **Services**: Business logic in `backend/app/services/services.py` - UserService, DataSourceService, InspectionTaskService
- **API Routes**: Domain-organized in `backend/app/api/` - auth, data_sources, inspection_tasks, projects
- **Core Configuration**: Settings via pydantic-settings in `backend/app/core/config.py`

### Frontend Architecture (Vue 3 + TypeScript)
- **Vue 3 + TypeScript**: Modern reactive framework with Composition API
- **Element Plus**: UI component library for enterprise interfaces
- **Pinia**: State management store (configured in `frontend/src/stores/`)
- **Axios**: HTTP client with JWT auth interceptors in `frontend/src/utils/api.ts`
- **Vite**: Build tool with hot reload and TypeScript support
- **Vue Router**: Client-side routing in `frontend/src/router/`

### Key Database Relationships
- Users (creator) create DataSources and InspectionTasks (foreign key relationships)
- InspectionTasks reference DataSources (many-to-one)
- InspectionResults store execution history for each task (one-to-many)
- All entities track creation/ownership and timestamps

### API Structure
All APIs prefixed with `/api/v1/`:
- `/auth` - JWT authentication (register, login, token management)
- `/data-sources` - Database connection CRUD with connection testing
- `/inspection-tasks` - Task CRUD, execution, and history
- `/projects` - Basic project management (optional feature)

### Configuration Management
- Backend: `backend/.env` with DATABASE_URL (SQLite for dev), JWT secrets, CORS origins
- Uses pydantic-settings for type-safe configuration management
- Frontend: `frontend/.env` with VITE_API_BASE_URL and app settings

## Important Implementation Notes

### SQL Query Constraints
Inspection tasks require SQL queries that return **single values only** (no multi-row/multi-column results). The system includes SQL hinting functionality based on data source schema information. Both `check_sql` and `expected_sql` must return single values or NULL/empty rows.

### Task Execution Logic
Tasks execute check_sql and expected_sql, then evaluate expressions like "check_value == expected_value". The evaluation supports operators: ==, !=, >, <, >=, <=. Results are stored in InspectionResults with boolean pass/fail status and comprehensive error handling.

### Data Source Connection Testing
- **Mandatory Connection Testing**: Users must test connections before creating data sources
- **Two Test Endpoints**: 
  - `/api/v1/data-sources/{id}/test` - Test existing data source connections
  - `/api/v1/data-sources/test-connection` - Test unsaved configurations
- **Frontend Validation**: Create button disabled until connection test passes
- **Visual Feedback**: Connection test results shown with success/error indicators

### Data Source Types
Support for MySQL, ClickHouse, and StarRocks defined in DataSourceType enum. Connection testing (`test_connection()`) and schema fetching (`get_sql_schema()`) are implemented with placeholder logic - need actual database drivers for production use.

### Authentication System
JWT-based authentication with Bearer tokens. UserService includes password hashing (bcrypt-style) and validation logic. Token expiration is 30 minutes by default. Frontend automatically handles token storage in localStorage and 401 redirects.

### Frontend API Integration
Axios is pre-configured with base URL, authentication interceptors, and Element Plus error message handling. Automatic token injection and 401 error handling with redirect to login page.

### Development Database
Uses SQLite (`backend/dq.db`) for development convenience. Schema includes automatic timestamp management (created_at, updated_at) and proper indexing for performance.

### Development Modes 
- **Simple Development**: `./start.sh`  
- **Backend Development**: `./start.sh backend`
- **Frontend Development**: `./start.sh frontend`

### Testing Framework
- Frontend: Vitest for unit tests with Vue Test Utils
- Backend: No test framework currently configured - consider adding pytest
- ESLint and TypeScript strict checking enabled

## UI/UX Design System

### Apple Design Language
The frontend uses a custom Apple-inspired design system defined in `frontend/src/assets/apple.css`:
- **Color System**: Apple brand colors (blue, green, orange, red, purple) with grayscale palette
- **Typography**: 8-step font scale from 11px to 56px
- **Spacing**: 8pt grid system with consistent spacing tokens
- **Components**: Glassmorphism effects, subtle animations, and Apple-style interactions

### Key UI Components
- **Navigation**: Apple-style header with dropdown menus and badge counts
- **Cards**: Consistent card design with proper hover states and shadows
- **Forms**: Element Plus forms customized with Apple design tokens
- **Tables**: Clean table layouts with proper spacing and typography
- **Buttons**: Apple-style button variants (primary, secondary, etc.)

### Page Structure
- **HomeView**: Compact hero section with enhanced statistics display
- **DataSourcesView**: Table layout with connection testing and management
- **ProjectsView**: Project management with task statistics
- **InspectionTasksView**: Task management with execution history

### Responsive Design
- Mobile-first approach with breakpoints at 768px and 480px
- Grid layouts that adapt to screen size
- Collapsible navigation for mobile devices
- Touch-friendly interaction targets