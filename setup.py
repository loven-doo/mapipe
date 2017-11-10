from setuptools import setup

setup(name='mapipe',
    version='1.2.1',
    packages=['mapipe', 'mapipe.tools', 'mumapipe'],
    entry_points={
        'console_scripts': [
            'mapipe = mapipe.mapipe_lib:main',
            'mumapipe = mumapipe.mumapipe_lib:main'
        ]
    },
    package_data={
        'mapipe': [
            'configs/*',
        ]
    },
    install_requires=[
        'HTSeq'
    ]
    )
