_ONES = [
    "", "One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine",
    "Ten", "Eleven", "Twelve", "Thirteen", "Fourteen", "Fifteen", "Sixteen",
    "Seventeen", "Eighteen", "Nineteen",
]
_TENS = ["", "", "Twenty", "Thirty", "Forty", "Fifty", "Sixty", "Seventy", "Eighty", "Ninety"]


def _under_thousand(n: int) -> str:
    if n >= 100:
        rest = n % 100
        head = f"{_ONES[n // 100]} Hundred"
        return head if rest == 0 else f"{head} {_under_thousand(rest)}"
    if n >= 20:
        rest = n % 10
        head = _TENS[n // 10]
        return head if rest == 0 else f"{head} {_ONES[rest]}"
    return _ONES[n]


def rupees_in_words(amount: int) -> str:
    if amount < 0:
        raise ValueError("amount")
    if amount == 0:
        return "Zero Rupees Only"
    crore, rem = divmod(amount, 10_000_000)
    lakh, rem = divmod(rem, 100_000)
    thousand, rem = divmod(rem, 1000)
    parts = []
    if crore:
        parts.append(f"{_under_thousand(crore)} Crore")
    if lakh:
        parts.append(f"{_under_thousand(lakh)} Lakh")
    if thousand:
        parts.append(f"{_under_thousand(thousand)} Thousand")
    if rem:
        parts.append(_under_thousand(rem))
    return " ".join(parts) + " Rupees Only"
