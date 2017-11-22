from setuptools import setup

setup(name='mapipe',
    version='1.3.0',
    packages=['mapipe', 'mapipe.tools', 'mapipe.gff_tools', 'mumapipe'],
    entry_points={
        'console_scripts': [
            'mapipe = mapipe.mapipe_lib:main',
            'mumapipe = mumapipe.mumapipe_lib:main',
            'mapipe.gff_tools.gff3_to_gtf = mapipe.gff_tools.gff3_to_gtf:main'
        ]
    },
    package_data={
        'mapipe': [
            'configs/*',
        ]
    }
    )
