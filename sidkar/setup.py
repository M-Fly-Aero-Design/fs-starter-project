from setuptools import find_packages, setup

package_name = 'sidkar'

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
    maintainer='sidkar',
    maintainer_email='sidkar@umich.edu',
    description='Mfly',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'talker = sidkar.publisher_member_function:main',
            'listener = sidkar.subscriber_member_function:main',
        ],
    },
)
