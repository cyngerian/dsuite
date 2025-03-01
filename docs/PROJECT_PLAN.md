# MLB Statistics Tracking System (STS) - Project Plan

## Project Overview
A comprehensive baseball statistics system that ingests MLB data in real-time, processes it through an ELT pipeline, and provides a robust API for data access. The system is designed to serve as a foundation for future analysis and visualization projects.

## Table of Contents

1. [Project Structure](#1-project-structure)
   - [Directory Structure](#directory-structure)
   - [Architecture Diagram](#architecture-diagram)

2. [Phase 1: Core Infrastructure](#2-phase-1-core-infrastructure)
   1. [Data Pipeline Components](#1-data-pipeline-components)
      - [Ingestion Service](#ingestion-service)
      - [Transformation Service](#transformation-service)
      - [Database Design](#database-design)
   2. [Initial Features](#2-initial-features)
      - [Core Database Tables](#core-database-tables)
   3. [API Integration](#3-api-integration)
      - [API Design Principles](#api-design-principles)
      - [Core API Endpoints](#core-api-endpoints)
      - [Data Flow Patterns](#data-flow-patterns)

3. [Development Principles](#3-development-principles)
   1. [Version Control](#1-version-control)
   2. [Testing Strategy](#2-testing-strategy)
   3. [Documentation](#3-documentation)
   4. [Monitoring and Logging](#4-monitoring-and-logging)

4. [Development Environments and CI/CD](#4-development-environments-and-cicd)
   - [Development Environments](#development-environments)
   - [CI/CD Pipeline Structure](#cicd-pipeline-structure)
   - [Development Workflow](#development-workflow)
   - [Environment Configuration](#environment-configuration)
   - [Quality Gates](#quality-gates)

5. [Implementation Plan](#5-implementation-plan)
   - [Phase 1: Core Infrastructure](#phase-1-core-infrastructure-1)
   - [Phase 2: Basic Features](#phase-2-basic-features)
   - [Phase 3: System Enhancement](#phase-3-system-enhancement)

6. [Quality Assurance](#6-quality-assurance)
   - [Testing Requirements](#testing-requirements)
   - [Documentation Requirements](#documentation-requirements)

7. [Deployment Strategy](#7-deployment-strategy)
   - [Container Organization](#container-organization)
   - [Environment Configuration](#environment-configuration-1)

8. [Monitoring and Maintenance](#8-monitoring-and-maintenance)
   - [Health Checks](#health-checks)
   - [Backup Strategy](#backup-strategy)

9. [Future Projects](#9-future-projects)
   - [MLB Stats Analysis Project](#mlb-stats-analysis-project)
   - [MLB Stats Dashboard Project](#mlb-stats-dashboard-project)

## 1. Project Structure

### Directory Structure
```
dsuite/
├── .github/
│   └── workflows/               # CI/CD pipelines
├── docs/
│   ├── CHANGELOG.md            # Track major changes
│   ├── GUIDELINES.md          # Project guidelines and development rules
│   └── architecture/           # Architecture diagrams and docs
├── services/
│   ├── ingestion/             # MLB API data ingestion service
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   ├── src/
│   │   │   ├── historical.py  # Historical data ingestion
│   │   │   └── live.py        # Live data ingestion
│   │   └── tests/
│   ├── transformation/         # Data transformation service
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   ├── src/
│   │   │   ├── schema/        # Database schema definitions
│   │   │   ├── raw/          # Raw data transformations
│   │   │   └── derived/      # Derived statistics
│   │   └── tests/
│   ├── minio/                 # MinIO data lake service
│   │   ├── Dockerfile
│   │   ├── config/
│   │   │   └── minio.json    # MinIO server configuration
│   │   └── init/
│   │       └── create-buckets.sh  # Bucket initialization script
│   ├── postgres/              # PostgreSQL database service
│   │   ├── Dockerfile
│   │   ├── init/
│   │   │   ├── 01-init.sql   # Database initialization
│   │   │   └── 02-schemas.sql # Schema definitions
│   │   └── config/
│   │       └── postgresql.conf # PostgreSQL configuration
│   └── api/                   # REST API service
│       ├── Dockerfile
│       ├── requirements.txt
│       ├── src/
│       │   └── routes/
│       └── tests/
├── scripts/
│   ├── schema_analysis/       # JSON schema analysis tools
│   └── setup/                 # Setup and initialization scripts
├── tests/
│   ├── integration/
│   └── e2e/
├── .env.example
├── docker-compose.yml
└── README.md
```

### Architecture Diagram
```mermaid
graph TD
    MLB[MLB Stats API] --> |Raw JSON| ING[Ingestion Service]
    ING --> |Store| MINIO[MinIO Data Lake]
    MINIO --> |Raw JSON| TRANS[Transformation Service]
    TRANS --> |Raw Data| RAW[(Raw Data)]
    RAW --> |SQL Transformations| DERIVED[(Derived Stats)]

    subgraph PostgreSQL DB
        RAW
        DERIVED
    end

    RAW --> API[REST API Service]
    DERIVED --> API

    subgraph Data Pipeline
        ING
        MINIO
        TRANS
    end

    subgraph External Access
        API
    end
```

```mermaid
graph TB
    subgraph External
        MLBAPI[MLB API]
    end

    subgraph Ingestion
        AS[API Scraper]
        SCH[Scheduler]
        VAL[Validator]
    end

    subgraph Storage ["Storage (MinIO)"]
        LIVE[mlb-live]
        CURR[mlb-current]
        HIST[mlb-historical]
    end

    subgraph Services
        MOV[Data Mover]
        MON[Monitoring]
        VALID[Validation Service]
    end

    subgraph Monitoring
        DASH[Dashboard]
        ALERT[Alerting]
        METRICS[Metrics Store]
    end

    %% External to Ingestion
    MLBAPI -->|Raw Data| AS
    SCH -->|Schedule| AS
    AS -->|Validation| VAL

    %% Ingestion to Storage
    AS -->|Live Data| LIVE
    VAL -->|Validated Data| CURR
    MOV -->|Archive| HIST

    %% Storage Flow
    LIVE -->|Finalized Games| CURR
    CURR -->|Season End| HIST

    %% Monitoring Flow
    AS -->|Metrics| METRICS
    VAL -->|Validation Results| METRICS
    LIVE -->|Storage Metrics| METRICS
    CURR -->|Storage Metrics| METRICS
    HIST -->|Storage Metrics| METRICS

    %% Dashboard
    METRICS -->|Real-time| DASH
    METRICS -->|Alerts| ALERT

    classDef external fill:#f96,stroke:#333,stroke-width:2px
    classDef storage fill:#58a,stroke:#333,stroke-width:2px
    classDef service fill:#7b3,stroke:#333,stroke-width:2px
    classDef monitoring fill:#c7d,stroke:#333,stroke-width:2px

    class MLBAPI external
    class LIVE,CURR,HIST storage
    class AS,SCH,VAL,MOV service
    class DASH,ALERT,METRICS monitoring
```

## 2. Phase 1: Core Infrastructure

### 1. Data Pipeline Components

#### Ingestion Service
- Implements the [detailed ingestion model](docs/INGESTION_MODEL.md)
- Separate modules for historical and live data
- Rate limiting and error handling
- Metadata tracking for ingestion status
- MinIO storage organization by year/month/day

#### Transformation Service
- Schema validation and evolution
- Raw data transformations
- Derived statistics calculations
- Independent operation from ingestion

#### Database Design
- Schema-first approach
- Separate schemas for raw and derived data
- Optimized indexing strategy
- Version control for schema changes

### 2. Initial Features

#### Core Database Tables
```mermaid
classDiagram
    %% MLB Game Data Schema
    %% Essential entities and relationships
    direction TB
    %% Central entity representing a baseball game
    class Game {
    }

    %% Baseball team participating in games
    class Team {
        +int away.springLeague.id
        +str away.springLeague.name
        +str away.springLeague.abbreviation
        +int away.springLeague.id
        +int away.division.id
    }

    %% Baseball player on a team
    class Player {
        +int player.id
        +str player.fullName
        +str player.primaryPosition.code
        +str player.primaryNumber
    }

    %% Individual play within a game
    class Play {
        +int player.id
    }

    %% Stadium where games are played
    class Venue {
        +int id
        +str name
    }

    %% Essential relationships
    Game "1" -- "2" Team : has
    Game --> Venue : played at
    Team o-- Player : rosters
    Game "1" -- "*" Play : contains
    Play --> Player : involves
    Team --> Venue : home field
```

```mermaid
erDiagram
    GAMES ||--o{ GAME_EVENTS : contains
    GAMES ||--|| GAME_INFO : describes
    GAME_EVENTS ||--o{ PITCHES : contains
    PLAYERS ||--o{ GAME_EVENTS : participates
    TEAMS ||--o{ GAMES : plays

    DERIVED_STATS ||--|| PLAYERS : describes
    DERIVED_STATS ||--|| TEAMS : describes
```

### 3. API Integration

#### API Design Principles
- RESTful endpoints following OpenAPI 3.0 specification
- Versioned API paths (e.g., `/api/v1/`)
- JWT-based authentication and role-based access control
- Rate limiting and request throttling
- Comprehensive error handling and status codes
- Consistent response formats
- Query parameter support for filtering and pagination
- Caching headers and ETags for performance
- CORS configuration for web security

#### Core API Endpoints
```
GET /api/v1/games
  - Current and scheduled games
  - Historical game lookup
  - Game state and live updates

GET /api/v1/stats
  - Player statistics
  - Team statistics
  - Derived metrics
  - Historical trends

GET /api/v1/players
  - Player information
  - Career statistics
  - Current status

GET /api/v1/teams
  - Team information
  - Season statistics
  - Roster data
```

#### Data Flow Patterns
1. **Real-time Updates**
   - WebSocket connection for live game data
   - Server-Sent Events for alerts
   - Polling fallback for compatibility

2. **Data Caching**
   - API response caching
   - Database query caching
   - In-memory data stores

3. **Error Handling**
   - Graceful degradation
   - Retry with exponential backoff
   - Comprehensive error logging
   - Monitoring alerts

4. **Performance Optimization**
   - Query optimization
   - Connection pooling
   - Load balancing
   - Performance monitoring

#### Message Bus Architecture
The system implements Apache Kafka as a message bus to facilitate real-time data flow and event-driven architecture. For detailed implementation specifications, see [Message Bus Plan](docs/MESSAGE_BUS_PLAN.md).

Key Components:
- Apache Kafka for message streaming
- Schema Registry for message validation
- Event-driven communication between services
- Centralized monitoring and metrics collection

```mermaid
graph TB
    subgraph External
        MLBAPI[MLB API]
    end

    subgraph Message Bus
        KAFKA[Apache Kafka]
        SR[Schema Registry]
        subgraph Topics
            RAW[Raw Events]
            VAL[Validated Events]
            STOR[Storage Events]
            METR[Metrics]
        end
    end

    subgraph Services
        ING[Ingestion Service]
        TRANS[Transformation]
        MIN[MinIO]
        PG[PostgreSQL]
        API[API Service]
        MON[Monitoring]
    end

    %% Data Flow
    MLBAPI -->|Raw Data| ING
    ING -->|Game Events| RAW
    RAW -->|Consume| TRANS
    TRANS -->|Validated Data| VAL
    VAL -->|Store| MIN
    VAL -->|Store| PG

    %% Storage Events
    MIN -->|Storage Events| STOR
    PG -->|Database Events| STOR

    %% Metrics Flow
    ING -->|Metrics| METR
    TRANS -->|Metrics| METR
    MIN -->|Metrics| METR
    PG -->|Metrics| METR
    API -->|Metrics| METR
    METR -->|Collect| MON

    %% Schema Registry
    SR -.->|Schema Validation| RAW
    SR -.->|Schema Validation| VAL
    SR -.->|Schema Validation| STOR
    SR -.->|Schema Validation| METR

    classDef external fill:#f96,stroke:#333,stroke-width:2px
    classDef messagebus fill:#58a,stroke:#333,stroke-width:2px
    classDef service fill:#7b3,stroke:#333,stroke-width:2px
    classDef topic fill:#c7d,stroke:#333,stroke-width:2px

    class MLBAPI external
    class KAFKA,SR messagebus
    class ING,TRANS,MIN,PG,API,MON service
    class RAW,VAL,STOR,METR topic
```

The message bus implementation provides:
1. Real-time data streaming between services
2. Reliable event processing and delivery
3. Schema validation and evolution
4. Centralized monitoring and metrics
5. Scalable and fault-tolerant architecture

## 3. Development Principles

### 1. Version Control
- Each project maintains its own repository
- Feature branch workflow
- Semantic versioning
- Comprehensive commit messages

### 2. Testing Strategy
- Unit tests per service
- Integration tests between services
- End-to-end tests for critical paths
- Performance testing

### 3. Documentation
- API documentation (OpenAPI)
- Setup guides
- Integration guides
- Deployment procedures

### 4. Monitoring and Logging
- Centralized logging
- Error tracking
- Performance metrics
- Audit trails

## 4. Development Environments and CI/CD

### Development Environments
- Local development environment
- Staging environment
- Production environment

### CI/CD Pipeline Structure
- Continuous Integration (CI)
- Continuous Deployment (CD)

### Development Workflow
- Feature development
- Code review
- Unit testing
- Integration testing
- Deployment

### Environment Configuration
- Configuration management
- Environment-specific settings
- Dependency injection

### Quality Gates
- Code quality checks
- Security scans
- Performance benchmarks
- Compliance checks

## 5. Implementation Plan

### Phase 1: Core Infrastructure
1. Basic ingestion service
   - Fixed-interval polling implementation (30-60 seconds)
   - Basic MLB API integration
   - Simple error handling and retries
   - Initial MinIO bucket setup
2. Storage setup
   - MinIO bucket configuration
   - Basic data organization
   - Initial validation rules
3. Simple API endpoints
   - Core CRUD operations
   - Basic error handling
   - Initial documentation
4. Initial testing
   - Unit test framework
   - Basic integration tests
   - Performance baselines

### Phase 2: Basic Features
1. Core database tables
   - Schema implementation
   - Initial indexes
   - Data migration utilities
2. Enhanced Ingestion Features
   - Dynamic polling based on game state
   - Advanced error handling
   - Bulk load utility implementation
   - Historical data reconstruction
3. Message Bus Integration
   - Kafka setup and configuration
   - Core message types
   - Basic event handling
4. Advanced Data Flow
   - Enhanced validation pipeline
   - Data transformation service
   - Automated data movement
5. Error Handling
   - Circuit breakers
   - Retry strategies
   - Error reporting
   - Alert system

### Phase 3: System Enhancement
1. Advanced Features
   - Adaptive polling based on historical patterns
   - Machine learning for optimal polling
   - Advanced caching strategies
   - Predictive game state handling
2. Performance Optimization
   - Query optimization
   - Connection pooling
   - Load balancing
   - Cache optimization
3. Advanced Monitoring
   - Detailed performance metrics
   - Advanced alerting rules
   - Predictive monitoring
   - Capacity planning
4. System Hardening
   - Security enhancements
   - Disaster recovery
   - Advanced backup strategies
   - Performance tuning

### Implementation Timeline
```mermaid
gantt
    title Implementation Phases
    dateFormat  YYYY-MM-DD
    section Phase 1
    Core Infrastructure    :2024-01-01, 30d
    Basic Polling         :10d
    Storage Setup         :10d
    Simple API           :10d
    section Phase 2
    Enhanced Features    :2024-02-01, 45d
    Dynamic Polling     :15d
    Message Bus        :15d
    Data Flow         :15d
    section Phase 3
    System Enhancement :2024-03-15, 60d
    Adaptive Polling  :20d
    Optimization     :20d
    Hardening       :20d
```

## 6. Quality Assurance

### Testing Requirements
- Unit tests
- Integration tests
- End-to-end tests
- Performance tests

### Documentation Requirements
- API documentation
- Setup guides
- Integration guides
- Deployment procedures

## 7. Deployment Strategy

### Container Organization
```yaml
# docker-compose.pipeline.yml
version: '3.8'
services:
  ingestion:
    build: ./services/ingestion
    environment:
      - MLB_API_KEY=${MLB_API_KEY}

  minio:
    image: minio/minio
    volumes:
      - minio_data:/data

  postgres:
    image: postgres:latest
    volumes:
      - pg_data:/var/lib/postgresql/data

  api:
    build: ./services/api
    ports:
      - "8000:8000"
```

### Environment Configuration
- Container orchestration
- Environment-specific configurations
- Dependency injection

## 8. Monitoring and Maintenance

### Health Checks
- Service availability
- API response times
- Data freshness
- Error rates

### Backup Strategy
- Database backups
- MinIO backups
- Configuration backups
- Restore procedures

## 9. Future Projects

### MLB Stats Analysis Project
A separate project that will build upon the core pipeline to provide advanced statistical analysis:

1. **Key Features**
   - Advanced player metrics
   - Team performance analysis
   - Predictive modeling
   - Custom statistical frameworks
   - Research environment with Jupyter notebooks
   - Model validation framework
   - Simulation capabilities

2. **Integration Points**
   - API access to raw and derived data
   - Export pipeline for analysis results
   - Scheduled jobs for regular analysis
   - Event-driven analysis triggers

3. **Technology Stack**
   - Python for statistical analysis
   - R for specialized baseball statistics
   - PostgreSQL for result storage
   - Redis for caching
   - Docker for deployment

### MLB Stats Dashboard Project
A visualization layer built with R Shiny to provide interactive access to statistics:

1. **Key Features**
   - Interactive data visualization
   - Custom report generation
   - Real-time game tracking
   - Historical data analysis
   - User customization
   - Export capabilities

2. **Integration Points**
   - API integration with core pipeline
   - Real-time data updates
   - Authentication services
   - Export functionality

3. **Technology Stack**
   - R Shiny for dashboard
   - PostgreSQL for data access
   - Redis for caching
   - Docker for deployment

Both future projects will maintain their own repositories and deployment pipelines while integrating seamlessly with the core pipeline through well-defined APIs and data contracts.
