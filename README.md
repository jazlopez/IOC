# IOC

Install virtualenv 

```
$virtualenv venv

New python executable in /Users/jaziel/PycharmProjects/IOC/venv/bin/python
Installing setuptools, pip, wheel...done.
```

Activate virtualenv

```
$source venv/bin/activate
```

Install project dependencies

```
pip install -r requirements.txt 
Collecting attrs==15.2.0 (from -r requirements.txt (line 1))
  Downloading attrs-15.2.0-py2.py3-none-any.whl
Collecting beautifulsoup4==4.4.1 (from -r requirements.txt (line 2))
  Downloading beautifulsoup4-4.4.1-py2-none-any.whl (81kB)
    100% |████████████████████████████████| 81kB 884kB/s 
Collecting cffi==1.6.0 (from -r requirements.txt (line 3))
  Downloading cffi-1.6.0-cp27-cp27m-macosx_10_10_intel.whl (211kB)
    100% |████████████████████████████████| 215kB 1.1MB/s 
...
```