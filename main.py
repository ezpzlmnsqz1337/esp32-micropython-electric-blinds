from microWebSrv import MicroWebSrv
import machine
import stepper
import time
import adafruit

ws = None

# handle password for configuration over web page

with open('pass', 'r') as f:
    USER_PASSWORD = f.readline().rstrip('\n').rstrip('\r')

# motors settings
motors = (
    stepper.MyStepper(5, 18, 19, 21, 0),
    stepper.MyStepper(13, 12, 14, 27, 1)
)

for m in motors:
    m.disable()


with open('config', 'r') as f:
    for m in motors:
        m.setPosition(int(f.readline()))
        m.setTargetPosition(m.getPosition())
        m.setLimit(int(f.readline()))

timMotor = machine.Timer(0)
timState = machine.Timer(1)


def moveMotors():
    ready = 0
    for m in motors:
        if not m.move():
            ready += 1

    if ready == 2:
        timMotor.deinit()


motors[0].invertDirection(True)


timMotor.init(period=1, mode=machine.Timer.PERIODIC,
              callback=lambda t: moveMotors())


def saveConfig():
    with open('config', 'w') as f:
        for m in motors:
            f.write(str(m.getTargetPosition()) + '\n')
            f.write(str(m.getLimit()) + '\n')


def startMotors():
    timMotor.deinit()
    timMotor.init(period=1, mode=machine.Timer.PERIODIC,
                  callback=lambda t: moveMotors())

# web socket callbacks


def sendMotorsPosition():
    global ws
    for i, m in enumerate(motors):
        ignore = 1 if m.getIgnoreLimits() == True else 0
        if ws != None:
            ws.SendText('blindsPosition:motor:%i:position:%i:target:%i:limit:%i:ignoreLimit:%i' %
                        (i, m.getPosition(), m.getTargetPosition(), m.getLimit(), ignore))


def goUp(msg):
    global ws
    index = int(msg.split(':')[1])
    steps = int(msg.split(':')[2])
    motor = motors[index]
    motor.setTargetPosition(motor.getTargetPosition() - steps)
    if ws != None:
        ws.SendText('motor:%i:goto:%s ' %
                    (index, motor.getTargetPosition() - steps))
    saveConfig()
    startMotors()


def goDown(msg):
    global ws
    index = int(msg.split(':')[1])
    steps = int(msg.split(':')[2])
    motor = motors[index]
    motor.setTargetPosition(motor.getTargetPosition() + steps)
    if ws != None:
        ws.SendText('motor:%i:go to: %i' %
                    (index, motor.getTargetPosition() + steps))
    saveConfig()
    startMotors()


def stop(msg):
    global ws
    index = int(msg.split(':')[1])
    motor = motors[index]
    motor.setTargetPosition(motor.getPosition())
    motor.disable()
    if ws != None:
        ws.SendText('motor:%i, stop' % index)
    saveConfig()
    startMotors()


def closeBlinds():
    global ws
    for m in motors:
        m.setTargetPosition(m.getLimit())
        if ws != None:
            ws.SendText('motors, close, limit: %i ' %
                        (m.getLimit()))
    saveConfig()
    startMotors()


def openBlinds():
    global ws
    for m in motors:
        m.setTargetPosition(0)
        if ws != None:
            ws.SendText('motors: open, bottom limit: %i ' %
                        (0))
    saveConfig()
    startMotors()


def closeBlind(msg):
    global ws
    index = int(msg.split(':')[1])
    motor = motors[index]
    motor.setTargetPosition(motor.getLimit())
    if ws != None:
        ws.SendText('motor: %i, close, limit: %i ' %
                    (index, motor.getLimit()))
    saveConfig()
    startMotors()


def openBlind(msg):
    global ws
    index = int(msg.split(':')[1])
    motor = motors[index]
    motor.setTargetPosition(0)
    if ws != None:
        ws.SendText('motor: %i, open, bottom limit: %i ' %
                    (index, 0))
    saveConfig()
    startMotors()


def setTopPosition(msg):
    global ws
    password = msg.split(':')[2]
    if password == USER_PASSWORD:
        index = int(msg.split(':')[1])
        motor = motors[index]
        motor.setTopPosition()
        if ws != None:
            ws.SendText('setTopPosition:motor:%i:position:%i' %
                        (index, motor.getPosition()))
        saveConfig()


def setLimit(msg):
    global ws
    password = msg.split(':')[2]
    if password == USER_PASSWORD:
        index = int(msg.split(':')[1])
        motor = motors[index]
        motor.setLimit(motor.getTargetPosition())
        if ws != None:
            ws.SendText('setLimit:motor:%i:position:%i' %
                        (index, motor.getPosition()))
        saveConfig()


def setIgnoreLimits(msg):
    global ws
    password = msg.split(':')[2]
    if password == USER_PASSWORD:
        ignoreLimits = True if msg.split(':')[1] == '1' else False
        for m in motors:
            m.setIgnoreLimits(ignoreLimits)

        if ws != None:
            ws.SendText('setIgnoreLimits:%i' % ignoreLimits)


# web server part from here

def _onConnectCallback():
    timMotor.deinit()


def _acceptWebSocketCallback(webSocket, httpClient):
    global ws
    ws = webSocket
    print('WS ACCEPT')
    webSocket.RecvTextCallback = _recvTextCallback
    webSocket.RecvBinaryCallback = _recvBinaryCallback
    webSocket.ClosedCallback = _closedCallback
    startMotors()


def _recvTextCallback(webSocket, msg):
    if 'up' in msg:
        goUp(msg)
    elif 'down' in msg:
        goDown(msg)
    elif 'stop' in msg:
        stop(msg)
    elif 'closeBlind' in msg:
        closeBlind(msg)
    elif 'openBlind' in msg:
        openBlind(msg)
    elif 'CLOSE' in msg:
        closeBlinds()
    elif 'OPEN' in msg:
        openBlinds()
    elif 'setTopPosition' in msg:
        setTopPosition(msg)
    elif 'setLimit' in msg:
        setLimit(msg)
    elif 'getBlindsPosition' in msg:
        timState.init(period=1000, mode=machine.Timer.PERIODIC,
                      callback=lambda t: sendMotorsPosition())
    elif 'setIgnoreLimits' in msg:
        setIgnoreLimits(msg)


def _recvBinaryCallback(webSocket, data):
    print('WS RECV DATA : %s' % data)


def _closedCallback(webSocket):
    print('WS CLOSED')
    timState.deinit()

# ----------------------------------------------------------------------------


@MicroWebSrv.route('/open')
def handlerFuncGet(httpClient, httpResponse):
    openBlinds()


@MicroWebSrv.route('/close')
def handlerFuncGet(httpClient, httpResponse):
    closeBlinds()

# routeHandlers = [
#     ('/open-balcony',	'GET', lambda t: openBlind('openBlind:0')),
#     ('/open-window',	'GET', lambda t: openBlind('openBlind:1')),
#     ('/open',	'GET', lambda t: openBlinds()),
#     ('/close-balcony',	'GET', lambda t: closeBlind('closeBlind:0')),
#     ('/close-window',	'GET', lambda t: closeBlind('closeBlind:1')),
#     ('/close',	'GET', lambda t: closeBlinds())
# ]


# , routeHandlers=routeHandlers)
srv = MicroWebSrv(webPath='www/', port='8082')
srv.MaxWebSocketRecvLen = 256
srv.WebSocketThreaded = True
srv.OnConnectCallback = _onConnectCallback
srv.AcceptWebSocketCallback = _acceptWebSocketCallback
srv.Start(threaded=True)
print('server started')

# ----------------------------------------------------------------------------

# adafruit


def adafruitCb(topic, data):
    print('ADA CB ' + str(data))
    for m in motors:
        if data == b'OPEN':
            openBlinds()
        elif data == b'CLOSE':
            closeBlinds()
    saveConfig()
    startMotors()


def checkAda():
    try:
        adafruit.check()
    except Exception as e:
        print('Check for feed value failed {}{}\n'.format(
            type(e).__name__, e))
        adafruit.subscribe(adafruitCb)
        # machine.reset()


adafruit.subscribe(adafruitCb)

while True:
    checkAda()
    time.sleep(1)
