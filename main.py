#! /Users/mjmoon/opt/miniconda3/envs/covid-19/bin python3.8
from datetime import datetime
import pandas as pd
import numpy as np
import re
from py import RetrieveCanada
from py import RetrieveGlobal


def main():
    """Update csv files."""
    print('{}: Reading data for Canada.'.format(
        datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
        ))
    can = RetrieveCanada()
    can.auth()
    can.update_data()
    print('{}: Reading Global data.'.format(
        datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
        ))
    rg = RetrieveGlobal()
    rg.update_data()

    # merge and save to json
    wrld_cases = pd.read_csv('data/World-confirmed.csv')
    wrld_mortality = pd.read_csv('data/World-deaths.csv')
    wrld_recovered = pd.read_csv('data/World-recovered.csv')

    wrld_cases = wrld_cases.melt(
        id_vars=['Country/Region', 'Province/State', 'Lat', 'Long'],
        var_name='date', value_name='count_cases'
        )[['Country/Region', 'date', 'count_cases']]
    wrld_cases = wrld_cases[wrld_cases['count_cases'] > 0]
    wrld_mortality = wrld_mortality.melt(
        id_vars=['Country/Region', 'Province/State', 'Lat', 'Long'],
        var_name='date', value_name='count_mortality'
        )[['Country/Region', 'date', 'count_mortality']]
    wrld_mortality = wrld_mortality[wrld_mortality['count_mortality'] > 0]
    wrld_recovered = wrld_recovered.melt(
        id_vars=['Country/Region', 'Province/State', 'Lat', 'Long'],
        var_name='date', value_name='count_recovered'
    )[['Country/Region', 'date', 'count_recovered']]
    wrld_recovered = wrld_recovered[wrld_recovered['count_recovered'] > 0]

    wrld = wrld_cases.merge(
        wrld_mortality, on=['Country/Region', 'date'], how='outer'
        ).merge(
        wrld_recovered, on=['Country/Region', 'date'], how='outer'
        )
    wrld = wrld.rename(columns={'Country/Region': 'country'})
    wrld['date'] = pd.to_datetime(wrld['date'])
    wrld['date_str'] = wrld['date'].dt.strftime('%Y-%m-%d')
    wrld = wrld.sort_values(['country', 'date'])
    wrld['num_days'] = wrld.groupby('country').apply(
        lambda x: (x['date'] - x['date'].min()).dt.days).values

    wrld.to_json('data/world.json', orient='records')

    can_cases = pd.read_csv('data/Canada-Cases.csv')
    can_mortality = pd.read_csv('data/Canada-Mortality.csv')
    can_recovered = pd.read_csv('data/Canada-Recovered.csv')

    join_columns = ['province', 'age', 'date']
    recovered_columns = ['province', 'date', 'cumulative']

    can_cases = can_cases.rename(
        columns={'date_report': 'date'}
        )[join_columns]
    can_cases['date'] = pd.to_datetime(
        can_cases['date'], format='%d-%m-%Y')
    can_cases['count'] = 1
    can_mortality = can_mortality.rename(
        columns={'date_death_report': 'date'}
        )[join_columns]
    can_mortality['date'] = pd.to_datetime(
        can_mortality['date'], format='%d-%m-%Y')
    can_mortality['count'] = 1
    can_recovered = can_recovered.rename(
        columns={'date_recovered': 'date', 'cumulative_recovered': 'cumulative'}
        )[recovered_columns]
    can_recovered['date'] = pd.to_datetime(
        can_recovered['date'], format='%d-%m-%Y')

    can_cases['age'] = can_cases['age'].apply(group_age)
    can_mortality['age'] = can_mortality['age'].apply(group_age)

    can_counts = can_cases.groupby(['province', 'age', 'date']).count().join(
        can_mortality.groupby(['province', 'age', 'date']).count(),
        lsuffix='_cases', rsuffix='_mortality'
        ).reset_index()

    can_recovered = can_recovered.sort_values(['province', 'date'])
    can_recovered = can_recovered.dropna().copy()
    can_recovered['count_recovered'] = can_recovered.groupby('province').apply(
        lambda g: g['cumulative'].diff()).fillna(0).values
    can_recovered = can_recovered[can_recovered['count_recovered'] > 0].copy()
    can_recovered['age'] = 'N/A'
    can_counts = can_counts.merge(
        can_recovered, how='outer',
        on=['province', 'date', 'age']
        )
    can_counts = can_counts.fillna(0)
    can_counts.to_json('data/canada.json', orient='records')


def group_age(age):
    """Group age."""
    if (age == 'Not Reported') | (pd.isna(age)):
        return 'N/A'
    groups = ['<20'] + ['{}0-{}9'.format(x, x) for x in np.arange(2, 12)]
    if age in groups:
        return age
    num = int(re.sub('-', '', re.findall(r'\d+-?', age)[0]))
    if num < 20:
        return groups[0]
    if re.match('^<', age):
        return groups[int(num/10)-2]
    return groups[int(num/10)-1]


if __name__ == '__main__':
    main()
