# Copyright 2025 Raymond Xu
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Integration tests for the FLASH transmitter and THUNDER receiver."""

import time

import pytest

import rclpy
from rclpy.executors import SingleThreadedExecutor
from rclpy.node import Node

from std_msgs.msg import Int32, String

from raymondx.flash import Flash
from raymondx.thunder import STOP_SIGNAL, Thunder

# Fast enough that the whole exchange finishes in well under a second.
TEST_PERIOD = 0.02


class Spy(Node):
    """Passive observer that counts what actually reaches the two topics."""

    def __init__(self):
        super().__init__('spy')
        self.numbers_seen = 0
        self.stop_msgs = 0
        self.numbers_at_stop = None
        self.create_subscription(Int32, 'numbers', self.on_number, 10)
        self.create_subscription(String, 'control', self.on_control, 10)

    def on_number(self, msg):
        self.numbers_seen += 1

    def on_control(self, msg):
        if msg.data == STOP_SIGNAL:
            self.stop_msgs += 1
            self.numbers_at_stop = self.numbers_seen


def spin_until(executor, predicate, timeout):
    """Spin the executor until predicate() is true or timeout elapses."""
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline and not predicate():
        executor.spin_once(timeout_sec=0.01)
    return predicate()


def spin_for(executor, duration):
    """Spin the executor for a fixed wall-clock duration."""
    deadline = time.monotonic() + duration
    while time.monotonic() < deadline:
        executor.spin_once(timeout_sec=0.01)


@pytest.fixture
def system():
    """Bring up FLASH, THUNDER and a Spy on one executor, then tear them down."""
    rclpy.init()
    flash = Flash(period=TEST_PERIOD)
    thunder = Thunder()
    spy = Spy()
    executor = SingleThreadedExecutor()
    for node in (flash, thunder, spy):
        executor.add_node(node)
    try:
        yield executor, flash, thunder, spy
    finally:
        for node in (flash, thunder, spy):
            node.destroy_node()
        rclpy.shutdown()


def test_thunder_sends_stop_after_exactly_ten_numbers(system):
    executor, flash, thunder, spy = system

    assert spin_until(executor, lambda: spy.stop_msgs > 0, timeout=10.0), \
        'THUNDER never sent a STOP signal'

    assert thunder.count == 10, \
        'THUNDER should send STOP on its 10th number, not its %dth' % thunder.count
    assert spy.numbers_at_stop >= 10, \
        'STOP was sent before 10 numbers were on the wire'


def test_thunder_sends_stop_only_once(system):
    executor, flash, thunder, spy = system

    assert spin_until(executor, lambda: spy.stop_msgs > 0, timeout=10.0)
    spin_for(executor, 0.5)

    assert spy.stop_msgs == 1, \
        'THUNDER sent %d STOP signals, expected exactly 1' % spy.stop_msgs


def test_flash_stops_transmitting_after_stop(system):
    executor, flash, thunder, spy = system

    assert spin_until(executor, lambda: not flash.transmitting, timeout=10.0), \
        'FLASH never stopped transmitting'

    settled = spy.numbers_seen
    # 0.5s is 25 timer periods -- if FLASH were still running we would see them.
    spin_for(executor, 0.5)

    assert spy.numbers_seen == settled, \
        'FLASH published %d more numbers after STOP' % (spy.numbers_seen - settled)


def test_thunder_ignores_nothing_before_ten(system):
    executor, flash, thunder, spy = system

    assert spin_until(executor, lambda: thunder.count >= 5, timeout=10.0)

    assert spy.stop_msgs == 0, \
        'THUNDER sent STOP after only %d numbers' % thunder.count
