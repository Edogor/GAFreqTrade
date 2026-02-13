# Testing Instructions for Docker Support

## Quick Test (5 minutes)

Follow these steps to verify the Docker support implementation:

### 1. Run the Docker Setup Test
```bash
python test_docker_setup.py
```

Expected output: All tests should pass ✓

If any test fails, the script will provide instructions on how to fix it.

### 2. Enable Docker Mode

**Option A: Use the pre-configured example**
```bash
cp config/eval_config_docker.yaml config/eval_config.yaml
```

**Option B: Manually edit config**
Edit `config/eval_config.yaml` and ensure these lines are set:
```yaml
freqtrade:
  use_docker: true
  docker_image: "freqtradeorg/freqtrade:stable"
  docker_user_data_path: "./freqtrade/user_data"
```

### 3. Ensure Docker Image is Available
```bash
docker pull freqtradeorg/freqtrade:stable
docker run --rm freqtradeorg/freqtrade:stable --version
```

You should see the Freqtrade version output.

### 4. Download Test Data (if not already done)

```bash
# Make sure the directories exist
mkdir -p freqtrade/user_data/data
mkdir -p freqtrade/user_data/strategies

# Download sample data
docker run --rm -v "$(pwd)/freqtrade/user_data:/freqtrade/user_data" \
  freqtradeorg/freqtrade:stable \
  download-data \
  --exchange binance \
  --pairs BTC/USDT ETH/USDT \
  --timeframe 5m 1h \
  --days 30
```

This might take a few minutes depending on your internet speed.

### 5. Run a Small Test Evolution

```bash
python run_evolution.py --no-mock --generations 2 --population 5
```

**Expected behavior:**
- Should NOT show "No such file or directory: 'freqtrade'" errors
- Should show "Running backtest for strategy: Strategy_Gen000_Strat_XXX"
- May show some warnings about strategies with no valid trades (this is normal if they're bad strategies)
- Should complete all generations

**If it works:** ✅ Docker support is working correctly!

**If it fails:** See troubleshooting section below.

## Full Test (15-30 minutes)

Once the quick test works, try a more realistic run:

```bash
python run_evolution.py --no-mock --generations 10 --population 20
```

This will:
- Generate 20 strategies per generation
- Run 10 generations
- Use real Freqtrade backtesting via Docker
- Save results to checkpoints and database

Monitor progress with:
```bash
# In another terminal
tail -f logs/evolution.log
```

## Troubleshooting

### Error: "Docker not found"
```bash
# Install Docker first
# Visit: https://docs.docker.com/get-docker/

# Verify installation
docker --version
```

### Error: "Permission denied" on Docker
```bash
# Linux: Add user to docker group
sudo usermod -aG docker $USER
# Log out and back in

# Or use sudo (not recommended for production)
sudo python run_evolution.py --no-mock --generations 2 --population 5
```

### Error: "Cannot pull image"
```bash
# Check internet connection
ping google.com

# Try pulling manually
docker pull freqtradeorg/freqtrade:stable

# Check Docker hub status
# Visit: https://status.docker.com/
```

### Error: "No data available"
Make sure you downloaded data first:
```bash
docker run --rm -v "$(pwd)/freqtrade/user_data:/freqtrade/user_data" \
  freqtradeorg/freqtrade:stable \
  download-data \
  --exchange binance \
  --pairs BTC/USDT ETH/USDT \
  --timeframe 5m \
  --days 30
```

### Error: "Strategy file not found"
The generated strategies should be automatically placed in:
```bash
freqtrade/user_data/strategies/
```

Check that this directory exists and is writable:
```bash
ls -la freqtrade/user_data/strategies/
```

### Still Having Issues?

1. **Run the diagnostic script:**
   ```bash
   python test_docker_setup.py
   ```
   This will identify the specific problem.

2. **Check the logs:**
   ```bash
   tail -50 logs/evolution.log
   ```

3. **Verify Docker is running:**
   ```bash
   docker ps
   ```

4. **Test Docker manually:**
   ```bash
   docker run --rm -v "$(pwd)/freqtrade/user_data:/freqtrade/user_data" \
     freqtradeorg/freqtrade:stable \
     --version
   ```

5. **Check configuration:**
   ```bash
   cat config/eval_config.yaml | grep -A5 "use_docker"
   ```
   Should show `use_docker: true`

## What Success Looks Like

When everything is working correctly, you should see:

```
03:10:57 - INFO - Starting evolution...
03:10:57 - INFO - Database initialized
03:10:57 - INFO - Starting GAFreqTrade Evolution
03:10:57 - INFO - Initializing population...
03:10:57 - INFO - Population initialized with 5 strategies
03:10:57 - INFO - GENERATION 0
03:10:57 - INFO - Evaluating generation 0...
03:10:57 - INFO - Evaluating Gen000_Strat_001...
03:10:57 - INFO - Running backtest for strategy: Strategy_Gen000_Strat_001
03:10:58 - INFO - Backtest completed in 3.45s
03:10:58 - INFO - Evaluating Gen000_Strat_002...
...
```

Note: Backtests should complete (even if strategies have no trades), not fail with "No such file or directory: 'freqtrade'".

## Expected Behavior

### Normal Outcomes:
- ✅ Some strategies may produce no valid trades (this is normal for random strategies)
- ✅ Evolution may remove poorly performing strategies
- ✅ Backtests should complete successfully (even if results are poor)
- ✅ Progress should be saved to checkpoints/

### Issues to Report:
- ❌ "No such file or directory: 'freqtrade'" errors
- ❌ Docker-related errors after following setup
- ❌ All backtests failing with the same error
- ❌ Python exceptions or crashes

## Performance Notes

Docker backtesting is slightly slower than native execution due to container overhead, but provides better isolation and consistency. Typical backtest times:

- Per strategy: 2-10 seconds (depends on data size and timerange)
- Generation of 10 strategies: 20-100 seconds
- Full evolution (10 generations, 20 strategies): 30-60 minutes

## Next Steps After Successful Test

1. **Adjust population and generation sizes** based on your needs
2. **Configure fitness weights** in `config/ga_config.yaml`
3. **Add more trading pairs** to test strategies on different markets
4. **Monitor evolution progress** with visualization tools
5. **Review top strategies** in the leaderboard

## Resources

- Full setup guide: `DOCKER_SETUP.md`
- Implementation details: `DOCKER_IMPLEMENTATION_SUMMARY.md`
- General usage: `README.md`
- Development guide: `QUICKSTART.md`

## Feedback

If you encounter any issues or have suggestions:
1. Check existing documentation
2. Run `python test_docker_setup.py` for diagnostics
3. Review logs in `logs/evolution.log`
4. Open an issue with error details and logs

---

**Happy Testing! 🚀**
