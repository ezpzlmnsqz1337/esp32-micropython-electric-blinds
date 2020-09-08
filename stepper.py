import machine
import time


class MyStepper:
    def __init__(self, pin0, pin1, pin2, pin3, speed):
        self.pin0 = machine.Pin(pin0, machine.Pin.OUT)
        self.pin1 = machine.Pin(pin1, machine.Pin.OUT)
        self.pin2 = machine.Pin(pin2, machine.Pin.OUT)
        self.pin3 = machine.Pin(pin3, machine.Pin.OUT)

        self.position = 0
        self.target = 0

        self.speed = speed
        self.topLimit = 0
        self.bottomLimit = 0
        # 5 18 19 21

    def setPosition(self, newPosition):
        self.position = newPosition

    def getPosition(self):
        return self.position

    def setTopLimit(self, newLimit):
        self.topLimit = newLimit

    def getTopLimit(self):
        return self.topLimit

    def setBottomLimit(self, newLimit):
        self.bottomLimit = newLimit

    def getBottomLimit(self):
        return self.bottomLimit

    def setTargetPosition(self, targetPosition):
        self.target = targetPosition

    def getTargetPosition(self):
        return self.target

    def move(self):
        if self.position == self.target or self.position <= self.topLimit or self.position >= self.bottomLimit:
            self.disable()
        if self.position < self.target:
            self.rotateCW(1)
        elif self.position > self.target:
            self.rotateCCW(1)

    def disable(self):
        self.pin0.value(0)
        self.pin1.value(0)
        self.pin2.value(0)
        self.pin3.value(0)

    def rotateCW(self, steps):
        totalSteps = 0
        while totalSteps < steps:
            self.rotateCWStep()
            totalSteps += 8
        self.position += 1

    def rotateCCW(self, steps):
        totalSteps = 0
        while totalSteps < steps:
            self.rotateCCWStep()
            totalSteps += 8
        self.position -= 1

    def rotateCWAngle(self, angle):
        for i in range(angle * 64 / 45):
            self.rotateCWStep()

    def rotateCCWAngle(self, angle):
        for i in range(angle * 64 / 45):
            self.rotateCCWStep()

    def loop(self):
        for i in range(360 * 64 / 45):
            self.rotateCWStep()
        # pauza po dobu 1 sekundy
        time.sleep(1)

        for i in range(360 * 64 / 45):
            self.rotateCCWStep()

        # pauza po dobu 1 sekundy
        time.sleep(1)

    def rotateCWStep(self):
        self.step1()
        self.step2()
        self.step3()
        self.step4()
        self.step5()
        self.step6()
        self.step7()
        self.step8()

    def rotateCCWStep(self):
        self.step8()
        self.step7()
        self.step6()
        self.step5()
        self.step4()
        self.step3()
        self.step2()
        self.step1()

    def step1(self):
        self.pin0.value(1)
        self.pin1.value(0)
        self.pin2.value(0)
        self.pin3.value(0)
        time.sleep(self.speed)

    def step2(self):
        self.pin0.value(1)
        self.pin1.value(1)
        self.pin2.value(0)
        self.pin3.value(0)
        time.sleep(self.speed)

    def step3(self):
        self.pin0.value(0)
        self.pin1.value(1)
        self.pin2.value(0)
        self.pin3.value(0)
        time.sleep(self.speed)

    def step4(self):
        self.pin0.value(0)
        self.pin1.value(1)
        self.pin2.value(1)
        self.pin3.value(0)
        time.sleep(self.speed)

    def step5(self):
        self.pin0.value(0)
        self.pin1.value(0)
        self.pin2.value(1)
        self.pin3.value(0)
        time.sleep(self.speed)

    def step6(self):
        self.pin0.value(0)
        self.pin1.value(0)
        self.pin2.value(1)
        self.pin3.value(1)
        time.sleep(self.speed)

    def step7(self):
        self.pin0.value(0)
        self.pin1.value(0)
        self.pin2.value(0)
        self.pin3.value(1)
        time.sleep(self.speed)

    def step8(self):
        self.pin0.value(1)
        self.pin1.value(0)
        self.pin2.value(0)
        self.pin3.value(1)
        time.sleep(self.speed)
