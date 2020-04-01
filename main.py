#! /Users/mjmoon/opt/miniconda3/envs/covid-19/bin python3.8
from datetime import datetime
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

if __name__ == '__main__':
    main()
