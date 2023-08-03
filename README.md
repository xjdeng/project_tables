# project_tables

This project aims to take two tables in .csv format, one the template and another the target table.  It attempts to take the columns in the template table and find columns from the target table containing essentially the same information though with different header names or data formatting and creates a new table with that data transformed to fit the column name and data format specifications dictated by the template.  The GPT4 LLM will be used to offer guidance as to which columns will be selected and what transformations will be needed.

The process takes several steps:

1. Input the template and target tables and a preliminary mapping of columns will be generated in JSON format.  The user is free to edit the mappings if they don't agree with them before submitting it for the next step.
2. Now the LLM will generate the code needed to make the necessary data transformations to convert the select columns from the target table to that in the template.  This code will be displayed for the user to modify if need be.
3. The user submits the code and if it executes correctly, then the user will be given the final table to download as a .csv file.

There's a [Jupyter notebook](colab.ipynb) for this as well as a pure [Python script](run.py).

Requirements:

- openai >= 0.27
- gradio > 3
- pandas > 1.0
- faker

(Note: faker is only needed if you want to play with [retraining data](generate_data.py).)
