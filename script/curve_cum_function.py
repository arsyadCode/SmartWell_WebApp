import numpy as np
import pandas as pd

# Function for exponential decline curve
def exponential_rate(qi, di, t):
    return qi * np.exp(-di * t)

# Function for harmonic decline curve
def harmonic_rate(qi, di, t):
    return qi / (1 +di * t)

# Function for hyperbolic decline curve
def hyperbolic_rate(qi, di, b, t):
    return qi / ((1 + b * di *  t)** (1/b))

def hyperbolic_decline_rate(qi, qfinal, b, series_time):
    return (((qi / qfinal)**b)-1) / (b * series_time.iloc[-1])

# Function for Cumulative Production
def cum_exponential(initial_rate, di_exponential, rate_now):
    return (initial_rate - rate_now) / di_exponential

def cum_hyperbolic(initial_rate, di_hyperbolic, rate_now, b):
    return (initial_rate/(di_hyperbolic*(1-b)))*(1-(rate_now/initial_rate)**(1-b))

def cum_harmonic(initial_rate, di_harmonic, rate_now):
    return (initial_rate/di_harmonic) * np.log(initial_rate/rate_now)

def oil_r_squared_error(df_range, rate_series):
    SST = np.sum((df_range['CORR_OIL_RATE_STBD'] - np.mean(df_range['CORR_OIL_RATE_STBD']))**2)
    SSE = np.sum(((df_range['CORR_OIL_RATE_STBD'] - rate_series)**2))
    return 1 - SSE / SST

def gas_r_squared_error(df_range, rate_series):
    SST = np.sum((df_range['CORR_GAS_RES_RATE_MMSCFD'] - np.mean(df_range['CORR_GAS_RES_RATE_MMSCFD']))**2)
    SSE = np.sum(((df_range['CORR_GAS_RES_RATE_MMSCFD'] - rate_series)**2))
    return 1 - SSE / SST

def process_data(excel_file, well_name, initial_date, final_date, rate_column, rate_type):
    df = pd.read_excel(excel_file, sheet_name=well_name)
    df['DATE_STAMP'] = pd.to_datetime(df['DATE_STAMP'], format='%d/%m/%Y', dayfirst=True)
    df['TIME'] = range(len(df))

    df_filtered = df[(df['DATE_STAMP'] >= initial_date) & (df['DATE_STAMP'] <= final_date) & (df[rate_column] != 0)].copy()

    initial_rate = df_filtered[rate_column].iloc[0]
    final_rate = df_filtered[rate_column].iloc[-1]

    decline_exponent = [i/10 for i in range(1, 11)]
    error_values = {}

    for b in decline_exponent:
        decline_rate = hyperbolic_decline_rate(initial_rate, final_rate, b, df_filtered['TIME'])
        model = hyperbolic_rate(initial_rate, decline_rate, b, df_filtered['TIME'])
        error_values[b] = oil_r_squared_error(df_filtered, model) if rate_type == 'oil' else gas_r_squared_error(df_filtered, model)

    best_b = min(error_values, key=lambda x: abs(error_values[x] - 1))

    exp_di = np.sum(df_filtered['TIME'] * (np.log(initial_rate/df_filtered[rate_column])))/(np.sum(df_filtered['TIME']**2))
    har_di = (np.sum(df.TIME * initial_rate / df_filtered[rate_column]) - np.sum(df_filtered['TIME'])) / np.sum(df_filtered['TIME']**2)
    hyper_di = hyperbolic_decline_rate(initial_rate, final_rate, best_b, df_filtered['TIME'])

    exp_model = exponential_rate(initial_rate, exp_di, df_filtered['TIME'])
    har_model = harmonic_rate(initial_rate, har_di, df_filtered['TIME'])
    hyper_model = hyperbolic_rate(initial_rate, hyper_di, best_b, df_filtered['TIME'])

    return best_b, exp_di, har_di, hyper_di, exp_model, har_model, hyper_model, df_filtered