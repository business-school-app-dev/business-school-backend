from flask import Flask, request, jsonify, current_app
from sqlalchemy.orm import Session
from sqlalchemy import select
import numpy as np
import pandas as pd


#from .schema import UserInfo, Asset, Liability

@app.route("/simulation/run", methods=["POST"]) 
def run_simulation():
    '''
    For the Monte-Carlo simulation, plans to run the simulation based on
    input data from the sliders, returning raw data for frontend to then
    plot.
    '''

    # Extracting all the data from the csv.
    data = request.get_json()
    df = pd.read_csv("Washington__D_C__Software_Engineer_Use_Cases__5_rows_.csv")
    row = df[df["current_age"] == current_age].iloc[0].to_dict() # finds the row with the age (in our case from the params)
    risk_profile = data.get("risk") # low, medium, high

    salary = row["starting_salary"]
    salary_mu = row["salary_growth_mu"]
    salary_sigma = row["salary_growth_sigma"] #found a distribution that i can run over (will assume growth is the same)

    lifestyle_spend_pct = row["lifestyle_spend_pct"] 
    tax_rate = row["effective_tax_rate"]

    home_value = row["home_value"]
    home_mu = row["home_growth_mu"]
    home_sigma = row["home_growth_sigma"]  # same thing with home (assume distribution is the same)

    mortgage_balance = row["mortgage_balance"] 
    mortgage_apr = row["mortgage_apr"]

    balance_401k = row["balance_401k"]
    balance_ira = row["balance_ira"]
    balance_taxable = row["balance_taxable"]

    ira_contrib = row["annual_ira_contrib"]
    contrib_401k_pct = row["annual_401_contrib_pct"]

    child_cost = row["annual_children_cost"]
    child_years = row["children_years"]
    
    # For the data that provides a mean and stdev, we're gonna run multiple samples of it to simulate variance and chance.
    # want to run the simulation for salary growth once then hold that value 
    num_samples = 10000
    years = 10
    #rng = np.random.default_rng(seed=42) # creates a generator
    # salary_growths = rng.normal(salary_mu, salary_sigma, (num_samples, years)) # this is where the monte carlo takes place
    # salary_final_mean = np.mean(salary_growths)
    # salary_final_sigma = np.std(salary_growths)

    home_growths = rng.normal(home_mu, home_sigma, (num_samples, years))
    home_final_mean = np.mean(home_growths)
    home_final_sigma = np.std(home_growths)

    investment_risk = { # what do the numbers here represent?
        "low" : [0.04, 0.07],
        "medium" : [0.06, 0.12],
        "high" : [0.08, 0.18],
    }
    
    inv_mu = investment_risk.get(risk_profile)[0]
    inv_sigma = investment_risk.get(risk_profile)[1]
    market_returns = rng.normal(inv_mu, inv_sigma, (num_samples, years))
    networths = []
    rng = np.random.default_rng(seed=42)
    for i in range(num_samples):
        #W = (home_value - mortgage_balance + balance_ira + balance_401k + balance_taxable)
        local_salary = salary
        local_hv = home_value
        mb = mortgage_balance
        local_ira = balance_ira
        local_401k = balance_401k
        local_taxable = balance_taxable
        # runs a simulation on salary growth - has a local array and takes the mean growth
        # compounds that to the salary
        for year in range(years): # repeats once for each year 
            salary_growths = rng.normal(salary_mu, salary_sigma, num_samples) # this is where the monte carlo takes place
            salary_final_mean = np.mean(salary_growths)
            salary_final_sigma = np.std(salary_growths)
            local_salary *= (1 + salary_final_mean) # compounds the salary

            home_growths = rng.normal(home_mu, home_sigma, num_samples)
            home_final_mean = np.mean(home_growths)
            home_final_sigma = np.std(home_growths)
            local_hv *= (1 + home_final_mean) # compounds the home growth

            market_returns = rng.normal(inv_mu, inv_sigma, num_samples)
            returns_final_mean = np.mean(market_returns)
            returns_final_sigma = np.std(market_returns) # need an investment value

            local_ira = local_ira * (1 + returns_final_mean) + ira_contrib
            local_401k = (local_401k * (1 + returns_final_mean)) + (local_salary * contrib_401k_pct)
            local_taxable = local_taxable * (1 + returns_final_mean) + max(0, local_salary * (1 - lifestyle_spend_pct - tax_rate - contrib_401k_pct))
            debt_payment = mb * mortgage_apr
            mb = max(0, mb - debt_payment)
            spending = local_salary * lifestyle_spend_pct + (child_cost if year < child_years else 0)
            # salary_rate = salary_growths[i, year] ------- we could do this with one salary growth array but this way there is more randomization (every growth has its separate simualtion)
            # home_rate = home_growths[i, year]
            # market_rate = market_returns[i, year]

            # s *= (1 + salary_rate)
            # hv *= (1 + home_rate)

            # ira = ira * (1 + market_rate) + ira_contrib
            # k401 = k401 * (1 + market_rate) + s * contrib_401k_pct
            # taxable = taxable * (1 + market_rate) + max(0, s * (1 - lifestyle_spend_pct - tax_rate - contrib_401k_pct))

            # debt_payment = mb * mortgage_apr
            # mb = max(0, mb - debt_payment)
            
            # spending = s * lifestyle_spend_pct + (child_cost if year < child_years else 0)

            # W = hv - mb + ira + k401 + taxable - spending
        W = local_hv - mb + local_ira + local_k401 + local-taxable - spending
        networths.append(W)

    summary = {
        "mean": np.mean(networths),
        "stdev": np.std(networths),
    }

    return jsonify({
        "summary": summary,
    })

    '''
    data = {}
    years = data.get("years", 30)
    runs = data.get("runs", 1000)

    income_start = 80000
    income_growth = 0.04
    yearly_spending = 45000
    n_children = 1

    total_assets = 120000
    total_liabs = 60000
    
    # Monte Carlo simulation
    results = []
    for _ in range(runs):
        income = income_start
        assets_val = total_assets
        liabs_val = total_liabs
        networths = []

        for _ in range(years):
            growth_noise = np.random.normal(loc=income_growth, scale=0.05)
            interest_asset = np.random.normal(0.04, 0.02)
            interest_liab = np.random.normal(0.06, 0.02)

            income *= (1 + growth_noise)
            assets_val *= (1 + interest_asset)
            liabs_val *= (1 + interest_liab)

            child_expense = 3000 * n_children
            yearly_net = income - yearly_spending - child_expense
            networth = assets_val - liabs_val + yearly_net
            networths.append(networth)
        
        results.append(networths[-1])
    
    results = np.array(results)
    summary = {
        "mean": float(np.mean(results)),
        "stdev": float(np.std(results)),
        "p10": float(np.percentile(results, 10)),
        "p90": float(np.percentile(results, 90)),
    }

    return jsonify({
        "summary": summary,
        "distribution": results.tolist()
    })
    # Compute summary statistics
    '''