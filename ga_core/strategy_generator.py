"""
Strategy Generator for GAFreqTrade

This module generates random Freqtrade trading strategies using technical indicators
and configurable entry/exit conditions.
"""

import random
import os
from datetime import datetime
from typing import Dict, List, Tuple, Any
from functools import reduce

try:
    from ga_core.strategy_template import get_template
except ModuleNotFoundError:
    from strategy_template import get_template


class IndicatorLibrary:
    """Library of available technical indicators with their configurations"""
    
    INDICATORS = {
        'rsi': {
            'name': 'RSI',
            'calculation': 'dataframe["rsi"] = ta.RSI(dataframe, timeperiod={period})',
            'params': {'period': (7, 21, 14)},  # (min, max, default)
            'column': 'rsi',
            'type': 'momentum'
        },
        'macd': {
            'name': 'MACD',
            'calculation': '''macd = ta.MACD(dataframe, fastperiod={fast}, slowperiod={slow}, signalperiod={signal})
        dataframe["macd"] = macd["macd"]
        dataframe["macdsignal"] = macd["macdsignal"]
        dataframe["macdhist"] = macd["macdhist"]''',
            'params': {
                'fast': (8, 16, 12),
                'slow': (20, 30, 26),
                'signal': (7, 12, 9)
            },
            'column': 'macd',
            'type': 'trend'
        },
        'bb': {
            'name': 'Bollinger Bands',
            'calculation': '''bollinger = qtpylib.bollinger_bands(qtpylib.typical_price(dataframe), window={period}, stds={std})
        dataframe["bb_lowerband"] = bollinger["lower"]
        dataframe["bb_middleband"] = bollinger["mid"]
        dataframe["bb_upperband"] = bollinger["upper"]
        dataframe["bb_percent"] = (dataframe["close"] - dataframe["bb_lowerband"]) / (dataframe["bb_upperband"] - dataframe["bb_lowerband"])
        dataframe["bb_width"] = (dataframe["bb_upperband"] - dataframe["bb_lowerband"]) / dataframe["bb_middleband"]''',
            'params': {
                'period': (15, 25, 20),
                'std': (1.5, 2.5, 2.0)
            },
            'column': 'bb_middleband',
            'type': 'volatility'
        },
        'ema': {
            'name': 'EMA',
            'calculation': 'dataframe["ema_{period}"] = ta.EMA(dataframe, timeperiod={period})',
            'params': {'period': (5, 50, 20)},
            'column': 'ema_{period}',
            'type': 'trend'
        },
        'sma': {
            'name': 'SMA',
            'calculation': 'dataframe["sma_{period}"] = ta.SMA(dataframe, timeperiod={period})',
            'params': {'period': (10, 100, 50)},
            'column': 'sma_{period}',
            'type': 'trend'
        },
        'adx': {
            'name': 'ADX',
            'calculation': 'dataframe["adx"] = ta.ADX(dataframe, timeperiod={period})',
            'params': {'period': (10, 20, 14)},
            'column': 'adx',
            'type': 'trend'
        },
        'cci': {
            'name': 'CCI',
            'calculation': 'dataframe["cci"] = ta.CCI(dataframe, timeperiod={period})',
            'params': {'period': (10, 30, 20)},
            'column': 'cci',
            'type': 'momentum'
        },
        'mfi': {
            'name': 'MFI',
            'calculation': 'dataframe["mfi"] = ta.MFI(dataframe, timeperiod={period})',
            'params': {'period': (10, 20, 14)},
            'column': 'mfi',
            'type': 'momentum'
        },
        'stoch': {
            'name': 'Stochastic',
            'calculation': '''stoch = ta.STOCH(dataframe, fastk_period={fastk}, slowk_period={slowk}, slowd_period={slowd})
        dataframe["slowk"] = stoch["slowk"]
        dataframe["slowd"] = stoch["slowd"]''',
            'params': {
                'fastk': (3, 7, 5),
                'slowk': (2, 5, 3),
                'slowd': (2, 5, 3)
            },
            'column': 'slowk',
            'type': 'momentum'
        },
        'atr': {
            'name': 'ATR',
            'calculation': 'dataframe["atr"] = ta.ATR(dataframe, timeperiod={period})',
            'params': {'period': (10, 20, 14)},
            'column': 'atr',
            'type': 'volatility'
        }
    }
    
    @classmethod
    def get_random_indicators(cls, min_count: int = 2, max_count: int = 6) -> List[Dict]:
        """Select random indicators"""
        count = random.randint(min_count, max_count)
        indicator_keys = random.sample(list(cls.INDICATORS.keys()), min(count, len(cls.INDICATORS)))
        
        selected = []
        for key in indicator_keys:
            indicator = cls.INDICATORS[key].copy()
            indicator['key'] = key
            
            # Randomize parameters within ranges
            params = {}
            for param_name, (min_val, max_val, default) in indicator['params'].items():
                if isinstance(min_val, int):
                    params[param_name] = random.randint(min_val, max_val)
                else:
                    params[param_name] = round(random.uniform(min_val, max_val), 2)
            
            indicator['selected_params'] = params
            selected.append(indicator)
        
        return selected


class ConditionGenerator:
    """Generate entry and exit conditions based on indicators"""
    
    CONDITION_TEMPLATES = {
        'rsi': {
            'buy': [
                'dataframe["rsi"] < {buy_rsi_threshold}',
                'dataframe["rsi"].shift(1) > dataframe["rsi"]',  # RSI falling
            ],
            'sell': [
                'dataframe["rsi"] > {sell_rsi_threshold}',
                'dataframe["rsi"].shift(1) < dataframe["rsi"]',  # RSI rising
            ]
        },
        'macd': {
            'buy': [
                'dataframe["macd"] > dataframe["macdsignal"]',
                'dataframe["macdhist"] > 0',
                '(qtpylib.crossed_above(dataframe["macd"], dataframe["macdsignal"]))',
            ],
            'sell': [
                'dataframe["macd"] < dataframe["macdsignal"]',
                'dataframe["macdhist"] < 0',
                '(qtpylib.crossed_below(dataframe["macd"], dataframe["macdsignal"]))',
            ]
        },
        'bb': {
            'buy': [
                'dataframe["close"] < dataframe["bb_lowerband"]',
                'dataframe["bb_percent"] < {bb_buy_threshold}',
            ],
            'sell': [
                'dataframe["close"] > dataframe["bb_upperband"]',
                'dataframe["bb_percent"] > {bb_sell_threshold}',
            ]
        },
        'ema': {
            'buy': [
                'dataframe["close"] > dataframe["ema_{ema_period}"]',
                '(qtpylib.crossed_above(dataframe["close"], dataframe["ema_{ema_period}"]))',
            ],
            'sell': [
                'dataframe["close"] < dataframe["ema_{ema_period}"]',
                '(qtpylib.crossed_below(dataframe["close"], dataframe["ema_{ema_period}"]))',
            ]
        },
        'sma': {
            'buy': [
                'dataframe["close"] > dataframe["sma_{sma_period}"]',
                '(qtpylib.crossed_above(dataframe["close"], dataframe["sma_{sma_period}"]))',
            ],
            'sell': [
                'dataframe["close"] < dataframe["sma_{sma_period}"]',
                '(qtpylib.crossed_below(dataframe["close"], dataframe["sma_{sma_period}"]))',
            ]
        },
        'adx': {
            'buy': [
                'dataframe["adx"] > {adx_threshold}',
            ],
            'sell': [
                'dataframe["adx"] < {adx_threshold}',
            ]
        },
        'cci': {
            'buy': [
                'dataframe["cci"] < {cci_buy_threshold}',
            ],
            'sell': [
                'dataframe["cci"] > {cci_sell_threshold}',
            ]
        },
        'mfi': {
            'buy': [
                'dataframe["mfi"] < {mfi_buy_threshold}',
            ],
            'sell': [
                'dataframe["mfi"] > {mfi_sell_threshold}',
            ]
        },
        'stoch': {
            'buy': [
                'dataframe["slowk"] < {stoch_buy_threshold}',
                '(qtpylib.crossed_above(dataframe["slowk"], dataframe["slowd"]))',
            ],
            'sell': [
                'dataframe["slowk"] > {stoch_sell_threshold}',
                '(qtpylib.crossed_below(dataframe["slowk"], dataframe["slowd"]))',
            ]
        }
    }
    
    @classmethod
    def generate_conditions(cls, indicators: List[Dict], min_conditions: int = 1, 
                          max_conditions: int = 4) -> Tuple[List[str], Dict]:
        """Generate buy and sell conditions from indicators"""
        
        buy_conditions = []
        sell_conditions = []
        hyperopt_params = {}
        
        # Get available indicators that have condition templates
        available_indicators = [ind for ind in indicators if ind['key'] in cls.CONDITION_TEMPLATES]
        
        if not available_indicators:
            # Fallback: use volume as basic condition
            buy_conditions.append('dataframe["volume"] > 0')
            sell_conditions.append('dataframe["volume"] > 0')
            return buy_conditions, sell_conditions, hyperopt_params
        
        num_buy_conditions = random.randint(min_conditions, min(max_conditions, len(available_indicators) * 2))
        num_sell_conditions = random.randint(min_conditions, min(max_conditions, len(available_indicators) * 2))
        
        # Generate buy conditions
        for _ in range(num_buy_conditions):
            indicator = random.choice(available_indicators)
            templates = cls.CONDITION_TEMPLATES[indicator['key']]['buy']
            template = random.choice(templates)
            
            # Fill in parameters
            condition, params = cls._fill_condition_parameters(template, indicator)
            if condition and condition not in buy_conditions:
                buy_conditions.append(condition)
                hyperopt_params.update(params)
        
        # Generate sell conditions
        for _ in range(num_sell_conditions):
            indicator = random.choice(available_indicators)
            templates = cls.CONDITION_TEMPLATES[indicator['key']]['sell']
            template = random.choice(templates)
            
            # Fill in parameters
            condition, params = cls._fill_condition_parameters(template, indicator)
            if condition and condition not in sell_conditions:
                sell_conditions.append(condition)
                hyperopt_params.update(params)
        
        # Ensure at least one condition each
        if not buy_conditions:
            buy_conditions.append('dataframe["volume"] > 0')
        if not sell_conditions:
            sell_conditions.append('dataframe["volume"] > 0')
        
        return buy_conditions, sell_conditions, hyperopt_params
    
    @classmethod
    def _fill_condition_parameters(cls, template: str, indicator: Dict) -> Tuple[str, Dict]:
        """Fill in condition template with parameters"""
        params = {}
        condition = template
        
        # Handle indicator-specific parameters
        if '{' in template:
            if indicator['key'] == 'rsi':
                if 'buy_rsi_threshold' in template:
                    threshold = random.randint(20, 40)
                    params['buy_rsi_threshold'] = threshold
                    condition = condition.replace('{buy_rsi_threshold}', f'self.buy_rsi_threshold.value')
                if 'sell_rsi_threshold' in template:
                    threshold = random.randint(60, 80)
                    params['sell_rsi_threshold'] = threshold
                    condition = condition.replace('{sell_rsi_threshold}', f'self.sell_rsi_threshold.value')
            
            elif indicator['key'] == 'bb':
                if 'bb_buy_threshold' in template:
                    threshold = round(random.uniform(0.1, 0.3), 2)
                    params['bb_buy_threshold'] = threshold
                    condition = condition.replace('{bb_buy_threshold}', f'self.bb_buy_threshold.value')
                if 'bb_sell_threshold' in template:
                    threshold = round(random.uniform(0.7, 0.9), 2)
                    params['bb_sell_threshold'] = threshold
                    condition = condition.replace('{bb_sell_threshold}', f'self.bb_sell_threshold.value')
            
            elif indicator['key'] in ['ema', 'sma']:
                period = indicator['selected_params']['period']
                condition = condition.replace('{ema_period}', str(period))
                condition = condition.replace('{sma_period}', str(period))
            
            elif indicator['key'] == 'adx':
                if 'adx_threshold' in template:
                    threshold = random.randint(20, 30)
                    params['adx_threshold'] = threshold
                    condition = condition.replace('{adx_threshold}', f'self.adx_threshold.value')
            
            elif indicator['key'] == 'cci':
                if 'cci_buy_threshold' in template:
                    threshold = random.randint(-150, -50)
                    params['cci_buy_threshold'] = threshold
                    condition = condition.replace('{cci_buy_threshold}', f'self.cci_buy_threshold.value')
                if 'cci_sell_threshold' in template:
                    threshold = random.randint(50, 150)
                    params['cci_sell_threshold'] = threshold
                    condition = condition.replace('{cci_sell_threshold}', f'self.cci_sell_threshold.value')
            
            elif indicator['key'] == 'mfi':
                if 'mfi_buy_threshold' in template:
                    threshold = random.randint(15, 35)
                    params['mfi_buy_threshold'] = threshold
                    condition = condition.replace('{mfi_buy_threshold}', f'self.mfi_buy_threshold.value')
                if 'mfi_sell_threshold' in template:
                    threshold = random.randint(65, 85)
                    params['mfi_sell_threshold'] = threshold
                    condition = condition.replace('{mfi_sell_threshold}', f'self.mfi_sell_threshold.value')
            
            elif indicator['key'] == 'stoch':
                if 'stoch_buy_threshold' in template:
                    threshold = random.randint(15, 30)
                    params['stoch_buy_threshold'] = threshold
                    condition = condition.replace('{stoch_buy_threshold}', f'self.stoch_buy_threshold.value')
                if 'stoch_sell_threshold' in template:
                    threshold = random.randint(70, 85)
                    params['stoch_sell_threshold'] = threshold
                    condition = condition.replace('{stoch_sell_threshold}', f'self.stoch_sell_threshold.value')
        
        return condition, params


class StrategyGenerator:
    """Main strategy generator class"""
    
    def __init__(self, output_dir: str = "strategies/generated"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def generate_random_strategy(self, generation: int = 0, strategy_num: int = 1,
                                min_indicators: int = 2, max_indicators: int = 6,
                                min_conditions: int = 1, max_conditions: int = 4) -> Dict[str, Any]:
        """
        Generate a random trading strategy
        
        Args:
            generation: Current generation number
            strategy_num: Strategy number within generation
            min_indicators: Minimum number of indicators
            max_indicators: Maximum number of indicators
            min_conditions: Minimum entry/exit conditions
            max_conditions: Maximum entry/exit conditions
            
        Returns:
            Dictionary with strategy metadata and file path
        """
        
        # Generate unique strategy ID and class name
        strategy_id = f"Gen{generation:03d}_Strat_{strategy_num:03d}"
        class_name = f"Strategy_{strategy_id}"
        
        # Select random indicators
        indicators = IndicatorLibrary.get_random_indicators(min_indicators, max_indicators)
        
        # Generate indicator calculations code
        indicator_calculations = self._generate_indicator_code(indicators)
        
        # Generate conditions
        buy_conditions, sell_conditions, hyperopt_params = ConditionGenerator.generate_conditions(
            indicators, min_conditions, max_conditions
        )
        
        # Generate hyperopt parameters code
        hyperopt_code = self._generate_hyperopt_parameters(hyperopt_params)
        
        # Format entry/exit conditions
        entry_code = self._format_conditions(buy_conditions)
        exit_code = self._format_conditions(sell_conditions)
        
        # Generate random strategy parameters
        timeframe = random.choice(['1m', '5m', '15m', '30m', '1h'])
        stoploss = round(random.uniform(-0.15, -0.05), 3)
        
        trailing_stop = random.choice([True, False])
        trailing_stop_positive = round(random.uniform(0.005, 0.02), 3) if trailing_stop else 0.0
        trailing_stop_positive_offset = round(random.uniform(0.01, 0.03), 3) if trailing_stop else 0.0
        trailing_only_offset_is_reached = trailing_stop
        
        minimal_roi = self._generate_minimal_roi()
        startup_candle_count = max(30, max([ind['selected_params'].get('period', 30) for ind in indicators]))
        
        # Fill template
        template = get_template()
        strategy_code = template.format(
            generation_date=datetime.now().isoformat(),
            generation=generation,
            strategy_id=strategy_id,
            class_name=class_name,
            strategy_description=f"Auto-generated strategy using {len(indicators)} indicators",
            parents="None (Random)",
            timeframe=timeframe,
            minimal_roi=repr(minimal_roi),
            stoploss=stoploss,
            trailing_stop=trailing_stop,
            trailing_stop_positive=trailing_stop_positive,
            trailing_stop_positive_offset=trailing_stop_positive_offset,
            trailing_only_offset_is_reached=trailing_only_offset_is_reached,
            startup_candle_count=startup_candle_count,
            hyperopt_parameters=hyperopt_code,
            indicator_calculations=indicator_calculations,
            entry_conditions=entry_code,
            exit_conditions=exit_code
        )
        
        # Add reduce import if needed
        if 'reduce' in strategy_code:
            strategy_code = strategy_code.replace(
                'from typing import Dict, Optional, Union, Tuple',
                'from typing import Dict, Optional, Union, Tuple\nfrom functools import reduce'
            )
        
        # Write to file
        filename = f"{class_name}.py"
        filepath = os.path.join(self.output_dir, filename)
        
        with open(filepath, 'w') as f:
            f.write(strategy_code)
        
        # Return metadata
        metadata = {
            'strategy_id': strategy_id,
            'class_name': class_name,
            'generation': generation,
            'strategy_num': strategy_num,
            'file_path': filepath,
            'indicators': [ind['key'] for ind in indicators],
            'num_buy_conditions': len(buy_conditions),
            'num_sell_conditions': len(sell_conditions),
            'timeframe': timeframe,
            'stoploss': stoploss,
            'trailing_stop': trailing_stop,
            'hyperopt_params': list(hyperopt_params.keys()),
            'created_at': datetime.now().isoformat()
        }
        
        return metadata
    
    def _generate_indicator_code(self, indicators: List[Dict]) -> str:
        """Generate indicator calculation code"""
        code_lines = []
        
        for indicator in indicators:
            calc_template = indicator['calculation']
            params = indicator['selected_params']
            
            # Format calculation with selected parameters
            calc_code = calc_template.format(**params)
            code_lines.append(f"        # {indicator['name']}")
            code_lines.append(f"        {calc_code}")
            code_lines.append("")
        
        return "\n".join(code_lines)
    
    def _generate_hyperopt_parameters(self, hyperopt_params: Dict) -> str:
        """Generate hyperopt parameter definitions"""
        if not hyperopt_params:
            return "    # No hyperopt parameters"
        
        code_lines = []
        
        for param_name, default_value in hyperopt_params.items():
            if isinstance(default_value, int):
                # Integer parameter
                min_val = max(0, default_value - 20)
                max_val = default_value + 20
                code_lines.append(
                    f"    {param_name} = IntParameter({min_val}, {max_val}, default={default_value}, space='buy')"
                )
            elif isinstance(default_value, float):
                # Decimal parameter
                min_val = max(0.0, default_value - 0.2)
                max_val = default_value + 0.2
                code_lines.append(
                    f"    {param_name} = DecimalParameter({min_val:.2f}, {max_val:.2f}, default={default_value:.2f}, decimals=2, space='buy')"
                )
        
        return "\n".join(code_lines)
    
    def _format_conditions(self, conditions: List[str]) -> str:
        """Format conditions for the strategy"""
        if not conditions:
            return "        # No conditions"
        
        code_lines = []
        for condition in conditions:
            code_lines.append(f"        conditions.append({condition})")
        
        return "\n".join(code_lines)
    
    def _generate_minimal_roi(self) -> Dict[str, float]:
        """Generate minimal ROI table"""
        roi_steps = sorted([
            random.randint(0, 10),
            random.randint(15, 30),
            random.randint(40, 60),
            random.randint(70, 120)
        ])
        
        roi_values = sorted([
            round(random.uniform(0.01, 0.03), 3),
            round(random.uniform(0.03, 0.06), 3),
            round(random.uniform(0.06, 0.10), 3),
            round(random.uniform(0.10, 0.20), 3)
        ], reverse=True)
        
        return {str(step): value for step, value in zip(roi_steps, roi_values)}


def generate_initial_population(population_size: int, output_dir: str = "strategies/generated") -> List[Dict]:
    """
    Generate initial population of random strategies
    
    Args:
        population_size: Number of strategies to generate
        output_dir: Directory to save generated strategies
        
    Returns:
        List of strategy metadata dictionaries
    """
    generator = StrategyGenerator(output_dir)
    population = []
    
    for i in range(population_size):
        metadata = generator.generate_random_strategy(generation=0, strategy_num=i+1)
        population.append(metadata)
    
    return population


if __name__ == "__main__":
    # Test: Generate 5 random strategies
    print("Generating 5 test strategies...")
    population = generate_initial_population(5, "strategies/generated")
    
    print(f"\nGenerated {len(population)} strategies:")
    for strategy in population:
        print(f"  - {strategy['class_name']}: {len(strategy['indicators'])} indicators, "
              f"{strategy['num_buy_conditions']} buy conditions, "
              f"{strategy['num_sell_conditions']} sell conditions")
