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
        self.limit = 0
        self.invertDir = False
        # 5 18 19 21

    def invertDirection(self, invert):
        self.invertDir = invert

    def setPosition(self, newPosition):
        self.position = newPosition

    def getPosition(self):
        return self.position

    def setLimit(self):
        self.limit = self.position

    def getLimit(self):
        return self.limit

    def setTopPosition(self):
        self.position = 0
        self.target = 0

    def setTargetPosition(self, targetPosition):
        self.target = targetPosition

    def getTargetPosition(self):
        return self.target

    def move(self):
        if self.position == self.target or self.position <= self.limit or self.position >= self.limit:
            self.disable()
        if self.position < self.target:
            if self.invertDir:
                self.rotateCCW(1)
            else:
                self.rotateCW(1)
        elif self.position > self.target:
            if self.invertDir:
                self.rotateCW(1)
            else:
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
            totalSteps += 1
        self.position += steps * -1 if self.invertDir else steps

    def rotateCCW(self, steps):
        totalSteps = 0
        while totalSteps < steps:
            self.rotateCCWStep()
            totalSteps += 1
        self.position -= steps * -1 if self.invertDir else steps

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
