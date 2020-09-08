from microWebSrv import MicroWebSrv
import machine
import stepper

motors = [
    stepper.MyStepper(5, 18, 19, 21, 0.001),
    stepper.MyStepper(13, 12, 14, 27, 0.001)
]

timMotor0 = machine.Timer(1)
timMotor1 = machine.Timer(2)

# motors[0].loop()

motors[0].setTargetPosition(9999)
motors[1].setTargetPosition(9999)


timMotor0.init(period=10, mode=machine.Timer.PERIODIC,
               callback=lambda t: motors[0].move())
timMotor1.init(period=10, mode=machine.Timer.PERIODIC,
               callback=lambda t: motors[1].move())


def _acceptWebSocketCallback(webSocket, httpClient):
    print("WS ACCEPT")
    webSocket.RecvTextCallback = _recvTextCallback
    webSocket.RecvBinaryCallback = _recvBinaryCallback
    webSocket.ClosedCallback = _closedCallback


def _recvTextCallback(webSocket, msg):
    if 'up' in msg:
        index = int(msg.split(':')[1])
        steps = int(msg.split(':')[2])
        motor = motors[index]
        motor.setTargetPosition(motor.getPosition() + steps)
        webSocket.SendText("STEPPER ROTATING:%s steps" % steps)
    elif 'down' in msg:
        index = int(msg.split(':')[1])
        steps = int(msg.split(':')[2])
        motor = motors[index]
        motor.setTargetPosition(motor.getPosition() - steps)
        webSocket.SendText("STEPPER ROTATING:%s steps" % steps)
    elif 'stop' in msg:
        index = int(msg.split(':')[1])
        motor = motors[index]
        motor.setTargetPosition(motor.getPosition())
        motor.disable()
        webSocket.SendText("STEPPER STOP")
    elif 'open' in msg:
        index = int(msg.split(':')[1])
        motor = motors[index]
        motor.setTargetPosition(motor.getTopLimit())
        webSocket.SendText("STEPPER TO TOP LIMIT:%s topLimit" %
                           motor.getTopLimit())
    elif 'close' in msg:
        index = int(msg.split(':')[1])
        motor = motors[index]
        motor.setTargetPosition(motor.getBottomLimit())
        webSocket.SendText("STEPPER TO BOTTOM LIMIT:%s topLimit" %
                           motor.getTopLimit())


def _recvBinaryCallback(webSocket, data):
    print("WS RECV DATA : %s" % data)


def _closedCallback(webSocket):
    print("WS CLOSED")

# ----------------------------------------------------------------------------

# routeHandlers = [
#	( "/test",	"GET",	_httpHandlerTestGet ),
#	( "/test",	"POST",	_httpHandlerTestPost )
# ]


srv = MicroWebSrv(webPath='www/')
srv.MaxWebSocketRecvLen = 256
srv.WebSocketThreaded = True
srv.AcceptWebSocketCallback = _acceptWebSocketCallback
print("server start")
srv.Start(threaded=True)
print("server started")

# ----------------------------------------------------------------------------
