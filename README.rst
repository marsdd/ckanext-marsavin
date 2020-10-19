================
ckanext-marsavin
================

.. Extension supports all the required modifications for Avin data hub
   project.  It is supported by MaRS Discovery District IT.

------------
To Do:
------------
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

2. Install the ckanext-marsavin and ckanext-multilang Python packages into your virtual environment::

     pip install /path/to/project/ckanext-marsavin
     pip install /path/to/project/ckanext-multilang

3. Add ``marsavin`` to the ``ckan.plugins`` setting in your CKAN
   config file (by default the config file is located at
   ``/path/to/config.ini``).

4. initialize database::

      ckan db init --config=/path/to/config.ini
      ckan db upgrade --plugin marsavin
      ckan db upgrade --plugin multilang

6. make sure to update Solr search schema::

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