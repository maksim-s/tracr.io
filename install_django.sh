#!/bin/sh
wget https://www.djangoproject.com/m/releases/1.6/Django-1.6b1.tar.gz
tar xzvf Django-1.6b1.tar.gz
cd Django-1.6b1
python setup.py install
cd ..
rm -rf Django-1.6b1 Django-1.6b1.tar.gz