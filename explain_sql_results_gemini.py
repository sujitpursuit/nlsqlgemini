import google.generativeai as genai

def explain_result (sql_prompt, sql_result):
  
    user_prompt= f'If the {sql_prompt} is a asking for a list then do not Summarize. Otherwise Summarize the results from sql query in maximum 6 sentences. The result is an output from the following query {sql_prompt}. Result: {sql_result}. In the response do not mention database related words like SQL ,  Rows, TimeStamps  etc'

    models = genai.GenerativeModel('gemini-pro')
    response = models.generate_content(user_prompt)
    explain_result = response.text
    print(explain_result)
    return explain_result
    
    