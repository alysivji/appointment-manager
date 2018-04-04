from setuptools import setup, find_packages

setup(
    name='appointment-manager',
    version='0.0.1',
    description='This project will expose an API that users can use to createe, delete, and modify appointments.',
    url='https://github.com/alysivji/appointment-manager',
    author='Aly Sivji',
    author_email='alysivji@gmail.com',
    classifiers=[
        'Programming Language :: Python :: 3.6',
    ],
    packages=find_packages(exclude=['tests', ]),
    install_requires=[''],
    download_url='https://github.com/alysivji/appointment-manager',
)
