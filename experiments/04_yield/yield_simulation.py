import os
import json
import numpy as np

def generate_yield_simulation_report():
    print("--- Yield Prediction Simulation ---")
    print("NOTE: Real-world yield data is unavailable. This script documents the simulation protocol.")
    
    # We document the parameters of the simulation explicitly.
    simulation_params = {
        "Status": "SIMULATION ONLY",
        "Reason": "Lack of accessible farm-level historical yield datasets",
        "Variables_Simulated": ["soil_quality", "rainfall_mm", "fertilizer_kg", "temperature", "humidity"],
        "Methodology": "Yield = f(soil, rain, fertilizer, temp, humidity) * area_acres + N(0, 0.5)"
    }
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    out_dir = os.path.join(script_dir, '../../paper/results/yield_simulation')
    os.makedirs(out_dir, exist_ok=True)
    
    with open(os.path.join(out_dir, 'yield_simulation_protocol.json'), 'w') as f:
        json.dump(simulation_params, f, indent=4)
        
    print("Yield simulation protocol saved.")

if __name__ == '__main__':
    generate_yield_simulation_report()
