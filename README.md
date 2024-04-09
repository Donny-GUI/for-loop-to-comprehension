# for-loop-to-comprehension
Converts all possible For loops to comprehension versions to speed up code. Still a work in progress. Pure python implementation currently.




# Examples 

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



```
