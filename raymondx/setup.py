from setuptools import find_packages, setup

package_name = 'raymondx'

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
    maintainer='Raymond',
    maintainer_email='raymondx@umich.edu',
    description='Two-way pub/sub: FLASH transmits until THUNDER says STOP',
    license='Apache License 2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
                'flash = raymondx.flash:main',
                'thunder = raymondx.thunder:main',
        ],
    },
)
