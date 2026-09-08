# System Usability Scale (SUS) Study: Recruitment & Administration Script

## Goal
To obtain real, empirical usability data for the UzhavarHub platform to support the Q1 journal submission. Do NOT invent or simulate this data.

## Target Participants
- **N = 15 minimum**
- 50% Farmers (sellers)
- 50% Consumers (buyers)

## 1. Recruitment Message (Email / WhatsApp Template)

> **Subject:** Participate in a brief usability study for a new agricultural app
>
> Hello,
> 
> We are researchers developing **UzhavarHub**, an agricultural platform that connects farmers directly with consumers using AI-driven crop and price forecasting.
> 
> We are conducting a brief usability study and would love your feedback. The session will take approximately 10-15 minutes. You will be asked to complete 2-3 simple tasks on our platform and then fill out a short 10-question survey.
> 
> Your feedback is completely anonymous and will be used solely for academic research. 
> 
> If you're interested in participating, please let us know when you might be available.
> 
> Thank you,
> [YOUR NAME]

## 2. Administration Instructions (During the Session)

1. **Introduction:** Briefly explain the purpose of UzhavarHub without biasing the participant (e.g., "This is an app to buy and sell produce"). Do not explain exactly how the buttons work—the goal is to see if they can figure it out.
2. **Tasks:** Ask the participant to complete simple tasks relevant to their role:
   - *For Farmers:* "Please try to list a new batch of tomatoes for sale and check the recommended crop."
   - *For Consumers:* "Please try to find and purchase 5kg of potatoes."
3. **Survey:** After they complete the tasks (or give up), present them with the 10 SUS questions found in `sus_survey.md`. You can do this on paper or via a Google Form.
   - **Important:** Ensure they answer all 10 questions on a scale of 1 (Strongly Disagree) to 5 (Strongly Agree).
4. **Data Entry:** Enter their responses into the `sus_responses.csv` template in this directory. Remove the placeholder row once real data is entered.

## 3. Running the Analysis

Once you have filled `sus_responses.csv` with the 15 participants' scores:
Run the python script from the terminal:
```bash
python paper/user_study/sus_score.py
```
This will automatically calculate the final SUS score, standard deviation, and grade, which you can then insert into the manuscript.
