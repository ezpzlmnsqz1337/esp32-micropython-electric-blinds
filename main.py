import machine
import stepper
import adafruit

# handle password for configuration over web page/adafruit feed
USER_PASSWORD = ''

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

timCheck = machine.Timer(0)
timMotor = machine.Timer(1)


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


def startMotors():
    timMotor.deinit()
    timMotor.init(period=1, mode=machine.Timer.PERIODIC,
                  callback=lambda t: moveMotors())

# adafruit.io part


def adafruitCb(topic, msg):
    print('ADA CB ' + str(msg))
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
    elif 'OPEN' in msg:
        openBlinds()
    elif 'CLOSE' in msg:
        closeBlinds()
    elif 'setTopPosition' in msg:
        setTopPosition(msg)
    elif 'setLimit' in msg:
        setLimit(msg)
    elif 'getBlindsPosition' in msg:
        sendMotorsPosition()
    elif 'setIgnoreLimits' in msg:
        setIgnoreLimits(msg)


def checkAda():
    print('Check ada')
    try:
        adafruit.check()  # check incoming messages
        # sendMotorsPosition()  # send information about blinds position
    except Exception as e:
        print('Check for feed value failed {}{}\n'.format(
            type(e).__name__, e))
        adafruit.retry()
        # machine.reset()


adafruit.subscribe(adafruitCb)
timCheck.init(period=1000, mode=machine.Timer.PERIODIC,
              callback=lambda t: checkAda())

# blinds operations callbacks


def sendMotorsPosition():
    for i, m in enumerate(motors):
        ignore = 1 if m.getIgnoreLimits() == True else 0
        adafruit.publish('blindsPosition:motor:%i:position:%i:target:%i:limit:%i:ignoreLimit:%i' %
                         (i, m.getPosition(), m.getTargetPosition(), m.getLimit(), ignore))


def goUp(msg):
    index = int(msg.split(':')[1])
    steps = int(msg.split(':')[2])
    motor = motors[index]
    motor.setTargetPosition(motor.getTargetPosition() - steps)
    adafruit.publish('motor:%i:goto:%s ' %
                     (index, motor.getTargetPosition() - steps))
    saveConfig()
    startMotors()


def goDown(msg):
    index = int(msg.split(':')[1])
    steps = int(msg.split(':')[2])
    motor = motors[index]
    motor.setTargetPosition(motor.getTargetPosition() + steps)
    adafruit.publish('motor:%i:go to: %i' %
                     (index, motor.getTargetPosition() + steps))
    saveConfig()
    startMotors()


def stop(msg):
    index = int(msg.split(':')[1])
    motor = motors[index]
    motor.setTargetPosition(motor.getPosition())
    motor.disable()
    adafruit.publish('motor:%i, stop' % index)
    saveConfig()
    startMotors()


def closeBlind(msg):
    index = int(msg.split(':')[1])
    motor = motors[index]
    motor.setTargetPosition(motor.getLimit())
    adafruit.publish('motor: %i, close, limit: %i ' %
                     (index, motor.getLimit()))
    saveConfig()
    startMotors()


def openBlind(msg):
    index = int(msg.split(':')[1])
    motor = motors[index]
    motor.setTargetPosition(0)
    adafruit.publish('motor: %i, open, bottom limit: %i ' %
                     (index, 0))
    saveConfig()
    startMotors()


def openBlinds():
    for m in motors:
        m.setTargetPosition(0)
        adafruit.publish('motors: open')
    saveConfig()
    startMotors()


def closeBlinds():
    for m in motors:
        m.setTargetPosition(m.getLimit())
    adafruit.publish('motors: close')
    saveConfig()
    startMotors()


def setTopPosition(msg):
    password = msg.split(':')[2]
    if password == USER_PASSWORD:
        index = int(msg.split(':')[1])
        motor = motors[index]
        motor.setTopPosition()
        adafruit.publish('setTopPosition:motor:%i:position:%i' %
                         (index, motor.getPosition()))
        saveConfig()


def setLimit(msg):
    password = msg.split(':')[2]
    if password == USER_PASSWORD:
        index = int(msg.split(':')[1])
        motor = motors[index]
        motor.setLimit(motor.getTargetPosition())
        adafruit.publish('setLimit:motor:%i:position:%i' %
                         (index, motor.getPosition()))
        saveConfig()


def setIgnoreLimits(msg):
    password = msg.split(':')[2]
    if password == USER_PASSWORD:
        ignoreLimits = True if msg.split(':')[1] == '1' else False
        for m in motors:
            m.setIgnoreLimits(ignoreLimits)
        adafruit.publish('setIgnoreLimits:%i' % ignoreLimits)
