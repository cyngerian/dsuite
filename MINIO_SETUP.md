# MinIO Configuration and Access Guide

## Current MinIO Setup

### Server Details
- Host: localhost
- API Port: 9000
- Web Console Port: 9001
- Data Directory: `/var/lib/mlb-stats/minio/`

### Authentication
- Default Root User: `minioadmin`
- Default Root Password: `minioadmin`

### Existing Buckets
- `mlb-current`: Current season data
- `mlb-historical`: Historical baseball data
- `mlb-live`: Live game data

### Directory Structure
```
/var/lib/mlb-stats/minio/
├── mlb-current/
├── mlb-historical/
└── mlb-live/
```

## Docker Configuration

### Docker Compose Configuration
```yaml
minio:
  image: minio/minio
  container_name: mlb_minio
  environment:
    MINIO_ROOT_USER: ${MINIO_ACCESS_KEY:-minioadmin}
    MINIO_ROOT_PASSWORD: ${MINIO_SECRET_KEY:-minioadmin}
  ports:
    - "9000:9000"
    - "9001:9001"
  volumes:
    - /var/lib/mlb-stats/minio:/data
  command: server /data --console-address ":9001"
  user: "1000:1000"
```

## Accessing MinIO from a New Project

### Environment Variables
Set these in your new project's environment:
```bash
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
```

### Python Example
```python
from minio import Minio

def create_minio_client() -> Minio:
    """
    Create a MinIO client instance with the current configuration.
    
    Returns:
        Minio: Configured MinIO client instance
    """
    return Minio(
        endpoint="localhost:9000",
        access_key="minioadmin",
        secret_key="minioadmin",
        secure=False  # Set to True if using HTTPS
    )

# Usage example
client = create_minio_client()
objects = client.list_objects('mlb-current')
for obj in objects:
    print(obj.object_name)
```

### Docker Network Configuration
If your new project uses Docker, add this to your `docker-compose.yml`:
```yaml
services:
  your_service:
    # ... your service config ...
    environment:
      MINIO_ENDPOINT: minio:9000  # Use container name when in same network
      MINIO_ACCESS_KEY: minioadmin
      MINIO_SECRET_KEY: minioadmin
    networks:
      - minio-network  # Make sure to connect to same network as MinIO

networks:
  minio-network:
    external: true
    name: mlb-network  # Use the existing MLB stats network
```

## Maintenance Notes

### Permissions
- The MinIO data directory is owned by user:group `airbaggie:airbaggie`
- Directory permissions are set to 755
- If permission issues occur, run:
  ```bash
  sudo chown -R $USER:$USER /var/lib/mlb-stats/minio/
  sudo chmod -R 755 /var/lib/mlb-stats/minio/
  ```

### Troubleshooting
If MinIO becomes unresponsive or has permission issues:
1. Stop the MinIO container
2. Remove the `.minio.sys` directory:
   ```bash
   sudo rm -rf /var/lib/mlb-stats/minio/.minio.sys
   ```
3. Restart the MinIO container
4. MinIO will recreate the `.minio.sys` directory with correct permissions

### Health Check
MinIO container includes a health check that verifies the service is running:
```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:9000/minio/health/live"]
  interval: 5s
  timeout: 5s
  retries: 5
  start_period: 10s
``` 