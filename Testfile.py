total1 = 0
total2 = 0

for _ in range(5):
    num = int(input())

    if 2 <= num < 5:
        total1 += num

    if abs(num) <= 3:
        total2 += num

print(total1, total2)