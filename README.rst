===========
missingdata
===========


.. image:: https://img.shields.io/pypi/v/missingdata.svg
        :target: https://pypi.python.org/pypi/missingdata

.. image:: https://img.shields.io/travis/raamana/missingdata.svg
        :target: https://travis-ci.org/raamana/missingdata

.. image:: https://readthedocs.org/projects/missingdata/badge/?version=latest
        :target: https://missingdata.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status


missing data visualization and imputation

Goals
--------

Povide an easy to use yet thorough assessment of missing values in one's dataset:

 - in addition to the blackholes plot bellow, 
 - show the variable-to-variable, subject-to-subject co-missingness, and 
 - quantify the TYPE of missingness etc 


Note
~~~~~~~~~~~~~

    To easily manage your data with missing values etc, I strongly recommend you to move away from CSV files and start managing your data in self-contained flexible data structures like `pyradigm <http://github.com/raamana/pyradigm>`_, as your data, as well your needs, will only get bigger & more complicated e.g. with mixed-types, missing values and large number of groups.


These would be great contributions if you have time.


Features
--------

* visualization
* imputation (coming!)
* other handling


blackholes plot
~~~~~~~~~~~~~~~~

.. image:: docs/flyer.png


State
-------
 - Software is beta and under dev
 - Contributions most welcome.


Installation
--------------

.. code-block:: bash

    pip install -U missingdata

