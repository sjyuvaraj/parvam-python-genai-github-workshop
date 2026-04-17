# If Condition


# Syntax:
# if condition:
#   statements


number = 20


if number % 2 == 0:
    print(f"{number} is an Even Number.")


if number % 2 == 0 and number % 5 == 0:
    print(f"{number} is both multiples of 2 & 5.")


# If - else Condition:


# Syntax:
# if condition:
#   True Statement
# else:
#   False Statement
if number % 2 == 0:
    print(f"{number} is an even number.")
else:
    print(f"{number} is an odd number.")


# If Else (Elif) Ladder:


# Syntax:
# if condition:
#   True Statement
# elif condition:
#   True Statement
# elif condition:
#   True Statement
# else:
#   False Statement


marks = 68
if marks > 85:
    print("Distinction")
elif marks > 75:
    print("First Class")
elif marks > 65:
    print("Second Class")
elif marks > 55:
    print("Above Average")
elif marks > 35:
    print("Below Average")
else:
    print("Fail")


# Nested If-else:


# Syntax:
# if condition1:
#   if condition2:
#       True
#   else:
#       False
# else:
#   False


num1 = 35
num2 = 25
num3 = 30


if num1 > num2:
    if num1 > num3:
        print(f"{num1} is greatest!")
    else:
        print(f"{num3} is greatest!")
else:
    if num2 > num3:
        print(f"{num2} is greatest!")
    else:
        print(f"{num3} is greatest!")
