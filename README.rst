.. image:: http://pascal.bazile.free.fr/paraglidingFolder/divers/GPS/OpenAir-Format/img/Paragliding-OpenAir-FrenchFiles_SiaEurocontrol.jpg
   :target: http://pascal.bazile.free.fr/paraglidingFolder/divers/GPS/OpenAir-Format/
   :alt: Paragliding OpenAir FrenchFiles

poaff - `Paragliding OpenAir French Files`_
==============

.. code::

	/!\ ATTENTION: Seules des données officielles doivent êtres utilisées pour la navigation aérienne.
	/!\ WARNING  : Only official data must be used for air navigation

Programme d'extraction et de formatage par lots ; basé sur des données issues des standards AIXM_ :code:`(Aeronautical Information Exchange Modele)` et XML_ SIA-France_ :code:`(Service de l'Information Aéronautique)`
Ces traitements sont nécessaires pour la génération des centaines de cartographies publiées sur le blog `Paragliding OpenAir FrenchFiles`_
Les données sources utilisés pour la contruction de ce site sont majoritairement issues des sources officielles SIA-France_ et Eurocontrol_
Vous pouvez également suivre les évolutions via la page `Paragliding OpenAir French Files (on Facebook)`_


**Table of Contents**

.. contents::
   :backlinks: none
   :local:


Installation
------------

geojson is compatible with Python 3.6, 3.7 and 3.8. The recommended way to install is via pip_:

.. code::

  pip install -r requirements.txt

.. _pip: http://www.pip-installer.org


Utilisation
-----------

.. code:: python

	>>> #!/usr/bin/env python3  
	>>> $ python3 poaff.py  



.. _Paragliding OpenAir French Files: http://pascal.bazile.free.fr/paraglidingFolder/divers/GPS/OpenAir-Format/
.. _Paragliding OpenAir French Files (on Facebook): https://www.facebook.com/Paragliding-OpenAir-FrenchFiles-102040114894513/
.. _Carte OACI France: https://www.geoportail.gouv.fr/donnees/carte-oaci-vfr
.. _AIXM Aeronautical Information Exchange Model: http://www.aixm.aero/
.. _SIA-France: https://www.sia.aviation-civile.gouv.fr/
.. _Eurocontrol: https://www.eurocontrol.int/
.. _XML: https://www.w3.org/TR/xml/
