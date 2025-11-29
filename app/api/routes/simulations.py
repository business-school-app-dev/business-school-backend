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
            remaining = lower_bound
    return total_tax

# gets a yearly home payment based on the principal 
def get_home_payment(principal):
    term_years = 30
    annual_rate = 0.05
    yearly_payment_num = annual_rate * ((1 + annual_rate) ** term_years)
    yearly_payment_denom = ((1 + annual_rate) ** term_years) - 1
    yearly_payment = principal * (yearly_payment_num / yearly_payment_denom)

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
    starting_salary = float(salary_row["Starting Salary"].iloc[0])
    salary_mu = float(salary_row["Salary_growth_mean"].iloc[0])
    salary_sigma = float(salary_row["salary_growth_sd"] .iloc[0])

    # extracting relavant location information and adjusts the starting salary based on location
    locations_df = locations_table[locations_table["State"] == location]
    starting_salary *= float(locations_df["inc-nat ratio"].iloc[0])
    home_and_child_df = home_and_child_table[home_and_child_table["State"] == location]
    home_growth_rate = float(home_and_child_df["Average Home Growth Rate"].iloc[0])
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
                "effective_tax_rate_starting" : effective_tax_rate_starting
    
            }
    return params


def run_simulation(params):
    
    num_samples = 10000
    years = 20
    rng = np.random.default_rng(seed=42) # creates a generator

    networths = []
    rng = np.random.default_rng(seed=42)
    for i in range(num_samples):
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
            local_salary *= (1 + salary_final_mean) 

            # user does not own a house (false case)
            if (bought_a_house == False):
                # the user cannot afford a house yet. rent simulated for the year
                if (local_salary < float(home_and_child_df["Salary Needed to Buy a House"].iloc[0])): # param
                    rent_or_mortgage_payment = 0.3 * (local_salary) # param
                # the user has the money to make a down payment
                else:
                    # finds the corresponding home_value (also based on spending category) 
                    rounded_salary = round(local_salary / 20000) * 20000
                    home_and_rent_df = home_and_rental_table[home_and_rental_table["Starting Salary"] == rounded_salary] # param
                    if (spending_type == "eager"):
                        home_value = float(home_and_rent_df["Home Value (3x) (eager spending)"].iloc[0])
                    else:
                        home_value = float(home_and_rent_df["Home Value (2.5x) (conservative spending)"].iloc[0])
                    # assumes a 9 % downpayment (first time home buyer) 
                    principal = 0.91 * (home_value) # the money that is loaned
                    rent_or_mortgage_payment = 0.09 * (home_value) # the down payment (the housing cost for the year)
                    annual_payment = get_home_payment(principal) # sets the annual payment (will be used in future iterations)
                    mortgage_balance = principal                # sets the mortgage balance (to be used in future iterations)
            # user owns a house
            else: 
                # compounds the growth rate of home value
                local_hv *= float(home_and_child_df["Average Home Growth Rate"].iloc[0]) # param
                # checks if the user has remaining mortgage
                if (mortgage_balance > 0):
                    interest = mortgagee_balance * annual_rate
                    principal_paid = annual_payment - interest # calulate portion of payment that goes towards the mortgage
                    # checks if this would be the last payment (the mortgage would be paid off). 
                    if (principal_paid > mortgage_balance):
                        principal_paid = mortgage_balance
                        effective_payment = interest + principal_paid # if this is the last payment, only what is left of the mortgage will be accounted for in the yearly housing fee
                    else:
                        effective_payment = annual_payment # if it is not the last year, the entire annual_payment is accounted for in the yearly housing fee
                    mortgage_balance -= principle_paid
                    rent_or_mortgage_payment = effective_payment

            tax_payment = get_tax_value(locations_df, location, local_salary) # param?
            after_tax_income = local_salary - tax_payment
            yearly_spending = 0 # param
            if (spending_type == "eager"):
                yearly_spending = 0.5 * (after_tax_income) # follows the 80-20 rule (approximating 30 percent for housing)
            else:
                yearly_spending = 0.4 * (after_tax_income) # follows a 70-30 rule
            total_cash += after_tax_income - rent_or_mortgage_payment - yearly_spending
            
        local_networth = total_cash + home_value - mortgage_balance
        networths.append(local_networth)
    summary = {
        "mean": np.mean(networths),
        "stdev": np.std(networths),
    }

    return jsonify({
        "summary": summary,
    })



@simulation_bp.route("/simulation/run", methods=["POST"]) 
def map_inputs():
    data = request.get_json()
    params = get_params(data)
    return jsonify(params)

   