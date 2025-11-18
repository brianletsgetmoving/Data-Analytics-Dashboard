"""Forecasting calculation utilities."""
from typing import List, Dict, Any
import statistics


def calculate_moving_average(data: List[float], window: int) -> List[float]:
    """
    Calculate moving average for a list of values.
    
    Args:
        data: List of numeric values
        window: Window size for moving average
    
    Returns:
        List of moving average values
    """
    if len(data) < window:
        return data
    
    result = []
    for i in range(len(data)):
        if i < window - 1:
            result.append(sum(data[:i+1]) / (i + 1))
        else:
            result.append(sum(data[i-window+1:i+1]) / window)
    
    return result


def calculate_exponential_smoothing(data: List[float], alpha: float = 0.3) -> List[float]:
    """
    Calculate exponential smoothing forecast.
    
    Args:
        data: List of numeric values
        alpha: Smoothing parameter (0 < alpha < 1)
    
    Returns:
        List of smoothed values
    """
    if not data:
        return []
    
    result = [data[0]]
    for i in range(1, len(data)):
        smoothed = alpha * data[i] + (1 - alpha) * result[i-1]
        result.append(smoothed)
    
    return result


def calculate_linear_trend(data: List[Dict[str, Any]], value_key: str, period_key: str) -> Dict[str, float]:
    """
    Calculate linear trend using simple linear regression.
    
    Args:
        data: List of dictionaries with period and value
        value_key: Key for the value in each dictionary
        period_key: Key for the period (should be numeric)
    
    Returns:
        Dictionary with slope and intercept
    """
    if len(data) < 2:
        return {"slope": 0, "intercept": 0}
    
    periods = [item[period_key] for item in data]
    values = [item[value_key] for item in data]
    
    n = len(periods)
    sum_x = sum(periods)
    sum_y = sum(values)
    sum_xy = sum(periods[i] * values[i] for i in range(n))
    sum_x2 = sum(x * x for x in periods)
    
    denominator = n * sum_x2 - sum_x * sum_x
    if denominator == 0:
        return {"slope": 0, "intercept": sum_y / n if n > 0 else 0}
    
    slope = (n * sum_xy - sum_x * sum_y) / denominator
    intercept = (sum_y - slope * sum_x) / n
    
    return {"slope": slope, "intercept": intercept}


def calculate_confidence_interval(data: List[float], confidence: float = 0.95) -> Dict[str, float]:
    """
    Calculate confidence interval for forecast.
    
    Args:
        data: List of numeric values
        confidence: Confidence level (default 0.95 for 95%)
    
    Returns:
        Dictionary with mean, lower_bound, upper_bound
    """
    if not data:
        return {"mean": 0, "lower_bound": 0, "upper_bound": 0}
    
    mean = statistics.mean(data)
    if len(data) < 2:
        return {"mean": mean, "lower_bound": mean, "upper_bound": mean}
    
    stdev = statistics.stdev(data)
    # Simplified confidence interval (using z-score approximation)
    z_score = 1.96 if confidence == 0.95 else 2.576 if confidence == 0.99 else 1.645
    margin = z_score * stdev / (len(data) ** 0.5)
    
    return {
        "mean": mean,
        "lower_bound": mean - margin,
        "upper_bound": mean + margin,
    }


def detect_seasonality(data: List[Dict[str, Any]], value_key: str, period_key: str) -> Dict[str, Any]:
    """
    Detect seasonality in time series data.
    
    Args:
        data: List of dictionaries with period and value
        value_key: Key for the value
        period_key: Key for the period
    
    Returns:
        Dictionary with seasonality information
    """
    if len(data) < 12:
        return {"has_seasonality": False, "seasonal_pattern": None}
    
    # Group by month/period and calculate averages
    seasonal_values = {}
    for item in data:
        period = item[period_key]
        if period not in seasonal_values:
            seasonal_values[period] = []
        seasonal_values[period].append(item[value_key])
    
    seasonal_averages = {k: statistics.mean(v) for k, v in seasonal_values.items()}
    overall_avg = statistics.mean(seasonal_averages.values())
    
    # Check for significant variation
    max_seasonal = max(seasonal_averages.values())
    min_seasonal = min(seasonal_averages.values())
    variation = (max_seasonal - min_seasonal) / overall_avg if overall_avg > 0 else 0
    
    has_seasonality = variation > 0.1  # 10% variation threshold
    
    return {
        "has_seasonality": has_seasonality,
        "seasonal_pattern": seasonal_averages,
        "variation_percent": variation * 100,
    }

