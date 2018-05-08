import os
import sqlite3
import uuid
import threading
from pathlib import Path
from TransmitThread import TransmitThread
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash

app = Flask(__name__)
app.config.from_object(__name__)
app.config.update(dict(DATABASE=os.path.join(app.root_path, 'flaskr.db')), SECRET_KEY='development key',
                  USERNAME='admin', PASSWORD='default')
app.config.from_envvar('FLASKR_SETTINGS',silent=True)

staticVar = 0
dict = ()

@app.route('/')
def show_entries():
    global staticVar
    staticVar = staticVar+1
    return "Hello Welcome to USRP Service application! You will be served as you request!"

@app.route('/txdata/<clienID>/<usrpIp>/<frequency>/<path:fname>',methods=['GET'])
def transmit(clienID,usrpIp,frequency,fname):
    global dict
    print ('Hello ' + clienID + ',this is your username ' + usrpIp + ' freq ' + frequency + ' file ' + fname)
    if(clienID == 0 ):
        clientID = str(uuid.uuid4().hex)
        print('New request for ',usrpIp,'to transmit file ',fname,'at frequecy',frequency)

    myFile = Path(fname)
    if(myFile.is_file):
        print(myFile,' exists! Request for ',usrpIp,'to transmit file ',fname,'at frequecy',frequency)
    else:
        print(myFile,' does not exist!')

    isUsrptransmiting = False
    shallStartTxn = False
    transmitThread = None
    for key in dict:
        if(key == usrpIp):
            transmitThread = dict[key]
            if transmitThread.getClientId() == clientID:
                transmitThread.killThreadExecution()
                shallStartTxn = True
            elif transmitThread.timeOutEvent(gmtime(0)):
                shallStartTxn = True

    if(not isUsrptransmiting)|shallStartTxn:
        if fname.endswith('.iq12'):
            decIM = 12
        else:
            decIM = 48
        usrpIp = "addr="+str(usrpIp)
        print(usrpIp)
        fname = "/"+fname
        transmitThread = threading.Thread(target=TransmitThread,args=(fname, str(usrpIp), decIM, frequency))
        #thread = threading.Thread(target=transmitThread, args=())
        transmitThread.daemon = True  # Daemonize thread
        print("Service is Transmitting " + str(clienID) + "this is your username " + str(usrpIp) + " freq " + str(frequency) + " file " + str(fname) +" decIM "+str(decIM))
        transmitThread.start()
        dict[str(usrpIp)] = transmitThread
        print('Service is Transmitting '+ clienID+',this is your username '+usrpIp+ ' freq '+frequency+ ' file '+ fname)
        return {'clientId':clientID}
    else:
        response = flask.Response(response=json.dumps(dict(status='err')), status=400, mimetype='application/json')
        return respone


@app.route('/stoptransmitting/<clientID>',methods=['GET'])
def stopTransmit(clientID):
    global dict
    clientFound = false
    print("Stop transmission requested on this client ID" + clientID)
    for key in dict:
        transmissionThread = dict[key]
        if transmissionThread.getClientId()==clientID:
            clientFound=true
            transmissionThread.killThreadExecution
    if clientFound:
        return flask.Response(response=json.dumps(dict(status='ok')),status=200, mimetype='text/html')
    else:
        return flask.Response(response=json.dumps(dict(status='err')), status=400, mimetype='text/html')


@app.route('/about/')
def about():
    return 'The about page'

def logg(data):
    print("INFO:", data)
