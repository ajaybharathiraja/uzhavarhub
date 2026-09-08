import numpy as np

# PENDING DATA COLLECTION
# Once you have collected the 10-question responses from your N=15 participants,
# replace these empty arrays with the actual integer responses (1-5).
# Each sub-array represents one participant's 10 answers.
responses = [
    # [5, 1, 5, 1, 5, 1, 5, 1, 5, 1], # Example of a perfect score (100)
    # [1, 5, 1, 5, 1, 5, 1, 5, 1, 5], # Example of the worst score (0)
]

def calculate_sus(responses):
    if not responses:
        return "PENDING: No data collected yet."
        
    scores = []
    for resp in responses:
        if len(resp) != 10:
            raise ValueError("Each response must have exactly 10 answers.")
            
        # Odd items: scale position minus 1
        odd_score = (resp[0]-1) + (resp[2]-1) + (resp[4]-1) + (resp[6]-1) + (resp[8]-1)
        
        # Even items: 5 minus scale position
        even_score = (5-resp[1]) + (5-resp[3]) + (5-resp[5]) + (5-resp[7]) + (5-resp[9])
        
        # Total sum multiplied by 2.5
        sus = (odd_score + even_score) * 2.5
        scores.append(sus)
        
    mean_score = np.mean(scores)
    std_score = np.std(scores)
    
    # Grading (approximate, based on standard SUS curve)
    if mean_score >= 80.3:
        grade = "A"
    elif mean_score >= 68:
        grade = "C (Above Average)"
    elif mean_score >= 51:
        grade = "F (Below Average)"
    else:
        grade = "F (Poor)"
        
    return {
        "N": len(scores),
        "Mean_SUS": round(mean_score, 2),
        "Std_Dev": round(std_score, 2),
        "Grade": grade
    }

if __name__ == "__main__":
    result = calculate_sus(responses)
    print("--- SUS Evaluation Results ---")
    if isinstance(result, str):
        print(result)
    else:
        for k, v in result.items():
            print(f"{k}: {v}")
