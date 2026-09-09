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

"""THUNDER: prints numbers from FLASH and stops it after ten of them."""

import rclpy
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node

from std_msgs.msg import Int32, String

STOP_SIGNAL = 'STOP'
MESSAGE_LIMIT = 10


class Thunder(Node):
    """Listens on 'numbers' and publishes STOP on 'control' at the limit."""

    def __init__(self, limit=MESSAGE_LIMIT):
        super().__init__('thunder')
        self.limit = limit
        self.count = 0
        self.stop_sent = False
        self.stop_sent_at = None
        self.publisher_ = self.create_publisher(String, 'control', 10)
        self.number_sub = self.create_subscription(
            Int32, 'numbers', self.number_callback, 10)

    def number_callback(self, msg):
        if self.stop_sent:
            return
        self.count += 1
        self.get_logger().info(
            'THUNDER received: %d (%d/%d)' % (msg.data, self.count, self.limit))
        if self.count >= self.limit:
            self.send_stop()

    def send_stop(self):
        self.stop_sent = True
        self.stop_sent_at = self.count
        msg = String()
        msg.data = STOP_SIGNAL
        self.publisher_.publish(msg)
        self.get_logger().info('THUNDER sent STOP after %d numbers' % self.count)
        self.get_logger().info('THUNDER signing off -- communication ended.')


def main(args=None):
    rclpy.init(args=args)
    thunder = Thunder()
    try:
        rclpy.spin(thunder)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        thunder.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
