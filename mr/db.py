#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import influxdb
from influxdb import InfluxDBClient
import pandas as pd
from influxdb import DataFrameClient
import datetime


# In[ ]:



class DBCreateDrop:

    def __init__(self, dbname):
        print('enter insert init')
        host = 'localhost'
        self.client = DataFrameClient(host, '8086')
        print(self.client.get_list_database())
        #self.dropdb('CellData')
        self.createdb(dbname)

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


# In[ ]:

#ad:
#class DATABASE(object):

class DATReadWrite(object):
    r""" DATABASE takes an input as database name. It creates a client connection
      to influxDB and It reads/ writes UE data for a given dabtabase and a measurement.


    Parameters
    ----------
    host: str (default='r4-influxdb.ricplt.svc.cluster.local')
        hostname to connect to InfluxDB
    port: int (default='8086')
        port to connect to InfluxDB
    username: str (default='root')
        user to connect
    password: str (default='root')
        password of the use

    Attributes
    ----------
    client: influxDB client
        DataFrameClient api to connect influxDB
    data: DataFrame
        fetched data from database
    """

    def __init__(self, dbname,host="localhost", port='8086'):
        print('enter inint DATABASE')
        self.data = None
        self.client = DataFrameClient(host, port, dbname)
        print('self.client=', self.client)

    def read_data(self, meas, limit=100):
        """Read data method for a given measurement and limit

        Parameters
        ----------
        meas: str (default='cellMeasReport')
        limit:int (defualt=100)
        """
        #print('self.client=', self.client)
        #self.client.get_list_database()
        #print('self.client.get_list_database()=', self.client.get_list_database())
        #self.client.switch_database('mydb_01')
        #print(self.client.get_list_measurements())
        #print(self.client.query('select * from mydb_01'))
        result = self.client.query('select * from ' + meas + ' limit ' + str(limit))
        print('result=',result)
        print("Querying data : " + meas + " : size - " + str(len(result[meas])))
        try:
            if len(result[meas]) != 0:
                self.data = result[meas]
                self.data['new_observation'] = self.data.index
            else:
                raise NoDataError

        except NoDataError:
            print('Data not found for ' + meas + ' vnf')

    def write_lp_prediction(self, df, meas='LP'):
        """Write data method for a given measurement

        Parameters
        ----------
        meas: str (default='LP')
        """
        self.client.write_points(df, meas)

class DATABASE(object):
    r""" DATABASE takes an input as database name. It creates a client connection
      to influxDB and It reads/ writes UE data for a given dabtabase and a measurement.
    Parameters
    ----------
    host: str (default='r4-influxdb.ricplt.svc.cluster.local')
        hostname to connect to InfluxDB
    port: int (default='8086')
        port to connect to InfluxDB
    username: str (default='root')
        user to connect
    password: str (default='root')
        password of the use
    Attributes
    ----------
    client: influxDB client
        DataFrameClient api to connect influxDB
    data: DataFrame
        fetched data from database
    """

    def __init__(self, dbname, user='root', password='root', host="r4-influxdb.ricplt", port='8086'):
        self.data = None
        self.client = DataFrameClient(host, port, user, password, dbname)

    def read_data(self, meas, limit=100):
        """Read data method for a given measurement and limit
        Parameters
        ----------
        meas: str (default='cellMeasReport')
        limit:int (defualt=100)
        """

        result = self.client.query('select * from ' + meas + ' limit ' + str(limit))
        print("Querying data : " + meas + " : size - " + str(len(result[meas])))
        try:
            if len(result[meas]) != 0:
                self.data = result[meas]
                self.data['measTimeStampRf'] = self.data.index
            else:
                raise NoDataError

        except NoDataError:
            print('Data not found for ' + meas + ' vnf')

    def write_lp_prediction(self, df, meas='LP'):
        """Write data method for a given measurement
        Parameters
        ----------
        meas: str (default='LP')
        """
        self.client.write_points(df, meas)

# In[ ]:

#lp:

# class DUMMY:

#     def __init__(self):
#         self.cell = pd.read_csv('lp/cells.csv')
#         self.data = None

#     def read_data(self, meas='cellMeasReport', limit=100):
#         self.data = self.cell.head(limit)

#     def write_lp_prediction(self, df, meas='LP'):
#         pass


#ad:

class DUMMY:

    def __init__(self):
        self.ue = pd.read_csv('ad/valid.csv')
        self.data = None

    def read_data(self, meas='ueMeasReport', limit=100000):
        if meas == 'valid':
            self.data = self.ue.head(limit)
        else:
            self.data = self.ue.head(limit).drop('Anomaly', axis=1)

    def write_anomaly(self, df, meas_name='QP'):
        pass

    

# In[ ]:


class Error(Exception):
    """Base class for other exceptions"""
    pass


class NoDataError(Error):
    """Raised when there is no data available in database for a given measurment"""
    pass

