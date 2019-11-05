

def add(number_list):
    total = 0
    for num in number_list:
        total += int(num)
    return total


def difference(numbers):
    return int(numbers[0]) - int(numbers[1])


def product(numbers):
    return int(numbers[0]) * int(numbers[1])


def abs_val(number):
    x = int(number[0])
    if x < 0:
        return -x
    return x


def power(numbers):
    x = int(numbers[0])
    exponent = int(numbers[1])

    if exponent >= 0:
        total = 1
        for y in range(0, exponent):
            total *= x
        return total

    return "Error: " + str(exponent) + " is not a positive integer."


def main():
    pass


if __name__ == '__main__':
    main()
