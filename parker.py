import time
import itertools

total = 10
spinner_chars = ['|', '/', '-', '\\']
spinner = itertools.cycle(spinner_chars)

for x in range(1, total+1):
    if x != total:
        spinner_char = next(spinner)
    else:
        spinner_char = ''
    print(f"\rPage {x} of {total} {spinner_char}", end='')

    time.sleep(2)
print('\nDone!')