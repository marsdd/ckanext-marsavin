================
ckanext-marsavin
================

.. Extension supports all the required modifications for Avin data hub
   project.  It is supported by MaRS Discovery District IT.

------------
To Do:
------------
#. Figure out how to manage the ini file for dev / production (low priority)

-------------
CKAN Version:
-------------

Current version is 2.9.0

--------------------------
Difference with upstream:
--------------------------

There are some changes that makes our repo separate from upstream.  I've moved 90% + changes to the plugin
or the ckan-docker repo, but there are some changes that still require our own version, mostly
because of the bugs that exist that isn't fixed in upstream yet.

I have submitted them and they must ultimately be tracked, but until they are resolved and 2.9.1 releases,
we don't have the lastest code base



------------
Installation
------------

.. Add any additional install steps to the list below.
   For example installing any non-Python dependencies or adding any required
   config settings.  Please make sure virutalenv module is installed on your python install.

To install ckanext-marsavin (local environment):

First set up the environment, docker is probably your best bet in getting things going quickly, so scroll down to the
[docker install](#installation-docker) section to get that going.

1. Clone the repository::

   git git@github.com:marsdd/ckan.git /path/to/ckan

2. Create Virtual environment::

   virtualenv --python /path/to/python /path/to/ckan/venv

3. Activate your CKAN virtual environment, for example::

     . /path/to/ckan/venv/bin/activate

4. Install the ckanext-marsavin and ckanext-multilang Python packages into your virtual environment::

     pip install /path/to/project/ckanext-marsavin
     pip install /path/to/project/ckanext-multilang

5. Add ``marsavin`` to the ``ckan.plugins`` setting in your CKAN
   config file (by default the config file is located at
   ``/path/to/config.ini``).

6. initialize database::

      ckan db init --config=/path/to/config.ini
      ckan db upgrade --plugin marsavin
      ckan db upgrade --plugin multilang

8. make sure to update Solr search schema::

      cd /usr/lib/ckan/venv/src/ckan && ckan-paster --plugin=ckanext-marsavin package update_search_schema -c "${CKAN_CONFIG}/production.ini"
      ckan --config=/path/to/config.ini marsavin update_package_search_schema
      ckan --config=/path/to/config.ini marsavin initsearch

7. rebuild the search index::

   ckan --config=/path/to/config.ini search-index rebuild

8. Restart CKAN::

   sh /path/to/ckan/contrib/docker/ckan-entrypoint.sh

---------------------
Installation (docker)
---------------------

See https://github.com/marsdd/ckan-docker for instructions on how to do docker installs.


-----------------------
Command line reference
-----------------------

* Manage user: https://docs.ckan.org/en/2.9/maintaining/cli.html#user-create-and-manage-users
* Sysadmin user admin: https://docs.ckan.org/en/2.9/maintaining/cli.html#sysadmin-give-sysadmin-rights