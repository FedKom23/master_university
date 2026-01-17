from setuptools import setup, Extension

module = Extension('custom_json', sources=['custom_json.c'])

setup(
    name='custom_json',
    version='1.0',
    description='Custom JSON parser',
    ext_modules=[module]
)
