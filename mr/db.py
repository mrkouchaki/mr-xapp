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
    print('///////////enter class DBCreatDrop\\\\\\\\\\\\')
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
    print('///////////enter class DATReadWrite\\\\\\\\\\\\')
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
    print('///////////enter class DATABASE(object)\\\\\\\\\\\\')
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
        print('///////enter def __init__ in class DATABASE\\\\\\\\\\')
        self.data = None
        self.client = DataFrameClient(host, port, user, password, dbname)
        print('self.client=', self.client)

    def read_data(self, meas, limit=100):
        print('///////enter def read_data(self, meas, limit=100): in class DATABASE\\\\\\\\\\')
        """Read data method for a given measurement and limit
        Parameters
        ----------
        meas: str (default='cellMeasReport')
        limit:int (defualt=100)
        """
        print('meas=', meas)
        print('limit=', limit)
        result = self.client.query('select * from ' + meas + ' limit ' + str(limit))
        print('result=', result)
        print("Querying data : " + meas + " : size - " + str(len(result[meas])))
        try:
            print('result[meas]=', result[meas])
            print('len(result[meas])=', len(result[meas]))
            if len(result[meas]) != 0:
                self.data = result[meas]
                print('self.data==', self.data)
                self.data['measTimeStampRf'] = self.data.index
                print('self.data[measTimeStampRf]=', self.data['measTimeStampRf'] )
            else:
                print('else:')
                raise NoDataError

        except NoDataError:
            print('except NODataErro:')
            print('Data not found for ' + meas + ' vnf')

    def write_lp_prediction(self, df, meas='LP'):
        print('///////enter def write_lp_prediction(self, df, meas=LP): in class DATABASE\\\\\\\\\\')
        """Write data method for a given measurement
        Parameters
        ----------
        meas: str (default='LP')
        """
        self.client.write_points(df, meas)
        print('self.client.write_points(df, meas)=', self.client.write_points(df, meas))

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
    print('///////////enter class DUMMY in db\\\\\\\\\\\\\\')

    def __init__(self):
        print('///////enter def __init__ in class DUMMY\\\\\\\\\\')
        self.ue = pd.read_csv('mr/valid.csv')
        print('self.ue= pd.read_csv(mr/valid.csv)=', self.ue)
        self.data = None

    def read_data(self, meas='ueMeasReport', limit=100000):
        print('///////enter def read_data(self, meas=ueMeasReport, limit=100000): in class DATABASE\\\\\\\\\\')
        print('meas=', meas)
        if meas == 'valid':
            print('meas == valid:')
            self.data = self.ue.head(limit)
            print('self.data = self.ue.head(limit)=', self.data)
        else:
            self.data = self.ue.head(limit).drop('Anomaly', axis=1)
            print('self.data = self.ue.head(limit).drop(Anomaly, axis=1)=', self.data)

    def write_anomaly(self, df, meas_name='QP'):
        print('///////enter def write_anomaly(self, df, meas_name=QP): in class DATABASE\\\\\\\\\\')
        pass

    

# In[ ]:


class Error(Exception):
    print('////////enter class Error in db\\\\\\\\\\')
    """Base class for other exceptions"""
    pass


class NoDataError(Error):
    print('////////enter class NoDataError in db\\\\\\\\\\')
    """Raised when there is no data available in database for a given measurment"""
    pass

