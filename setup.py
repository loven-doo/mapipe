from setuptools import setup

setup(name='mapipe_no_git',
    version='0.1.0',
    packages=['mapipe_no_git'],
    entry_points={
        'console_scripts': [
            'mapipe_no_git = mapipe_no_git.mapipe_lib:main'
        ]
    },
    package_data={
        'mapipe_no_git': [
            'configs/*'
        ]
    }
    )

setup(name='mumapipe',
    version='0.1.0',
    packages=['mumapipe'],
    entry_points={
        'console_scripts': [
            'mumapipe = mumapipe.mumapipe_lib:main'
        ]
    },
    )