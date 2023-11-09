# Automatically validated problems
This file describes the format of test cases and return value for testing solutions to problems with dyalog.run. The example problem provided is intended to demonstrate the available features of the testing framework.

## Test Cases
Test cases, data and a sample solution are provided in a JSON file which describes a single object with the following members:

- id: unique problem identifier
- data: a list of objects
  - save: a string containing the APL expression used to save the file
  - any other members can be used as auxiliary APL values in the save expression
- testcases
  - basic: A list of test cases. If the entrypoint function is monadic, it is a list of strings. If it is dyadic, it is a list of two-element strings which are APL expressions for the left and right arguments respecitvely.
  - edge: Optional edge cases in the same format as basic
- reference: a string of the APL code reference solution
- post: string of an APL function which is applied monadically to post-process results of the reference and user solutions before comparison with the match function

## Return Value
The API returns a string which describes a JSON object with the following members:

- id: the problem ID
- submission: the user's code
- returncode: 
  - -1 if an error occured
  - 0 if at least one basic case failed
  - 1 if all basic cases passed but at least one edge case failed
  - 2 if all basic and edge cases passed
- rightarg: string representation of a failing right argument
- leftarg: string representation of a failing left argument
- result: string representation of the result of the user's code
- expected_result: string representation of the result of the reference solution

## Example problem
People's names and corresponding scores are stored in a CSV file. Weights may be provided, either as a numeric list or stored in a file of raw 8 bit signed integers.

Write an ambivalent function "Ranking" which accepts:

- as right argument a simple character vector giving the name of a CSV file
- as optional left argument, either:
  - a simple numeric vector of integers
  - a simple character vector giving the name of a file of raw 8 bit signed integers

The result is as follows:

- If called monadically, the function returns the list of names in the CSV file in order of descending score.
- If called dyadically, the function returns the list of names in the CSV file in order of descending score multiplied by the weights which are either provided directly or read from the file given as left argument.
