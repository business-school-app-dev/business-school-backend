from flask import Flask, request, jsonify, current_app, Blueprint
from sqlalchemy.orm import Session
from sqlalchemy import select
import numpy as np
import pandas as pd
import os
simulation_bp = Blueprint('simulation', __name__)

#from .schema import UserInfo, Asset, Liability

def get_tax_value(locations_df, state, salary):
    if (state == None):
        state_name = "United States overall"
    else:
        state_name = state

    # obtains the tax brackets for the users location and gets rid of any brakets which the user does not quaify for
    brackets = locations_df[locations_df["State"] == state_name].copy()
    brackets["Income range"] = pd.to_numeric(brackets["Income range"], errors="coerce")
    eligible_brackets = brackets[brackets["Income range"] <= salary]
    
    total_tax = 0
    remaining_salary = salary
    # starting at the highest bracket eligible, goes through all of the brackets compounding the correct tax on the taxable income in that bracket
    for i in reversed(range(len(eligible_brackets))):
        lower_bound = eligible_brackets.iloc[i]["Income range"]
        rate = eligible_brackets.iloc[i]["tax rate"]
        if (remaining_salary > lower_bound):
            taxable_amount = remaining_salary - lower_bound
            total_tax += taxable_amount * rate
            remaining_salary = lower_bound
    return total_tax

# gets a yearly home payment based on the principal 
def get_home_payment(principal):
    term_years = 30
    annual_rate = 0.05
    yearly_payment_num = annual_rate * ((1 + annual_rate) ** term_years)
    yearly_payment_denom = ((1 + annual_rate) ** term_years) - 1
    yearly_payment = principal * (yearly_payment_num / yearly_payment_denom)
    return yearly_payment

def get_params(data):
     # Extracting all the data from the csv.
    # data will be in the following form: 
    # {
    #     "job_id" : career_id              (if id data is not sent, then there would be a category and job field)
    #     "location" : location,
    #     "num_children" : num_children
    #     "spending" : eager/conservative
    # }

    # extracting input fields
    career_id = data.get("career_id")
    location = data.get("location")
    num_children = data.get("num_children")
    spending_type = data.get("spending")

    # defining paths to the parameter tables
    salaries_path = os.path.join(current_app.root_path, "salary_table.csv")
    home_and_child_path = os.path.join(current_app.root_path, "State-Specific Home Data & Child Data - Sheet1.csv")
    home_and_rental_path = os.path.join(current_app.root_path, "Home Value & Rent Value Table - Sheet1.csv")
    locations_path = os.path.join(current_app.root_path, "locations_table.csv")

    # reading data from the csvs 
    salary_table = pd.read_csv(salaries_path)
    locations_table = pd.read_csv(locations_path)
    home_and_rental_table = pd.read_csv(home_and_rental_path)
    home_and_child_table = pd.read_csv(home_and_child_path)

    # extracting relevant salary information
    salary_row = salary_table[salary_table["Career_ID"] == career_id] # extracts the row with the matching career_id
    if salary_row.empty:
        raise ValueError(f"Unknown career_id: {career_id}")
    starting_salary = float(salary_row["Starting Salary"].iloc[0])
    salary_mu = float(salary_row["Salary_growth_mean"].iloc[0])
    salary_sigma = float(salary_row["salary_growth_sd"] .iloc[0])

    # extracting relavant location information and adjusts the starting salary based on location
    locations_df = locations_table[locations_table["State"] == location]
    starting_salary *= float(locations_df["inc-nat ratio"].iloc[0])
    home_and_child_df = home_and_child_table[home_and_child_table["State"] == location]
    home_growth_rate = float(home_and_child_df["Average Home Growth Rate"].iloc[0]) / 100
    salary_to_buy_house = float(home_and_child_df["Salary Needed to Buy a House"].iloc[0])
    annual_child_cost = float(home_and_child_df["Cost of Raising Child"].iloc[0])

    # extracting tax rates
    effective_tax_rate_100k = float(locations_df["eff_tax_rate_100k"].iloc[0])
    effective_tax_rate_starting = (get_tax_value(locations_df, location, starting_salary)) / starting_salary

    if (spending_type == "eager"): 
        savings_rate = 0.2
        hv_to_salary_rat = 3

    else:
        savings_rate = 0.3
        hv_to_salary_rat = 2

    params = {
                "starting_salary": starting_salary, # slider
                "salary_growth_mean" : salary_mu,
                "salary_growth_sd" : salary_sigma, 

                "rent_pc_baseline" : 0.3,
                "salary_to_buy_house": salary_to_buy_house,
                "hv_to_salary_ratio" : hv_to_salary_rat,    # slider
                "home_growth_rate": home_growth_rate,

                "savings_rate" : savings_rate,      # slider

                "num_children" : num_children,       # slider
                "annual_child_cost" : annual_child_cost,

                "effective_tax_rate_100k" : effective_tax_rate_100k,
                "effective_tax_rate_starting" : effective_tax_rate_starting,
                                # 🔹 these two are what run_simulation expects but your dict is missing
                "location": location,
                "spending_type": spending_type,
    
            }
    return params, locations_df, home_and_rental_table


def simulate_core(
    params: dict,
    locations_df: pd.DataFrame,
    home_and_rental_table: pd.DataFrame,
    num_samples: int = 200,
    years: int = 20,
) -> dict:
    """
    Pure Python core simulation (no Flask / jsonify).
    Returns {"mean": float, "stdev": float}.
    """

    rng = np.random.default_rng(seed=42)

    starting_salary = params["starting_salary"]
    salary_mu = params["salary_growth_mean"]
    salary_sigma = params["salary_growth_sd"]

    home_growth_rate = params["home_growth_rate"]
    salary_to_buy_house = params["salary_to_buy_house"]
    annual_child_cost = params["annual_child_cost"]
    savings_rate = params["savings_rate"]  # not heavily used yet but good to carry
    num_children = params["num_children"]

    location = params["location"]
    spending_type = params["spending_type"]

    networths = []

    for _ in range(num_samples):
        local_salary = starting_salary
        total_cash = 0.0

        bought_a_house = False
        home_value = 0.0
        principal = 0.0
        annual_payment = 0.0
        mortgage_balance = 0.0


        for _year in range(years):
            # salary evolution
            growth = rng.normal(salary_mu, salary_sigma)
            local_salary *= (1.0 + growth)

            # housing logic
            if not bought_a_house:
                if local_salary < salary_to_buy_house:
                    rent_or_mortgage_payment = 0.3 * local_salary
                else:
                    rounded_salary = round(local_salary / 20_000) * 20_000

                    home_and_rent_df = home_and_rental_table[
                        home_and_rental_table["Starting Salary"] == rounded_salary
                    ]

                    if home_and_rent_df.empty:
                        home_and_rent_df = home_and_rental_table.iloc[[0]]

                    if spending_type == "eager":
                        hv_col = "Home Value (3x) (eager spending)"
                    else:
                        hv_col = "Home Value (2.5x) (conservative spending)"

                    home_value = float(home_and_rent_df[hv_col].iloc[0])

                    principal = 0.91 * home_value
                    down_payment = 0.09 * home_value

                    annual_payment = get_home_payment(principal)
                    mortgage_balance = principal

                    bought_a_house = True
                    rent_or_mortgage_payment = down_payment
            else:
                home_value *= (1.0 + home_growth_rate)

                if mortgage_balance > 0:
                    annual_rate = 0.05
                    interest = mortgage_balance * annual_rate
                    principal_paid = annual_payment - interest

                    if principal_paid > mortgage_balance:
                        principal_paid = mortgage_balance
                        effective_payment = interest + principal_paid
                    else:
                        effective_payment = annual_payment

                    mortgage_balance -= principal_paid
                    rent_or_mortgage_payment = effective_payment
                else:
                    rent_or_mortgage_payment = 0.0

            tax_payment = get_tax_value(locations_df, location, local_salary)
            after_tax_income = local_salary - tax_payment

            if spending_type == "eager":
                yearly_spending = 0.5 * after_tax_income
            else:
                yearly_spending = 0.4 * after_tax_income

            child_cost_total = annual_child_cost * num_children

            cash_this_year = (
                after_tax_income
                - rent_or_mortgage_payment
                - yearly_spending
                - child_cost_total
            )
            total_cash += cash_this_year

        local_networth = total_cash + home_value - mortgage_balance
        networths.append(local_networth)

    mean_networth = float(np.mean(networths))
    stdev_networth = float(np.std(networths))

    return {"mean": mean_networth, "stdev": stdev_networth}


def run_simulation(params, locations_df: pd.DataFrame, home_and_rental_table: pd.DataFrame):
    
    num_samples = 100
    years = 20
    rng = np.random.default_rng(seed=42) # creates a generator
    starting_salary = params["starting_salary"]
    salary_mu = params["salary_growth_mean"]
    salary_sigma = params["salary_growth_sd"]

    home_growth_rate = params["home_growth_rate"]
    salary_to_buy_house = params["salary_to_buy_house"]
    annual_child_cost = params["annual_child_cost"]
    savings_rate = params["savings_rate"]
    num_children = params["num_children"]

    location = params["location"]
    spending_type = params["spending_type"]

    networths = []
    rng = np.random.default_rng(seed=42)
    for _ in range(num_samples):
        local_salary = starting_salary # param
        total_cash = 0

        bought_a_house = False
        home_value = 0
        principal = 0
        
        annual_rate = 0.05
        loan_term_years = 30
        annual_payment = 0

        mortgage_balance = 0
        principal_paid = 0
        effective_payment = 0

        rent_or_mortgage_payment = 0
        
        for year in range(years): 
            # computes and adds salary growth
            salary_growths = rng.normal(salary_mu, salary_sigma, 100) # params
            salary_final_mean = np.mean(salary_growths)
            salary_final_sigma = np.std(salary_growths)
            local_salary *= (1.0 + salary_final_mean) 

            # user does not own a house (false case)
            if (bought_a_house == False):
                # the user cannot afford a house yet. rent simulated for the year
                if (local_salary < salary_to_buy_house): # param
                    rent_or_mortgage_payment = 0.3 * (local_salary) # param
                # the user has the money to make a down payment
                else:
                    # finds the corresponding home_value (also based on spending category) 
                    rounded_salary = round(local_salary / 20000) * 20000
                    home_and_rent_df = home_and_rental_table[home_and_rental_table["Starting Salary"] == rounded_salary] # param
                    if spending_type == "eager":
                        hv_col = "Home Value (3x) (eager spending)"
                    else:
                        hv_col = "Home Value (2.5x) (conservative spending)"

                    home_value = float(home_and_rent_df[hv_col].iloc[0])
                    principal = 0.91 * (home_value) # the money that is loaned
                    rent_or_mortgage_payment = 0.09 * (home_value) # the down payment (the housing cost for the year)
                    annual_payment = get_home_payment(principal) # sets the annual payment (will be used in future iterations)
                    mortgage_balance = principal                # sets the mortgage balance (to be used in future iterations)
                    bought_a_house = True
                
            # user owns a house
            else: 
                # compounds the growth rate of home value
                home_value *= (1.0 + home_growth_rate) # param
                # checks if the user has remaining mortgage
                if (mortgage_balance > 0):
                    interest = mortgage_balance * annual_rate
                    principal_paid = annual_payment - interest # calulate portion of payment that goes towards the mortgage
                    # checks if this would be the last payment (the mortgage would be paid off). 
                    if (principal_paid > mortgage_balance):
                        principal_paid = mortgage_balance
                        effective_payment = interest + principal_paid # if this is the last payment, only what is left of the mortgage will be accounted for in the yearly housing fee
                    else:
                        effective_payment = annual_payment # if it is not the last year, the entire annual_payment is accounted for in the yearly housing fee
                    mortgage_balance -= principal_paid
                    rent_or_mortgage_payment = effective_payment

            tax_payment = get_tax_value(locations_df, location, local_salary) # param?
            after_tax_income = local_salary - tax_payment
            yearly_spending = 0 # param
            if (spending_type == "eager"):
                yearly_spending = 0.5 * (after_tax_income) # follows the 80-20 rule (approximating 30 percent for housing)
            else:
                yearly_spending = 0.4 * (after_tax_income) # follows a 70-30 rule
            child_cost_total = annual_child_cost * num_children
            total_cash += after_tax_income - rent_or_mortgage_payment - yearly_spending - child_cost_total
            
        local_networth = total_cash + home_value - mortgage_balance
        networths.append(local_networth)

    mean_networth = float(np.mean(networths))
    stdev_networth = float(np.std(networths))

    return {"mean": mean_networth, "stdev": stdev_networth}


@simulation_bp.route("/simulation/run", methods=["POST"])
def simulation_run():
    """
    POST /api/v1/simulation/run

    Expects JSON:
    {
      "career_id": <int>,
      "location": <str>,
      "num_children": <int>,
      "spending": "eager" | "conservative"
    }
    """
    data = request.get_json() or {}
    years = int(data.get("years", 20))

    try:
        params, locations_df, home_and_rental_table = get_params(data)
        summary = run_simulation(params, locations_df, home_and_rental_table)

        # for debugging, you can also return params if you want to see what was used
        return jsonify(
            {
                "summary": summary,
                "params": {
                    k: v
                    for k, v in params.items()
                    if k not in ("location", "spending_type")
                },
            }
        )
    except Exception as e:
        # basic error reporting for now
        return jsonify({"error": str(e)}), 400

@simulation_bp.route("/simulation/params", methods=["POST"]) 
def map_inputs():
    data = request.get_json()
    params, _, _ = get_params(data)
    return jsonify(params)

   