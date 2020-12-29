.. image:: http://pascal.bazile.free.fr/paraglidingFolder/divers/GPS/OpenAir-Format/img/Paragliding-OpenAir-FrenchFiles_SiaEurocontrol.jpg
   :target: http://pascal.bazile.free.fr/paraglidingFolder/divers/GPS/OpenAir-Format/
   :alt: Paragliding OpenAir French Files


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


Périmètre géographique couvert
------------------------------
.. image:: http://pascal.bazile.free.fr/paraglidingFolder/divers/GPS/OpenAir-Format/img/geoPOAFF_border_20201210.jpg
   :target: http://pascal.bazile.free.fr/paraglidingFolder/divers/GPS/OpenAir-Format/img/geoPOAFF_border_20201210.jpg
   :alt: geoPOAFF_border
  
  
Exemples de cartographies vol-libre
-----------------------------------
Cartographie vol-libre (FreeFlight) couvrant l'intégralité des territoires Français:

.. image:: http://pascal.bazile.free.fr/paraglidingFolder/divers/GPS/OpenAir-Format/img/geoFrenchAll_sample_GeoJSON.jpg
   :target: http://pascal.bazile.free.fr/paraglidingFolder/divers/GPS/OpenAir-Format/img/geoFrenchAll_sample_GeoJSON.jpg
   :alt: FrenchAreas


Cartographie vol-libre (FreeFlight) couvrant la France-métropolitaine:

.. image:: http://pascal.bazile.free.fr/paraglidingFolder/divers/GPS/OpenAir-Format/img/geoFrench_sample_GeoJSON.jpg
   :target: http://pascal.bazile.free.fr/paraglidingFolder/divers/GPS/OpenAir-Format/img/geoFrench_sample_GeoJSON.jpg
   :alt: French
   
   
Quelques autres exemples de cartographies vol-libre (FreeFlight):

.. image:: http://pascal.bazile.free.fr/paraglidingFolder/divers/GPS/OpenAir-Format/img/20201020_GlobalView-1.png
   :target: http://pascal.bazile.free.fr/paraglidingFolder/divers/GPS/OpenAir-Format/img/20201020_GlobalView-1.png
   :alt: OtherFrench


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
.. [3] `Paragliding OpenAir French Files (on GitHub)`_ - Crédit `Pascal Bazile`_ - Programme de construction des cartographies `Paragliding OpenAir French Files`_ aux formats (GeoJSON_ ; `Openair New Format`_ et KML_)
.. [4] aixmParser_ - Crédit `Pascal Bazile`_ - Programme d'interprétation du format AIXM_ pour transformations aux formats (GeoJSON_ ; `Openair New Format`_)
.. [5] openairParser_ - Crédit `Pascal Bazile`_ - Programme d'interprétation du format Openair_ pour transformaion AIXM_
.. [6] `Carte OACI France`_ - Scan digitalisé
.. [7] SIA-France_ - Service de l'Information Aéronautique
.. [8] Eurocontrol_ - A pan-European, civil-military organisation dedicated to supporting European aviation
.. [9] AIXM_ - Aeronautical Information Exchange Modele
.. [10] XML_ - W3C Standard
.. [11] KML_ - Google Documentation
.. [12] `Openair Format`_ - Openair Documentation historique
.. [13] `Openair New Format`_ - Documentation des nouvelles évolutions du format Openair


Crédits
-------
* `Pascal Bazile`_ author of this software <pascal_bazile@yahoo.fr>
* the many open source libraries, projects, and data sources used by this software (show file content of 'requirements.txt' for complete components detail)


.. _Pascal Bazile: https://github.com/BPascal-91/
.. _Paragliding OpenAir French Files: http://pascal.bazile.free.fr/paraglidingFolder/divers/GPS/OpenAir-Format/
.. _Paragliding OpenAir French Files (on Facebook): https://www.facebook.com/Paragliding-OpenAir-FrenchFiles-102040114894513/
.. _Paragliding OpenAir French Files (on GitHub): https://github.com/BPascal-91/poaff/
.. _Carte OACI France: https://www.geoportail.gouv.fr/donnees/carte-oaci-vfr
.. _SIA-France: https://www.sia.aviation-civile.gouv.fr/
.. _aixmParser: https://github.com/BPascal-91/aixmParser/
.. _openairParser: https://github.com/BPascal-91/openairParser/
.. _Eurocontrol: https://www.eurocontrol.int/
.. _AIXM: http://www.aixm.aero/
.. _Openair Format: http://www.winpilot.com/UsersGuide/UserAirspace.asp
.. _Openair New Format: http://pascal.bazile.free.fr/paraglidingFolder/divers/GPS/OpenAir-Format/
.. _XML: https://www.w3.org/TR/xml/
.. _KML: https://developers.google.com/kml/documentation
.. _GeoJSON: http://geojson.org/
.. _pip: http://www.pip-installer.org

