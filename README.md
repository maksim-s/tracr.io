project-papasan
===============

You need to setup virtualenv for each fresh checkout of this repository. You 
can setup virtualenv by running the following command in the project root directory:

```
virtualenv .
```

All required system packages are listed in packages.txt and can be installed 
by running the following command:

```
sudo HOME=/tmp/ apt-get install -y $(cat packages.txt)
```

Activate virtualenv, before we install anything project specific:
```
source bin/activate
```

All required Python packages are listed in requirements.txt and can be 
installed by running the following command:

```
pip install -r requirements.txt
```
