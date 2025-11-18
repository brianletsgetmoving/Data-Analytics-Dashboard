"""Anomaly detection utilities."""
from typing import List, Dict, Any
import statistics


def calculate_z_score(value: float, mean: float, stddev: float) -> float:
    """
    Calculate Z-score for a value.
    
    Args:
        value: Value to calculate Z-score for
        mean: Mean of the distribution
        stddev: Standard deviation of the distribution
    
    Returns:
        Z-score
    """
    if stddev == 0:
        return 0
    return (value - mean) / stddev


def detect_anomalies_zscore(data: List[float], threshold: float = 2.0) -> List[Dict[str, Any]]:
    """
    Detect anomalies using Z-score method.
    
    Args:
        data: List of numeric values
        threshold: Z-score threshold (default 2.0 for 95% confidence)
    
    Returns:
        List of dictionaries with index, value, z_score, is_anomaly
    """
    if len(data) < 2:
        return []
    
    mean = statistics.mean(data)
    stddev = statistics.stdev(data) if len(data) > 1 else 0
    
    if stddev == 0:
        return []
    
    results = []
    for i, value in enumerate(data):
        z_score = calculate_z_score(value, mean, stddev)
        is_anomaly = abs(z_score) > threshold
        results.append({
            "index": i,
            "value": value,
            "z_score": z_score,
            "is_anomaly": is_anomaly,
        })
    
    return results


def detect_anomalies_iqr(data: List[float]) -> List[Dict[str, Any]]:
    """
    Detect anomalies using Interquartile Range (IQR) method.
    
    Args:
        data: List of numeric values
    
    Returns:
        List of dictionaries with index, value, is_anomaly
    """
    if len(data) < 4:
        return []
    
    sorted_data = sorted(data)
    q1 = statistics.median(sorted_data[:len(sorted_data)//2])
    q3 = statistics.median(sorted_data[len(sorted_data)//2:])
    iqr = q3 - q1
    
    lower_bound = q1 - 1.5 * iqr
    upper_bound = q3 + 1.5 * iqr
    
    results = []
    for i, value in enumerate(data):
        is_anomaly = value < lower_bound or value > upper_bound
        results.append({
            "index": i,
            "value": value,
            "is_anomaly": is_anomaly,
            "lower_bound": lower_bound,
            "upper_bound": upper_bound,
        })
    
    return results


def detect_time_series_anomalies(
    data: List[Dict[str, Any]],
    value_key: str,
    method: str = "zscore"
) -> List[Dict[str, Any]]:
    """
    Detect anomalies in time series data.
    
    Args:
        data: List of dictionaries with time series data
        value_key: Key for the value in each dictionary
        method: Detection method ('zscore' or 'iqr')
    
    Returns:
        List of dictionaries with anomaly information
    """
    values = [item[value_key] for item in data]
    
    if method == "zscore":
        anomalies = detect_anomalies_zscore(values)
    else:
        anomalies = detect_anomalies_iqr(values)
    
    # Merge anomaly information back into original data
    results = []
    for i, item in enumerate(data):
        anomaly_info = anomalies[i] if i < len(anomalies) else {}
        result_item = {**item, **anomaly_info}
        results.append(result_item)
    
    return results

