# System Usability Scale (SUS) - User Study Instructions

To achieve Q1 Journal readiness, you must collect real empirical data on the platform's usability. This folder contains the tools to evaluate UzhavarHub using the industry-standard System Usability Scale (SUS).

## 1. Study Protocol
1. Recruit N=15 participants (ideally individuals with some agricultural or e-commerce background, or laypeople serving as proxies for farmers/consumers).
2. Ask each participant to complete a set of core tasks on the UzhavarHub platform:
   - Register an account as a Farmer.
   - Enter mock soil parameters into the AI Crop Recommendation tool.
   - View the generated Integrated Market Strategy.
   - List the recommended crop for sale.
3. After completing the tasks, have them fill out the 10-item SUS questionnaire.

## 2. The Questionnaire
Participants should rate the following 10 statements on a scale from 1 (Strongly Disagree) to 5 (Strongly Agree):

1. I think that I would like to use this system frequently.
2. I found the system unnecessarily complex.
3. I thought the system was easy to use.
4. I think that I would need the support of a technical person to be able to use this system.
5. I found the various functions in this system were well integrated.
6. I thought there was too much inconsistency in this system.
7. I would imagine that most people would learn to use this system very quickly.
8. I found the system very cumbersome to use.
9. I felt very confident using the system.
10. I needed to learn a lot of things before I could get going with this system.

## 3. Data Entry
Once you have collected the survey responses:
1. Open `paper/user_study/sus_score.py`.
2. Locate the `responses = []` array on line 7.
3. Add a new list for each participant containing their 10 integer ratings.
   - Example for Participant 1: `[4, 2, 5, 1, 4, 2, 5, 1, 4, 1],`
4. Run the script: `python paper/user_study/sus_score.py`.
5. The script will output your final mean SUS score and letter grade. Insert these actual results into the "Results" section of `paper/manuscript.md`.
