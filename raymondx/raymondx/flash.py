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

"""FLASH: transmits random numbers until THUNDER tells it to stop."""

import random

import rclpy
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node

from std_msgs.msg import Int32, String

STOP_SIGNAL = 'STOP'
DEFAULT_PERIOD = 0.5


class Flash(Node):
    """Publishes a random number on 'numbers' until a STOP arrives on 'control'."""

    def __init__(self, period=DEFAULT_PERIOD):
        super().__init__('flash')
        self.transmitting = True
        self.sent = 0
        self.publisher_ = self.create_publisher(Int32, 'numbers', 10)
        self.control_sub = self.create_subscription(
            String, 'control', self.control_callback, 10)
        self.timer = self.create_timer(period, self.timer_callback)

    def timer_callback(self):
        if not self.transmitting:
            return
        msg = Int32()
        msg.data = random.randint(0, 100)
        self.publisher_.publish(msg)
        self.sent += 1
        self.get_logger().info('FLASH transmitting: %d' % msg.data)

    def control_callback(self, msg):
        # Ignore anything that is not a STOP, and ignore repeat STOPs.
        if msg.data != STOP_SIGNAL or not self.transmitting:
            return
        self.transmitting = False
        self.timer.cancel()
        self.get_logger().info('FLASH received STOP from THUNDER')
        self.get_logger().info(
            'FLASH going dark after %d numbers -- communication ended.' % self.sent)


def main(args=None):
    rclpy.init(args=args)
    flash = Flash()
    try:
        rclpy.spin(flash)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        flash.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
