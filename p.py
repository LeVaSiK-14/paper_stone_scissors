d = [
    {"user_id": 1, "life": 100},
    {"user_id": 2, "life": 100},
]
from random import randint
# print(d)

# d.pop([d.index(i) for i in d if i['user_id'] == 1][0])
# d.pop(a[0])

# print(d)

# a = [d.index(i) for i in d if i['user_id'] == 1][0]

d[[d.index(i) for i in d if i['user_id'] == 1][0]]['life'] -= randint(10,20)
# ([i['life'] for i in d if i['user_id'] == 1][0]) -= randint(10, 20)

print(d)