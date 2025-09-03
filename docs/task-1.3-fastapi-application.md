# Task 1.3: Core FastAPI Application

## Objective
Create the foundational FastAPI application with proper structure, configuration management, health checks, logging, and testing framework. The application will work with local job data stored as markdown files in the `data/jobs/` directory and prepare for future integration with a single job board endpoint.

## Configuration Enhancement

### Enhanced config.yaml Structure
```yaml
# Existing Azure configuration (from Task 1.2)
azure_openai:
  endpoint: "https://rag-cog.openai.azure.com/"
  api_version: "2024-02-15-preview"
  deployment_name: "gpt-4o-mini"
  model: "gpt-4o-mini"
  max_tokens: 4096
  temperature: 0.7

azure:
  resource_group: "generic-rag"
  subscription: "Sogeti AI Team"

# New FastAPI configuration
api:
  host: "0.0.0.0"
  port: 8000
  cors_origins: ["*"]
  docs_url: "/docs"
  redoc_url: "/redoc"

# Job data configuration
jobs:
  data_directory: "data/jobs"
  file_format: "markdown"
  refresh_interval: 300  # seconds

# Future job board integration (placeholder)
job_board:
  endpoint: null  # To be configured later
  api_key: null   # To be configured later
  poll_interval: 3600  # seconds

logging:
  level: "INFO"
  format: "json"
  file: null

health_checks:
  cache_ttl: 30  # seconds
  timeout: 5     # seconds
```

### Integration with Existing Components
## Tasks Breakdown

### 1.3.1 FastAPI Application Structure
- [ ] Create main FastAPI application instance
- [ ] Set up application factory pattern
- [ ] Configure CORS and middleware
- [ ] Implement application lifecycle events
- [ ] Set up dependency injection container

### 1.3.2 API Router Organization
- [ ] Create modular router structure:
  - Health check router
  - Job management router (local data from `data/jobs/`)
  - Application workflow router
- [ ] Implement proper API versioning (v1)
- [ ] Set up OpenAPI/Swagger documentation
- [ ] Add API request/response models for job processing

### 1.3.3 Configuration Management
- [ ] Enhance existing Pydantic configuration classes
- [ ] Add FastAPI-specific settings to existing Settings class
- [ ] Integrate with existing config.yaml structure
- [ ] Add API-specific configuration validation
- [ ] Enhance configuration testing utilities

### 1.3.4 Health Check Implementation
- [ ] Create basic health check endpoint
- [ ] Add detailed health checks:
  - Azure OpenAI service status (using existing service)
  - Local job data directory access and validation
  - Configuration validation
  - System resource monitoring
- [ ] Implement health check aggregation
- [ ] Add health check caching

### 1.3.5 Logging Infrastructure
- [ ] Set up structured logging with JSON format
- [ ] Configure log levels and rotation
- [ ] Add correlation IDs for request tracing
- [ ] Implement centralized logging patterns
- [ ] Add performance logging and metrics

### 1.3.6 Job Data Management
- [ ] Create job data service for reading markdown files from `data/jobs/`
- [ ] Implement job parsing and validation
- [ ] Add job data caching and refresh mechanisms
- [ ] Create job filtering and search capabilities
- [ ] Prepare structure for future job board API integration

### 1.3.7 Testing Framework Setup
- [ ] Configure pytest with FastAPI test client
- [ ] Set up test database and fixtures
- [ ] Create test utilities and helpers
- [ ] Implement test coverage reporting
- [ ] Add API integration test patterns

## Deliverables
1. Functional FastAPI application
2. Organized router structure with local job data support
3. Comprehensive configuration system
4. Working health checks
5. Structured logging system
6. Job data management service for markdown files
7. Complete testing framework

## Acceptance Criteria
- [ ] FastAPI application starts successfully
- [ ] Health check endpoints return proper status
- [ ] Job data can be read and parsed from `data/jobs/` directory
- [ ] API documentation is accessible via Swagger
- [ ] Logging works with structured output
- [ ] All tests pass with good coverage
- [ ] Configuration is properly validated

## Dependencies
- Task 1.1 (Project Setup) completed ✅
- Task 1.2 (Azure Integration) completed ✅
- UV package management working ✅
- Existing Pydantic configuration system ✅
- Azure OpenAI service integration ✅

## Estimated Time
**4-5 days**

## Key Packages
```toml
[project.dependencies]
fastapi = "^0.116.0"           # Latest stable version
uvicorn = "^0.35.0"            # Latest stable version
pydantic = "^2.11.0"           # Already installed
pydantic-settings = "^2.10.0"  # Already installed
structlog = "^25.4.0"          # Already installed
httpx = "^0.28.0"              # Already installed
python-multipart = "^0.0.20"   # For form data handling
```

## Files to Create/Modify
```
src/job_agent/
├── __init__.py
├── main.py                    # Update existing entry point
├── app.py                     # New FastAPI application factory
├── api/
│   ├── __init__.py
│   ├── deps.py               # Dependency injection
│   ├── v1/
│   │   ├── __init__.py
│   │   ├── health.py         # Health check endpoints
│   │   ├── jobs.py           # Job management (local data)
│   │   └── applications.py   # Application workflow
│   └── middleware.py         # Custom middleware
├── core/
│   ├── __init__.py
│   ├── config.py             # Enhance existing configuration
│   ├── logging.py            # New logging infrastructure
│   └── health.py             # Health check logic
├── models/
│   ├── __init__.py
│   ├── api.py                # API request/response models
│   ├── job.py                # Job data models
│   └── health.py             # Health check models
└── services/
    ├── __init__.py
    ├── openai_service.py     # Existing OpenAI service
    └── job_service.py        # New job data service

data/
└── jobs/                     # Existing job data directory
    ├── job1.md              # Existing sample jobs
    ├── job2.md
    └── job3.md

tests/
├── conftest.py               # Update existing test configuration
├── unit/
│   ├── test_config.py        # Enhance existing config tests
│   ├── test_health.py        # New health check tests
│   ├── test_job_service.py   # Job service tests
│   └── api/
│       ├── test_health.py    # API health endpoint tests
│       └── test_jobs.py      # Job API endpoint tests
└── integration/
    └── test_api_integration.py # FastAPI integration tests
```

## API Endpoints Structure
```
/api/v1/
├── /health              # Health check endpoints
├── /jobs                # Job management (local data from data/jobs/)
│   ├── GET /            # List all available jobs
│   ├── GET /{job_id}    # Get specific job details
│   └── POST /refresh    # Refresh job data from files
└── /applications        # Application workflow (future)
```

## Job Data Structure

### Current Job Data Format
The application will work with job descriptions stored as markdown files in the `data/jobs/` directory. Each job file follows a consistent format:

```markdown
# Example: job1.md
Klant
Gemeente Amsterdam
Klantreferentie
T169100
Locatie
Amsterdam
Inzetspercentage
90%
Gevraagde functie
Projectleider Sociaal Domein
Branche
Government
Verantwoordelijke sales
Jansen, Hans
Grade indicatie
D
Verwachte periode
01-10-25 t/m 14-04-26
Rol
Project Manager
```

### Job Data Service Requirements
- Parse markdown files into structured job objects
- Validate required fields and data formats
- Cache parsed job data with configurable refresh intervals
- Handle file system operations asynchronously
- Provide filtering and search capabilities
- Support for future job board API integration

### Job Model Structure
```python
class Job(BaseModel):
    id: str                           # Derived from filename
    client: str                       # Klant
    client_reference: str             # Klantreferentie
    location: str                     # Locatie
    percentage: str                   # Inzetspercentage
    function: str                     # Gevraagde functie
    industry: str                     # Branche
    sales_responsible: str            # Verantwoordelijke sales
    grade: str                        # Grade indicatie
    period: str                       # Verwachte periode
    role: str                         # Rol
    created_at: datetime              # File modification time
    updated_at: datetime              # Last processed time
```

## Configuration Example
```python
# Enhanced Settings class building on existing structure
class Settings(BaseSettings):
    """Application settings."""

    model_config = ConfigDict(env_file=".env", case_sensitive=False, extra="ignore")

    # Application (existing)
    app_name: str = "Job Agent"
    app_version: str = "0.1.0"
    debug: bool = False

    # API (existing + enhanced)
    api_v1_prefix: str = "/api/v1"
    allowed_hosts: list[str] = ["*"]
    cors_origins: list[str] = ["*"]
    docs_url: str = "/docs"
    redoc_url: str = "/redoc"

    # Logging (existing + enhanced)
    log_level: str = "INFO"
    log_format: str = "json"
    log_file: Optional[str] = None

    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    reload: bool = False

    # Job Data
    jobs_data_directory: str = "data/jobs"
    jobs_file_format: str = "markdown"
    jobs_refresh_interval: int = 300

    # Azure configurations (existing)
    azure_openai: Optional[AzureOpenAISettings] = None
    azure: Optional[AzureSettings] = None
```

## Health Check Example
```python
class HealthCheck(BaseModel):
    status: str
    timestamp: datetime
    version: str
    checks: Dict[str, Any]

class DetailedHealthCheck(HealthCheck):
    azure_openai: bool                    # Using existing Azure OpenAI service
    configuration: bool                   # Validate config.yaml loading
    job_data_access: bool                # Check data/jobs/ directory access
    job_data_validation: bool            # Validate job markdown files
    system_resources: Dict[str, Any]     # Memory, CPU, disk
```

## Integration with Existing Components

### Leveraging Task 1.2 Implementation
- **Configuration System**: Build upon existing Pydantic settings with config.yaml support
- **Azure OpenAI Service**: Integrate existing `AzureOpenAIService` for health checks and future endpoints
- **Credential Management**: Use existing `AzureCredentialManager` for secure authentication
- **Testing Framework**: Extend existing test suite with 84% coverage

### Health Check Integration
The health check system will utilize:
- `get_openai_service().test_connection()` for Azure OpenAI status
- `settings.azure_openai` configuration validation
- `azure_credential_manager.test_credential()` for authentication verification
- Local job data directory access and file validation
- Job markdown parsing and structure validation

## Testing Strategy
- Unit tests for all core components
- Integration tests for API endpoints
- Health check monitoring tests
- Job data service and parsing tests
- Configuration validation tests
- Performance testing for local file operations
- Mock external dependencies (future job board API)

## Performance Considerations
- Async/await patterns throughout (building on existing async Azure OpenAI service)
- Reuse existing `AzureOpenAIService` singleton pattern for connection pooling
- File system caching for job data with configurable refresh intervals
- Request/response caching where appropriate (especially for health checks)
- Background task processing setup for future job polling
- Resource monitoring and optimization
- Leverage existing Azure credential caching from `DefaultAzureCredential`
- Efficient markdown parsing and job data validation
