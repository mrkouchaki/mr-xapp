# ==================================================================================
#       Copyright (c) 2020 China Mobile Technology (USA) Inc. Intellectual Property.
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#          http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
# ==================================================================================

"""
This will be used before the LP xApp can read cell measurements from KPM, while now it reads directly from influxDB, or a fake data source
"""

import pandas as pd
from influxdb import DataFrameClient
import datetime
dbname = 'lpdatabase'

class INSERTDATA:

    def __init__(self):
        print('enter insert init')
        host = 'localhost'
        self.client = DataFrameClient(host, '8086')
        print(self.client.get_list_database())
        #self.dropdb('CellData')
        self.createdb('CellData')

    def createdb(self, dbname):
        print('enter insert createdb')
        print("Create database: " + dbname)
        self.client.create_database(dbname)
        print(self.client.get_list_database())
        self.client.switch_database(dbname)

    def dropdb(self, dbname):
        print('enter insert dropdb')
        print("DROP database: " + dbname)
        self.client.drop_database(dbname)

    def dropmeas(self, measname):
        print('enter insert dropmeas')
        print("DROP MEASUREMENT: " + measname)
        self.client.query('DROP MEASUREMENT '+measname)

def time(df):
    print('enter time')
    df.index = pd.date_range(start=datetime.datetime.now(), freq='10ms', periods=len(df))
    print('df.index=',df.index)
    print(df['measTimeStampRf'])
    print('lambda x: str(x)=', lambda x: str(x))
    df['measTimeStampRf'] = df['measTimeStampRf'].apply(lambda x: str(x))
    return df

def populatedb():
    data = pd.read_csv('/home/mreza/xApp_v1/xApp_n1/xapp_n1_main/cells.csv')
    data
    print(data)
    data = time(data)
    print('data after time(data)=', data)

    # inintiate connection and create database UEDATA
    db = INSERTDATA()
    print('insert data finished, go to write_point')
    db
    print('db =', db)
    db.client.write_points(data, 'cellMeas')
    print(db.client.write_points(data, 'cellMeas'))
    del data
