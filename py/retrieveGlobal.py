"""Import world COVID-19 data."""

import pandas as pd
import fileinput
import re
from datetime import date
from .helper import update_ref_access


class RetrieveGlobal:
    """
    Retrieve global COVID-19 data.

    Reference:
        COVID-19 Canada Open Data Working Group.
        Epidemiological Data from the COVID-19 Outbreak in Canada.
        https://github.com/ishaberry/Covid19Canada.
    """

    def __init__(self):
        """Retrieve global COVID-19 data."""
        self.reference = "Dong E, Du H, Gardner L. An interactive " +\
            "web-based dashboard to track COVID-19 in real time. " +\
            "Lancet Infect Dis; published online Feb 19. " +\
            "https://doi.org/10.1016/S1473-3099(20)30120-1."
        self.url = 'https://raw.githubusercontent.com/'
        self.repo = 'CSSEGISandData/COVID-19/master/'
        self.dir = 'csse_covid_19_data/csse_covid_19_time_series/'
        self.file = 'time_series_covid19_{}_global.csv'
        self.reports = ['confirmed', 'deaths', 'recovered']
        self.data = []

    def _save_values(self, r):
        """Retrieve data and save to csv."""
        path = self.url+self.repo+self.dir+self.file.format(r)
        try:
            df = pd.read_csv(path, low_memory=False)
            df.to_csv(
                'data/World-{}.csv'.format(r),
                index=False)
            self.data.append(df)
        except:
            print("Retrieving {} failed.".format(r))

    def update_data(self):
        """Update csv data."""
        for r in self.reports:
            self._save_values(r)
        # update reference access date in README.
        update_ref_access(self.reference)
