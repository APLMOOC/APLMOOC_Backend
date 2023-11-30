# Automatically validated problems
This file describes the format of test cases and return value for testing solutions to problems with dyalog.run. The example problem provided is intended to demonstrate the available features of the testing framework.

## TO DO
- [x] Write test framework
- [x] Test framework
  - [x] Empty solution
  - [x] Prohobited chars
- [x] Check TryAPL test framework
- [x] There must be a way for the test options to allow the source of an anonymous function for phase 1 style problems
  - problem author should wrap the user's submission with "Function←" and set "Function" as the entrypoint to the problem.

## Test Cases
Test cases, data and a sample solution are provided in a JSON file which describes a single object with the following members:

- id: string :: Unique problem identifier.
- entrypoint: string :: The name of the function entrypoint for this problem.
- env (optional): a list of objects ::
  - setup: string :: The APL expression to be executed before tests are run, for example to save a file.
  - Any other members can be used as auxiliary APL values in the setup expression. ⎕JSON documentation describes how JSON types convert to APL arrays.
- tests: object ::
  - basic: If the entrypoint function is called monadically, it is a list of strings. If called dyadically, it is a list of two-element lists of strings which are APL expressions for the left and right arguments respecitvely.
  - edge (optional): Edge cases in the same format as basic.
- reference: string :: The APL code for the reference solution.
- post: string :: An APL function which is applied monadically to post-process results of the reference and user solutions before comparison with the match function. This can be used to be lenient. For example, ravel the result so that scalars and 1-element vectors are both correct results.
- x (optional): string :: Prohibited characters.

## Return Value
The API returns a string which describes a JSON object with the following members:

- id: the problem ID
- submission: the user's code
- rarg: string representation of the last used right argument
- larg: string representation of the last used left argument
- result: string representation of the result of the user's code
- expected: string representation of the result of the reference solution
- report: string containing information about any issues while processing
- status: whether tests passed
  -   0      failed basic test
  -   1      passed basic tests but failed one or more edge cases
  -   2      passed all tests
- error: return code for errors
  -   98     prohibited characters used
  -   99     user submission was blank
  -   ¯710   timeout
  -   ¯315   internal error
  -   -n     APL error with error number n

## Example problem
Given a table of names and scores, return the names in order of their scores descending from highest first to lowest last. People's names and corresponding scores are stored in a CSV file. Weights may be provided, either as a numeric list or stored in a file of raw 8 bit signed integers.

Write an ambivalent function "Ranking" which accepts:

- as right argument a simple character vector giving the name of a CSV file which has two columns "name" and "score"
- as optional left argument, either:
  - a simple numeric vector of integers
  - a simple character vector giving the name of a file of raw 8 bit signed integers

Example files `table.csv`, `table2.csv` and `weights` and provided in the `example_files` folder.

The result is as follows:

- If called monadically, the function returns the list of names in the CSV file in order of descending score.
- If called dyadically, the function returns the list of names in the CSV file in order of descending score multiplied by the weights which are either provided directly or read from the file given as left argument.
