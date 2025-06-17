import numpy as np
import numpy_financial as npf

INTEREST_DEDUCTIBLE = 1 - 0.64

YEARLY_INSURANCE = 0.0013
YEARLY_VVE = 0.005
YEARLY_WOZ = 0.000577 # For Amsterdam 2025, Rotterdam is a bit higher

def annuity_mortgage(
    principal: float,
    interest_rate: float,
    years: int,
) -> np.ndarray:
    """
    Calculate the monthly payment for an annuity mortgage using numpy-financial.
    Returns a list of the monthly payments for each month of the mortgage.
    """
    monthly_rate = interest_rate / 12
    months = years * 12
    payment = npf.pmt(rate=monthly_rate, nper=months, pv=-principal)

    bruto_payments = [payment] * months
    interest_payments = npf.ipmt(rate=monthly_rate, nper=months, per=list(range(1, months + 1)), pv=-principal)

    interest_deductible = INTEREST_DEDUCTIBLE * interest_payments
    net_payments = bruto_payments - interest_deductible

    return net_payments


def annuity_mortgage_remaining_principal(
    principal: float,
    interest_rate: float,
    years: int,
) -> np.ndarray:
    monthly_rate = interest_rate / 12
    months = years * 12
    payment = npf.ppmt(rate=monthly_rate, nper=months, per=list(range(1, months + 1)), pv=-principal)
    cumsum = np.cumsum(payment)
    return principal - cumsum


def linear_mortgage(
    principal: float,
    interest_rate: float,
    years: int,
) -> np.ndarray:
    """
    Calculate the monthly payment for a linear mortgage.
    Returns a list of the monthly payments for each month of the mortgage.
    """
    monthly_rate = interest_rate / 12
    months = years * 12
    linear_payment = principal / months

    remaining_principal = linear_mortgage_remaining_principal(principal, years)
    interest_payments = np.array([remaining_principal[i] * monthly_rate for i in range(months)])
    interest_deductible = INTEREST_DEDUCTIBLE * interest_payments

    net_payments = linear_payment + interest_payments - interest_deductible

    return net_payments

def linear_mortgage_remaining_principal(
    principal: float,
    years: int,
) -> np.ndarray:
    """
    Calculate the remaining principal for a linear mortgage.
    Returns a list of the remaining principal for each month of the mortgage.
    """
    months = years * 12
    linear_payment = principal / months
    return np.array([principal - (linear_payment * i) for i in range(months)])


def overhead_costs(
    initial_asset_value: float,
    yearly_asset_appreciation: float,
    years: int,
) -> np.ndarray:
    """
    Calculate the yearly overhead costs of the house.
    Returns a list of the yearly overhead costs for each month.
    """
    house_value_per_month = asset_appreciation(initial_asset_value, yearly_asset_appreciation, years)

    monthly_insurance = house_value_per_month * (YEARLY_INSURANCE / 12)
    monthly_vve = house_value_per_month * (YEARLY_VVE / 12)
    monthly_woz = house_value_per_month * (YEARLY_WOZ / 12)

    # TODO: add one-time costs to first month
    return monthly_insurance + monthly_vve + monthly_woz


def asset_appreciation(
    initial_asset_value: float,
    yearly_asset_appreciation: float,
    years: int,
) -> np.ndarray:
    months = years * 12
    return monthly_asset_appreciation(initial_asset_value, months, yearly_asset_appreciation)

def monthly_asset_appreciation(
    initial_asset_value: float,
    months: int,
    yearly_asset_appreciation: float,
) -> np.ndarray:
    monthly_asset_appreciation = yearly_asset_appreciation / 12
    return np.array([initial_asset_value * (1 + monthly_asset_appreciation) ** i for i in range(months)])


class Mortgage:
    def __init__(self, principal: float, interest_rate: float, years: int):
        self.principal = principal
        self.interest_rate = interest_rate
        self.years = years

class LinearMortgage(Mortgage):
    def monthly_payment(self) -> np.ndarray:
        return linear_mortgage(self.principal, self.interest_rate, self.years)

    def remaining_principal(self) -> np.ndarray:
        return linear_mortgage_remaining_principal(self.principal, self.years)

class AnnuityMortgage(Mortgage):
    def monthly_payment(self) -> np.ndarray:
        return annuity_mortgage(self.principal, self.interest_rate, self.years)

    def remaining_principal(self) -> np.ndarray:
        return annuity_mortgage_remaining_principal(self.principal, self.interest_rate, self.years)
