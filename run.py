
import ast, json
import time
import pandas as pd
import openai
import gradio as gr
import os
import getpass

if not os.environ.get("OPENAI_API_KEY"):
    print("OpenAI API Key not found! Please enter your key:")
    os.environ['OPENAI_API_KEY'] = getpass.getpass("Enter your OpenAI key here:")

def smartload_json(j):
  try:
    return json.loads(j)
  except ValueError:
    return ast.literal_eval(j)

def askgpt(message, model = "gpt-4"):
  chat_completion = openai.ChatCompletion.create(model=model, temperature = 0, messages=[{"role": "user", "content": message}])
  return chat_completion.choices[0].message.content

def getmapping(table, template, *args, **kwargs):
  msg = f"""

  In the financial sector, one of the routine tasks is mapping data from various sources in Excel tables. For example, a company may have a target format for employee health insurance tables (Template) and may receive tables from other departments with essentially the same information, but with different column names, different value formats, and duplicate or irrelevant columns.

  There will be 2 tables as input.  One is called the Template.  The other is called the Table.

  First column: The date of the start of the policy, in the mm-dd-yyyy format
  Second column: The name of the employee in the Firstname Lastname format
  Third column: The insurance plan.  Possible values: Gold, Silver, Bronze
  Fourth column: The policy number starting with 2 characters followed by numbers
  Fifth column: The premium the employee pays for the policy

  For each column in the Template, give the corresponding column in the Table that it should map to.  Return the result as a JSON where each key is a column name in the Template and the value is the column name in the Table.  Note that the dates in the Table may be in a different format; ignore that for now if it's the case.  If you can't solve it or if there's any problem that is preventing you from giving the answer I'm looking for, then return a JSON with a single key, "Error", with a corresponding value that's an explanation for why you can't solve it.  Do not offer any explanation outside of the JSON.  You must return a JSON no matter what.  You must return a JSON no matter what: the response must begin with a {{ and end with a }}
  Also include an additional "Explanation" key which explains why the particular mapping was chosen.
  
  Template:

  ---

  {template.to_string()}

  ---

  Table:

  ---

  {table.to_string()}

  ---
  """
  return askgpt(msg, *args, **kwargs)

def get_conversion_code(mapping_json, table, template, model = "gpt-4"):
  msg = f"""

Assume the tables below are given as Pandas dataframes with variable names 'template' and 'table' along with the mapping_json mapping the columns in the template table to ones in the 'table' table, write Python code that'll convert the data from the format in 'table' to the format in the mapped column in 'template'.

Make sure each column in 'template' is a key in the json 'mapping_json' and the column in 'table' is its corresponding value according to the json

For dates, if you can't determine if a date format is in dd-mm-yyyy or mm-dd-yyyy (whether the date or month comes first), then assume mm-dd-yyyy by default

Please keep the code as simple as possible and do not include return statements in it as it'll cause the code to crash!

Return a JSON with 2 keys: 'Code' containing only the uncommented code and 'Comments' containing the comments.  Do not put any comments in the Code!!!!!!!!!!!!! Don't make the code unnecessarily long, if no transformation is needed, please make the value for the key 'Code' the empty string!!!!!!!!!!!!!!!!!!!!

The response must be a proper JSON that begins with {{ and ends with }}!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

mapping_json:

---

{str(mapping_json)}

---

template:

---

{template.to_string()}

---

table:

---

{table.to_string()}

---

  """
  return askgpt(msg, model)  


def mapping_interface(table, template):
  # Read the CSV files using pandas
  try:
    template_df = pd.read_csv(template.name)
    table_df = pd.read_csv(table.name)
  except Exception:
    return "Error reading input .CSV files.  Make sure they are proper .CSVs.", "Error" 

  # Call the external function
  keeplooping = 5
  while keeplooping:
    result = getmapping(table_df, template_df)
    try:
        result1 = smartload_json(result)
        keeplooping = 0
    except ValueError:
        keeplooping -= 1
  errormsg = result1.get('Error')
  if errormsg:
    return result1, "Error"
  message = result1.get("Explanation")
  if message:
    del result1['Explanation']
  else:
    message = ""
  return message, result1 

def code_generation_interface(mapping_input, table, template):
  try:
    mapping_json = smartload_json(mapping_input)
  except Exception:
    return "Error reading JSON from Mappings textbox", "Error"
  try:
    template_df = pd.read_csv(template.name)
    table_df = pd.read_csv(table.name)
  except Exception:
    return "Error reading input .CSV files.  Make sure they are proper .CSVs.", "Error"
  keeplooping = 5
  while keeplooping:
    result1 = get_conversion_code(mapping_json, table_df, template_df)
    try:
        result_json = smartload_json(result1)
        code = result_json['Code']
        comments = result_json['Comments']
        keeplooping = 0
    except (ValueError, SyntaxError):
        keeplooping -= 1
  return comments, code

def exec_code(code, mapping_input, table, template):
  with open("error.txt",'w') as f:
    f.write("Error: check your inputs and run again.")
  try:
    mapping_json = smartload_json(mapping_input)
  except Exception:
    return "Error reading JSON from Mappings textbox", "error.txt"
  try:
    tablename = table.name
    template = pd.read_csv(template.name)
    table = pd.read_csv(tablename) 
    
  except Exception:
    return "Error reading input .CSV files", "error.txt"
  try:
    exec(code)
  except Exception as e:
    table.to_csv("debug.csv")
    return "Your code failed with the following error:\n{}".format(e), "error.txt"
  df = pd.DataFrame()
  for key in mapping_json:
    val = mapping_json[key]
    df[key] = table[val]
  outname = "{}.csv".format(time.time())
  df.to_csv(outname, index = None)
  return "Your file is ready!", outname

def create_interface():
    

    with gr.Blocks() as interface:
        gr.Markdown("#Interface")
        gr.Markdown("### Upload your template .csv here")
        template_input = gr.components.File(label="Upload template CSV (.csv)")
        gr.Markdown("### Upload your 2nd table (to convert to your template format) here")
        table_input = gr.components.File(label="Upload table CSV (.csv)")
        btn_process = gr.Button("Process CSVs")
        gr.Markdown("### Message (regarding the CSVs)")
        message_textbox = gr.components.Textbox(label="Message (regarding the CSVs)")
        gr.Markdown("### Mappings aka mapping_json")
        gr.Markdown("Your mappings will appear in a JSON below where the key is a column in the template and the value is the corresponding column in the 2nd table.")
        mapping_textbox = gr.components.Textbox(label="Mappings aka mapping_json")
        btn_process.click(fn=mapping_interface, inputs=[table_input, template_input], outputs=[message_textbox, mapping_textbox])
        btn_generate = gr.Button("Generate Date Transform Code")
        gr.Markdown("### Message (regarding code generation)")
        message_textbox2 = gr.components.Textbox(label="Message (regarding code generation)")
        gr.Markdown("### Date transformation code")
        gr.Markdown("You may need to edit the date transformation code below. The variable 'table' refers to the 2nd table and 'mapping_json' refers to the mapping json in the previous box.")
        code_textbox = gr.components.Textbox(label = 'Data transformation code')
        btn_generate.click(fn=code_generation_interface, inputs=[mapping_textbox, table_input, template_input], outputs = [message_textbox2, code_textbox])
        btn_execute = gr.Button("Execute Data Transform")
        gr.Markdown("### Message (regarding code execution)")
        message_textbox3 = gr.components.Textbox(label="Message (regarding code execution)")
        gr.Markdown("### Your final table will appear in a download link below if everything goes right!")
        file_download = gr.File()
        btn_execute.click(fn=exec_code, inputs = [code_textbox, mapping_textbox, table_input, template_input], outputs = [message_textbox3, file_download])
        return interface

def run():
    interface = create_interface()
    interface.close()
    interface.launch(server_name="0.0.0.0", debug=True)
    

if __name__ == "__main__":
    run()