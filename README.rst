.. image:: http://pascal.bazile.free.fr/paraglidingFolder/divers/GPS/OpenAir-Format/img/Paragliding-OpenAir-FrenchFiles_SiaEurocontrol.jpg
   :target: http://pascal.bazile.free.fr/paraglidingFolder/divers/GPS/OpenAir-Format/
   :alt: Paragliding OpenAir FrenchFiles


poaff - `Paragliding OpenAir French Files`_
==============

.. code::
	/!\ ATTENTION: Seules des données officielles doivent êtres utilisées pour la navigation aérienne.
	/!\ WARNING  : Only official data must be used for air navigation


Programme d'extraction et de formatage par lots ; basé sur des données issues des standards AIXM_ :code:`(Aeronautical Information Exchange Modele)` et XML_ du SIA-France_ :code:`(Service de l'Information Aéronautique)`.
Ces traitements sont nécessaires pour la génération des centaines de cartographies publiées sur le blog `Paragliding OpenAir French Files`_.
Les données sources utilisés pour la contruction de ce site sont majoritairement issues des sources officielles SIA-France_ et Eurocontrol_.
Vous pouvez également suivre les évolutions via la page `Paragliding OpenAir French Files (on Facebook)`_.


**Table of Contents**

.. contents::
   :backlinks: none
   :local:


Installation
------------
geojson is compatible with Python 3.6, 3.7 and 3.8. The recommended way to install is via pip_:

.. code::

	pip install -r requirements.txt



Utilisation
-----------

.. code:: python

	>>> #!/usr/bin/env python3  
	>>> $ python3 poaff.py  


Liens externes
--------------
.. [1] `Paragliding OpenAir French Files`_ - On Web
.. [2] `Paragliding OpenAir French Files (on Facebook)`_ - On Facebook
.. [3] `Carte OACI France`_ - Scan digitalisé
.. [4] SIA-France_ - Service de l'Information Aéronautique
.. [5] Eurocontrol_ - A pan-European, civil-military organisation dedicated to supporting European aviation
.. [6] AIXM_ - Aeronautical Information Exchange Modele
.. [7] XML_ - W3C Standard
.. [8] KML_ - Google Documentation
.. [9] `Openair Format`_ - Openair Documentation historique
.. [10] `Openair New Format`_ - Documentation des nouvelles évolutions du format Openair


Credits
-------
* `Pascal Bazile`_ author of this software <pascal_bazile@yahoo.fr>
* the many open source libraries, projects, and data sources used by this software (show file content of 'requirements.txt' for complete components detail)


.. _Pascal Bazile: https://github.com/BPascal-91/
.. _Paragliding OpenAir French Files: http://pascal.bazile.free.fr/paraglidingFolder/divers/GPS/OpenAir-Format/
.. _Paragliding OpenAir French Files (on Facebook): https://www.facebook.com/Paragliding-OpenAir-FrenchFiles-102040114894513/
.. _Carte OACI France: https://www.geoportail.gouv.fr/donnees/carte-oaci-vfr
.. _SIA-France: https://www.sia.aviation-civile.gouv.fr/
.. _Eurocontrol: https://www.eurocontrol.int/
.. _AIXM: http://www.aixm.aero/
.. _Openair Format: http://www.winpilot.com/UsersGuide/UserAirspace.asp
.. _Openair New Format: http://pascal.bazile.free.fr/paraglidingFolder/divers/GPS/OpenAir-Format/
.. _XML: https://www.w3.org/TR/xml/
.. _KML: https://developers.google.com/kml/documentation
.. _GeoJSON: http://geojson.org/
.. _pip: http://www.pip-installer.org

