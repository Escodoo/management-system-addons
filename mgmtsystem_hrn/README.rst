=======================
Management System - HRN
=======================

.. 
   !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
   !! This file is generated by oca-gen-addon-readme !!
   !! changes will be overwritten.                   !!
   !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
   !! source digest: sha256:f0dcddbda0714df641adbfb931a08754eaffefd24037e4da599eef9dca548965
   !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

.. |badge1| image:: https://img.shields.io/badge/maturity-Beta-yellow.png
    :target: https://odoo-community.org/page/development-status
    :alt: Beta
.. |badge2| image:: https://img.shields.io/badge/licence-AGPL--3-blue.png
    :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
    :alt: License: AGPL-3
.. |badge3| image:: https://img.shields.io/badge/github-Escodoo%2Fmanagement--system--addons-lightgray.png?logo=github
    :target: https://github.com/Escodoo/management-system-addons/tree//mgmtsystem_hrn
    :alt: Escodoo/management-system-addons

|badge1| |badge2| |badge3|

This module implements the change of integer values to float and a new risk formula characterized by People (Qty People). This is a module inherited from Hazard Risk.

**Table of contents**

.. contents::
   :local:

Configuration
=============

To configure the risk calculation module:

* Go to Settings > Management System.
* In the Risk Computation group, select the risk calculation formula.
* Within the formula, include the new field as "D".

To configure the Equipment Safety Category, follow these steps:

* Go to Maintenance -> Configuration -> Equipment Safety Categories.
* Create a record to be used as an installed or security-required category

Usage
=====

To use the risk formula, follow these steps:

* Navigate to Management Systems > Manuals > Risks -> People.
* Create a new record to specify the risk factor associated with the number of people.

To use Safety Categories, follow these steps:

* Go to Maintenance -> Configuration -> Equipment Safety Categories.
* Create a record to be used as an installed or security-required category.
* Then, go to Maintenance -> Equipment.
* Select the equipment you wish to configure.
* Access the Safety page and define the installed and required safety categories based on the records created in the previous step.

Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/Escodoo/management-system-addons/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us to smash it by providing a detailed and welcomed
`feedback <https://github.com/Escodoo/management-system-addons/issues/new?body=module:%20mgmtsystem_hrn%0Aversion:%20%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_.

Do not contact contributors directly about support or help with technical issues.

Credits
=======

Authors
~~~~~~~

* Escodoo

Contributors
~~~~~~~~~~~~

`Escodoo <https://www.escodoo.com.br>`_:

* Marcel Savegnago <marcel.savegnago@escodoo.com.br>
* Kaynnan Lemes <kaynnan.lemes@escodoo.com.br>
* Douglas Custodio <douglas.custodio@escodoo.com.br>

Maintainers
~~~~~~~~~~~

This module is part of the `Escodoo/management-system-addons <https://github.com/Escodoo/management-system-addons/tree//mgmtsystem_hrn>`_ project on GitHub.

You are welcome to contribute.
