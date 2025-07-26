import re

# Problem 1: Caesar Cipher
def caesar_cipher(message, shift, mode='encode'):
    result = []
    for char in message:
        if char.isalpha():
            base = ord('A') if char.isupper() else ord('a')
            direction = shift if mode == 'encode' else -shift
            shifted = (ord(char) - base + direction) % 26 + base
            result.append(chr(shifted))
        else:
            result.append(char)
    return ''.join(result)

# Problem 2: Indian Currency Format
def format_indian_currency(num):
    num_str = str(num)
    if '.' in num_str:
        int_part, dec_part = num_str.split('.')
    else:
        int_part, dec_part = num_str, ''

    n = len(int_part)
    if n <= 3:
        formatted = int_part
    else:
        formatted = int_part[-3:]
        int_part = int_part[:-3]
        while len(int_part) > 0:
            formatted = int_part[-2:] + ',' + formatted
            int_part = int_part[:-2]

    if dec_part:
        formatted = formatted + '.' + dec_part
    return formatted

# Problem 3: Combining Two Lists
def combine_lists(list1, list2):
    combined = sorted(list1 + list2, key=lambda x: x['positions'][0])
    result = []

    for curr in combined:
        if not result:
            result.append(curr)
        else:
            prev = result[-1]
            l1, r1 = prev['positions']
            l2, r2 = curr['positions']
            overlap = max(0, min(r1, r2) - max(l1, l2))
            len2 = r2 - l2
            if overlap > len2 / 2:
                prev['values'].extend(curr['values'])
            else:
                result.append(curr)
    return result

# Problem 4: Minimizing Loss
def minimizing_loss(prices):
    min_loss = float('inf')
    buy_year, sell_year = -1, -1
    for i in range(len(prices)):
        for j in range(i + 1, len(prices)):
            if prices[j] < prices[i]:
                loss = prices[i] - prices[j]
                if loss < min_loss:
                    min_loss = loss
                    buy_year, sell_year = i + 1, j + 1
    return buy_year, sell_year, min_loss

# ---------- Testing ----------
if __name__ == "__main__":
    # Caesar Cipher
    print("Caesar Encode:", caesar_cipher("HELLO WORLD", 3, 'encode'))
    print("Caesar Decode:", caesar_cipher("KHOOR ZRUOG", 3, 'decode'))

    # Indian Currency Format
    print("Indian Format:", format_indian_currency(123456.7891))  # 1,23,456.7891

    # Combining Lists
    list1 = [{"positions": [0, 5], "values": [1, 2]}]
    list2 = [{"positions": [3, 8], "values": [3, 4]}]
    print("Combined Lists:", combine_lists(list1, list2))

    # Minimizing Loss
    prices = [20, 15, 7, 2, 13]
    b, s, l = minimizing_loss(prices)
    print(f"Buy Year: {b}, Sell Year: {s}, Min Loss: {l}")
