#!/usr/bin/env python
# coding: utf-8

# In[ ]:


from setuptools import setup, find_packages

setup(
    name="mr",
    version="0.0.1",
    packages=find_packages(exclude=["tests.*", "tests"]),
    description="mr xApp for test",
    url="https://github.com/mrkouchaki/mr-xapp",
    install_requires=["ricxappframe>=1.1.1,<2.0.0", "pandas>=1.1.3", "joblib>=0.3.2", "Scikit-learn>=0.21", "schedule>=0.0.0", "influxdb"],
    entry_points={"console_scripts": ["run-mr.py=mr.main:start"]},  # adds a magical entrypoint for Docker
    license="Apache 2.0",
    data_files=[("", ["LICENSE.txt"])],
)

