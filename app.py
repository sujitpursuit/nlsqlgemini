
import run_sql
import explain_sql_results_gemini
import google.generativeai as genai
import pandas as pd

import os

from flask import Flask, request,jsonify
from flask_cors import CORS

class response_object:
    def __init__(self, sql_query, sql_result, result_summary):
        self.sql_query = sql_query
        self.sql_result = sql_result
        self.result_summary = result_summary

app = Flask(__name__)
CORS(app)

MAX_GEN_RETRY=3

def parse_triple_quotes(in_str):
# Parse out the string after ```sql and before ```
  # Using Python's string manipulation methods to extract the SQL query
  start = in_str.find("```sql") + len("```sql\n")  # Start after ```sql and the newline
  end = in_str.rfind("```")  # Find the last occurrence of ```
  out_str = in_str[start:end].strip()  # Extract the SQL query and strip leading/trailing whitespace
  print(f'OUTPUT STRING {out_str}')
  return out_str

def nl_sql_nl_gemini(sql_prompt):
 
 
  ####

    api_key=os.getenv("GEMINI_API_KEY")
    genai.configure(api_key=api_key)  # Configure the API key for all subsequent calls.

    prompt = """
        You are an Microsoft SQL server expert. Given an input question, create a complete, syntactically correct Microsoft SQL query to run on the database.
                If the user asks to list down errors or any other information that could fetch more than 10 rows, then,
                unless the user specifies in the question for a specific number of examples to obtain, query for at most 5 results using the TOP clause as per MS SQL.
                You can order the results to return the most informative data in the database.
                If the user asks to list down source systems, applications or modules, use the DISTINCT statement and return the complete list, do not restrict to 5.
                Never query for all columns from a table. There is no need to query for the GUID column unless asked by the user or needed for a specific use case.
                Wrap each column name in square brackets ([]) to denote them as delimited identifiers.
                Pay attention to use only the column names you can see in the table below. Be careful to not query for columns that do not exist.
                Make sure that the generate SQL has an alias for calculated fields.
                Pay attention to use CAST(GETDATE() as date) function to get the current date, if the question involves "today".
              

                        CREATE TABLE [dbo].[demo_data](
                        [GUID] [nvarchar](50) NULL,
                        [TimeStamp2] [datetime] NULL,
                        [SourceSystem] [nvarchar](100) NULL,
                        [SourceApplication] [nvarchar](max) NULL,
                        [SourceModule] [nvarchar](max) NULL,
                        [Type] [nvarchar](50) NULL,
                        [Tags] [nvarchar](max) NULL,
                        [Description] [nvarchar](max) NULL
                        )
          
    """

    models = genai.GenerativeModel('gemini-pro')
    response = models.generate_content(   prompt + "\n\n Generate SQL for : " + sql_prompt,
                                          generation_config=genai.types.GenerationConfig(temperature=0)
                                      )
    sql_string = response.text
 
    print(f'SQL Generated {sql_string}')
    if ( sql_string.find("```sql") != -1   or   sql_string.find("```SQL") != -1 ) :
        sql_string=parse_triple_quotes(sql_string)

    sql_result=pd.DataFrame()
  

    #Try generating three times if it gives SQL error
    for x in range(MAX_GEN_RETRY):

      try:
        sql_result=run_sql.execute_query_df(sql_string)
        break

      except:
        continue

    explain_result=explain_sql_results_gemini.explain_result(sql_prompt, sql_result)
  
    sql_result_json=sql_result.to_json(orient='records')

    #print ('DF to JSON\n'+sql_result_json)

    return_response = response_object(sql_string, sql_result_json, explain_result)
   
    return return_response

@app.route('/nlsql/', methods=['GET', 'POST'])
def prompt_process():
    sql_prompt = request.args.get('prompt')

    detail_flag = request.args.get('detail')
    if not detail_flag: 
       detail_flag='N'

    

    if (  sql_prompt ):
     
      return_response=nl_sql_nl_gemini (sql_prompt)

      if (detail_flag.upper()=="Y"):
        #Send query, results and summary
        return vars(return_response)
      else:
        #send only summary
        return  f"\"result_summary\": \"{return_response.result_summary}\""
      
    else:
       return("No prompt given. Please provide prompt as argument")
    
  
    
   


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=105)
 

    