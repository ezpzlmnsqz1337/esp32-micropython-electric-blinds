from microWebSrv import MicroWebSrv
import machine
import stepper
import adafruit


USER_PASSWORD = ''

with open('pass', 'r') as f:
    USER_PASSWORD = f.readline().rstrip('\n').rstrip('\r')


motors = (
    stepper.MyStepper(5, 18, 19, 21, 0),
    stepper.MyStepper(13, 12, 14, 27, 1)
)

with open('config', 'r') as f:
    for m in motors:
        m.setPosition(int(f.readline()))
        m.setTargetPosition(m.getPosition())
        m.setLimit(int(f.readline()))

timCheck = machine.Timer(0)
timMotor = machine.Timer(1)
timState = machine.Timer(2)

motorsLock = False


def moveMotors():
    for m in motors:
        m.move()


motors[0].invertDirection(True)


timMotor.init(period=1, mode=machine.Timer.PERIODIC,
              callback=lambda t: moveMotors())


def saveConfig():
    with open('config', 'w') as f:
        for m in motors:
            f.write(str(m.getTargetPosition()) + '\n')
            f.write(str(m.getLimit()) + '\n')

# adafruit.io part


def adafruitCb(topic, data):
    print('ADA CB ' + str(data))
    for m in motors:
        if data == b'OPEN':
            m.setTargetPosition(0)
        elif data == b'CLOSE':
            m.setTargetPosition(m.getLimit())


def checkAda():
    try:
        adafruit.check()
    except:
        adafruit.retry(adafruitCb)


adafruit.subscribe(adafruitCb)

timCheck.init(period=1000, mode=machine.Timer.PERIODIC,
              callback=lambda t: checkAda())

# web socket callbacks


def sendMotorsPosition(webSocket):
    for i, m in enumerate(motors):
        ignore = 1 if m.getIgnoreLimits() == True else 0
        webSocket.SendText('blindsPosition:motor:%i:position:%i:target:%i:limit:%i:ignoreLimit:%i' %
                           (i, m.getPosition(), m.getTargetPosition(), m.getLimit(), ignore))


def goUp(webSocket, msg):
    index = int(msg.split(':')[1])
    steps = int(msg.split(':')[2])
    motor = motors[index]
    motor.setTargetPosition(motor.getTargetPosition() - steps)
    webSocket.SendText('motor:%i:goto:%s ' %
                       (index, motor.getTargetPosition() - steps))
    saveConfig()


def goDown(webSocket, msg):
    index = int(msg.split(':')[1])
    steps = int(msg.split(':')[2])
    motor = motors[index]
    motor.setTargetPosition(motor.getTargetPosition() + steps)
    webSocket.SendText('motor:%i:go to: %i' %
                       (index, motor.getTargetPosition() + steps))
    saveConfig()


def stop(webSocket, msg):
    index = int(msg.split(':')[1])
    motor = motors[index]
    motor.setTargetPosition(motor.getPosition())
    motor.disable()
    webSocket.SendText('motor:%i, stop' % index)
    saveConfig()


def closeBlinds(webSocket, msg):
    index = int(msg.split(':')[1])
    motor = motors[index]
    motor.setTargetPosition(motor.getLimit())
    webSocket.SendText('motor: %i, close, limit: %i ' %
                       (index, motor.getLimit()))
    saveConfig()


def openBlinds(webSocket, msg):
    index = int(msg.split(':')[1])
    motor = motors[index]
    motor.setTargetPosition(0)
    webSocket.SendText('motor: %i, open, bottom limit: %i ' %
                       (index, 0))
    saveConfig()


def setTopPosition(webSocket, msg):
    password = msg.split(':')[2]
    if password == USER_PASSWORD:
        index = int(msg.split(':')[1])
        motor = motors[index]
        motor.setTopPosition()
        webSocket.SendText('setTopPosition:motor:%i:position:%i' %
                           (index, motor.getPosition()))
        saveConfig()


def setLimit(webSocket, msg):
    password = msg.split(':')[2]
    if password == USER_PASSWORD:
        index = int(msg.split(':')[1])
        motor = motors[index]
        motor.setLimit(motor.getTargetPosition())
        webSocket.SendText('setLimit:motor:%i:position:%i' %
                           (index, motor.getPosition()))
        saveConfig()


def setIgnoreLimits(webSocket, msg):
    password = msg.split(':')[2]
    if password == USER_PASSWORD:
        ignoreLimits = True if msg.split(':')[1] == '1' else False
        for m in motors:
            m.setIgnoreLimits(ignoreLimits)
        webSocket.SendText('setIgnoreLimits:%i' % ignoreLimits)


# web server part from here


def _acceptWebSocketCallback(webSocket, httpClient):
    print('WS ACCEPT')
    webSocket.RecvTextCallback = _recvTextCallback
    webSocket.RecvBinaryCallback = _recvBinaryCallback
    webSocket.ClosedCallback = _closedCallback

    timState.init(period=1000, mode=machine.Timer.PERIODIC,
                  callback=lambda t: sendMotorsPosition(webSocket))


def _recvTextCallback(webSocket, msg):
    if 'up' in msg:
        goUp(webSocket, msg)
    elif 'down' in msg:
        goDown(webSocket, msg)
    elif 'stop' in msg:
        stop(webSocket, msg)
    elif 'close' in msg:
        closeBlinds(webSocket, msg)
    elif 'open' in msg:
        openBlinds(webSocket, msg)
    elif 'setTopPosition' in msg:
        setTopPosition(webSocket, msg)
    elif 'setLimit' in msg:
        setLimit(webSocket, msg)
    elif 'getBlindsPosition' in msg:
        sendMotorsPosition(webSocket)
    elif 'setIgnoreLimits' in msg:
        setIgnoreLimits(webSocket, msg)


def _recvBinaryCallback(webSocket, data):
    print('WS RECV DATA : %s' % data)


def _closedCallback(webSocket):
    print('WS CLOSED')
    timState.deinit()

# ----------------------------------------------------------------------------

# routeHandlers = [
#    ( '/open-balcony',	'GET', motors[0].setTargetPosition(0)),
#	( '/open-window',	'GET',	motors[0].setTargetPosition(0) ),
#	( '/open',	'GET',	motors[0].setTargetPosition(0) ),
#	( '/close-balcony',	'GET',	motors[0].setTargetPosition(0) ),
#	( '/close-window',	'GET',	motors[0].setTargetPosition(0) ),
#	( '/close',	'GET',	motors[0].setTargetPosition(0) )
# ]


srv = MicroWebSrv(webPath='www/')
srv.MaxWebSocketRecvLen = 256
srv.WebSocketThreaded = True
srv.AcceptWebSocketCallback = _acceptWebSocketCallback
srv.Start(threaded=True)
print('server started')

# ----------------------------------------------------------------------------
