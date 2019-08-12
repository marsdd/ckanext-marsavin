================
ckanext-marsavin
================

.. Extension supports all the required modifications for Avin data hub
   project.  It is supported by MaRS Discovery District IT.

------------
To Do:
------------
#. Figure out how to migrate db changes required by the plugin
#. Figure out how to handle deployments without changing the general docker
   provided by upstream (low priority)
#. Figure out how to manage the ini file for dev / production (low priority)


------------
Installation
------------

.. Add any additional install steps to the list below.
   For example installing any non-Python dependencies or adding any required
   config settings.

To install ckanext-marsavin (local environment):

1. Activate your CKAN virtual environment, for example::

     . /path/to/ckan/venv/bin/activate

2. Install the ckanext-marsavin Python package into your virtual environment::

     pip install /path/to/project/ckanext-marsavin

3. Add ``marsavin`` to the ``ckan.plugins`` setting in your CKAN
   config file (by default the config file is located at
   ``/path/to/config.ini``).

4. initialize database::

      paster --plugin=ckanext-marsavin init --config=/path/to/config.ini

5. Restart CKAN
      sh /path/to/ckan/contrib/docker/ckan-entrypoint.sh

---------------------
Installation (docker)
---------------------

Add following in the docker file anywhere before the entrypoint but after
ckan installation section

ARG MARS_PLUGIN_VERSION

     ckan-pip install https://github.com/marsdd/ckanext-marsavin/archive/$MARS_PLUGIN_VERSION.zip


Then rebuild witht he build arg::

   docker build -f /path/to/ckan/Dockerfile --build-arg MARS_PLUGIN_VERSION=<name-of-branch-or-tag>

