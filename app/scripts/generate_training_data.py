import os
import random
import csv
import sys

import numpy as np
import pandas as pd

from app import create_app
from app.api.routes.simulations import get_params, simulate_core
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# how many different user configurations to simulate
N_CONFIGS = 200  # you can bump this later to 500/1000 offline
SAMPLES_PER_CONFIG = 200  # same as your API
YEARS_CHOICES = [10, 11, 12,13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60]

def main():
    app = create_app()

    with app.app_context():
        base_path = app.root_path

        # load CSVs to get valid career_ids and states
        salaries_path = os.path.join(base_path, "salary_table.csv")
        locations_path = os.path.join(base_path, "locations_table.csv")

        salary_table = pd.read_csv(salaries_path)
        locations_table = pd.read_csv(locations_path)

        # only keep rows with valid Category + Starting Salary for now
        valid_salary_rows = salary_table[
            salary_table["Starting Salary"].notna()
        ]
        career_ids = list(valid_salary_rows["Career_ID"].astype(str).unique())

        # list of states that appear in both locations_table and home/child table is safer,
        # but for now we'll just use locations_table states:
        location_values = list(locations_table["State"].unique())

        spending_options = ["eager", "conservative"]
        num_children_options = [0, 1, 2, 3]

        print(f"Found {len(career_ids)} career_ids and {len(location_values)} locations")

        # output CSV
        out_path = os.path.join(base_path, "..", "simulation_training_data.csv")
        out_path = os.path.abspath(out_path)

        fieldnames = [
            # raw "UI" inputs
            "career_id",
            "location",
            "num_children",
            "spending",
            "years",

            # numeric params from get_params
            "starting_salary",
            "salary_growth_mean",
            "salary_growth_sd",
            "home_growth_rate",
            "salary_to_buy_house",
            "annual_child_cost",
            "savings_rate",
            "hv_to_salary_ratio",
            "effective_tax_rate_starting",
            "effective_tax_rate_100k",

            # simulation outputs
            "mean_networth",
            "stdev_networth",
            
        ]

        with open(out_path, "w", newline="", encoding="utf-8") as f_out:
            writer = csv.DictWriter(f_out, fieldnames=fieldnames)
            writer.writeheader()

            n_written = 0

            for i in range(N_CONFIGS):
                career_id = random.choice(career_ids)
                location = random.choice(location_values)
                num_children = random.choice(num_children_options)
                spending = random.choice(spending_options)
                years = random.choice(YEARS_CHOICES)

                data = {
                    "career_id": career_id,
                    "location": location,
                    "num_children": num_children,
                    "spending": spending,
                    "years": years,
                }

                try:
                    params, locations_df, home_and_rental_table = get_params(data)
                except Exception as e:
                    print(f"[{i}] Skipping config (params error): {e}")
                    continue

                try:
                    summary = simulate_core(
                        params,
                        locations_df,
                        home_and_rental_table,
                        num_samples=SAMPLES_PER_CONFIG,
                        years=years,
                    )
                except Exception as e:
                    print(f"[{i}] Skipping config (simulation error): {e}")
                    continue

                row = {
                    "career_id": career_id,
                    "location": location,
                    "num_children": num_children,
                    "spending": spending,
                    "years": years,
                    "starting_salary": params["starting_salary"],
                    "salary_growth_mean": params["salary_growth_mean"],
                    "salary_growth_sd": params["salary_growth_sd"],
                    "home_growth_rate": params["home_growth_rate"],
                    "salary_to_buy_house": params["salary_to_buy_house"],
                    "annual_child_cost": params["annual_child_cost"],
                    "savings_rate": params["savings_rate"],
                    "hv_to_salary_ratio": params["hv_to_salary_ratio"],
                    "effective_tax_rate_starting": params["effective_tax_rate_starting"],
                    "effective_tax_rate_100k": params["effective_tax_rate_100k"],
                    "mean_networth": summary["mean"],
                    "stdev_networth": summary["stdev"],
                }

                writer.writerow(row)
                n_written += 1
                print(f"[{i}] wrote config; total written: {n_written}")

        print(f"\n✅ Done. Wrote {n_written} rows to {out_path}")


if __name__ == "__main__":
    main()
