"""Retrieve data from google spreadsheet."""
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pandas as pd
from .helper import update_ref_access


class RetrieveCanada:
    """
    Retrieve public COVID-19 data for Canada.

    Reference:
        COVID-19 Canada Open Data Working Group.
        Epidemiological Data from the COVID-19 Outbreak in Canada.
        https://github.com/ishaberry/Covid19Canada.
    """

    def __init__(self):
        """Retrieve public COVID-19 data for Canada."""
        self.scopes = ['https://www.googleapis.com/auth/spreadsheets.readonly']
        # The public Canada COVID-19 data.
        self.sheet_id = '1D6okqtBS3S2NRC7GFVHzaZ67DuTw7LX49-fqSLwJyeo'
        self.stop_names = ['Codebook', 'Contributors']
        self.reference = 'COVID-19 Canada Open Data Working Group. ' +\
            'Epidemiological Data from the COVID-19 Outbreak in Canada. ' +\
            'https://github.com/ishaberry/Covid19Canada.'
        self.creds = None
        self.sheet = None

    def auth(self):
        """Authenticate to the API with Google API credentials."""
        # The file token.pickle stores the user's access and refresh tokens,
        # and is created automatically when the authorization flow completes
        # for the first time.
        if os.path.exists('credentials/token.pickle'):
            with open('credentials/token.pickle', 'rb') as token:
                self.creds = pickle.load(token)
        # If there are no (valid) credentials available, let the user log in.
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials/credentials.json', self.scopes)
                self.creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('credentials/token.pickle', 'wb') as token:
                pickle.dump(self.creds, token)

    def _save_values(self, nm):
        """Retrieve data and save to csv."""
        try:
            result = self.sheet.values().get(
                spreadsheetId=self.sheet_id,
                range=nm).execute()
            values = result.get('values', [])
            df = pd.DataFrame(
                values[4:], columns=values[3])
            df.to_csv(
                'data/Canada-{}.csv'.format(nm),
                index=False)
        except:
            print("Retrieving {} failed.".format(nm))

    def update_data(self):
        """Update csv data."""
        service = build('sheets', 'v4', credentials=self.creds)
        # Call the Sheets API
        self.sheet = service.spreadsheets()
        sheets = self.sheet.get(
            spreadsheetId=self.sheet_id).execute()['sheets']
        sheet_names = [x['properties']['title'] for x in sheets]
        for nm in sheet_names:
            if nm not in self.stop_names:
                self._save_values(nm)
        # update reference access date in README.
        update_ref_access(self.reference)
