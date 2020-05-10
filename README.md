TempHumi
========

TempHumi is a simple service for collecting temperature and humidity
data from Seeed Sensors, and for presenting the collected measurements
via a web interface.

Automatic tests
===============

Running test.py will execute all the tests.

Development
==================================

To run in a development environment, execute:
```
./run_dev.sh

# or
pip3 install -e .

export FLASK_APP=temphumi
export FLASK_ENV=production
# just once
FLASK_APP=temphumi flask init-db

# every time
FLASK_APP=temphumi flask run

```

Code must be lint'ed before submission. To do that, execute
the following command line:
```
find . -name '*.py' | xargs pylint3
```

You can also configure git pre-commit script by running:
```
ln -sf ../../pre-commit .git/hook/pre-commit
```


Production deployment
=====================

TempHumi comes with a systemd configuration files that can serve as
a template. Real production deployments should use a real WSGI server
capable of serving several requests in parallel.

```
python3 setup.py sdist bdist_wheel
sudo pip3 install dist/temphumi-1.0.0.tar.gz
```

Once the package is installed, you can run it using flask driver.
However, it is easier to run the temphumi application using uwsgi.
Use the provided `conf/uwsgi/temphumi.ini` file.
```
sudo cp conf/uwsgi/temphumi.ini /etc/uwsgi/apps-available
sudo ln -s /etc/uwsgi/apps-available/temphumi.ini /etc/uwsgi/apps-enabled
```
