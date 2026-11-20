# test_case_new.py - End-to-End Data Analytics Pipeline with 5 Planted Errors (4 Fixable, 1 Ambiguous)
import math
import json

class AnalyticsBatch:
    def __init__(self, batch_name, scale_factor=2.0):
        self.batch_name = batch_name
        self.scale_factor = scale_factor
        self.values = [12, 24, 36, 48]

    def summary_header(self):
        # ERROR 1 (TypeError - fixable): concatenating str and int
        return "Batch items: " + 4

    def latest_reading(self):
        items = [10, 20, 30]
        # ERROR 2 (IndexError - fixable): off-by-one index len(items)
        return items[len(items)]

    def lookup_metadata(self):
        meta = {"owner": "team_alpha", "version": "1.0"}
        # ERROR 3 (KeyError - fixable): missing dictionary key 'region'
        return meta["region"]

    def compute_scaled_total(self):
        total_sum = sum(self.values)
        # ERROR 4 (NameError - fixable): typo 'totl_sum' -> 'total_sum'
        return totl_sum * self.scale_factor

    def verify_convergence(self, current_loss, target_loss):
        # ERROR 5 (Ambiguous LogicalError - manual fix needed): self-comparison current_loss == current_loss
        if current_loss == current_loss:
            return True
        return False

def main():
    batch = AnalyticsBatch("experiment_01")
    print(batch.summary_header())
    print(batch.latest_reading())
    print(batch.lookup_metadata())
    print(batch.compute_scaled_total())
    print(batch.verify_convergence(0.25, 0.05))

if __name__ == "__main__":
    main()
