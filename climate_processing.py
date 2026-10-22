import argparse

from datetime import datetime

import numpy as np
import pandas as pd

EXPECTED_DAYS = {1: 31, 2: 28, 3: 31, 4: 30, 5: 31, 6: 30, 7: 31, 8: 31, 9: 30, 10: 31, 11: 30, 12: 31}


def add_time_data(dataframe: pd.DataFrame):
    """
    Function to update a dataframe with only unixtimestamps with temporal explicit values.
    :param dataframe:
    :return:
    """
    values_dates = pd.DatetimeIndex(dataframe['time'])
    dataframe['year'] = values_dates.year
    dataframe['month'] = values_dates.month
    dataframe['day'] = values_dates.day
    dataframe['hour'] = values_dates.hour
    dataframe['time_day'] = values_dates.hour + values_dates.day / 60.0


def parse_args():
    """ Parse command line arguments.
    """
    parser = argparse.ArgumentParser(description="Climate Data processing of variables")

    parser.add_argument(
        "--type-data", help="Name of variable to process.",
        default=['temp_environment'],
        choices=['temp_environment', 'temp_leaf', 'temp_soil', 'water_soil', 'moisture_leaf',
                 'humidity_environment', 'conduct_soil'])

    parser.add_argument(
        "--path-file", help="Path to data file (.csv).", required=True)

    parser.add_argument(
        "--path-save", help="Path to save file.", required=True)

    # parser.add_argument(
    #     "--field", help="Path to save file.", required=True, choices=['rengo', 'graneros', 'peumo'])

    parser.add_argument(
        "--date-start", help="Initial Date of the timelapse.", required=True, type=str)

    parser.add_argument(
        "--date-end", help="End date for the timelapse.", required=True, type=str)

    return parser.parse_args()


def get_day_info(day_data: pd.DataFrame, field='valor'):
    data_field = []
    data_hour = day_data[day_data['time_day'] < 1]
    if len(data_hour) > 0:
        data_field += [data_hour[field].mean()]
    else:
        data_field += [-1]

    for i in range(1, 24):
        data_hour = day_data[(day_data['time_day'] >= i) & (day_data['time_day'] < (i + 1))]
        if len(data_hour) > 0:
            data_field += [data_hour[field].mean()]
        else:
            data_field += [data_field[-1]]

    return data_field


def diff_month(d1: datetime, d2: datetime):
    return (d1.year - d2.year) * 12 + d1.month - d2.month


def get_sensors_data(data_variables: pd.DataFrame, months_check: np.ndarray, years_check: np.ndarray):
    """
    Function to generate a dataframe with standarized measurements for every year, month, day and hour of the original
    data frame.

    :param dataframe: dataframe with info data. Each row is a measurement for a sensor.
    :param months_check: number of month to check. (example: np.array([10,11,12,1]))
    :param years_check: number of month to year of each month. (example: np.array([2022,2022,2022,2023]))

    :return:
    """
    name_devices = data_variables['device_id'].unique()

    sensors_data = pd.DataFrame(columns=['Año', 'Mes', 'Dia', 'Hora'] + name_devices.tolist())

    years_data = []
    months_data = []
    days_data = []
    hours_data = []
    # time_data = []

    devices = {name: [] for name in name_devices}
    for i, month in enumerate(months_check):

        year = years_check[i]
        yearly_data = data_variables[(data_variables['year'] == year)].copy()
        monthly_data = yearly_data[(yearly_data['month'] == month)].copy()
        days_in_month = monthly_data['day'].unique()

        for day_name in days_in_month:
            years_data += [year for j in range(24)]
            months_data += [month for j in range(24)]
            days_data += [day_name for j in range(24)]
            hours_data += [j for j in range(24)]

            info_day = monthly_data[monthly_data['day'] == day_name].copy()
            for i, sensor_name in enumerate(name_devices):
                sensor_info = info_day[info_day['device_id'] == sensor_name].copy()

                devices[sensor_name] += get_day_info(sensor_info)
            # for j in range(24):
            #     time_data += [int(time.mktime(datetime(year, month, day_name, j, 1, 1).timetuple()))]

    sensors_data['Año'] = years_data
    sensors_data['Mes'] = months_data
    sensors_data['Dia'] = days_data
    sensors_data['Hora'] = hours_data
    # sensors_data['time'] = time_data
    for sensor_name in name_devices:
        sensors_data[sensor_name] = devices[sensor_name]

    return sensors_data


def get_ranges_check(indices_missing: np.ndarray):
    pos_idx = 0
    ranges_check = []
    range_check = [indices_missing[pos_idx]]

    for i, idx in enumerate(indices_missing[1:]):
        if indices_missing[pos_idx] + 1 != idx:
            range_check += [indices_missing[pos_idx]]
            ranges_check += [range_check]
            range_check = [indices_missing[pos_idx + 1]]

        pos_idx += 1
    # while pos_idx < len(indices_missing) - 1:
    #     # if (pos_idx + 1) == len(indices_missing):
    #     #     range_check += [indices_missing[pos_idx]]
    #     #     ranges_check += [range_check]
    #     #     break
    #
    #     while indices_missing[pos_idx + 1] == indices_missing[pos_idx] + 1 and (pos_idx < len(indices_missing) - 1):
    #         pos_idx += 1
    #
    #     if (pos_idx < len(indices_missing) - 1):
    #         range_check += [indices_missing[pos_idx]]
    #         ranges_check += [range_check]
    #         pos_idx += 1
    #     else:
    #         break
    #
    # # if len(range_check) == 1:
    range_check += [indices_missing[-1]]
    ranges_check += [range_check]

    return ranges_check


def predict_position_last_samples(data: pd.DataFrame, range_check_data: list[int], range_predict_data: list[int],
                                  name_dependent_variable: str, name_x='Hour'):
    """
    Function to predict values in a given range based on past values.

    :param data: dataframe with climate data
    :param range_check_data: Range of data to take information from
    :param range_predict_data: indices of values to replace
    :param name_dependent_variable: Name of sensor
    :param name_x: name variable to look for (default= hour)

    :return:
    """
    x_values = data.loc[range_check_data[0]:range_check_data[1] - 1, name_x].unique()

    average_values = {}

    for x in x_values:
        indices_check = (data.loc[range_check_data[0]:(range_check_data[1] - 1), name_x] == x)
        indices_check = indices_check.index[indices_check]
        average_values[x] = np.mean(data.loc[indices_check, name_dependent_variable])

    predictions = []
    for i in range(range_predict_data[0], range_predict_data[1] + 1):
        predictions += [average_values[data.loc[i, name_x]]]

    return predictions


def fill_values(data: pd.DataFrame, name_device: str, range_evaluate=48, name_identifier='Hora'):
    """
    Function to fill locations with value -1, meaning a non-filled value.

    :param data: data
    :param name_device: Column name in dataframe
    :param range_evaluate: number of samples to consider before.
    :param name_identifier: name of column to check.
    :return:
    """

    if (data.loc[0:23, name_device] == -1).all():
        data.loc[0:23, name_device] = 0
    elif (data.loc[0:23, name_device] == -1).any():
        subdata_neg = (data.loc[0:23, name_device] == -1)
        subdata_pos = (data.loc[0:23, name_device] != -1)
        data.loc[subdata_neg.index[subdata_neg], name_device] = data.loc[
            subdata_pos.index[subdata_pos], name_device].mean()
    indices_missing = data[(data[name_device] == -1)].index

    if len(indices_missing) == 0:
        print("NO MISSING DATA POINTS")
        return

    else:
        ranges_check = get_ranges_check(indices_missing)
        for i, range_predict in enumerate(ranges_check):
            lower_range = max(0, range_predict[0] - range_evaluate)
            idx = range_predict[0]
            data.loc[range_predict[0]:range_predict[1], name_device] = predict_position_last_samples(data, [lower_range,
                                                                                                            idx],
                                                                                                     range_predict,
                                                                                                     name_device,
                                                                                                     name_identifier)


def fix_month(year_check, month_check, days_missing, sensors_names_columns, fill_value=-1):
    n_days = len(days_missing)
    years = [year_check] * (n_days * 24)
    months = [month_check] * (n_days * 24)
    horas = [i for i in range(24)] * n_days
    days = []
    for i, day_missed in enumerate(days_missing):
        days += [day_missed] * 24

    missing_data = pd.DataFrame(days, columns=['Dia'])
    missing_data['Año'] = years
    missing_data['Mes'] = months
    missing_data['Dia'] = days
    missing_data['Hora'] = horas
    for name in sensors_names_columns:
        missing_data[name] = fill_value  # Add emtpy values
    return missing_data


def add_missing_days(sensor_data: pd.DataFrame, sensors_names: list[str], months_to_check: np.ndarray,
                     years_check: np.ndarray):
    """
    Function to add missing days into the data.
    :param sensor_data: Sensors data
    :param sensors_names: Sensor names
    :param months_to_check: number for each month to each
    :param years_check: Corresponding year for each month
    :return:
    """
    starting_day = sensor_data.loc[0, 'Dia']
    # expected_days = EXPECTED_DAYS[months_to_check[0]]
    # days_in_month = np.arange(starting_day, expected_days + 1)
    # subdata = sensor_data[(sensor_data['Mes'] == months_to_check[0]) & (sensor_data['Año'] == years_check[0])]
    # days_present = subdata['Dia'].unique()

    # days_missing = np.setdiff1d(days_in_month, days_present)
    missing_days = []
    # if len(days_missing) > 0:
    #     missing_days_in_month = fix_month(years_check[0],months_to_check[0], days_missing, sensors_names, fill_value=-1)
    #     missing_days += [missing_days_in_month]

    for i, month_check in enumerate(months_to_check[:-1]):
        year_check = years_check[i]
        expected_days = EXPECTED_DAYS[month_check]
        days_in_month = np.arange(starting_day, expected_days + 1)
        subdata = sensor_data[(sensor_data['Mes'] == month_check) & (sensor_data['Año'] == year_check)]
        days_present = subdata['Dia'].unique()

        days_missing = np.setdiff1d(days_in_month, days_present)

        if len(days_missing) > 0:
            missing_days_in_month = fix_month(year_check, month_check, days_missing, sensors_names, fill_value=-1)
            missing_days += [missing_days_in_month]
            # break  # DELETE
        starting_day = 1

    year_check = years_check[-1]
    month_check = months_to_check[-1]
    # expected_days = EXPECTED_DAYS[months_to_check[-1]]
    last_day = sensor_data['Dia'].iloc[-1]
    days_in_month = np.arange(starting_day, last_day + 1)
    subdata = sensor_data[(sensor_data['Mes'] == month_check) & (sensor_data['Año'] == year_check)]
    days_present = subdata['Dia'].unique()

    days_missing = np.setdiff1d(days_in_month, days_present)

    if len(days_missing) > 0:
        missing_days_in_month = fix_month(year_check, month_check, days_missing, sensors_names, fill_value=-1)
        missing_days += [missing_days_in_month]

    final_data = pd.concat([sensor_data] + missing_days, ignore_index=True)
    final_data = final_data.sort_values(by=['Año', 'Mes', 'Dia'], ascending=[True, True, True])
    final_data.index = np.arange(len(final_data))
    return final_data


def fixed_data(sensor_data: pd.DataFrame, sensors_names: list[str], months_to_check: np.ndarray,
               years_check: np.ndarray):
    sensor_data = add_missing_days(sensor_data, sensors_names, months_to_check, years_check)

    for device in sensors_names:
        fill_values(sensor_data, device)
    return sensor_data


def get_units_cold(temp):
    if temp < 1.3:
        return 0
    elif temp < 2.5:
        return 0.5
    elif temp < 9.2:
        return 1
    elif temp < 12.5:
        return 0.5
    elif temp < 16:
        return 0
    elif temp < 18.1:
        return -0.5
    else:
        return -1

def get_yearly_cold_stats(subdata, names):
    portions_cold = {name: np.empty([len(subdata)]) for name in names}
    cold_units = {name: np.empty([len(subdata)]) for name in names}
    cold_hours = {name: np.empty([len(subdata)]) for name in names}
    slp = 1.6
    tetmlt = 277
    a0 = 139500
    a1 = 2.567e18
    aa = a0/a1
    log_a1 = np.log(a1)
    e0 = 4153.5
    e1 = 12888.8
    ee = e1 - e0

    mult_slp_tetmlt = slp * tetmlt


    temp_k = {name: subdata[name].values + 273 for name in names}
    ftmprt = {name: mult_slp_tetmlt * (temp_k[name] - tetmlt) / temp_k[name] for name in names}
    sr = {name: np.exp(ftmprt[name]) for name in names}
    xi = {name: sr[name] / (1 + sr[name]) for name in names}
    xs = {name: aa * np.exp(ee / temp_k[name]) for name in names}
    ak1 = {name: a1 * np.exp(-e1 / temp_k[name]) for name in names}
    Inter_S = {name: 0 for name in names}
    Inter_E = {name: xs[name][0] - (xs[name][0] - Inter_S[name]) * np.exp(-ak1[name][0]) for name in names}
    for name in names:
        portions_cold[name][-1] = 0
        cold_units[name][-1] = 0
        cold_hours[name][-1] = 0
        xi[name][-1] = 1

    for i, item in subdata.iterrows():
        for name in names:
            cold_units[name][i] = get_units_cold(item[name]) + cold_units[name][i - 1]
            cold_hours[name][i] = get_chill_hours(item[name]) + cold_hours[name][i - 1]
            if Inter_E[name] < 1:
                Inter_S[name] = Inter_E[name]
            else:
                Inter_S[name] = Inter_E[name] * (1 - xi[name][i - 1])
            Inter_E[name] = xs[name][i] - (xs[name][i] - Inter_S[name]) * np.exp(-ak1[name][i])
            if Inter_E[name] >= 1:
                portions_cold[name][i] = Inter_E[name] * xi[name][i] + portions_cold[name][i - 1]
            else:
                portions_cold[name][i] = portions_cold[name][i - 1]
    return portions_cold, cold_units, cold_hours

def get_cold_stats(data:pd.DataFrame, names:list[str], years:list[int] , months:list[int]):
    portions_cold = {name: np.empty([len(data)]) for name in names}
    cold_units = {name: np.empty([len(data)]) for name in names}
    cold_hours = {name: np.empty([len(data)]) for name in names}

    for year in years:
        subdata = data[((data['Mes'] >= months[0]) & (data['Mes'] <= months[1]) \
              & (data['Año'] == year))]

        portions_cold_yearly, cold_units_yearly, cold_hours_yearly = get_yearly_cold_stats(subdata,names)
        indices_past = data[(data['Año'] == year) & (data['Mes'] < months[0])].index
        indices_future =data[(data['Año'] == year) & (data['Mes'] > months[1])].index
        for name in names:
            portions_cold[name][indices_past] = 0
            cold_units[name][indices_past] = 0
            cold_hours[name][indices_past] = 0

            portions_cold[name][subdata.index] = portions_cold_yearly[name]
            cold_units[name][subdata.index] = cold_units_yearly[name]
            cold_hours[name][subdata.index] = cold_hours_yearly[name]

            portions_cold[name][indices_future] = portions_cold_yearly[name][-1]
            cold_units[name][indices_future] = cold_units_yearly[name][-1]
            cold_hours[name][indices_future] = cold_hours_yearly[name][-1]
    return portions_cold, cold_units, cold_hours

def get_portions_hot(day_data, field):
    hc = ((day_data[field].max() + day_data[field].min()) / 2) - 4.5
    # print('hc: ',hc)
    return hc


def calculate_chill_data(data: pd.DataFrame, name_devices: list, years_check: list):
    years = np.unique(years_check)
    range_month_chill = [5, 7]  # May-July
    portions_cold, cool_units, cool_hours = get_cold_stats(data, name_devices, years, range_month_chill)


    for name in name_devices:
        data[name + ' HF'] = cool_hours[name]
        data[name + ' PF'] = portions_cold[name]
        data[name + ' UF'] = cool_units[name]


def get_chill_hours(temp):
    if temp < 7.2:
        return 1
    return 0

def calculate_heat_units(data: pd.DataFrame, name_devices: list, years_check: list):
    range_month_heat = [7, 12]  # May-December
    years = np.unique(years_check)
    for year in years:
        count_columns_pc = {name: 0 for name in name_devices}
        for month in range(range_month_heat[0], range_month_heat[1] + 1):
            sub_data = data[(data['Mes'] == month) & (data['Año'] == year)]
            days_in_month = np.arange(1, EXPECTED_DAYS[month] + 1)
            for day in days_in_month:
                day_indices = sub_data[sub_data['Dia'] == day].index
                for name in name_devices:
                    count_columns_pc[name] += get_portions_hot(sub_data.loc[day_indices], name)
                    count_columns_pc[name] = max(0, count_columns_pc[name])
                    data.loc[day_indices, name + ' HC'] = count_columns_pc[name]


def process_temperature(data, name_devices, years_check):
    # for name_col in name_devices:
    #     data[name_col + ' HF'] = 0
    # for name_col in name_devices:
    #     data[name_col + ' PF'] = 0
    for name_col in name_devices:
        data[name_col + ' HC'] = 0.0
    calculate_chill_data(data, name_devices, years_check)
    calculate_heat_units(data, name_devices, years_check)


