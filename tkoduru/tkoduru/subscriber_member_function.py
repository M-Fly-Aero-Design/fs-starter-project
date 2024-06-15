# Copyright 2016 Open Source Robotics Foundation, Inc.
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

import rclpy
from rclpy.node import Node

from std_msgs.msg import String

MESSAGES_REQUIRED = 10 # Number of messages to be received before stopping the subscriber

class MinimalSubscriber(Node):

    def __init__(self):
        super().__init__('minimal_subscriber')

        # Listen to FLASH (Signals outputted by the publisher)
        self.subscription = self.create_subscription(
            String,
            'FLASH',
            self.listener_callback,
            10)
        self.subscription  # prevent unused variable warning
        self.current_message = 0 # Number of messages received so far

        # Transmit to THUNDER (Tell the publisher to stop transmitting messages)
        self.publisher_ = self.create_publisher(String, 'THUNDER', 10)
        timer_period = 0.5
        self.timer = self.create_timer(timer_period, self.timer_callback)
        self.i = 0

    def listener_callback(self, msg):
        if(self.current_message < MESSAGES_REQUIRED):
            self.get_logger().info('THUNDER: "%s"' % msg.data)
            self.current_message += 1

    def timer_callback(self):
        msg = String()
        msg.data = 'STOP'
        
        if(self.current_message >= MESSAGES_REQUIRED):
            self.publisher_.publish(msg)
            self.get_logger().info('SENDING "%s"' % msg.data)
            self.destroy_node()
            rclpy.shutdown()


def main(args=None):
    rclpy.init(args=args)

    minimal_subscriber = MinimalSubscriber()

    rclpy.spin(minimal_subscriber)

    # Destroy the node explicitly
    # (optional - otherwise it will be done automatically
    # when the garbage collector destroys the node object)
    minimal_subscriber.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
