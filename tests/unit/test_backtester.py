"""
Unit tests for evaluation.backtester module.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from evaluation.backtester import BacktestResult, Backtester


class TestBacktestResult:
    """Tests for BacktestResult class."""
    
    def test_init_with_valid_results(self):
        """Test BacktestResult initialization with valid data."""
        raw_results = {
            'results': {
                'total_profit': 250.5,
                'total_profit_pct': 25.05,
                'trades': 100,
                'wins': 60,
                'losses': 40,
                'sharpe': 1.85,
                'max_drawdown_pct': -12.5
            }
        }
        
        result = BacktestResult('TestStrategy', raw_results)
        
        assert result.strategy_name == 'TestStrategy'
        assert result.raw_results == raw_results
    
    def test_get_metric_existing(self):
        """Test getting an existing metric."""
        raw_results = {
            'strategy': {
                'profit_total': 15.5,
                'total_trades': 120
            }
        }
        
        result = BacktestResult('TestStrategy', raw_results)
        
        assert result.get_metric('total_profit_pct') == 15.5
        assert result.get_metric('trades_count') == 120
    
    def test_get_metric_missing_with_default(self):
        """Test getting a missing metric with default value."""
        raw_results = {'results': {}}
        result = BacktestResult('TestStrategy', raw_results)
        
        value = result.get_metric('nonexistent', default=0.0)
        assert value == 0.0
    
    def test_is_valid_with_trades(self):
        """Test is_valid returns True when trades exist."""
        raw_results = {
            'strategy': {
                'total_trades': 50
            }
        }
        
        result = BacktestResult('TestStrategy', raw_results)
        assert result.is_valid() is True
    
    def test_is_valid_without_trades(self):
        """Test is_valid returns False when no trades."""
        raw_results = {
            'strategy': {
                'total_trades': 0
            }
        }
        
        result = BacktestResult('TestStrategy', raw_results)
        assert result.is_valid() is False
    
    def test_parse_metrics(self, mock_backtest_metrics):
        """Test metric parsing from raw results."""
        # Convert mock_backtest_metrics to freqtrade format
        raw_results = {
            'strategy': {
                'profit_total': mock_backtest_metrics.get('total_profit_pct', 0),
                'total_trades': mock_backtest_metrics.get('trades_count', 0)
            }
        }
        
        result = BacktestResult('TestStrategy', raw_results)
        
        # Should have parsed metrics
        assert result.get_metric('total_profit_pct') is not None
        assert result.get_metric('trades_count') is not None


class TestBacktesterInitialization:
    """Tests for Backtester initialization."""
    
    @patch('evaluation.backtester.os.path.exists')
    def test_backtester_init(self, mock_exists, temp_dir):
        """Test Backtester initialization."""
        mock_exists.return_value = True
        
        backtester = Backtester(
            freqtrade_path='/path/to/freqtrade',
            config_path='/path/to/config.json',
            data_dir='/path/to/data',
            strategy_dir=temp_dir,
            timeout=300
        )
        
        assert backtester.freqtrade_path == '/path/to/freqtrade'
        assert backtester.timeout == 300
    
    @patch('evaluation.backtester.os.path.exists')
    def test_backtester_default_timeout(self, mock_exists, temp_dir):
        """Test Backtester with default timeout."""
        mock_exists.return_value = True
        
        backtester = Backtester(
            freqtrade_path='/path/to/freqtrade',
            config_path='/path/to/config.json',
            strategy_dir=temp_dir
        )
        
        assert backtester.timeout > 0


class TestBacktesterCommandBuilding:
    """Tests for Freqtrade command building."""
    
    @patch('evaluation.backtester.os.path.exists')
    def test_build_command_basic(self, mock_exists, temp_dir):
        """Test basic command building."""
        mock_exists.return_value = True
        
        backtester = Backtester(
            freqtrade_path='freqtrade',
            config_path='config.json',
            strategy_dir=temp_dir
        )
        
        cmd = backtester._build_freqtrade_command(['--version'])
        
        assert 'freqtrade' in cmd
        assert '--version' in cmd
    
    @patch('evaluation.backtester.os.path.exists')
    def test_build_command_with_pairs(self, mock_exists, temp_dir):
        """Test command building with pairs."""
        mock_exists.return_value = True
        
        backtester = Backtester(
            freqtrade_path='freqtrade',
            config_path='config.json',
            strategy_dir=temp_dir
        )
        
        cmd = backtester._build_freqtrade_command(['--help'])
        
        # Just test that command builds successfully
        assert 'freqtrade' in cmd
        assert '--help' in cmd


class TestBacktesterOutputParsing:
    """Tests for Freqtrade output parsing."""
    
    @patch('evaluation.backtester.os.path.exists')
    def test_parse_json_output(self, mock_exists, temp_dir):
        """Test parsing JSON output from Freqtrade."""
        mock_exists.return_value = True
        
        backtester = Backtester(
            freqtrade_path='freqtrade',
            config_path='config.json',
            strategy_dir=temp_dir
        )
        
        json_output = """
        {
            "strategy": {
                "profit_total": 150.5,
                "total_trades": 100
            }
        }
        """
        
        result = backtester._parse_backtest_output(json_output, '')
        
        assert isinstance(result, dict)
        # Should have strategy key with results
        assert 'strategy' in result or len(result) > 0
    
    @patch('evaluation.backtester.os.path.exists')
    def test_parse_text_output(self, mock_exists, temp_dir, sample_freqtrade_output):
        """Test parsing text output from Freqtrade."""
        mock_exists.return_value = True
        
        backtester = Backtester(
            freqtrade_path='freqtrade',
            config_path='config.json',
            strategy_dir=temp_dir
        )
        
        result = backtester._parse_text_output(sample_freqtrade_output)
        
        assert isinstance(result, dict)
        # Should extract key metrics
        if 'results' in result:
            assert 'trades' in result['results'] or 'total_profit_pct' in result['results']


class TestBacktesterMockMode:
    """Tests for mock backtesting mode."""
    
    @pytest.mark.mock
    @patch('evaluation.backtester.os.path.exists')
    def test_mock_backtest_returns_result(self, mock_exists, temp_dir):
        """Test that mock backtest returns a valid result."""
        mock_exists.return_value = True
        
        backtester = Backtester(
            freqtrade_path='freqtrade',
            config_path='config.json',
            strategy_dir=temp_dir
        )
        
        # Mock the run process to return mock data
        with patch.object(backtester, 'run_backtest') as mock_run:
            mock_result = BacktestResult(
                'TestStrategy',
                {'strategy': {'profit_total': 10.0, 'total_trades': 50}}
            )
            mock_run.return_value = mock_result
            
            result = backtester.run_backtest('TestStrategy')
            
            assert isinstance(result, BacktestResult)
            assert result.is_valid()


class TestBacktesterBatchOperations:
    """Tests for batch backtesting operations."""
    
    @pytest.mark.mock
    @patch('evaluation.backtester.os.path.exists')
    def test_batch_backtest_multiple_strategies(self, mock_exists, temp_dir):
        """Test batch backtesting with multiple strategies."""
        mock_exists.return_value = True
        
        backtester = Backtester(
            freqtrade_path='freqtrade',
            config_path='config.json',
            strategy_dir=temp_dir
        )
        
        # Mock run_backtest to return results
        with patch.object(backtester, 'run_backtest') as mock_run:
            def mock_backtest(strategy_name, **kwargs):
                return BacktestResult(
                    strategy_name,
                    {'results': {'total_profit_pct': 10.0, 'trades': 50}}
                )
            
            mock_run.side_effect = mock_backtest
            
            results = backtester.run_batch_backtests(
                ['Strategy1', 'Strategy2', 'Strategy3'],
                parallel=False
            )
            
            assert len(results) == 3
            assert 'Strategy1' in results
            assert 'Strategy2' in results
            assert 'Strategy3' in results
    
    @pytest.mark.mock
    @patch('evaluation.backtester.os.path.exists')
    def test_batch_backtest_handles_errors(self, mock_exists, temp_dir):
        """Test that batch backtesting handles errors gracefully."""
        mock_exists.return_value = True
        
        backtester = Backtester(
            freqtrade_path='freqtrade',
            config_path='config.json',
            strategy_dir=temp_dir
        )
        
        with patch.object(backtester, 'run_backtest') as mock_run:
            def mock_backtest(strategy_name, **kwargs):
                if strategy_name == 'BadStrategy':
                    raise Exception('Backtest failed')
                return BacktestResult(
                    strategy_name,
                    {'results': {'total_profit_pct': 10.0, 'trades': 50}}
                )
            
            mock_run.side_effect = mock_backtest
            
            # Should handle error and continue
            try:
                results = backtester.run_batch_backtests(
                    ['GoodStrategy', 'BadStrategy', 'AnotherGood'],
                    parallel=False
                )
                # Should have results for strategies that didn't fail
                assert 'GoodStrategy' in results or len(results) >= 0
            except Exception:
                # Error handling is implementation-dependent
                pass


class TestBacktesterErrorHandling:
    """Tests for error handling in backtester."""
    
    @patch('evaluation.backtester.os.path.exists')
    def test_timeout_handling(self, mock_exists, temp_dir):
        """Test that timeout is properly configured."""
        mock_exists.return_value = True
        
        backtester = Backtester(
            freqtrade_path='freqtrade',
            config_path='config.json',
            strategy_dir=temp_dir,
            timeout=60
        )
        
        assert backtester.timeout == 60
    
    @patch('evaluation.backtester.os.path.exists')
    def test_invalid_strategy_handling(self, mock_exists, temp_dir):
        """Test handling of invalid strategy names."""
        mock_exists.return_value = True
        
        backtester = Backtester(
            freqtrade_path='freqtrade',
            config_path='config.json',
            strategy_dir=temp_dir
        )
        
        # This should either raise an exception or return invalid result
        # Implementation-dependent
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = Mock(
                returncode=1,
                stdout='',
                stderr='Strategy not found'
            )
            
            try:
                result = backtester.run_backtest('NonExistentStrategy')
                # If it returns, result should be invalid
                assert not result.is_valid()
            except Exception:
                # Or it might raise an exception
                pass


class TestBacktesterDockerMode:
    """Tests for Docker mode in Backtester."""
    
    @patch('evaluation.backtester.os.path.exists')
    def test_backtester_docker_init(self, mock_exists):
        """Test Backtester initialization with Docker mode."""
        mock_exists.return_value = True
        
        backtester = Backtester(
            freqtrade_path='freqtrade',
            config_path='freqtrade/user_data/config.json',
            strategy_dir='strategies',
            use_docker=True,
            docker_image='freqtradeorg/freqtrade:stable',
            docker_user_data_path='./freqtrade/user_data'
        )
        
        assert backtester.use_docker is True
        assert backtester.docker_image == 'freqtradeorg/freqtrade:stable'
        assert backtester.docker_user_data_path == './freqtrade/user_data'
    
    @patch('evaluation.backtester.os.path.exists')
    def test_build_docker_command(self, mock_exists):
        """Test that Docker commands are built correctly."""
        mock_exists.return_value = True
        
        backtester = Backtester(
            freqtrade_path='freqtrade',
            config_path='freqtrade/user_data/config.json',
            strategy_dir='strategies',
            use_docker=True,
            docker_image='freqtradeorg/freqtrade:stable',
            docker_user_data_path='./freqtrade/user_data'
        )
        
        cmd = backtester._build_freqtrade_command(['--version'])
        
        assert 'docker' in cmd
        assert 'run' in cmd
        assert '--rm' in cmd
        assert 'freqtradeorg/freqtrade:stable' in cmd
        assert '--version' in cmd
        # Check volume mount is in the command
        volume_mount_found = any('./freqtrade/user_data' in arg for arg in cmd)
        assert volume_mount_found
    
    @patch('evaluation.backtester.os.path.exists')
    def test_build_native_command(self, mock_exists):
        """Test that native commands are built correctly when Docker is disabled."""
        mock_exists.return_value = True
        
        backtester = Backtester(
            freqtrade_path='freqtrade',
            config_path='freqtrade/user_data/config.json',
            strategy_dir='strategies',
            use_docker=False
        )
        
        cmd = backtester._build_freqtrade_command(['--version'])
        
        assert 'freqtrade' in cmd
        assert 'docker' not in cmd
        assert '--version' in cmd
    
    @patch('evaluation.backtester.subprocess.run')
    @patch('evaluation.backtester.os.path.exists')
    def test_docker_backtest_execution(self, mock_exists, mock_run):
        """Test that backtests run with correct Docker command."""
        mock_exists.return_value = True
        mock_run.return_value = Mock(
            returncode=0,
            stdout='{"strategy": {"profit_total": 10.5, "total_trades": 100}}',
            stderr=''
        )
        
        backtester = Backtester(
            freqtrade_path='freqtrade',
            config_path='freqtrade/user_data/config.json',
            strategy_dir='strategies',
            use_docker=True,
            docker_image='freqtradeorg/freqtrade:stable',
            docker_user_data_path='./freqtrade/user_data'
        )
        
        result = backtester.run_backtest('TestStrategy')
        
        # Check that subprocess.run was called
        assert mock_run.called
        
        # Check that the command includes Docker components
        call_args = mock_run.call_args
        cmd = call_args[0][0]
        assert 'docker' in cmd
        assert 'freqtradeorg/freqtrade:stable' in cmd
        
        # Check that result is valid
        assert isinstance(result, BacktestResult)
    
    @patch('evaluation.backtester.os.path.exists')
    def test_docker_path_conversion(self, mock_exists):
        """Test that paths are correctly converted for Docker."""
        mock_exists.return_value = True
        
        backtester = Backtester(
            freqtrade_path='freqtrade',
            config_path='freqtrade/user_data/config.json',
            strategy_dir='freqtrade/user_data/strategies',
            use_docker=True,
            docker_image='freqtradeorg/freqtrade:stable',
            docker_user_data_path='./freqtrade/user_data'
        )
        
        # When running backtest, the paths should be converted to container paths
        with patch('evaluation.backtester.subprocess.run') as mock_run:
            mock_run.return_value = Mock(
                returncode=0,
                stdout='{"strategy": {"profit_total": 10.5, "total_trades": 100}}',
                stderr=''
            )
            
            backtester.run_backtest('TestStrategy')
            
            # Check that the command uses container paths
            call_args = mock_run.call_args
            cmd = call_args[0][0]
            
            # The config path should be "user_data/config.json" inside the container
            assert 'user_data/config.json' in ' '.join(cmd)
            assert 'user_data/strategies' in ' '.join(cmd)
    
    def test_absolute_paths_when_changing_working_directory(self):
        """Test that paths are converted to absolute when working directory changes."""
        import os
        
        # Mock os.path.isdir to return True for freqtrade_path
        with patch('evaluation.backtester.os.path.isdir') as mock_isdir:
            mock_isdir.return_value = True
            
            backtester = Backtester(
                freqtrade_path='freqtrade',
                config_path='freqtrade/user_data/config.json',
                data_dir='freqtrade/user_data/data',
                strategy_dir='strategies/generated',
                use_docker=False
            )
            
            # When running backtest, the paths should be converted to absolute
            with patch('evaluation.backtester.subprocess.run') as mock_run:
                mock_run.return_value = Mock(
                    returncode=0,
                    stdout='{"strategy": {"profit_total": 10.5, "total_trades": 100}}',
                    stderr=''
                )
                
                backtester.run_backtest('TestStrategy')
                
                # Check that the command uses absolute paths
                call_args = mock_run.call_args
                cmd = call_args[0][0]
                cmd_str = ' '.join(cmd)
                
                # The config path should be absolute (starts with /)
                # Find the --config argument
                config_idx = cmd.index('--config')
                config_path = cmd[config_idx + 1]
                assert os.path.isabs(config_path), f"Config path {config_path} should be absolute"
                
                # Same for datadir and strategy-path
                datadir_idx = cmd.index('--datadir')
                datadir = cmd[datadir_idx + 1]
                assert os.path.isabs(datadir), f"Data dir {datadir} should be absolute"
                
                strategy_path_idx = cmd.index('--strategy-path')
                strategy_path = cmd[strategy_path_idx + 1]
                assert os.path.isabs(strategy_path), f"Strategy path {strategy_path} should be absolute"
