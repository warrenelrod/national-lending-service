_credit_mapping = {
    30: {
        "760+": 6.32,
        "720-759": 6.36,
        "680-719": 6.41,
        "640-679": 6.46,
        "600-639": 6.50,
        "Below 600": 6.54,
    },
    15: {
        "760+": 5.50,
        "720-759": 5.55,
        "680-719": 5.60,
        "640-679": 5.65,
        "600-639": 5.70,
        "Below 600": 5.75,
    }
}

# term_years = [10, 15, 20, 25, 30]
term_years = [15, 30]


def annual_rate(loan_term_years, credit_range):
    return _credit_mapping[loan_term_years][credit_range]


def monthly_payment(principal, annual_rate, years):
    monthly_rate = annual_rate / 100 / 12
    months = years * 12

    if monthly_rate == 0:
        return principal / months

    return principal * (monthly_rate * (1 + monthly_rate) ** months) / (
        (1 + monthly_rate) ** months - 1
    )
