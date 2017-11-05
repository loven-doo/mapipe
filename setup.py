from setuptools import setup

setup(name='mapipe',
    version='0.3.0',
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

#setup(name='mumapipe',
#    version='0.3.0',
#    packages=['mumapipe'],
#    entry_points={
#        'console_scripts': [
#            'mumapipe = mumapipe.mumapipe_lib:main'
#        ]
#    },
#    )
