from setuptools import find_packages, setup

package_name = 'andypan'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Andy Pan',
    maintainer_email='andypan@umich.edu',
    description='Examples of minimal publisher/subscriber using rclpy',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
        	'talker = andypan.publisher_member_function:main',
        	'listener = andypan.subscriber_member_function:main',
        ],
    },
)
