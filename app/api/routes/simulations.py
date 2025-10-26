import flask as Flask
from flask import request, jsonify, current_app
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

    df = pd.read_csv("Washington__D_C__Software_Engineer_Use_Cases__5_rows_.csv")
    row = df[df["current_age"] == current_age].to_numpy()[0] # finds the row with the age (in our case from the params)
    salary_mu = row[7] 
    salary_sigma = row[8]
    num_samples = 10000
    rng = np.random.default_rng(seed=42) # creates a generator
    salary_growths = rng.normal(salary_mu, salary_sigma, num_samples) # this is where the monte carlo takes place
    salary_final_mean = np.mean(salary_growths)
    salary_final_sigma = np.std(salary_growths)

    home_mu = row[22]
    home_sigma = row[23]
    home_growths = rng.normal(home_mu, home_sigma, num_samples)
    home_final_mean = np.mean(home_growths)
    home_final_sigma = np.std(home_growths)


    summary = {
        "mean": salary_final_mean,
        "stdev": salary_final_sigma,
        "home_mean" : home_final_mean,
        "home_sigma" : home_final_sigma,
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