'''
ubutton.py, A MicroPython library for controlling PWM outputs

Copyright (C) 2019, Sean Lanigan

uButton is free software: you can redistribute it and/or modify it under the
terms of the GNU Lesser General Public License as published by the Free
Software Foundation, either version 3 of the License, or (at your option) any
later version.

uButton is distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more
details.

You should have received a copy of the GNU Lesser General Public License along
with uButton.  If not, see <https://www.gnu.org/licenses/>.
'''
from machine import Pin, Timer
from time import ticks_ms
from micropython import const
import uasyncio as asyncio

delay = const(5)


class uButton(object):
    __slots__ = (
        '_pin', '_cb_sh', '_cb_ln', '_run_sh', '_run_ln', '_time_sh',
        '_time_ln', '_bounce', '_long', '_trg_val', '_cb_sh_wait')

    def __init__(self, pin, cb_short=None, short_wait=True, cb_long=None, bounce_time=25, long_time=500, act_low=True):
        if not isinstance(pin, Pin):
            raise TypeError("'pin' must be an instance of 'machine.Pin'")
        self._pin = pin
        if cb_short:
            if not callable(cb_short):
                raise TypeError("'cb_short' must be a callable")
            self._cb_sh = cb_short
        else:
            self._cb_sh = lambda *a, **k: None  # no-op
        if not isinstance(short_wait, bool):
            raise TypeError("'short_wait' must be a bool")
        self._cb_sh_wait = short_wait
        if cb_long:
            if not callable(cb_long):
                raise TypeError("'cb_long' must be a callable")
            self._cb_ln = cb_long
        else:
            self._cb_ln = lambda *a, **k: None  # no-op
        if not isinstance(bounce_time, int):
            raise TypeError("'bounce_time' must be an int")
        self._bounce = bounce_time
        if not isinstance(long_time, int):
            raise TypeError("'long_time' must be an int")
        self._long = long_time
        if not isinstance(act_low, bool):
            raise TypeError("'act_low' must be a bool")
        if act_low:
            self._trg_val = 0
            self._pin.irq(self._cb_press, Pin.IRQ_FALLING)
        else:
            self._trg_val = 1
            self._pin.irq(self._cb_press, Pin.IRQ_RISING)

        self._time_sh = 0
        self._time_ln = 0
        self._run_sh = False
        self._run_ln = False

    @property
    def callback_short(self):
        return self._cb_sh

    @callback_short.setter
    def callback_short(self, cb):
        if not callable(cb):
            raise TypeError("'cb' must be callable")
        self._cb_sh = cb

    @property
    def callback_long(self):
        return self._cb_ln

    @callback_long.setter
    def callback_long(self, cb):
        if not callable(cb):
            raise TypeError("'cb' must be callable")
        self._cb_ln = cb

    def _cb_press(self, pin):
        if self._pin.value() == self._trg_val:
            now = ticks_ms()
            self._time_sh = now + self._bounce
            self._run_sh = True
            self._time_ln = now + self._long
            self._run_ln = True

    async def run(self):
        # We store trg_val in a local variable, so it doesn't need to be
        # referenced each run through the loop - but this means that it
        # cannot be changed after the asyncio loop has started
        trg_val = self._trg_val
        sh_wait = self._cb_sh_wait
        trg_delay = False
        while True:
            run_sh = self._run_sh
            run_ln = self._run_ln
            if run_sh or run_ln:
                now = ticks_ms()
                val = self._pin.value()
            # If using delayed short trigger, check if a short press is pending
            if sh_wait:
                if trg_delay:
                    # If a short press is pending, check if the button value
                    # has returned to normal, i.e. if the button is released
                    if val != trg_val:
                        self._cb_sh()
                        trg_delay = False
            if run_sh:
                if now > self._time_sh:
                    self._run_sh = False
                    if val == trg_val:
                        # If using the delayed short trigger, flag that a short
                        # press is pending - otherwise run callback immediately
                        if sh_wait:
                            trg_delay = True
                        else:
                            self._cb_sh()
            if run_ln:
                if now > self._time_ln:
                    self._run_ln = False
                    if val == trg_val:
                        self._cb_ln()
                        # Since a long press has just been triggered, cancel
                        # any pending short press
                        trg_delay = False

            await asyncio.sleep_ms(delay)