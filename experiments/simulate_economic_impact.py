import os
import json
import pandas as pd
import numpy as np

def simulate_economic_impact():
    print("--- Simulating Economic Impact (ROI) of UzhavarHub ---")
    
    # Assumptions based on typical smallholder farming in the region
    num_farmers = 500
    avg_hectares_per_farmer = 1.5
    avg_yield_per_hectare_kg = 8000
    
    # Traditional Heuristic Farming
    # - Farmers often guess market demand, leading to gluts and low selling prices
    # - Sales go through middlemen who take ~30% cut
    traditional_avg_price_per_kg = 15.0 # Local currency
    traditional_middleman_cut = 0.30
    traditional_spoilage_rate = 0.15 # Due to delayed supply chain
    
    # UzhavarHub Assisted Farming
    # - Farmers grow recommended crops and sell directly at dynamically optimized prices
    # - Direct-to-consumer eliminates middleman cut
    # - Demand forecasting reduces spoilage
    uzhavarhub_avg_price_per_kg = 18.0 # Better pricing via direct-to-consumer & dynamic pricing
    uzhavarhub_platform_fee = 0.05 # Platform takes 5% fee
    uzhavarhub_spoilage_rate = 0.05 # Reduced due to demand forecasting
    
    traditional_profits = []
    uzhavarhub_profits = []
    
    np.random.seed(42)
    
    for _ in range(num_farmers):
        # Simulate variance in farmer yield
        farmer_yield = avg_yield_per_hectare_kg * avg_hectares_per_farmer * np.random.normal(1.0, 0.1)
        
        # Traditional Calculation
        usable_yield_trad = farmer_yield * (1 - traditional_spoilage_rate)
        gross_revenue_trad = usable_yield_trad * traditional_avg_price_per_kg
        net_revenue_trad = gross_revenue_trad * (1 - traditional_middleman_cut)
        traditional_profits.append(net_revenue_trad)
        
        # UzhavarHub Calculation
        usable_yield_uzh = farmer_yield * (1 - uzhavarhub_spoilage_rate)
        gross_revenue_uzh = usable_yield_uzh * uzhavarhub_avg_price_per_kg
        net_revenue_uzh = gross_revenue_uzh * (1 - uzhavarhub_platform_fee)
        uzhavarhub_profits.append(net_revenue_uzh)
        
    mean_profit_trad = np.mean(traditional_profits)
    mean_profit_uzh = np.mean(uzhavarhub_profits)
    
    profit_increase_percentage = ((mean_profit_uzh - mean_profit_trad) / mean_profit_trad) * 100
    
    results = {
        "Farmers_Simulated": num_farmers,
        "Base_Scenario": {
            "Mean_Profit_Traditional": float(mean_profit_trad),
            "Mean_Profit_UzhavarHub": float(mean_profit_uzh),
            "Profit_Increase_Percentage": float(profit_increase_percentage)
        },
        "Key_Drivers": [
            "Elimination of 30% middleman cut (replaced by 5% platform fee)",
            "Spoilage reduction from 15% to 5% via demand forecasting",
            "20% unit price increase via direct-to-consumer dynamic pricing"
        ],
        "Sensitivity_Analysis": {}
    }
    
    # Sensitivity Analysis helper
    def run_scenario(middleman_cut, uzh_spoilage, uzh_price):
        trad_profits = []
        uzh_profits = []
        np.random.seed(42)
        for _ in range(num_farmers):
            farmer_yield = avg_yield_per_hectare_kg * avg_hectares_per_farmer * np.random.normal(1.0, 0.1)
            
            usable_trad = farmer_yield * (1 - traditional_spoilage_rate)
            rev_trad = usable_trad * traditional_avg_price_per_kg * (1 - middleman_cut)
            trad_profits.append(rev_trad)
            
            usable_uzh = farmer_yield * (1 - uzh_spoilage)
            rev_uzh = usable_uzh * uzh_price * (1 - uzhavarhub_platform_fee)
            uzh_profits.append(rev_uzh)
            
        return ((np.mean(uzh_profits) - np.mean(trad_profits)) / np.mean(trad_profits)) * 100

    # 1. Middleman Cut (+/- 50% of 30% = 15% or 45%)
    results["Sensitivity_Analysis"]["Middleman_Cut"] = {
        "-50% (15% cut)": run_scenario(0.15, uzhavarhub_spoilage_rate, uzhavarhub_avg_price_per_kg),
        "+50% (45% cut)": run_scenario(0.45, uzhavarhub_spoilage_rate, uzhavarhub_avg_price_per_kg)
    }
    
    # 2. Spoilage Reduction (Base diff is 10%. Worst = 5% diff, Best = 15% diff)
    # Trad spoilage is 15%. So Uzh spoilage becomes 10% (worst) or 0% (best)
    results["Sensitivity_Analysis"]["Spoilage_Reduction"] = {
        "-50% Effect (10% Uzh Spoilage)": run_scenario(traditional_middleman_cut, 0.10, uzhavarhub_avg_price_per_kg),
        "+50% Effect (0% Uzh Spoilage)": run_scenario(traditional_middleman_cut, 0.00, uzhavarhub_avg_price_per_kg)
    }
    
    # 3. Price Uplift (+/- 50% of 20% uplift = 10% or 30% uplift -> 16.5 or 19.5 price)
    results["Sensitivity_Analysis"]["Price_Uplift"] = {
        "-50% (10% uplift)": run_scenario(traditional_middleman_cut, uzhavarhub_spoilage_rate, 16.5),
        "+50% (30% uplift)": run_scenario(traditional_middleman_cut, uzhavarhub_spoilage_rate, 19.5)
    }
    
    # Combined Worst/Best Case
    results["Sensitivity_Analysis"]["Combined_Extremes"] = {
        "Pessimistic (-50% all)": run_scenario(0.15, 0.10, 16.5),
        "Optimistic (+50% all)": run_scenario(0.45, 0.00, 19.5)
    }
    
    os.makedirs('paper/results', exist_ok=True)
    with open('paper/results/economic_impact.json', 'w') as f:
        json.dump(results, f, indent=4)
        
    print(f"Simulation complete. Mean Profit Increase: {profit_increase_percentage:.2f}%")
    print("Results saved to paper/results/economic_impact.json")

if __name__ == '__main__':
    simulate_economic_impact()
