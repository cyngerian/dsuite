# MLB Data Ingestion Model

## Overview
The MLB Statistics Tracking System (STS) employs a sophisticated data ingestion model that handles different phases of the baseball season and various data states. The system is designed to manage pre-season, regular season, and post-season data through a carefully orchestrated set of storage buckets and utilities.

## Storage Architecture

### MinIO Buckets

#### 1. mlb-live
- **Purpose**: Temporary storage for real-time game data
- **Characteristics**:
  - Receives direct updates from MLB API
  - High update frequency (10-60 second intervals)
  - Stores raw JSON responses
  - Implements versioning for change tracking
- **Data Retention**: Until game completion and validation

#### 2. mlb-current
- **Purpose**: Current season's validated data
- **Structure**:
  ```
  mlb-current/
  ├── pre-season/
  │   └── games/
  ├── regular-season/
  │   └── games/
  └── post-season/
      └── games/
  ```
- **Characteristics**:
  - Only bucket containing pre-season data
  - Receives validated data from mlb-live
  - Regular validation for post-game adjustments
  - Seasonal data migration to mlb-historical

#### 3. mlb-historical
- **Purpose**: Long-term storage of completed seasons
- **Structure**:
  ```
  mlb-historical/
  ├── regular-season/
  │   ├── 2022/
  │   ├── 2023/
  │   └── 2024/
  └── post-season/
      ├── 2022/
      ├── 2023/
      └── 2024/
  ```
- **Characteristics**:
  - Immutable storage
  - Annual updates post-season
  - Optimized for analytical queries

## Core Utilities

### 1. API Scraper Service
- **Primary Responsibilities**:
  - MLB API polling and interaction
  - Rate limiting management
  - Initial JSON validation
  - Differential updates (tracking changed sections)
  - Error handling and retries
- **Features**:
  - Configurable polling intervals
  - Smart caching of static game data
  - Automatic API version handling
  - Request compression and optimization
  - Exponential backoff for errors
  - State-based polling frequency adjustment

### 2. Scheduler Service
- **Primary Responsibilities**:
  - Master schedule management
  - Polling interval optimization
  - Game coverage validation
  - Request timing optimization
  - Parallel processing coordination
- **Features**:
  - Phase 1: Fixed-interval polling (30-60 seconds)
  - Phase 2: Dynamic scheduling based on game state
    ```python
    POLL_INTERVALS = {
        'pre_game': 300,     # 5 minutes
        'warm_up': 60,       # 1 minute
        'in_progress': 30,   # 30 seconds
        'delayed': 120,      # 2 minutes
        'final': 3600,       # 1 hour
        'cancelled': 7200    # 2 hours
    }
    ```
  - Phase 3: Adaptive intervals based on:
    - Historical update patterns
    - Current game situation (runners on base, close game, etc.)
    - API response patterns
    - System load and performance metrics
  - Game priority management
  - Schedule conflict resolution
  - Game delay/postponement handling

### 3. Data Validation Service
- **Primary Responsibilities**:
  - JSON schema validation
  - Data consistency checks
  - Cross-reference validation
  - Historical data comparison
- **Features**:
  - Schema version management
  - Validation rule sets by game state
  - Error classification and reporting
  - Automatic correction for known issues

### 4. Data Movement Service
- **Primary Responsibilities**:
  - Inter-bucket data migration
  - Post-season archival
  - Data cleanup operations
- **Features**:
  - Atomic operations
  - Validation during migration
  - Rollback capabilities
  - Audit logging

### 5. Monitoring Service
- **Primary Responsibilities**:
  - System health monitoring
  - Data quality metrics
  - Performance analytics
  - Alert management
- **Features**:
  - Real-time metrics dashboard
  - Customizable alerting
  - Historical performance tracking
  - SLA monitoring
- **Key Metrics**:
  - Request success rates
  - Data freshness (lag time)
  - Coverage completeness
  - Error rates and types
  - Resource utilization
  - Play event update frequency
  - Data validation status

### 6. Bulk Load Utility
- **Primary Responsibilities**:
  - Historical data reconstruction
  - Manual data ingestion
  - Batch processing of offline data
  - Data backfilling operations
  - Historical data validation
- **Features**:
  - Parallel processing of large datasets
  - Configurable validation rules for historical data
  - Progress tracking and resumability
  - Data source flexibility:
    ```python
    SUPPORTED_SOURCES = {
        'mlb_statsapi': ['json', 'xml'],
        'retrosheet': ['event', 'roster'],
        'custom_format': ['csv', 'json', 'parquet']
    }
    ```
  - Automatic schema detection and mapping
  - Data deduplication
  - Conflict resolution strategies:
    - Timestamp-based
    - Source priority
    - Manual resolution
  - Detailed audit logging
- **Key Operations**:
  - Full season reconstruction
  - Partial season backfill
  - Single game correction
  - Player statistics reconciliation
  - Team statistics validation
- **Integration Points**:
  - Direct write access to mlb-historical
  - Validation pipeline integration
  - Message bus notifications
  - Monitoring system integration
- **Example Usage**:
  ```python
  async def bulk_load_season(
      year: int,
      source: str,
      options: Dict[str, Any]
  ) -> BulkLoadResult:
      """
      Bulk load an entire season's worth of data.

      Args:
          year: The season year to load
          source: Data source identifier
          options: Configuration options for load

      Returns:
          BulkLoadResult with statistics and validation results
      """
      async with BulkLoadManager() as manager:
          # Configure load options
          manager.set_validation_rules(year)
          manager.set_conflict_strategy(options.get('conflict_strategy'))

          # Execute load operation
          result = await manager.load_season(
              year=year,
              source=source,
              parallel_games=options.get('parallel_games', 4),
              validate_as_loaded=True
          )

          # Publish results to message bus
          await manager.publish_load_results(result)

          return result
  ```

## Master Schedule Management

### Schedule Validation System
- Continuous schedule updates from MLB
- Game status tracking
  - Scheduled
  - Delayed
  - In Progress
  - Final
  - Postponed
- Game ID validation
- Coverage monitoring
- Schedule conflict detection

### Data Quality Assurance
- Regular data consistency checks
- Cross-validation with multiple sources
- Automated correction of known issues
- Manual review flagging system

## System Architecture Diagram

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

## Message Bus Integration

The system implements a message bus architecture for:
- Inter-service communication
- Event-driven updates
- Metric collection
- System-wide logging

### Message Types
1. **Control Messages**
   - Schedule updates
   - Polling interval adjustments
   - Configuration changes
   - Service commands
2. **Data Messages**
   - Game state changes
   - Poll results
   - Data validation results
   - Storage operations
3. **Metric Messages**
   - Poll timing and frequency
   - API response times
   - Cache hit rates
   - Health checks
   - Resource utilization

## Recommendations
1. Implement Apache Kafka or RabbitMQ for message bus
2. Use Prometheus and Grafana for metrics/monitoring
3. Implement circuit breakers for API calls
4. Add data versioning in MinIO
5. Create separate validation pipelines for different game states
6. Implement adaptive polling based on game state
7. Use caching to reduce API load
8. Monitor and adjust polling frequencies based on actual update patterns
