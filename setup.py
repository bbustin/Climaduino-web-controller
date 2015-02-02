import os
from setuptools import setup, find_packages

requires = [
    'python-rrdtool',
    'paho-mqtt',
    'django',
    ]

setup(
    name='climaduino-web-controller',
    version='0.1',
    description='Web Controller for Climaduino climate control system',
    packages=find_packages(),
    install_requires=requires,
    tests_require=requires,
    zip_safe=False,
    # long_description=README,
    url='http://www.instructables.com/id/Introducing-Climaduino-The-Arduino-Based-Thermosta/?ALLSTEPS',
    author='Brian Bustin',
    # author_email='yourname@example.com',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License', # example license
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        # Replace these appropriately if you are stuck on Python 2.
        # 'Programming Language :: Python :: 3',
        # 'Programming Language :: Python :: 3.2',
        # 'Programming Language :: Python :: 3.3',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
)