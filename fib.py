from functools import lru_cache
import sys

# Exceeds the limit対策
sys.set_int_max_str_digits(0)

# Decorator for reuse of previous results
@lru_cache(maxsize=10000000)

# n-th Fibonacci number
def fib(seq):
    a, b = 0, 1
    if seq == 0:
        return a
    elif abs(seq) == 1:
        result = b
    else:
	# Algorithm for O(log n).
        if abs(seq) % 2 == 0:
            k = abs(seq) / 2
            result = ((2 * fib(k - 1)) + fib(k)) * fib(k)
        else:
            k = (abs(seq) + 1) / 2
            result = fib(k) * fib(k) + fib(k - 1) * fib(k - 1)

    if seq > 0:
        return result
    else:
	# Processing when n is a negative number.
        return result * (-1) ** (abs(seq) + 1)


print(fib(1000000))
