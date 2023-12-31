d # Edge Cases

I'll go over some possible edge cases that aren't specifically handled in my code but could be if given enough time. Keep in mind that not all possible edge cases are covered here and in practice, new version of the program will likely need to be released to address the most common edge cases that can crop up.

That being said, here are some edge cases I've thought of and a brief discussion on how to address them:

## Different Languages
It's possible that the tables could be in another language, esp the headers.  In that case, we may need to detect and translate it with GPT4.

## Long Spreadsheets
This is probably the most likely edge case (exceeding GPT4's context length) and although there seems to be an easy solution, it may end up confusing the program if the user uses it in a non-linear way.  Let me explain.

My suggested solution is to randomly sample, say, 100 rows from the spreadsheet regardless of the length.  However, at each stage of the process (like figuring out the mappings, figuring out the transformation logic, etc.) the spreadsheet is reloaded (by design.)  It's possible that you'll end up selecting a different random set of rows each time which might get you different results.

One possible workaround may be to always fetch the first N rows instead of any spreadsheet but in that case, you might not get a good random sample of elements especially if the sheet is sorted.

All of the possible solutions above for random sampling are definitely feasible but essentially, you're trading a larger edge case (large spreadsheets) for a smaller one (potentially inconsistent solutions from inconsistent random sampling or picking a biased sample from a sorted sheet.)

## Malicious Code
Giving a random person the ability to execute arbitrary code on any company computer is a huge security risk and it's prudent to limit the scope of the types of code that can be executed in the transformation logic.

But keep in mind this will probably be run on a company owned computer on their own network by their own employees who have to abide by common sense codes of conduct and violating them by, say, running malicious code will easily result in disciplinary action.

However, a hacker from outside could also gain access to such a computer but may not necessarily have direct code execution priviledges on the machine until they discover this module for putting transformation logic code in.

## Different spreadsheet formats
My MVP/POC here only supports .csv formats but if others formats like .xls, .xlsx, .odt, etc. are common, I can certainly add additional routines to detect these formats and use the appropriate reader for loading it into Pandas.
