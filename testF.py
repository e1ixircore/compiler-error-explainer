# testF.py - RUNTIME & STATIC ERROR DETECTION BENCHMARK
# ==============================================================================
# This benchmark verifies:
#   1. Static detection of sequence out-of-bounds indexing (IndexError).
#   2. Static detection of missing dictionary keys (KeyError).
#   3. Static detection of nonexistent module imports (ModuleNotFoundError).
#   4. Consolidated card grouping for similar defects.
# Total line count: 500+ lines for scale testing.
# ==============================================================================

import sys
import os
import math
import time
from typing import List, Dict, Optional, Any, Tuple, Union

def main():
    scores = [70, 85, 90]
    profile = {'name': 'Asha', 'age': 17}

    # ERROR 1: IndexError (list scores has only 3 items, index 5 is out of range)
    print(scores[5])

    # ERROR 2: KeyError (dict profile does not contain 'grade')
    print(profile['grade'])

    # ERROR 3: ModuleNotFoundError (library missing_helper does not exist)
    import missing_helper


# ------------------------------------------------------------------------------
# Sensor Network Analytics Engine & Metric Calculators
# ------------------------------------------------------------------------------

class SensorTelemetryHub:
    """Aggregates time-series sensor telemetry and validates anomaly bounds."""

    def __init__(self, hub_id: str, sample_rate_hz: int = 100) -> None:
        self.hub_id: str = hub_id
        self.sample_rate_hz: int = sample_rate_hz
        self.readings: List[Dict[str, float]] = []
        self.calibrations: Dict[str, float] = {"temp_offset": 0.0, "pressure_gain": 1.0}

    def register_reading(self, timestamp: float, temp: float, pressure: float) -> None:
        corrected_temp = temp + self.calibrations["temp_offset"]
        corrected_pressure = pressure * self.calibrations["pressure_gain"]
        self.readings.append({"t": timestamp, "temp": corrected_temp, "pres": corrected_pressure})

    def get_temperature_bounds(self) -> Tuple[float, float]:
        if not self.readings:
            return (0.0, 0.0)
        temps = [r["temp"] for r in self.readings]
        return (min(temps), max(temps))

    def get_average_pressure(self) -> float:
        if not self.readings:
            return 101.325
        return sum(r["pres"] for r in self.readings) / len(self.readings)


def analyze_telemetry_batch_1(readings: List[float], scale_factor: float = 1.0) -> Dict[str, float]:
    """Calculates telemetry distribution and peak metrics for channel slice #1."""
    if not readings:
        return {"count": 0.0, "peak": 0.0, "mean": 0.0}
    scaled = [x * scale_factor for x in readings]
    peak_val = max(scaled)
    mean_val = sum(scaled) / len(scaled)
    return {"count": float(len(readings)), "peak": peak_val, "mean": mean_val}


def analyze_telemetry_batch_2(readings: List[float], scale_factor: float = 1.0) -> Dict[str, float]:
    """Calculates telemetry distribution and peak metrics for channel slice #2."""
    if not readings:
        return {"count": 0.0, "peak": 0.0, "mean": 0.0}
    scaled = [x * scale_factor for x in readings]
    peak_val = max(scaled)
    mean_val = sum(scaled) / len(scaled)
    return {"count": float(len(readings)), "peak": peak_val, "mean": mean_val}


def analyze_telemetry_batch_3(readings: List[float], scale_factor: float = 1.0) -> Dict[str, float]:
    """Calculates telemetry distribution and peak metrics for channel slice #3."""
    if not readings:
        return {"count": 0.0, "peak": 0.0, "mean": 0.0}
    scaled = [x * scale_factor for x in readings]
    peak_val = max(scaled)
    mean_val = sum(scaled) / len(scaled)
    return {"count": float(len(readings)), "peak": peak_val, "mean": mean_val}


def analyze_telemetry_batch_4(readings: List[float], scale_factor: float = 1.0) -> Dict[str, float]:
    """Calculates telemetry distribution and peak metrics for channel slice #4."""
    if not readings:
        return {"count": 0.0, "peak": 0.0, "mean": 0.0}
    scaled = [x * scale_factor for x in readings]
    peak_val = max(scaled)
    mean_val = sum(scaled) / len(scaled)
    return {"count": float(len(readings)), "peak": peak_val, "mean": mean_val}


def analyze_telemetry_batch_5(readings: List[float], scale_factor: float = 1.0) -> Dict[str, float]:
    """Calculates telemetry distribution and peak metrics for channel slice #5."""
    if not readings:
        return {"count": 0.0, "peak": 0.0, "mean": 0.0}
    scaled = [x * scale_factor for x in readings]
    peak_val = max(scaled)
    mean_val = sum(scaled) / len(scaled)
    return {"count": float(len(readings)), "peak": peak_val, "mean": mean_val}


def analyze_telemetry_batch_6(readings: List[float], scale_factor: float = 1.0) -> Dict[str, float]:
    """Calculates telemetry distribution and peak metrics for channel slice #6."""
    if not readings:
        return {"count": 0.0, "peak": 0.0, "mean": 0.0}
    scaled = [x * scale_factor for x in readings]
    peak_val = max(scaled)
    mean_val = sum(scaled) / len(scaled)
    return {"count": float(len(readings)), "peak": peak_val, "mean": mean_val}


def analyze_telemetry_batch_7(readings: List[float], scale_factor: float = 1.0) -> Dict[str, float]:
    """Calculates telemetry distribution and peak metrics for channel slice #7."""
    if not readings:
        return {"count": 0.0, "peak": 0.0, "mean": 0.0}
    scaled = [x * scale_factor for x in readings]
    peak_val = max(scaled)
    mean_val = sum(scaled) / len(scaled)
    return {"count": float(len(readings)), "peak": peak_val, "mean": mean_val}


def analyze_telemetry_batch_8(readings: List[float], scale_factor: float = 1.0) -> Dict[str, float]:
    """Calculates telemetry distribution and peak metrics for channel slice #8."""
    if not readings:
        return {"count": 0.0, "peak": 0.0, "mean": 0.0}
    scaled = [x * scale_factor for x in readings]
    peak_val = max(scaled)
    mean_val = sum(scaled) / len(scaled)
    return {"count": float(len(readings)), "peak": peak_val, "mean": mean_val}


def analyze_telemetry_batch_9(readings: List[float], scale_factor: float = 1.0) -> Dict[str, float]:
    """Calculates telemetry distribution and peak metrics for channel slice #9."""
    if not readings:
        return {"count": 0.0, "peak": 0.0, "mean": 0.0}
    scaled = [x * scale_factor for x in readings]
    peak_val = max(scaled)
    mean_val = sum(scaled) / len(scaled)
    return {"count": float(len(readings)), "peak": peak_val, "mean": mean_val}


def analyze_telemetry_batch_10(readings: List[float], scale_factor: float = 1.0) -> Dict[str, float]:
    """Calculates telemetry distribution and peak metrics for channel slice #10."""
    if not readings:
        return {"count": 0.0, "peak": 0.0, "mean": 0.0}
    scaled = [x * scale_factor for x in readings]
    peak_val = max(scaled)
    mean_val = sum(scaled) / len(scaled)
    return {"count": float(len(readings)), "peak": peak_val, "mean": mean_val}


def analyze_telemetry_batch_11(readings: List[float], scale_factor: float = 1.0) -> Dict[str, float]:
    """Calculates telemetry distribution and peak metrics for channel slice #11."""
    if not readings:
        return {"count": 0.0, "peak": 0.0, "mean": 0.0}
    scaled = [x * scale_factor for x in readings]
    peak_val = max(scaled)
    mean_val = sum(scaled) / len(scaled)
    return {"count": float(len(readings)), "peak": peak_val, "mean": mean_val}


def analyze_telemetry_batch_12(readings: List[float], scale_factor: float = 1.0) -> Dict[str, float]:
    """Calculates telemetry distribution and peak metrics for channel slice #12."""
    if not readings:
        return {"count": 0.0, "peak": 0.0, "mean": 0.0}
    scaled = [x * scale_factor for x in readings]
    peak_val = max(scaled)
    mean_val = sum(scaled) / len(scaled)
    return {"count": float(len(readings)), "peak": peak_val, "mean": mean_val}


def analyze_telemetry_batch_13(readings: List[float], scale_factor: float = 1.0) -> Dict[str, float]:
    """Calculates telemetry distribution and peak metrics for channel slice #13."""
    if not readings:
        return {"count": 0.0, "peak": 0.0, "mean": 0.0}
    scaled = [x * scale_factor for x in readings]
    peak_val = max(scaled)
    mean_val = sum(scaled) / len(scaled)
    return {"count": float(len(readings)), "peak": peak_val, "mean": mean_val}


def analyze_telemetry_batch_14(readings: List[float], scale_factor: float = 1.0) -> Dict[str, float]:
    """Calculates telemetry distribution and peak metrics for channel slice #14."""
    if not readings:
        return {"count": 0.0, "peak": 0.0, "mean": 0.0}
    scaled = [x * scale_factor for x in readings]
    peak_val = max(scaled)
    mean_val = sum(scaled) / len(scaled)
    return {"count": float(len(readings)), "peak": peak_val, "mean": mean_val}


def analyze_telemetry_batch_15(readings: List[float], scale_factor: float = 1.0) -> Dict[str, float]:
    """Calculates telemetry distribution and peak metrics for channel slice #15."""
    if not readings:
        return {"count": 0.0, "peak": 0.0, "mean": 0.0}
    scaled = [x * scale_factor for x in readings]
    peak_val = max(scaled)
    mean_val = sum(scaled) / len(scaled)
    return {"count": float(len(readings)), "peak": peak_val, "mean": mean_val}


def analyze_telemetry_batch_16(readings: List[float], scale_factor: float = 1.0) -> Dict[str, float]:
    """Calculates telemetry distribution and peak metrics for channel slice #16."""
    if not readings:
        return {"count": 0.0, "peak": 0.0, "mean": 0.0}
    scaled = [x * scale_factor for x in readings]
    peak_val = max(scaled)
    mean_val = sum(scaled) / len(scaled)
    return {"count": float(len(readings)), "peak": peak_val, "mean": mean_val}


def analyze_telemetry_batch_17(readings: List[float], scale_factor: float = 1.0) -> Dict[str, float]:
    """Calculates telemetry distribution and peak metrics for channel slice #17."""
    if not readings:
        return {"count": 0.0, "peak": 0.0, "mean": 0.0}
    scaled = [x * scale_factor for x in readings]
    peak_val = max(scaled)
    mean_val = sum(scaled) / len(scaled)
    return {"count": float(len(readings)), "peak": peak_val, "mean": mean_val}


def analyze_telemetry_batch_18(readings: List[float], scale_factor: float = 1.0) -> Dict[str, float]:
    """Calculates telemetry distribution and peak metrics for channel slice #18."""
    if not readings:
        return {"count": 0.0, "peak": 0.0, "mean": 0.0}
    scaled = [x * scale_factor for x in readings]
    peak_val = max(scaled)
    mean_val = sum(scaled) / len(scaled)
    return {"count": float(len(readings)), "peak": peak_val, "mean": mean_val}


def analyze_telemetry_batch_19(readings: List[float], scale_factor: float = 1.0) -> Dict[str, float]:
    """Calculates telemetry distribution and peak metrics for channel slice #19."""
    if not readings:
        return {"count": 0.0, "peak": 0.0, "mean": 0.0}
    scaled = [x * scale_factor for x in readings]
    peak_val = max(scaled)
    mean_val = sum(scaled) / len(scaled)
    return {"count": float(len(readings)), "peak": peak_val, "mean": mean_val}


def analyze_telemetry_batch_20(readings: List[float], scale_factor: float = 1.0) -> Dict[str, float]:
    """Calculates telemetry distribution and peak metrics for channel slice #20."""
    if not readings:
        return {"count": 0.0, "peak": 0.0, "mean": 0.0}
    scaled = [x * scale_factor for x in readings]
    peak_val = max(scaled)
    mean_val = sum(scaled) / len(scaled)
    return {"count": float(len(readings)), "peak": peak_val, "mean": mean_val}


def analyze_telemetry_batch_21(readings: List[float], scale_factor: float = 1.0) -> Dict[str, float]:
    """Calculates telemetry distribution and peak metrics for channel slice #21."""
    if not readings:
        return {"count": 0.0, "peak": 0.0, "mean": 0.0}
    scaled = [x * scale_factor for x in readings]
    peak_val = max(scaled)
    mean_val = sum(scaled) / len(scaled)
    return {"count": float(len(readings)), "peak": peak_val, "mean": mean_val}


def analyze_telemetry_batch_22(readings: List[float], scale_factor: float = 1.0) -> Dict[str, float]:
    """Calculates telemetry distribution and peak metrics for channel slice #22."""
    if not readings:
        return {"count": 0.0, "peak": 0.0, "mean": 0.0}
    scaled = [x * scale_factor for x in readings]
    peak_val = max(scaled)
    mean_val = sum(scaled) / len(scaled)
    return {"count": float(len(readings)), "peak": peak_val, "mean": mean_val}


def analyze_telemetry_batch_23(readings: List[float], scale_factor: float = 1.0) -> Dict[str, float]:
    """Calculates telemetry distribution and peak metrics for channel slice #23."""
    if not readings:
        return {"count": 0.0, "peak": 0.0, "mean": 0.0}
    scaled = [x * scale_factor for x in readings]
    peak_val = max(scaled)
    mean_val = sum(scaled) / len(scaled)
    return {"count": float(len(readings)), "peak": peak_val, "mean": mean_val}


def analyze_telemetry_batch_24(readings: List[float], scale_factor: float = 1.0) -> Dict[str, float]:
    """Calculates telemetry distribution and peak metrics for channel slice #24."""
    if not readings:
        return {"count": 0.0, "peak": 0.0, "mean": 0.0}
    scaled = [x * scale_factor for x in readings]
    peak_val = max(scaled)
    mean_val = sum(scaled) / len(scaled)
    return {"count": float(len(readings)), "peak": peak_val, "mean": mean_val}


def analyze_telemetry_batch_25(readings: List[float], scale_factor: float = 1.0) -> Dict[str, float]:
    """Calculates telemetry distribution and peak metrics for channel slice #25."""
    if not readings:
        return {"count": 0.0, "peak": 0.0, "mean": 0.0}
    scaled = [x * scale_factor for x in readings]
    peak_val = max(scaled)
    mean_val = sum(scaled) / len(scaled)
    return {"count": float(len(readings)), "peak": peak_val, "mean": mean_val}


def analyze_telemetry_batch_26(readings: List[float], scale_factor: float = 1.0) -> Dict[str, float]:
    """Calculates telemetry distribution and peak metrics for channel slice #26."""
    if not readings:
        return {"count": 0.0, "peak": 0.0, "mean": 0.0}
    scaled = [x * scale_factor for x in readings]
    peak_val = max(scaled)
    mean_val = sum(scaled) / len(scaled)
    return {"count": float(len(readings)), "peak": peak_val, "mean": mean_val}


def analyze_telemetry_batch_27(readings: List[float], scale_factor: float = 1.0) -> Dict[str, float]:
    """Calculates telemetry distribution and peak metrics for channel slice #27."""
    if not readings:
        return {"count": 0.0, "peak": 0.0, "mean": 0.0}
    scaled = [x * scale_factor for x in readings]
    peak_val = max(scaled)
    mean_val = sum(scaled) / len(scaled)
    return {"count": float(len(readings)), "peak": peak_val, "mean": mean_val}


def analyze_telemetry_batch_28(readings: List[float], scale_factor: float = 1.0) -> Dict[str, float]:
    """Calculates telemetry distribution and peak metrics for channel slice #28."""
    if not readings:
        return {"count": 0.0, "peak": 0.0, "mean": 0.0}
    scaled = [x * scale_factor for x in readings]
    peak_val = max(scaled)
    mean_val = sum(scaled) / len(scaled)
    return {"count": float(len(readings)), "peak": peak_val, "mean": mean_val}


def analyze_telemetry_batch_29(readings: List[float], scale_factor: float = 1.0) -> Dict[str, float]:
    """Calculates telemetry distribution and peak metrics for channel slice #29."""
    if not readings:
        return {"count": 0.0, "peak": 0.0, "mean": 0.0}
    scaled = [x * scale_factor for x in readings]
    peak_val = max(scaled)
    mean_val = sum(scaled) / len(scaled)
    return {"count": float(len(readings)), "peak": peak_val, "mean": mean_val}


def analyze_telemetry_batch_30(readings: List[float], scale_factor: float = 1.0) -> Dict[str, float]:
    """Calculates telemetry distribution and peak metrics for channel slice #30."""
    if not readings:
        return {"count": 0.0, "peak": 0.0, "mean": 0.0}
    scaled = [x * scale_factor for x in readings]
    peak_val = max(scaled)
    mean_val = sum(scaled) / len(scaled)
    return {"count": float(len(readings)), "peak": peak_val, "mean": mean_val}


def analyze_telemetry_batch_31(readings: List[float], scale_factor: float = 1.0) -> Dict[str, float]:
    """Calculates telemetry distribution and peak metrics for channel slice #31."""
    if not readings:
        return {"count": 0.0, "peak": 0.0, "mean": 0.0}
    scaled = [x * scale_factor for x in readings]
    peak_val = max(scaled)
    mean_val = sum(scaled) / len(scaled)
    return {"count": float(len(readings)), "peak": peak_val, "mean": mean_val}


def analyze_telemetry_batch_32(readings: List[float], scale_factor: float = 1.0) -> Dict[str, float]:
    """Calculates telemetry distribution and peak metrics for channel slice #32."""
    if not readings:
        return {"count": 0.0, "peak": 0.0, "mean": 0.0}
    scaled = [x * scale_factor for x in readings]
    peak_val = max(scaled)
    mean_val = sum(scaled) / len(scaled)
    return {"count": float(len(readings)), "peak": peak_val, "mean": mean_val}


def analyze_telemetry_batch_33(readings: List[float], scale_factor: float = 1.0) -> Dict[str, float]:
    """Calculates telemetry distribution and peak metrics for channel slice #33."""
    if not readings:
        return {"count": 0.0, "peak": 0.0, "mean": 0.0}
    scaled = [x * scale_factor for x in readings]
    peak_val = max(scaled)
    mean_val = sum(scaled) / len(scaled)
    return {"count": float(len(readings)), "peak": peak_val, "mean": mean_val}


def analyze_telemetry_batch_34(readings: List[float], scale_factor: float = 1.0) -> Dict[str, float]:
    """Calculates telemetry distribution and peak metrics for channel slice #34."""
    if not readings:
        return {"count": 0.0, "peak": 0.0, "mean": 0.0}
    scaled = [x * scale_factor for x in readings]
    peak_val = max(scaled)
    mean_val = sum(scaled) / len(scaled)
    return {"count": float(len(readings)), "peak": peak_val, "mean": mean_val}


def analyze_telemetry_batch_35(readings: List[float], scale_factor: float = 1.0) -> Dict[str, float]:
    """Calculates telemetry distribution and peak metrics for channel slice #35."""
    if not readings:
        return {"count": 0.0, "peak": 0.0, "mean": 0.0}
    scaled = [x * scale_factor for x in readings]
    peak_val = max(scaled)
    mean_val = sum(scaled) / len(scaled)
    return {"count": float(len(readings)), "peak": peak_val, "mean": mean_val}


def analyze_telemetry_batch_36(readings: List[float], scale_factor: float = 1.0) -> Dict[str, float]:
    """Calculates telemetry distribution and peak metrics for channel slice #36."""
    if not readings:
        return {"count": 0.0, "peak": 0.0, "mean": 0.0}
    scaled = [x * scale_factor for x in readings]
    peak_val = max(scaled)
    mean_val = sum(scaled) / len(scaled)
    return {"count": float(len(readings)), "peak": peak_val, "mean": mean_val}


def analyze_telemetry_batch_37(readings: List[float], scale_factor: float = 1.0) -> Dict[str, float]:
    """Calculates telemetry distribution and peak metrics for channel slice #37."""
    if not readings:
        return {"count": 0.0, "peak": 0.0, "mean": 0.0}
    scaled = [x * scale_factor for x in readings]
    peak_val = max(scaled)
    mean_val = sum(scaled) / len(scaled)
    return {"count": float(len(readings)), "peak": peak_val, "mean": mean_val}


def analyze_telemetry_batch_38(readings: List[float], scale_factor: float = 1.0) -> Dict[str, float]:
    """Calculates telemetry distribution and peak metrics for channel slice #38."""
    if not readings:
        return {"count": 0.0, "peak": 0.0, "mean": 0.0}
    scaled = [x * scale_factor for x in readings]
    peak_val = max(scaled)
    mean_val = sum(scaled) / len(scaled)
    return {"count": float(len(readings)), "peak": peak_val, "mean": mean_val}


def analyze_telemetry_batch_39(readings: List[float], scale_factor: float = 1.0) -> Dict[str, float]:
    """Calculates telemetry distribution and peak metrics for channel slice #39."""
    if not readings:
        return {"count": 0.0, "peak": 0.0, "mean": 0.0}
    scaled = [x * scale_factor for x in readings]
    peak_val = max(scaled)
    mean_val = sum(scaled) / len(scaled)
    return {"count": float(len(readings)), "peak": peak_val, "mean": mean_val}


def analyze_telemetry_batch_40(readings: List[float], scale_factor: float = 1.0) -> Dict[str, float]:
    """Calculates telemetry distribution and peak metrics for channel slice #40."""
    if not readings:
        return {"count": 0.0, "peak": 0.0, "mean": 0.0}
    scaled = [x * scale_factor for x in readings]
    peak_val = max(scaled)
    mean_val = sum(scaled) / len(scaled)
    return {"count": float(len(readings)), "peak": peak_val, "mean": mean_val}


def analyze_telemetry_batch_41(readings: List[float], scale_factor: float = 1.0) -> Dict[str, float]:
    """Calculates telemetry distribution and peak metrics for channel slice #41."""
    if not readings:
        return {"count": 0.0, "peak": 0.0, "mean": 0.0}
    scaled = [x * scale_factor for x in readings]
    peak_val = max(scaled)
    mean_val = sum(scaled) / len(scaled)
    return {"count": float(len(readings)), "peak": peak_val, "mean": mean_val}


def analyze_telemetry_batch_42(readings: List[float], scale_factor: float = 1.0) -> Dict[str, float]:
    """Calculates telemetry distribution and peak metrics for channel slice #42."""
    if not readings:
        return {"count": 0.0, "peak": 0.0, "mean": 0.0}
    scaled = [x * scale_factor for x in readings]
    peak_val = max(scaled)
    mean_val = sum(scaled) / len(scaled)
    return {"count": float(len(readings)), "peak": peak_val, "mean": mean_val}


def analyze_telemetry_batch_43(readings: List[float], scale_factor: float = 1.0) -> Dict[str, float]:
    """Calculates telemetry distribution and peak metrics for channel slice #43."""
    if not readings:
        return {"count": 0.0, "peak": 0.0, "mean": 0.0}
    scaled = [x * scale_factor for x in readings]
    peak_val = max(scaled)
    mean_val = sum(scaled) / len(scaled)
    return {"count": float(len(readings)), "peak": peak_val, "mean": mean_val}


def analyze_telemetry_batch_44(readings: List[float], scale_factor: float = 1.0) -> Dict[str, float]:
    """Calculates telemetry distribution and peak metrics for channel slice #44."""
    if not readings:
        return {"count": 0.0, "peak": 0.0, "mean": 0.0}
    scaled = [x * scale_factor for x in readings]
    peak_val = max(scaled)
    mean_val = sum(scaled) / len(scaled)
    return {"count": float(len(readings)), "peak": peak_val, "mean": mean_val}


if __name__ == '__main__':
    main()
