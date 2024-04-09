# for-loop-to-comprehension
Converts all possible For loops to comprehension versions to speed up code. Still a work in progress. Pure python implementation currently.


# Not Implemented but will be

1. variable mutation ex: ```.append(variable + "world")``` || ```.append(int(variable))```
2. class methods ex:  ``` classy.method(x) for x in classy.attributes ```
3. list comprehensions nested  ``` [[y for y in x if y is None] for x in lista] ```


# Examples 

## Classic ➰
```Python3
# For loop
squares = []
for i in range(1, 11):
    squares.append(i ** 2)
```
Converts to...
```Python3
[i for i in range(1, 11)]
```

## With conditional equate and modulus ❓➗
```Python3 
numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
evens = []
for num in numbers:
    if num % 2 == 0:
        evens.append(num)
```

Converts to...
```Python3
[num for num in numbers if num % 2 == 0]
```

## Tuples from Zip of two lists 🤐
```Python3
names = ['Alice', 'Bob', 'Charlie']
ages = [30, 25, 35]
people = []
for name, age in zip(names, ages):
    people.append((name, age))
```

Converts to...
```Python3
[(name, age) for name, age in zip(names, ages)]
```

## String with character check 🧵
```Python3
text = "hello world"
unique_chars = []
for char in text:
    if char not in unique_chars:
        unique_chars.append(char)
```

Converts to...
```Python3
[char for char in text if char not in unique_chars]
```

## Two lists with Zip, atomic output  ✌ 1️⃣
```Python3
names = ['Alice', 'Bob', 'Charlie']
ages = [30, 25, 35]
people = []
for name, age in zip(names, ages):
    people.append(age)
```

Converts to...
```Python3
[name for name, age in zip(names, ages)]
```

