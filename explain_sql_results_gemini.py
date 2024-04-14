import google.generativeai as genai

def explain_result (sql_prompt, sql_result):
  
    user_prompt= f'Summarize the results from sql query in maximum four sentences. The result is an output from the following query {sql_prompt}. Result: {sql_result}'

    models = genai.GenerativeModel('gemini-pro')
    response = models.generate_content(user_prompt)
    explain_result = response.text
    print(explain_result)
    return explain_result
    
    