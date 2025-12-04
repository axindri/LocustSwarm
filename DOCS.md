# LocustSwarm
**Launcher and aggregator of Locust load tests in Docker containers**

![LocustSwarm Interface](img/preview.png)

## 📌 Main Purpose
Web interface for managing load tests with isolation of each test in a separate Docker container. Supports both predefined scenarios and custom scenarios with multi-stage load.

## 🏗️ Architecture

### Key Components
- **Flask application** - main web server (port 3000)
- **Docker** - test isolation in containers
- **Locust** - load testing framework
- **Pydantic** - configuration validation

### Data Storage
- **Configuration**: `config.json`
- **Test results**: `/tmp/results/{project}/{scenario}/{test_id}/`
- **Active tests**: RAM (no database)

## 📂 Project Structure

```
├── api/                   # Flask endpoints
│   ├── config.py          # Configuration management
│   ├── tests.py           # Start/stop tests
│   ├── results.py         # Get results
│   └── debug.py           # Debug functions
├── tests/                 # Locust scenarios
│   ├── {project}/         # Project-specific tests
│   └── utils.py           # Common utilities
├── models/                # Pydantic models
├── utils/                 # Helper modules
├── static/                # Web resources
├── templates/             # HTML templates
└── config.json            # Project configuration
```

## ⚙️ Configuration

### Environment Variables

| Variable | Type | Default | Description |
|------------|-----|--------------|-----------|
| **DEBUG** | bool | `True` | Debug mode, enables detailed logging |
| **DOCKER_BASE_URL** | string | `unix:///var/run/docker.sock` | URL for connecting to Docker Daemon |
| **ALLOW_PARALLEL** | bool | `False` | Allow parallel execution of multiple tests |
| **ACTIVE_TESTS_CLEANUP_TIMEOUT** | int | `60` | Timeout (in seconds) for cleaning up completed tests from the active list |
| **MIN_PORT** | int | `8080` | Minimum port for Locust web interface |
| **MAX_PORT** | int | `8090` | Maximum port for Locust web interface |
| **TMP_PATH** | string | `./tmp` | Path for temporary files |
| **CONFIG_PATH** | string | `./config.json` | Path to project configuration file |
| **HOST** | string | `http://127.0.0.1` | Base URL for Locust Swarm web interface |
| **PORT** | int | `3000` | Flask web server port |

**Automatically computed paths:**
- `results_path`: `{TMP_PATH}/results` - directory for storing test results

### Project Configuration File (`config.json`)

```json
{
  "projects_configs": {
    "project_one": {
      "name": "Project One",
      "host": "localhost",
      "scenarios": {
        "metrics": {
          "users": 1,
          "spawn_rate": 1,
          "run_time": "1m"
        },
        "regular": {
          "users": 20,
          "spawn_rate": 1,
          "run_time": "5m"
        },
        "stress": {
          "users": 500,
          "spawn_rate": 20,
          "run_time": "10m"
        },
        "custom": {
          "stages": [
            {
              "duration": 10,
              "users": 20,
              "spawn_rate": 1
            },
            {
              "duration": 60,
              "users": 50,
              "spawn_rate": 60
            },
            {
              "duration": 90,
              "users": 125,
              "spawn_rate": 90
            }
          ]
        }
      }
    },
    "project_2": {
      "name": "Project Two",
      "host": "localhost",
      "scenarios": {
        "metrics": {
          "users": 1,
          "spawn_rate": 1,
          "run_time": "1m"
        },
        "regular": {
          "users": 20,
          "spawn_rate": 1,
          "run_time": "5m"
        },
        "stress": {
          "users": 500,
          "spawn_rate": 20,
          "run_time": "10m"
        }
      }
    }
  }
}
```

### Example `.env` File
```env
DEBUG=True
DOCKER_BASE_URL=unix:///var/run/docker.sock
ALLOW_PARALLEL=False
ACTIVE_TESTS_CLEANUP_TIMEOUT=60
MIN_PORT=8080
MAX_PORT=8090
TMP_PATH='./tmp'
CONFIG_PATH='./config.json'
HOST=http://127.0.0.1
PORT=3000
```

## 🚀 Test Launch Process

1. **Configuration Preparation**
   - Uses `config.json` or custom JSON configuration
   - Projects, hosts, and scenarios are determined

2. **Test Parameter Selection**
   - Project (from configuration)
   - Scenario (regular or custom)
   - Mode: with Locust web interface or headless

3. **Test Launch**
   - Docker container is created with a unique name
   - Mounts:
     - Test directory (`/tests`)
     - Temporary directory (`/tmp`)
     - Volume for results
   - Scenario file is generated (for custom tests)
   - Locust is started with parameters from configuration

4. **Monitoring and Management**
   - Locust web interface (if enabled)
   - Real-time container status
   - Automatic cleanup of old tests

5. **Test Completion**
   - Manual stop or automatic completion
   - Saving reports (HTML, CSV)
   - Results archiving

## 📡 API Endpoints

### Test Management
```
POST   /api/tests/start     # Start test
POST   /api/tests/stop/{id} # Stop test
POST   /api/tests/clear-all # Stop all tests
GET    /api/tests/active    # Active tests
GET    /api/tests/completed # Completed tests
```

### Configuration
```
GET    /api/config          # Get configuration
POST   /api/config          # Update configuration
```

### Results
```
GET    /api/results/{test_id}/report       # HTML report
GET    /api/results/{test_id}/download-zip # Results archive
```

### Debug
```
GET    /api/debug/docker           # Container information
POST   /api/debug/docker/clear-all # Clear containers
```

## 🐳 Docker Integration

### Features
- Each test in a separate `locustio/locust:latest` container
- File system isolation through volumes
- Dynamic port assignment (8080-8090)
- Automatic cleanup of stopped containers

### Container Volumes
```
/tests:ro      # Test directory
/tmp:ro        # Temporary files
/results       # Test results
```

## 🎯 Scenario Types

### Regular Scenarios
- Fixed number of users
- Constant load ramp-up rate
- Specified execution time

### Custom Scenarios (Stages)
- Multi-stage load
- Dynamic user count changes
- Gradual load increase/decrease

## 🔧 Dependencies

```toml
docker>=7.1.0
flask>=3.1.2
gunicorn>=23.0.0
locust>=2.42.5
pydantic>=2.12.5
pydantic-settings>=2.12.0
```

## 📁 Temporary Files Structure

```
./tmp/                       # TMP_PATH
├── results/                 # Automatically created
│   ├── project_a/
│   │   └── scenario_x/
│   │       └── test_id/
│   │           ├── report.html
│   │           └── *.csv
│   └── project_b/
├── project_a/              # For project temporary files
│   └── custom_scenario.py  # Generated for custom tests
└── project_b/
```

## 🔄 Settings Interconnection

### Parallel Execution
- With `ALLOW_PARALLEL=False` (default), it's forbidden to start a new test if there's already an active one
- With `ALLOW_PARALLEL=True`, multiple simultaneous tests are allowed, each on its own port from the `MIN_PORT-MAX_PORT` range

### Active Tests Cleanup
- The system automatically removes completed tests from the active list after `ACTIVE_TESTS_CLEANUP_TIMEOUT` seconds
- This prevents accumulation of old records in memory

### Docker Ports
- With parallel execution: port is automatically selected from the range
- With single execution: port 8080 is used
- Forwarding: `8089/tcp` (container) → `selected_port` (host)


## ⚠️ Important Notes

1. **DOCKER_BASE_URL** - must point to an accessible Docker Daemon
2. **TMP_PATH** - must exist and be writable
3. **MIN_PORT/MAX_PORT** - must be free ports on the host
4. **HOST** - used for generating links in UI, must be correct for browser access
5. **DEBUG=True** - enables detailed logging but may slow down performance

---

**Note**: The project is intended for internal use in isolated environments. All tests are executed against hosts specified in the configuration.