# Docker Setup Guide for GAFreqTrade

This guide will help you set up GAFreqTrade to use Freqtrade via Docker, which is the recommended approach for isolated and consistent execution.

## Why Use Docker?

Using Docker for Freqtrade provides several benefits:
- **Isolation**: Freqtrade runs in a container, avoiding conflicts with system dependencies
- **Consistency**: Same environment across different systems
- **Easy Updates**: Just pull the latest image to update Freqtrade
- **No Installation**: No need to install Freqtrade and its dependencies directly on your system

## Prerequisites

1. **Docker installed and running**
   ```bash
   # Check Docker is installed
   docker --version
   
   # If not installed, visit: https://docs.docker.com/get-docker/
   ```

2. **Directory structure**
   ```
   GAFreqTrade/
   └── freqtrade/
       └── user_data/
           ├── config.json       # Your Freqtrade configuration
           ├── data/             # Market data directory
           └── strategies/       # Generated strategies go here
   ```

## Step-by-Step Setup

### 1. Verify Docker Installation

Run the test script to check your Docker setup:

```bash
python test_docker_setup.py
```

This will verify:
- Docker is installed and accessible
- Freqtrade Docker image is available
- Directory structure is correct
- Docker can mount volumes properly

### 2. Pull Freqtrade Docker Image

```bash
docker pull freqtradeorg/freqtrade:stable
```

You can also use specific versions:
```bash
docker pull freqtradeorg/freqtrade:2024.1  # Specific version
docker pull freqtradeorg/freqtrade:develop # Development version
```

### 3. Configure GAFreqTrade for Docker

**Option A: Use the Docker example config**

Copy the example Docker configuration:
```bash
cp config/eval_config_docker.yaml config/eval_config.yaml
```

**Option B: Manually edit your config**

Edit `config/eval_config.yaml` and set the Docker settings:

```yaml
freqtrade:
  # ... other settings ...
  
  # Docker Settings - Enable these
  use_docker: true                                    # IMPORTANT: Set to true
  docker_image: "freqtradeorg/freqtrade:stable"      # Docker image to use
  docker_user_data_path: "./freqtrade/user_data"     # Path to your user_data
  
  # Path settings (these will be translated for Docker)
  config_path: "freqtrade/user_data/config.json"
  strategy_path: "freqtrade/user_data/strategies"
  datadir: "freqtrade/user_data/data"
```

### 4. Set Up Freqtrade Configuration

Create or verify your `freqtrade/user_data/config.json`:

```json
{
  "max_open_trades": 3,
  "stake_currency": "USDT",
  "stake_amount": "unlimited",
  "tradable_balance_ratio": 0.99,
  "fiat_display_currency": "USD",
  "dry_run": true,
  "timeframe": "5m",
  
  "exchange": {
    "name": "binance",
    "key": "",
    "secret": "",
    "ccxt_config": {},
    "ccxt_async_config": {},
    "pair_whitelist": [
      "BTC/USDT",
      "ETH/USDT"
    ],
    "pair_blacklist": []
  },
  
  "datadir": "user_data/data"
}
```

### 5. Download Market Data

Download historical data using Docker:

```bash
# Basic example - download BTC/USDT and ETH/USDT data
docker run --rm -v "$(pwd)/freqtrade/user_data:/freqtrade/user_data" \
  freqtradeorg/freqtrade:stable \
  download-data \
  --exchange binance \
  --pairs BTC/USDT ETH/USDT \
  --timeframe 5m \
  --days 90

# Download more pairs
docker run --rm -v "$(pwd)/freqtrade/user_data:/freqtrade/user_data" \
  freqtradeorg/freqtrade:stable \
  download-data \
  --exchange binance \
  --pairs BTC/USDT ETH/USDT BNB/USDT ADA/USDT SOL/USDT \
  --timeframe 5m 1h \
  --days 180
```

### 6. Test Backtesting with Docker

Test that backtesting works with a sample strategy:

```bash
# Create a simple test strategy first
mkdir -p freqtrade/user_data/strategies

# Test backtesting with Docker
docker run --rm -v "$(pwd)/freqtrade/user_data:/freqtrade/user_data" \
  freqtradeorg/freqtrade:stable \
  backtesting \
  --config user_data/config.json \
  --strategy SampleStrategy \
  --timeframe 5m \
  --timerange 20240101-20240131
```

If this works, you're ready to run GAFreqTrade!

### 7. Run GAFreqTrade with Docker Mode

Now you can run evolution with real backtesting:

```bash
# Small test run
python run_evolution.py --no-mock --generations 4 --population 10

# Larger production run
python run_evolution.py --no-mock --generations 50 --population 50
```

## Troubleshooting

### Issue: "Docker permission denied"

**Solution**: Add your user to the docker group or use sudo

```bash
# Add user to docker group (Linux)
sudo usermod -aG docker $USER
# Log out and back in for changes to take effect

# OR run with sudo (not recommended for production)
sudo python run_evolution.py --no-mock --generations 4 --population 10
```

### Issue: "Cannot connect to Docker daemon"

**Solution**: Make sure Docker is running

```bash
# Start Docker (Linux)
sudo systemctl start docker

# Start Docker (macOS/Windows)
# Open Docker Desktop application
```

### Issue: "Image not found"

**Solution**: Pull the Freqtrade image

```bash
docker pull freqtradeorg/freqtrade:stable
```

### Issue: "Volume mount failed"

**Solution**: Use absolute paths

```bash
# In config/eval_config.yaml, use absolute path:
docker_user_data_path: "/full/path/to/GAFreqTrade/freqtrade/user_data"
```

### Issue: "No data available"

**Solution**: Download market data first

```bash
docker run --rm -v "$(pwd)/freqtrade/user_data:/freqtrade/user_data" \
  freqtradeorg/freqtrade:stable \
  download-data \
  --exchange binance \
  --pairs BTC/USDT ETH/USDT \
  --timeframe 5m \
  --days 90
```

### Issue: "Strategies not found"

**Solution**: Make sure strategies are in the correct directory

GAFreqTrade automatically places generated strategies in:
- `freqtrade/user_data/strategies/`

Make sure this directory exists and is writable:
```bash
mkdir -p freqtrade/user_data/strategies
chmod 755 freqtrade/user_data/strategies
```

## Advanced Configuration

### Using Different Docker Images

You can use different Freqtrade versions:

```yaml
# In config/eval_config.yaml
freqtrade:
  docker_image: "freqtradeorg/freqtrade:develop"  # Latest development
  # or
  docker_image: "freqtradeorg/freqtrade:2024.1"   # Specific version
```

### Custom Docker Arguments

If you need to pass additional Docker arguments, you can modify the Backtester class. The command building is in `evaluation/backtester.py` in the `_build_freqtrade_command` method.

### Running on Windows

On Windows, use PowerShell and adjust path syntax:

```powershell
# Pull image
docker pull freqtradeorg/freqtrade:stable

# Download data (PowerShell)
docker run --rm -v "${PWD}/freqtrade/user_data:/freqtrade/user_data" `
  freqtradeorg/freqtrade:stable `
  download-data `
  --exchange binance `
  --pairs BTC/USDT ETH/USDT `
  --timeframe 5m `
  --days 90

# Run evolution
python run_evolution.py --no-mock --generations 4 --population 10
```

## Verification Checklist

Before running a full evolution, verify:

- [ ] Docker is installed and running
- [ ] Freqtrade image is pulled: `docker pull freqtradeorg/freqtrade:stable`
- [ ] Directory structure exists: `freqtrade/user_data/{data,strategies}`
- [ ] Config file exists: `freqtrade/user_data/config.json`
- [ ] Market data is downloaded for your pairs and timeframe
- [ ] Docker mode is enabled in `config/eval_config.yaml`: `use_docker: true`
- [ ] Test script passes: `python test_docker_setup.py`
- [ ] Manual backtest works via Docker
- [ ] Test evolution run works: `python run_evolution.py --no-mock --generations 2 --population 5`

## Next Steps

Once your Docker setup is working:

1. **Run a small test evolution**
   ```bash
   python run_evolution.py --no-mock --generations 5 --population 10
   ```

2. **Monitor the evolution**
   ```bash
   python monitor.py --live
   ```

3. **View results**
   ```bash
   python show_leaderboard.py --top 10
   ```

4. **Scale up for production**
   ```bash
   python run_evolution.py --no-mock --generations 100 --population 50
   ```

## Support

If you encounter issues:
1. Run `python test_docker_setup.py` to diagnose problems
2. Check Docker logs: `docker logs <container_id>`
3. Verify paths are correct in `config/eval_config.yaml`
4. Ensure you have enough disk space for data and strategies
5. Check that Docker has sufficient resources allocated (CPU, Memory)

For more information:
- See [README.md](README.md) for general documentation
- See [QUICKSTART.md](QUICKSTART.md) for development setup
- Visit [Freqtrade Documentation](https://www.freqtrade.io/en/stable/) for Freqtrade-specific help
