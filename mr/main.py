
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
lp entrypoint module

RMR Messages
 #define TS_UE_LIST 30000
for now re-use the 30000 to receive a UEID for prediction
"""

import schedule
from zipfile import ZipFile
import json
from os import getenv
from ricxappframe.xapp_frame import RMRXapp, rmr, Xapp
from mr import sdl
#from lp.exceptions import UENotFound, CellNotFound

import os
import sys
import logging
import numpy as np
import torch
import tensorflow
from numpy import zeros, newaxis
from torch.nn import functional as F
from torch.utils.data import TensorDataset, DataLoader
import torch.nn as nn
from torch.nn.utils.rnn import pack_padded_sequence, pad_packed_sequence

from mr.db import DATABASE, DUMMY
import mr.populate as populate

xapp = None
print('first line of code: xapp=None=', xapp)
pos = 0
cell_data = None
rmr_xapp = None
ai_model = None

class UENotFound(BaseException):
    pass
class CellNotFound(BaseException):
    pass

def post_init(self):
    print('///////enter def post_init__/////////////////')
    """
    Function that runs when xapp initialization is complete
    """
    self.def_hand_called = 0
    self.traffic_steering_requests = 0


def handle_config_change(self, config):
    print('////////enter def handle_config_change//////////////')
    """
    Function that runs at start and on every configuration file change.
    """
    self.logger.debug("handle_config_change: config: {}".format(config))


def default_handler(self, summary, sbuf):
    print('/////////enter def default_handler///////////////')
    """
    Function that processes messages for which no handler is defined
    """
    self.def_hand_called += 1
    print('self.def_hand_called += 1=', self.def_hand_called)
    self.logger.warning("default_handler unexpected message type {}".format(summary[rmr.RMR_MS_MSG_TYPE]))
    self.rmr_free(sbuf)


def mr_req_handler(self, summary, sbuf):
    print('///////////enter def mr_req handler/////////////')
    """
    This is the main handler for this xapp, which handles load prediction requests.
    This app fetches a set of data from SDL, and calls the predict method to perform
    prediction based on the data

    The incoming message that this function handles looks like:
        {"UEPredictionSet" : ["UEId1","UEId2","UEId3"]}
    """
    self.traffic_steering_requests += 1
    # we don't use rts here; free the buffer
    self.rmr_free(sbuf)

    ue_list = []
    try:
        print('rmr.RMR_MS_PAYLOAD=', rmr.RMR_MS_PAYLOAD)
        print('summary[rmr.RMR_MS_PAYLOAD]=', summary[rmr.RMR_MS_PAYLOAD])
        req = json.loads(summary[rmr.RMR_MS_PAYLOAD])  # input should be a json encoded as bytes
        print('req = json.loads(summary[rmr.RMR_MS_PAYLOAD])=', req)
        ue_list = req["UEPredictionSet"]
        print('ue_list=req["UEPredictionSet"] =', ue_list)
        self.logger.debug("mr_req_handler processing request for UE list {}".format(ue_list))
    except (json.decoder.JSONDecodeError, KeyError):
        self.logger.warning("mr_req_handler failed to parse request: {}".format(summary[rmr.RMR_MS_PAYLOAD]))
        return
    print('ue_list mr_req_handler aftr 1st try=', ue_list)
    # iterate over the UEs, fetches data for each UE and perform prediction
    for ueid in ue_list:
        try:
            uedata = sdl.get_uedata(self, ueid)
            print('uedata = sdl.get_uedata(self, ueid)=', uedata)
            predict(self, uedata)
            print('predict(self, uedata)=', predict(self, uedata))
        except UENotFound:
            print('enter UENotFound in mr_req_handler')
            self.logger.warning("mr_req_handler received a TS Request for a UE that does not exist!")

def entry(self):
    print('////////////enter def entry///////////////')
    """  Read from DB in an infinite loop and run prediction every second
      TODO: do training as needed in the future
    """
    schedule.every(1).seconds.do(run_prediction, self)
    while True:
        schedule.run_pending()

def run_prediction(self):
    print('///////////////enter def run_prediction///////////////')
    """Read the latest cell_meas sample from influxDB and run it by the model inference
    """

    global pos
    sample = [3735, 0, 27648, 2295, 18, -1, 16383,-1, -1, -1]
    print('sample=[3735,...]=', sample)
    if cell_data:
        pos = (pos + 1) % len(cell_data)  # iterate through entire list one at a time
        print('pos=(pos + 1) % len(cell_data)=', pos)
        sample = cell_data[pos]
        print('sample = cell_data[pos]=', sample)
    predict(self, sample)

def predict(self, celldata):
    print('/////////////enter def predict/////////////////')      
    """
    This is the method that's to perform prediction based on a model
    For now it just returns dummy data
    :return:
    """
    ai_model = load_model_parameter()
    print('ai_model.summary()=', ai_model.summary())      
    ret = predict_unseen_data(ai_model, celldata)
    print('ret=predict_unseen_data(ai_model, celldata)=', ret)
    print("celldata: ", celldata)
    print("Classification: ", ret)
    return ret

def load_model_parameter():
    print('/////////////enter def load_model_parameters////////////////')
    PATH = 'model.pth'
    print('PATH = model.pth=', PATH)      
    cwd = os.getcwd()
    print('cwd=os.getcwd=', cwd)
    print('os.listdir(cwd)=', os.listdir(cwd))
    if not os.path.exists(PATH):
        with ZipFile('mr/model.zip', 'r') as zip:
            zip.printdir()
            zip.extractall()
    input_dim = 10
    hidden_dim = 256
    layer_dim = 3
    output_dim = 2
    device = "cpu"
    model = LSTMClassifier(input_dim, hidden_dim, layer_dim, output_dim)
    print('model=LSTClassifier=', model.summary())      
    # model = model.to(device)
    model.load_state_dict(torch.load(PATH))
    model.eval()
    print('model.eval()=', model.summary())      
    # print(model)
    return model

def predict_unseen_data(model, unseen_data):
    print('/////////////////enter def predict_unseen_data///////////////////')
    np_data = np.asarray(unseen_data, dtype=np.float32)
    print('np_data=', np_data)
    X_grouped = np_data[newaxis, newaxis, :]
    X_grouped = torch.tensor(X_grouped.transpose(0, 2, 1)).float()
    print('X_grouped=', X_grouped)
    y_fake = torch.tensor([0] * len(X_grouped)).long()
    tensor_test = TensorDataset(X_grouped, y_fake)
    print('tensor_test=', tensor_test)      
    test_dl = DataLoader(tensor_test, batch_size=1, shuffle=False)
    print('test_dl=', test_dl)       
    ret = []
    for batch, _ in test_dl:
        batch = batch.permute(0, 2, 1)
        print('batch=', batch)
        out = model(batch)
        print('out=', out)  
        y_hat = F.log_softmax(out, dim=1).argmax(dim=1)
        print('y_hat=', y_hat)
        ret += y_hat.tolist()
        print('ret += y_hat.tolist()=', ret)
    if ret[0] == 0:
        print('ret[0] == 0')  
        return "Normal"
    return "Congestion"

def connectdb(thread=False):
    print('////////////////////enter def connectdb///////////////////')
    # Create a connection to InfluxDB if thread=True, otherwise it will create a dummy data instance
    global db
    global cell_data
    if thread:
        print('///////////////enter if(thread) in connectdb///////////////////')  
        db = DUMMY()
        print('db =DUMMY()=', db)  
    else:
        print('//////enter else= populate.populate()////////////////')  
        populate.populatedb()  # temporary method to populate db, it will be removed when data will be coming through KPIMON to influxDB

        db = DATABASE('CellData')
        print('db =  DATABASE(celldata) =', db) 
        db.read_data("cellMeas")
        print('db.read_data("cellMeas")=', db.read_data("cellMeas"))
        cell_data = db.data.values.tolist()  # needs to be updated in future when live feed will be coming through KPIMON to influxDB
        print('cell_data = db.data.values.tolist()=', cell_data)
        #print('cell_data:, cell_data)

def start(thread=False):
 
    print('////////////////entered Starrrrrrrrrrrt///////////////////')
    """
    This is a convenience function that allows this xapp to run in Docker
    for "real" (no thread, real SDL), but also easily modified for unit testing
    (e.g., use_fake_sdl). The defaults for this function are for the Dockerized xapp.
    """
    global xapp, ai_model
    fake_sdl = getenv("USE_FAKE_SDL", None)
    print('fake_sdl = getenv(USE_FAKE_SDL, None)=', fake_sdl)
    xapp = Xapp(entrypoint=entry, rmr_port=4560, use_fake_sdl=fake_sdl)
    print('xapp = Xapp(entrypoint=entry, rmr_port=4560, use_fake_sdl=fake_sdl)=', xapp)
    connectdb(thread)
    ai_model = load_model_parameter()
    ai_model.summary()
    print('ai_model.summary=', ai_model.summary())
    xapp.run()


def stop():
    print('/////////////enter def stop//////////////////')      
    """
    can only be called if thread=True when started
    """
    xapp.stop()


def get_stats():
    print('//////////////////enter def get_stats()////////////////////')
    """
    hacky for now, will evolve
    """
    print('DefCalled:rmr_xapp.def_hand_called=', rmr_xapp.def_hand_called)
    print('SteeringRequests:rmr_xapp.traffic_steering_requests=', rmr_xapp.traffic_steering_requests) 
    return {"DefCalled": rmr_xapp.def_hand_called,
            "SteeringRequests": rmr_xapp.traffic_steering_requests}

class LSTMClassifier(nn.Module):
    print('/////////////////enter class LSTClassifier////////////////////')      
    def __init__(self, input_dim, hidden_dim, layer_dim, output_dim):
        print('///////enter def __init__ in LST//////////////////')  
        super().__init__()
        self.hidden_dim = hidden_dim
        self.layer_dim = layer_dim
        self.rnn = nn.LSTM(input_dim, hidden_dim, layer_dim, batch_first=True)
        self.fc = nn.Linear(hidden_dim, output_dim)
        self.batch_size = None
        self.hidden = None

    def forward(self, x):
        print('////////enter def forward in LST//////////////////') 
        h0, c0 = self.init_hidden(x)
        out, (hn, cn) = self.rnn(x, (h0, c0))
        out = self.fc(out[:, -1, :])
        return out

    def init_hidden(self, x):
        print('/////////enter def init_hidden in LST//////////////////')   
        h0 = torch.zeros(self.layer_dim, x.size(0), self.hidden_dim)
        c0 = torch.zeros(self.layer_dim, x.size(0), self.hidden_dim)
        return [t for t in (h0, c0)]
