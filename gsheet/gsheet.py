#!/usr/bin/env python3

import os.path
import pickle
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow

from googleapiclient.discovery import build
from google.oauth2 import service_account
from datetime import datetime
from addict import Dict

from teslapy import Tesla
from .user_info import params


def getTeslaBatteryData():
    CLIENT_ID = 'e4a9949fcfa04068f59abb5a658f2bac0a3428e4652315490b659d5ab3f35a9e'
    CLIENT_SECRET = 'c75f14bbadc8bee3a7594412c31416f8300256d7668ea7e6e7f06727bfb9d220'

    with Tesla(params.teslaUserId, params.teslaPw, CLIENT_ID, CLIENT_SECRET) as tesla:
        tesla.fetch_token()
        selected = cars = tesla.vehicle_list()
        vehicle = selected[0]
        print('%d vehicle(s), %d selected' % (len(cars), len(selected)))
        # print(vehicle.get_vehicle_summary())
        vehicle.sync_wake_up()

        d = vehicle.get_vehicle_data()
        data = Dict(d)

        dt_object = datetime.fromtimestamp(data.charge_state.timestamp/1000)
        row = [
            str(dt_object),
            data.charge_state.est_battery_range,
            data.charge_state.battery_range,
            data.charge_state.ideal_battery_range,
            data.charge_state.battery_level,
            data.charge_state.usable_battery_level,
            data.charge_state.charging_state,
            data.vehicle_state.car_version,
            data.vehicle_state.odometer
        ]
        print('Tesla data row', row)
        return row


# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
service = None


def initSheetApi(from_service_account=True):
    if from_service_account:
        print('- use service account to authorize access to', params.gSheetUserId)
        creds = service_account.Credentials.from_service_account_file(
            filename=params.serviceCredsFile, scopes=SCOPES)
        delegated_credentials = creds.with_subject(params.gSheetUserId)
        return build('sheets', 'v4', credentials=delegated_credentials)

    print('- use token to authorize access to google account')
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    return build('sheets', 'v4', credentials=creds)


def getHeaderRow():
    return ['timestamp', 'est_battery_range',
            'battery_range', 'ideal_battery_range', 'battery_level', 'usable_battery_level',
            'charging_state', 'car_version', 'odometer']


def header():
    sheet = service.spreadsheets()
    result = sheet.values().get(
        spreadsheetId=params.gSheetId, range=params.rangeName).execute()
    values = result.get('values', [])
    if not values:
        print('Add header row', getHeaderRow())
        append_values(getHeaderRow())


def append_values(row: list):
    body = {
        'values': [row]
    }
    result = service.spreadsheets().values().append(
        spreadsheetId=params.gSheetId, range=params.rangeName,
        valueInputOption='USER_ENTERED', body=body).execute()
    print('{0} cells appended.'.format(result
                                       .get('updates')
                                       .get('updatedCells')))
    return result


if __name__ == '__main__':
    service = initSheetApi()
    header()
    append_values(getTeslaBatteryData())
