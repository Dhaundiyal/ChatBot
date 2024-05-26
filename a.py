def interpret_script(script, variables):
    lines = script.split('\n')
    for line in lines:
        if "is" in line:
            conditions = line.split(" ")
            if conditions[1] == "A<B":
                if variables[conditions[0]] < variables[conditions[2]]:
                    print("Yes")
                    print(variables['A'])
                else:
                    print("No")
                    print(variables['B'])
            elif conditions[1] == "A>B":
                if conditions[3] == "A>C":
                    if variables['A'] > variables['C']:
                        print("Yes")
                        print(variables['A'])
                    else:
                        print("No")
                        print(variables['C'])
                elif conditions[3] == "B>C":
                    if variables['B'] > variables['C']:
                        print("Yes")
                        print(variables['B'])
                    else:
                        print("No")
                        print(variables['C'])

# Example usage:
script = """
is A>B

Yes

is A>C

Yes

print A

No

print C

si
"""

variables_line = "A B C"
variable_values = "5 3 7"
variables = dict(zip(variables_line.split(), map(int, variable_values.split())))

interpret_script(script, variables)
