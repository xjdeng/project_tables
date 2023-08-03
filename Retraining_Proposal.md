## Retraining Proposal

Note: my [generate_data.py](generate_data.py) script will generate some random data for the problem based on the template and the two files, Table A and Table B.

It's entirely possible that Table A and Table B are not representative of the entire population of all tables with their different formats so the synthetic data
from them will be biased.  For example, they're all around 10 entries long so the new tables will also be around 10 entries long.  However, that can easily be fixed 
by generating several tables, standardizing their formatting, and sitching them together.

It's important to prioritize the most common cases where the program fails to provide the correct transformation logic and save them along with their expected output for transformation logic.  Then modify the prompt for finding the transformation logic by providing these examples and their respective solutions in there, making sure not to exceed the context window.  If the number of examples for different edge cases is overwhelming, it may be necessary to look into training a custom model for this step.
