"""A set of helper functions."""
import fileinput
import re
from datetime import date
import pandas as pd


def update_ref_access(reference):
    """Update reference access date."""
    today = date.today().strftime('%B %d, %Y')
    reference_sub = re.escape(reference) + ' \((.*)\)'
    reference_new = reference + ' (Retrieved on {})'.format(today)
    print(reference_new)
    with fileinput.FileInput('README.md', inplace=True, backup='.bak') as file:
        for line in file:
            print(
                re.sub(
                    reference_sub,
                    reference_new,
                    line
                ), end=''
            )


def get_population_country():
    """
    Retrieve world population by country from Wikipedia.
    Source:
        https://en.wikipedia.org/wiki/
            List_of_countries_by_population_(United_Nations)
        https://en.wikipedia.org/wiki/MS_Zaandam
        https://www.princess.com/news/notices_and_advisories/
            notices/diamond-princess-update.html
        https://en.wikipedia.org/wiki/
            Demographics_of_the_Palestinian_territories
    """
    url = "https://en.wikipedia.org/wiki/"\
        + "List_of_countries_by_population_(United_Nations)"
    html = pd.read_html(url, attrs={'id': 'main'})
    data = html[0].iloc[:, [0, 4]].copy()
    data.columns = ['country', 'population']
    data['country'] = data['country'].apply(
        lambda x: re.sub(r'\[.+\]', '', x).strip())
    data = data.append([
        {'country': 'Diamond Princess', 'population': 3711},
        {'country': 'MS Zaandam', 'population': 1829},
        {'country': 'West Bank and Gaza', 'population': 4543126},
        {'country': 'Kosovo', 'population': 1797086}
    ]).copy()
    data = data.set_index('country')
    data.loc['Serbia', 'population'] =\
        data.loc['Serbia', 'population'] - data.loc['Kosovo', 'population']
    return data


def get_population_province():
    """
    Retrieve Canada's population by province.
    Source:
        https://en.wikipedia.org/wiki/
            Population_of_Canada_by_province_and_territory
    """
    url = "https://en.wikipedia.org/wiki/"\
        + "Population_of_Canada_by_province_and_territory"
    html = pd.read_html(url, attrs={'class': 'wikitable sortable'})
    data = html[0].iloc[:, [1,  -3]]
    data.columns = ['province', 'population']
    data = data.set_index('province')
    return data
