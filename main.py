#! /Users/mjmoon/opt/miniconda3/envs/covid-19/bin python3.8
from datetime import datetime
import pandas as pd
import numpy as np
import re
from py import RetrieveCanada
from py import RetrieveGlobal
from py.helper import get_population_country
from py.helper import get_population_province


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

    world_to_json()
    canada_to_json()


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


def world_to_json():
    """Save world data as json."""
    wrld_cases = pd.read_csv('data/World-confirmed.csv')
    wrld_mortality = pd.read_csv('data/World-deaths.csv')
    wrld_recovered = pd.read_csv('data/World-recovered.csv')
    pops = get_population_country()

    def prep_world(df, pops):
        """Prepare world count data for plotting."""
        country_matching = {
            'Burma': 'Myanmar',
            'Cabo Verde': 'Cape Verde',
            'Congo (Kinshasa)': 'DR Congo',
            'Congo (Brazzaville)': 'Congo',
            "Cote d'Ivoire": 'Ivory Coast',
            'Czechia': 'Czech Republic',
            'Holy See': 'Vatican City',
            'Korea, South': 'South Korea',
            'Taiwan*': 'Taiwan',
            'US': 'United States',
            'Timor-Leste': 'East Timor'
        }
        df = df.rename(columns={'Country/Region': 'country'})
        df['country'] = df['country'].replace(country_matching)
        df = df.groupby('country').sum().reset_index().melt(
            id_vars=['country', 'Lat', 'Long'],
            var_name='date', value_name='cumsum'
            )
        df['date'] = pd.to_datetime(df['date'], format='%m/%d/%y')
        df = df.sort_values(
            ['country', 'date']
        ).reset_index()[['country', 'date', 'cumsum']]

        df['count'] = df.groupby('country').apply(
            lambda g: g['cumsum'].diff()).fillna(0).values
        df = df[df['count'] != 0].reset_index().copy()
        df['date_str'] = df['date'].dt.strftime('%Y-%m-%d')
        df['num_days'] = df.groupby('country').apply(
            lambda x: (x['date'] - x['date'].min()).dt.days).values

        no_match = set([
            x for x in df['country']
            if x not in pops.index
        ])
        if no_match:
            print(', '.join(no_match) + ' not matched.')

        df = df.set_index('country').join(pops).reset_index()
        df['count_per_MM'] = df['count']/df['population']*1000000
        df['cumsum_per_MM'] = df['cumsum']/df['population']*1000000
        return df[[
            'country', 'date', 'num_days',
            'count', 'cumsum',
            'count_per_MM', 'cumsum_per_MM'
        ]]

    wrld_cases = prep_world(wrld_cases, pops)
    wrld_mortality = prep_world(wrld_mortality, pops)
    wrld_recovered = prep_world(wrld_recovered, pops)

    wrld_cases.to_json('data/worldCases.json', orient='records')
    wrld_recovered.to_json('data/worldMortality.json', orient='records')
    wrld_recovered.to_json('data/worldRecovered.json', orient='records')


def canada_to_json():
    """Save Canada data as json."""
    can_cases = pd.read_csv('data/Canada-Cases.csv')
    can_mortality = pd.read_csv('data/Canada-Mortality.csv')
    can_recovered = pd.read_csv('data/Canada-Recovered.csv')
    pops = get_population_province()

    def prep_canada_age(df):
        """Prepare Canada count data by age group for plotting."""
        df.columns = df.columns.str.replace(
            r'date_report|date_death_report', 'date')
        df = df[['province', 'age', 'date']].copy()
        df['date'] = pd.to_datetime(
            df['date'], format='%d-%m-%Y')
        df['count'] = 1
        df['age'] = df['age'].apply(group_age)
        df = df.groupby(
            ['province', 'date', 'age']).count().reset_index()
        df['cumsum'] = df.groupby(['province', 'age']).cumsum()
        df['num_days'] = df.groupby('province').apply(
            lambda x: (x['date'] - x['date'].min()).dt.days).values
        df['date_str'] = df['date'].dt.strftime('%Y-%m-%d')
        return df[[
            'province', 'date', 'date_str', 'num_days',
            'age', 'count', 'cumsum']]

    def prep_canada(df, pops):
        """Prepare Canada count data for plotting."""
        province_matching = {
            'NL': 'Newfoundland and Labrador',
            'BC': 'British Columbia',
            'NWT': 'Northwest Territories',
            'PEI': 'Prince Edward Island'
        }
        df['province'] = df['province'].replace(province_matching)
        df.columns = df.columns.str.replace(
            r'date_report|date_death_report|date_recovered', 'date')
        df['date'] = pd.to_datetime(
            df['date'], format='%d-%m-%Y')
        if 'cumulative_recovered' in df.columns:
            df = df.rename(columns={'cumulative_recovered': 'cumsum'})
            df = df[['province', 'date', 'cumsum']]
            df = df.sort_values(['province', 'date'])
            df['count'] = df.groupby('province').apply(
                lambda g: g['cumsum'].diff()).fillna(0).values
            df = df[df['count'] > 0].copy()
        else:
            df = df[['province', 'date']].copy()
            df['count'] = 1
            df = df.groupby(
                ['province', 'date']).count().reset_index()
            df['cumsum'] = df.groupby('province').cumsum()

        df['num_days'] = df.groupby('province').apply(
            lambda x: (x['date'] - x['date'].min()).dt.days).values
        df['date_str'] = df['date'].dt.strftime('%Y-%m-%d')

        no_match = set([
            x for x in df['province']
            if x not in pops.index
        ])
        if no_match:
            print(', '.join(no_match) + ' not matched.')

        df = df.set_index('province').join(pops).reset_index()
        df['count_per_MM'] = df['count']/df['population']*1000000
        df['cumsum_per_MM'] = df['cumsum']/df['population']*1000000

        return df[[
            'province', 'date', 'date_str', 'num_days',
            'count', 'cumsum', 'count_per_MM', 'cumsum_per_MM']]

    can_cases_age = prep_canada_age(can_cases)
    can_mortality_age = prep_canada_age(can_mortality)
    can_cases = prep_canada(can_cases, pops)
    can_mortality = prep_canada(can_mortality, pops)
    can_recovered = prep_canada(can_recovered, pops)

    can_cases_age.to_json(
        'data/canadaCasesAge.json', orient='records')
    can_mortality_age.to_json(
        'data/canadaMortalityAge.json', orient='records')
    can_cases.to_json(
        'data/canadaCases.json', orient='records')
    can_mortality.to_json(
        'data/canadaMortality.json', orient='records')
    can_recovered.to_json(
        'data/canadaRecovered.json', orient='records')


if __name__ == '__main__':
    main()
