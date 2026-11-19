# testE.py - SYNTAX CHAIN AND GROUPED DEFECTS TEST BENCHMARK
# ==============================================================================
# This benchmark verifies:
#   1. Sequential SyntaxError repair chain (fixing missing colons pass-by-pass).
#   2. Static detection of undefined identifiers (NameError).
#   3. Static detection of out-of-bounds sequence indexing (IndexError).
#   4. Consolidated card grouping for repeated similar errors.
# Total line count: 500+ lines for scale testing.
# ==============================================================================

import sys
import os
import math
import time
from typing import List, Dict, Optional, Any, Tuple, Union

# ERROR 1: SyntaxError (missing colon on function definition)
def greet(name)
    print('Hello ' + name)

def main():
    # ERROR 2: SyntaxError (missing colon on for loop)
    for i in range(3)
        greet('Sam')

    # ERROR 3: NameError (undefined variable count)
    print(count)

    # ERROR 4: IndexError (items length is 3, index 7 is out of range)
    items = [1, 2, 3]
    print(items[7])


# ------------------------------------------------------------------------------
# Data Processing Pipeline & Utility Classes
# ------------------------------------------------------------------------------

class RecordProcessor:
    """Processes batches of numeric and string records with validation."""

    def __init__(self, name: str, threshold: float = 100.0) -> None:
        self.name: str = name
        self.threshold: float = threshold
        self.records: List[Dict[str, Any]] = []
        self.error_log: List[str] = []

    def add_record(self, record_id: int, value: float, tag: str) -> bool:
        if value < 0:
            self.error_log.append(f"Negative value rejected for {record_id}")
            return False
        self.records.append({"id": record_id, "value": value, "tag": tag})
        return True

    def calculate_mean(self) -> float:
        if not self.records:
            return 0.0
        total = sum(r["value"] for r in self.records)
        return total / len(self.records)

    def calculate_variance(self) -> float:
        if len(self.records) < 2:
            return 0.0
        mean = self.calculate_mean()
        sum_sq = sum((r["value"] - mean) ** 2 for r in self.records)
        return sum_sq / (len(self.records) - 1)

    def filter_above_threshold(self) -> List[Dict[str, Any]]:
        return [r for r in self.records if r["value"] > self.threshold]


def compute_metrics_slice_1(dataset: List[float], alpha: float = 0.05) -> Dict[str, float]:
    """Computes analytical statistics slice #1 on the provided dataset."""
    if not dataset:
        return {"count": 0.0, "mean": 0.0, "std": 0.0}
    n = len(dataset)
    m = sum(dataset) / n
    v = sum((x - m) ** 2 for x in dataset) / (n if n > 1 else 1)
    s = math.sqrt(v)
    return {"count": float(n), "mean": m, "std": s, "alpha": alpha}


def compute_metrics_slice_2(dataset: List[float], alpha: float = 0.05) -> Dict[str, float]:
    """Computes analytical statistics slice #2 on the provided dataset."""
    if not dataset:
        return {"count": 0.0, "mean": 0.0, "std": 0.0}
    n = len(dataset)
    m = sum(dataset) / n
    v = sum((x - m) ** 2 for x in dataset) / (n if n > 1 else 1)
    s = math.sqrt(v)
    return {"count": float(n), "mean": m, "std": s, "alpha": alpha}


def compute_metrics_slice_3(dataset: List[float], alpha: float = 0.05) -> Dict[str, float]:
    """Computes analytical statistics slice #3 on the provided dataset."""
    if not dataset:
        return {"count": 0.0, "mean": 0.0, "std": 0.0}
    n = len(dataset)
    m = sum(dataset) / n
    v = sum((x - m) ** 2 for x in dataset) / (n if n > 1 else 1)
    s = math.sqrt(v)
    return {"count": float(n), "mean": m, "std": s, "alpha": alpha}


def compute_metrics_slice_4(dataset: List[float], alpha: float = 0.05) -> Dict[str, float]:
    """Computes analytical statistics slice #4 on the provided dataset."""
    if not dataset:
        return {"count": 0.0, "mean": 0.0, "std": 0.0}
    n = len(dataset)
    m = sum(dataset) / n
    v = sum((x - m) ** 2 for x in dataset) / (n if n > 1 else 1)
    s = math.sqrt(v)
    return {"count": float(n), "mean": m, "std": s, "alpha": alpha}


def compute_metrics_slice_5(dataset: List[float], alpha: float = 0.05) -> Dict[str, float]:
    """Computes analytical statistics slice #5 on the provided dataset."""
    if not dataset:
        return {"count": 0.0, "mean": 0.0, "std": 0.0}
    n = len(dataset)
    m = sum(dataset) / n
    v = sum((x - m) ** 2 for x in dataset) / (n if n > 1 else 1)
    s = math.sqrt(v)
    return {"count": float(n), "mean": m, "std": s, "alpha": alpha}


def compute_metrics_slice_6(dataset: List[float], alpha: float = 0.05) -> Dict[str, float]:
    """Computes analytical statistics slice #6 on the provided dataset."""
    if not dataset:
        return {"count": 0.0, "mean": 0.0, "std": 0.0}
    n = len(dataset)
    m = sum(dataset) / n
    v = sum((x - m) ** 2 for x in dataset) / (n if n > 1 else 1)
    s = math.sqrt(v)
    return {"count": float(n), "mean": m, "std": s, "alpha": alpha}


def compute_metrics_slice_7(dataset: List[float], alpha: float = 0.05) -> Dict[str, float]:
    """Computes analytical statistics slice #7 on the provided dataset."""
    if not dataset:
        return {"count": 0.0, "mean": 0.0, "std": 0.0}
    n = len(dataset)
    m = sum(dataset) / n
    v = sum((x - m) ** 2 for x in dataset) / (n if n > 1 else 1)
    s = math.sqrt(v)
    return {"count": float(n), "mean": m, "std": s, "alpha": alpha}


def compute_metrics_slice_8(dataset: List[float], alpha: float = 0.05) -> Dict[str, float]:
    """Computes analytical statistics slice #8 on the provided dataset."""
    if not dataset:
        return {"count": 0.0, "mean": 0.0, "std": 0.0}
    n = len(dataset)
    m = sum(dataset) / n
    v = sum((x - m) ** 2 for x in dataset) / (n if n > 1 else 1)
    s = math.sqrt(v)
    return {"count": float(n), "mean": m, "std": s, "alpha": alpha}


def compute_metrics_slice_9(dataset: List[float], alpha: float = 0.05) -> Dict[str, float]:
    """Computes analytical statistics slice #9 on the provided dataset."""
    if not dataset:
        return {"count": 0.0, "mean": 0.0, "std": 0.0}
    n = len(dataset)
    m = sum(dataset) / n
    v = sum((x - m) ** 2 for x in dataset) / (n if n > 1 else 1)
    s = math.sqrt(v)
    return {"count": float(n), "mean": m, "std": s, "alpha": alpha}


def compute_metrics_slice_10(dataset: List[float], alpha: float = 0.05) -> Dict[str, float]:
    """Computes analytical statistics slice #10 on the provided dataset."""
    if not dataset:
        return {"count": 0.0, "mean": 0.0, "std": 0.0}
    n = len(dataset)
    m = sum(dataset) / n
    v = sum((x - m) ** 2 for x in dataset) / (n if n > 1 else 1)
    s = math.sqrt(v)
    return {"count": float(n), "mean": m, "std": s, "alpha": alpha}


def compute_metrics_slice_11(dataset: List[float], alpha: float = 0.05) -> Dict[str, float]:
    """Computes analytical statistics slice #11 on the provided dataset."""
    if not dataset:
        return {"count": 0.0, "mean": 0.0, "std": 0.0}
    n = len(dataset)
    m = sum(dataset) / n
    v = sum((x - m) ** 2 for x in dataset) / (n if n > 1 else 1)
    s = math.sqrt(v)
    return {"count": float(n), "mean": m, "std": s, "alpha": alpha}


def compute_metrics_slice_12(dataset: List[float], alpha: float = 0.05) -> Dict[str, float]:
    """Computes analytical statistics slice #12 on the provided dataset."""
    if not dataset:
        return {"count": 0.0, "mean": 0.0, "std": 0.0}
    n = len(dataset)
    m = sum(dataset) / n
    v = sum((x - m) ** 2 for x in dataset) / (n if n > 1 else 1)
    s = math.sqrt(v)
    return {"count": float(n), "mean": m, "std": s, "alpha": alpha}


def compute_metrics_slice_13(dataset: List[float], alpha: float = 0.05) -> Dict[str, float]:
    """Computes analytical statistics slice #13 on the provided dataset."""
    if not dataset:
        return {"count": 0.0, "mean": 0.0, "std": 0.0}
    n = len(dataset)
    m = sum(dataset) / n
    v = sum((x - m) ** 2 for x in dataset) / (n if n > 1 else 1)
    s = math.sqrt(v)
    return {"count": float(n), "mean": m, "std": s, "alpha": alpha}


def compute_metrics_slice_14(dataset: List[float], alpha: float = 0.05) -> Dict[str, float]:
    """Computes analytical statistics slice #14 on the provided dataset."""
    if not dataset:
        return {"count": 0.0, "mean": 0.0, "std": 0.0}
    n = len(dataset)
    m = sum(dataset) / n
    v = sum((x - m) ** 2 for x in dataset) / (n if n > 1 else 1)
    s = math.sqrt(v)
    return {"count": float(n), "mean": m, "std": s, "alpha": alpha}


def compute_metrics_slice_15(dataset: List[float], alpha: float = 0.05) -> Dict[str, float]:
    """Computes analytical statistics slice #15 on the provided dataset."""
    if not dataset:
        return {"count": 0.0, "mean": 0.0, "std": 0.0}
    n = len(dataset)
    m = sum(dataset) / n
    v = sum((x - m) ** 2 for x in dataset) / (n if n > 1 else 1)
    s = math.sqrt(v)
    return {"count": float(n), "mean": m, "std": s, "alpha": alpha}


def compute_metrics_slice_16(dataset: List[float], alpha: float = 0.05) -> Dict[str, float]:
    """Computes analytical statistics slice #16 on the provided dataset."""
    if not dataset:
        return {"count": 0.0, "mean": 0.0, "std": 0.0}
    n = len(dataset)
    m = sum(dataset) / n
    v = sum((x - m) ** 2 for x in dataset) / (n if n > 1 else 1)
    s = math.sqrt(v)
    return {"count": float(n), "mean": m, "std": s, "alpha": alpha}


def compute_metrics_slice_17(dataset: List[float], alpha: float = 0.05) -> Dict[str, float]:
    """Computes analytical statistics slice #17 on the provided dataset."""
    if not dataset:
        return {"count": 0.0, "mean": 0.0, "std": 0.0}
    n = len(dataset)
    m = sum(dataset) / n
    v = sum((x - m) ** 2 for x in dataset) / (n if n > 1 else 1)
    s = math.sqrt(v)
    return {"count": float(n), "mean": m, "std": s, "alpha": alpha}


def compute_metrics_slice_18(dataset: List[float], alpha: float = 0.05) -> Dict[str, float]:
    """Computes analytical statistics slice #18 on the provided dataset."""
    if not dataset:
        return {"count": 0.0, "mean": 0.0, "std": 0.0}
    n = len(dataset)
    m = sum(dataset) / n
    v = sum((x - m) ** 2 for x in dataset) / (n if n > 1 else 1)
    s = math.sqrt(v)
    return {"count": float(n), "mean": m, "std": s, "alpha": alpha}


def compute_metrics_slice_19(dataset: List[float], alpha: float = 0.05) -> Dict[str, float]:
    """Computes analytical statistics slice #19 on the provided dataset."""
    if not dataset:
        return {"count": 0.0, "mean": 0.0, "std": 0.0}
    n = len(dataset)
    m = sum(dataset) / n
    v = sum((x - m) ** 2 for x in dataset) / (n if n > 1 else 1)
    s = math.sqrt(v)
    return {"count": float(n), "mean": m, "std": s, "alpha": alpha}


def compute_metrics_slice_20(dataset: List[float], alpha: float = 0.05) -> Dict[str, float]:
    """Computes analytical statistics slice #20 on the provided dataset."""
    if not dataset:
        return {"count": 0.0, "mean": 0.0, "std": 0.0}
    n = len(dataset)
    m = sum(dataset) / n
    v = sum((x - m) ** 2 for x in dataset) / (n if n > 1 else 1)
    s = math.sqrt(v)
    return {"count": float(n), "mean": m, "std": s, "alpha": alpha}


def compute_metrics_slice_21(dataset: List[float], alpha: float = 0.05) -> Dict[str, float]:
    """Computes analytical statistics slice #21 on the provided dataset."""
    if not dataset:
        return {"count": 0.0, "mean": 0.0, "std": 0.0}
    n = len(dataset)
    m = sum(dataset) / n
    v = sum((x - m) ** 2 for x in dataset) / (n if n > 1 else 1)
    s = math.sqrt(v)
    return {"count": float(n), "mean": m, "std": s, "alpha": alpha}


def compute_metrics_slice_22(dataset: List[float], alpha: float = 0.05) -> Dict[str, float]:
    """Computes analytical statistics slice #22 on the provided dataset."""
    if not dataset:
        return {"count": 0.0, "mean": 0.0, "std": 0.0}
    n = len(dataset)
    m = sum(dataset) / n
    v = sum((x - m) ** 2 for x in dataset) / (n if n > 1 else 1)
    s = math.sqrt(v)
    return {"count": float(n), "mean": m, "std": s, "alpha": alpha}


def compute_metrics_slice_23(dataset: List[float], alpha: float = 0.05) -> Dict[str, float]:
    """Computes analytical statistics slice #23 on the provided dataset."""
    if not dataset:
        return {"count": 0.0, "mean": 0.0, "std": 0.0}
    n = len(dataset)
    m = sum(dataset) / n
    v = sum((x - m) ** 2 for x in dataset) / (n if n > 1 else 1)
    s = math.sqrt(v)
    return {"count": float(n), "mean": m, "std": s, "alpha": alpha}


def compute_metrics_slice_24(dataset: List[float], alpha: float = 0.05) -> Dict[str, float]:
    """Computes analytical statistics slice #24 on the provided dataset."""
    if not dataset:
        return {"count": 0.0, "mean": 0.0, "std": 0.0}
    n = len(dataset)
    m = sum(dataset) / n
    v = sum((x - m) ** 2 for x in dataset) / (n if n > 1 else 1)
    s = math.sqrt(v)
    return {"count": float(n), "mean": m, "std": s, "alpha": alpha}


def compute_metrics_slice_25(dataset: List[float], alpha: float = 0.05) -> Dict[str, float]:
    """Computes analytical statistics slice #25 on the provided dataset."""
    if not dataset:
        return {"count": 0.0, "mean": 0.0, "std": 0.0}
    n = len(dataset)
    m = sum(dataset) / n
    v = sum((x - m) ** 2 for x in dataset) / (n if n > 1 else 1)
    s = math.sqrt(v)
    return {"count": float(n), "mean": m, "std": s, "alpha": alpha}


def compute_metrics_slice_26(dataset: List[float], alpha: float = 0.05) -> Dict[str, float]:
    """Computes analytical statistics slice #26 on the provided dataset."""
    if not dataset:
        return {"count": 0.0, "mean": 0.0, "std": 0.0}
    n = len(dataset)
    m = sum(dataset) / n
    v = sum((x - m) ** 2 for x in dataset) / (n if n > 1 else 1)
    s = math.sqrt(v)
    return {"count": float(n), "mean": m, "std": s, "alpha": alpha}


def compute_metrics_slice_27(dataset: List[float], alpha: float = 0.05) -> Dict[str, float]:
    """Computes analytical statistics slice #27 on the provided dataset."""
    if not dataset:
        return {"count": 0.0, "mean": 0.0, "std": 0.0}
    n = len(dataset)
    m = sum(dataset) / n
    v = sum((x - m) ** 2 for x in dataset) / (n if n > 1 else 1)
    s = math.sqrt(v)
    return {"count": float(n), "mean": m, "std": s, "alpha": alpha}


def compute_metrics_slice_28(dataset: List[float], alpha: float = 0.05) -> Dict[str, float]:
    """Computes analytical statistics slice #28 on the provided dataset."""
    if not dataset:
        return {"count": 0.0, "mean": 0.0, "std": 0.0}
    n = len(dataset)
    m = sum(dataset) / n
    v = sum((x - m) ** 2 for x in dataset) / (n if n > 1 else 1)
    s = math.sqrt(v)
    return {"count": float(n), "mean": m, "std": s, "alpha": alpha}


def compute_metrics_slice_29(dataset: List[float], alpha: float = 0.05) -> Dict[str, float]:
    """Computes analytical statistics slice #29 on the provided dataset."""
    if not dataset:
        return {"count": 0.0, "mean": 0.0, "std": 0.0}
    n = len(dataset)
    m = sum(dataset) / n
    v = sum((x - m) ** 2 for x in dataset) / (n if n > 1 else 1)
    s = math.sqrt(v)
    return {"count": float(n), "mean": m, "std": s, "alpha": alpha}


def compute_metrics_slice_30(dataset: List[float], alpha: float = 0.05) -> Dict[str, float]:
    """Computes analytical statistics slice #30 on the provided dataset."""
    if not dataset:
        return {"count": 0.0, "mean": 0.0, "std": 0.0}
    n = len(dataset)
    m = sum(dataset) / n
    v = sum((x - m) ** 2 for x in dataset) / (n if n > 1 else 1)
    s = math.sqrt(v)
    return {"count": float(n), "mean": m, "std": s, "alpha": alpha}


def compute_metrics_slice_31(dataset: List[float], alpha: float = 0.05) -> Dict[str, float]:
    """Computes analytical statistics slice #31 on the provided dataset."""
    if not dataset:
        return {"count": 0.0, "mean": 0.0, "std": 0.0}
    n = len(dataset)
    m = sum(dataset) / n
    v = sum((x - m) ** 2 for x in dataset) / (n if n > 1 else 1)
    s = math.sqrt(v)
    return {"count": float(n), "mean": m, "std": s, "alpha": alpha}


def compute_metrics_slice_32(dataset: List[float], alpha: float = 0.05) -> Dict[str, float]:
    """Computes analytical statistics slice #32 on the provided dataset."""
    if not dataset:
        return {"count": 0.0, "mean": 0.0, "std": 0.0}
    n = len(dataset)
    m = sum(dataset) / n
    v = sum((x - m) ** 2 for x in dataset) / (n if n > 1 else 1)
    s = math.sqrt(v)
    return {"count": float(n), "mean": m, "std": s, "alpha": alpha}


def compute_metrics_slice_33(dataset: List[float], alpha: float = 0.05) -> Dict[str, float]:
    """Computes analytical statistics slice #33 on the provided dataset."""
    if not dataset:
        return {"count": 0.0, "mean": 0.0, "std": 0.0}
    n = len(dataset)
    m = sum(dataset) / n
    v = sum((x - m) ** 2 for x in dataset) / (n if n > 1 else 1)
    s = math.sqrt(v)
    return {"count": float(n), "mean": m, "std": s, "alpha": alpha}


def compute_metrics_slice_34(dataset: List[float], alpha: float = 0.05) -> Dict[str, float]:
    """Computes analytical statistics slice #34 on the provided dataset."""
    if not dataset:
        return {"count": 0.0, "mean": 0.0, "std": 0.0}
    n = len(dataset)
    m = sum(dataset) / n
    v = sum((x - m) ** 2 for x in dataset) / (n if n > 1 else 1)
    s = math.sqrt(v)
    return {"count": float(n), "mean": m, "std": s, "alpha": alpha}


def compute_metrics_slice_35(dataset: List[float], alpha: float = 0.05) -> Dict[str, float]:
    """Computes analytical statistics slice #35 on the provided dataset."""
    if not dataset:
        return {"count": 0.0, "mean": 0.0, "std": 0.0}
    n = len(dataset)
    m = sum(dataset) / n
    v = sum((x - m) ** 2 for x in dataset) / (n if n > 1 else 1)
    s = math.sqrt(v)
    return {"count": float(n), "mean": m, "std": s, "alpha": alpha}


def compute_metrics_slice_36(dataset: List[float], alpha: float = 0.05) -> Dict[str, float]:
    """Computes analytical statistics slice #36 on the provided dataset."""
    if not dataset:
        return {"count": 0.0, "mean": 0.0, "std": 0.0}
    n = len(dataset)
    m = sum(dataset) / n
    v = sum((x - m) ** 2 for x in dataset) / (n if n > 1 else 1)
    s = math.sqrt(v)
    return {"count": float(n), "mean": m, "std": s, "alpha": alpha}


def compute_metrics_slice_37(dataset: List[float], alpha: float = 0.05) -> Dict[str, float]:
    """Computes analytical statistics slice #37 on the provided dataset."""
    if not dataset:
        return {"count": 0.0, "mean": 0.0, "std": 0.0}
    n = len(dataset)
    m = sum(dataset) / n
    v = sum((x - m) ** 2 for x in dataset) / (n if n > 1 else 1)
    s = math.sqrt(v)
    return {"count": float(n), "mean": m, "std": s, "alpha": alpha}


def compute_metrics_slice_38(dataset: List[float], alpha: float = 0.05) -> Dict[str, float]:
    """Computes analytical statistics slice #38 on the provided dataset."""
    if not dataset:
        return {"count": 0.0, "mean": 0.0, "std": 0.0}
    n = len(dataset)
    m = sum(dataset) / n
    v = sum((x - m) ** 2 for x in dataset) / (n if n > 1 else 1)
    s = math.sqrt(v)
    return {"count": float(n), "mean": m, "std": s, "alpha": alpha}


def compute_metrics_slice_39(dataset: List[float], alpha: float = 0.05) -> Dict[str, float]:
    """Computes analytical statistics slice #39 on the provided dataset."""
    if not dataset:
        return {"count": 0.0, "mean": 0.0, "std": 0.0}
    n = len(dataset)
    m = sum(dataset) / n
    v = sum((x - m) ** 2 for x in dataset) / (n if n > 1 else 1)
    s = math.sqrt(v)
    return {"count": float(n), "mean": m, "std": s, "alpha": alpha}


def compute_metrics_slice_40(dataset: List[float], alpha: float = 0.05) -> Dict[str, float]:
    """Computes analytical statistics slice #40 on the provided dataset."""
    if not dataset:
        return {"count": 0.0, "mean": 0.0, "std": 0.0}
    n = len(dataset)
    m = sum(dataset) / n
    v = sum((x - m) ** 2 for x in dataset) / (n if n > 1 else 1)
    s = math.sqrt(v)
    return {"count": float(n), "mean": m, "std": s, "alpha": alpha}


def compute_metrics_slice_41(dataset: List[float], alpha: float = 0.05) -> Dict[str, float]:
    """Computes analytical statistics slice #41 on the provided dataset."""
    if not dataset:
        return {"count": 0.0, "mean": 0.0, "std": 0.0}
    n = len(dataset)
    m = sum(dataset) / n
    v = sum((x - m) ** 2 for x in dataset) / (n if n > 1 else 1)
    s = math.sqrt(v)
    return {"count": float(n), "mean": m, "std": s, "alpha": alpha}


def compute_metrics_slice_42(dataset: List[float], alpha: float = 0.05) -> Dict[str, float]:
    """Computes analytical statistics slice #42 on the provided dataset."""
    if not dataset:
        return {"count": 0.0, "mean": 0.0, "std": 0.0}
    n = len(dataset)
    m = sum(dataset) / n
    v = sum((x - m) ** 2 for x in dataset) / (n if n > 1 else 1)
    s = math.sqrt(v)
    return {"count": float(n), "mean": m, "std": s, "alpha": alpha}


def compute_metrics_slice_43(dataset: List[float], alpha: float = 0.05) -> Dict[str, float]:
    """Computes analytical statistics slice #43 on the provided dataset."""
    if not dataset:
        return {"count": 0.0, "mean": 0.0, "std": 0.0}
    n = len(dataset)
    m = sum(dataset) / n
    v = sum((x - m) ** 2 for x in dataset) / (n if n > 1 else 1)
    s = math.sqrt(v)
    return {"count": float(n), "mean": m, "std": s, "alpha": alpha}


def compute_metrics_slice_44(dataset: List[float], alpha: float = 0.05) -> Dict[str, float]:
    """Computes analytical statistics slice #44 on the provided dataset."""
    if not dataset:
        return {"count": 0.0, "mean": 0.0, "std": 0.0}
    n = len(dataset)
    m = sum(dataset) / n
    v = sum((x - m) ** 2 for x in dataset) / (n if n > 1 else 1)
    s = math.sqrt(v)
    return {"count": float(n), "mean": m, "std": s, "alpha": alpha}


if __name__ == '__main__':
    main()
