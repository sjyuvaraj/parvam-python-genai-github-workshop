# DataTypes in Python

#primitive data types: string, integer, float, boolean
name = "sjyuvaraj"
age = 22
height = 5.10
isTrainer = True

# string
print(name, type(name))
# integer
print(age, type(age))
#float
print(height, type(height))
#boolean
print(isTrainer, type(isTrainer))

# ctrl + shift + ~ -opens terminal in vs code
# python filename.py - runs the file in terminal

# non primitive data types: list, tuple, set, dictionary=

#list represented using square brackets []
#list is ordered, mutable, we can change the values in list, allows duplicates
languages_known = ["Python","Java","C++","C"]

print("Languages Known:", type(languages_known))

#tuple represented using parentheses ()
#tuple is ordered, immutable, we cannot change the values in tuple, allows duplicates
even_numbers = (2,4,6,8)

print("Even Numbers:", type(even_numbers))

#set represented using curly braces {}
#set is unordered, mutable, we can change the values in set, does not allow duplicates
odd_numbers = {1,2,3,4,5}

print("Odd Numbers:", type(odd_numbers))

#dictionary represented using curly braces {}
#dictionary is ordered, mutable, we can change the values in dictionary, does not allow duplicates
profile = {
    "name": "Sjyuvaraj",
    "age": 22, 
    "role": "Trainer", 
    "technologies": ["Python","Java","C++","C"]
}

print("Profile:", type(profile))    