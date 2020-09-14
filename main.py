from microWebSrv import MicroWebSrv
import machine
import stepper

USER_PASSWORD = ''
with open('welcome.txt', 'r') as f:
    USER_PASSWORD = f.readline()

motors = (
    stepper.MyStepper(5, 18, 19, 21),
    stepper.MyStepper(13, 12, 14, 27)
)

timMotor = machine.Timer(1)

# motors[0].loop()


def moveMotors():
    for m in motors:
        m.move()


motors[1].invertDirection(True)


timMotor.init(period=1, mode=machine.Timer.PERIODIC,
              callback=lambda t: moveMotors())


def _acceptWebSocketCallback(webSocket, httpClient):
    print('WS ACCEPT')
    webSocket.RecvTextCallback = _recvTextCallback
    webSocket.RecvBinaryCallback = _recvBinaryCallback
    webSocket.ClosedCallback = _closedCallback


def _recvTextCallback(webSocket, msg):
    if 'up' in msg:
        index = int(msg.split(':')[1])
        steps = int(msg.split(':')[2])
        motor = motors[index]
        motor.setTargetPosition(motor.getPosition() + steps)
        webSocket.SendText('motor:%i:goto:%s ' %
                           (index, motor.getPosition() + steps))
    elif 'down' in msg:
        index = int(msg.split(':')[1])
        steps = int(msg.split(':')[2])
        motor = motors[index]
        motor.setTargetPosition(motor.getPosition() - steps)
        webSocket.SendText('motor:%i:go to: %i' %
                           (index, motor.getPosition() - steps))
    elif 'stop' in msg:
        index = int(msg.split(':')[1])
        motor = motors[index]
        motor.setTargetPosition(motor.getPosition())
        motor.disable()
        webSocket.SendText('motor:%i, stop' % index)
    elif 'close' in msg:
        index = int(msg.split(':')[1])
        motor = motors[index]
        motor.setTargetPosition(motor.getLimit())
        webSocket.SendText('motor: %i, close, limit: %i ' %
                           (index, motor.getLimit()))
    elif 'open' in msg:
        index = int(msg.split(':')[1])
        motor = motors[index]
        motor.setTargetPosition(0)
        webSocket.SendText('motor: %i, open, bottom limit: %i ' %
                           (index, 0))
    elif 'setTopPosition' in msg:
        password = msg.split(':')[2]
        if password == USER_PASSWORD:
            index = int(msg.split(':')[1])
            motor = motors[index]
            motor.setTopPosition()
            webSocket.SendText('setTopPosition:motor:%i:position:%i' %
                               (index, motor.getPosition()))
    elif 'setLimit' in msg:
        password = msg.split(':')[2]
        if password == USER_PASSWORD:
            index = int(msg.split(':')[1])
            motor = motors[index]
            motor.setLimit()
            webSocket.SendText('setLimit:motor:%i:position:%i' %
                               (index, motor.getPosition()))
    elif 'getBlindsPosition' in msg:
        webSocket.SendText('blindsPosition:motor:%i:position:%i' %
                           (0, motors[0].getPosition()))
        webSocket.SendText('blindsPosition:motor:%i:position:%i' %
                           (1, motors[1].getPosition()))


def _recvBinaryCallback(webSocket, data):
    print('WS RECV DATA : %s' % data)


def _closedCallback(webSocket):
    print('WS CLOSED')

# ----------------------------------------------------------------------------

# routeHandlers = [
#	( '/test',	'GET',	_httpHandlerTestGet ),
#	( '/test',	'POST',	_httpHandlerTestPost )
# ]


srv = MicroWebSrv(webPath='www/')
srv.MaxWebSocketRecvLen = 256
srv.WebSocketThreaded = True
srv.AcceptWebSocketCallback = _acceptWebSocketCallback
print('server start')
srv.Start(threaded=True)
print('server started')

# ----------------------------------------------------------------------------
