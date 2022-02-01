from microWebSrv import MicroWebSrv
import machine
import stepper
import time
import adafruit

ws = []

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


def saveConfig():
    with open('config', 'w') as f:
        for m in motors:
            f.write(str(m.getTargetPosition()) + '\n')
            f.write(str(m.getLimit()) + '\n')


def stopMotors():
    timMotor.deinit()


def startMotors():
    timMotor.init(period=1, mode=machine.Timer.PERIODIC,
                  callback=lambda t: moveMotors())


startMotors()
stopMotors()

# web socket callbacks


def sendMotorsPosition():
    stopMotors()
    global ws
    for x in ws:
        for i, m in enumerate(motors):
            ignore = 1 if m.getIgnoreLimits() == True else 0
            x.SendText('blindsPosition:motor:%i:position:%i:target:%i:limit:%i:ignoreLimit:%i' %
                       (i, m.getPosition(), m.getTargetPosition(), m.getLimit(), ignore))
    startMotors()


def goUp(msg):
    stopMotors()
    global ws
    index = int(msg.split(':')[1])
    steps = int(msg.split(':')[2])
    motor = motors[index]
    motor.setTargetPosition(motor.getTargetPosition() - steps)
    for x in ws:
        x.SendText('motor:%i:goto:%s ' %
                   (index, motor.getTargetPosition() - steps))
    saveConfig()
    startMotors()


def goDown(msg):
    stopMotors()
    global ws
    index = int(msg.split(':')[1])
    steps = int(msg.split(':')[2])
    motor = motors[index]
    motor.setTargetPosition(motor.getTargetPosition() + steps)
    for x in ws:
        x.SendText('motor:%i:go to: %i' %
                   (index, motor.getTargetPosition() + steps))
    saveConfig()
    startMotors()


def stop(msg):
    stopMotors()
    global ws
    index = int(msg.split(':')[1])
    motor = motors[index]
    motor.setTargetPosition(motor.getPosition())
    motor.disable()
    for x in ws:
        x.SendText('motor:%i, stop' % index)
    saveConfig()
    startMotors()


def closeBlinds():
    stopMotors()
    global ws
    for m in motors:
        m.setTargetPosition(m.getLimit())
        for x in ws:
            x.SendText('motors, close, limit: %i ' %
                       (m.getLimit()))
    saveConfig()
    startMotors()


def openBlinds():
    stopMotors()
    global ws
    for m in motors:
        m.setTargetPosition(0)
        for x in ws:
            x.SendText('motors: open, bottom limit: %i ' %
                       (0))
    saveConfig()
    startMotors()


def closeBlind(msg):
    stopMotors()
    global ws
    index = int(msg.split(':')[1])
    motor = motors[index]
    motor.setTargetPosition(motor.getLimit())
    for x in ws:
        x.SendText('motor: %i, close, limit: %i ' %
                   (index, motor.getLimit()))
    saveConfig()
    startMotors()


def openBlind(msg):
    stopMotors()
    global ws
    index = int(msg.split(':')[1])
    motor = motors[index]
    motor.setTargetPosition(0)
    for x in ws:
        x.SendText('motor: %i, open, bottom limit: %i ' %
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
        for x in ws:
            x.SendText('setTopPosition:motor:%i:position:%i' %
                       (index, motor.getPosition()))
        saveConfig()


def setLimit(msg):
    global ws
    password = msg.split(':')[2]
    if password == USER_PASSWORD:
        index = int(msg.split(':')[1])
        motor = motors[index]
        motor.setLimit(motor.getTargetPosition())
        for x in ws:
            x.SendText('setLimit:motor:%i:position:%i' %
                       (index, motor.getPosition()))
        saveConfig()


def setIgnoreLimits(msg):
    global ws
    password = msg.split(':')[2]
    if password == USER_PASSWORD:
        ignoreLimits = True if msg.split(':')[1] == '1' else False
        for m in motors:
            m.setIgnoreLimits(ignoreLimits)

        for x in ws:
            x.SendText('setIgnoreLimits:%i' % ignoreLimits)


# web server part from here

def _onConnectCallback():
    stopMotors()


def _acceptWebSocketCallback(webSocket, httpClient):
    stopMotors()
    global ws
    ws.append(webSocket)
    print(f'WS ACCEPT {len(ws)}')
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
        timState.deinit()
        timState.init(period=1000, mode=machine.Timer.PERIODIC,
                      callback=lambda t: sendMotorsPosition())
    elif 'setIgnoreLimits' in msg:
        setIgnoreLimits(msg)


def _recvBinaryCallback(webSocket, data):
    print('WS RECV DATA : %s' % data)


def _closedCallback(webSocket):
    global ws
    ws.remove(webSocket)
    print(f'WS CLOSED {len(ws)}')
    if len(ws) == 0:
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
    stopMotors()
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
    finally:
        adafruit.subscribe(adafruitCb)
        # machine.reset()


adafruit.subscribe(adafruitCb)

while True:
    checkAda()
    time.sleep(1)
