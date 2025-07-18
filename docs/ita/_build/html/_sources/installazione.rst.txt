Installazione
=============

Prerequisiti
------------

Prima di installare Images Deduplicator, assicurati di avere:

1. Python 3.8 o superiore (3.10+ consigliato)
2. ImageMagick installato (richiesto per Wand)
3. Git (opzionale, per l'installazione da sorgente)

Installazione di ImageMagick
--------------------------

Windows
~~~~~~~

1. Scarica l'installer di ImageMagick dal `sito ufficiale <https://imagemagick.org/script/download.php#windows>`_
2. Esegui l'installatore con queste opzioni:
   - Seleziona "Install development headers and libraries for C and C++"
   - Seleziona "Add application directory to your system path"
3. Verifica l'installazione aprendo un nuovo prompt dei comandi ed eseguendo:

   .. code-block:: bash

      magick --version

macOS
~~~~~

.. code-block:: bash

   # Installa Homebrew se non è già installato
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   
   # Installa ImageMagick
   brew install imagemagick

Linux (Debian/Ubuntu)
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   sudo apt-get update
   sudo apt-get install -y \
       imagemagick \
       libmagickwand-dev \
       libmagickcore-dev

Installazione tramite pip
------------------------

Il metodo consigliato per installare Images Deduplicator è utilizzare pip:

.. code-block:: bash

   # Installa il pacchetto
   pip install images-deduplicator
   
   # Esegui l'applicazione
   images-dedup

Installazione da sorgente
------------------------

1. Clona il repository:

.. code-block:: bash

   git clone https://github.com/Nsfr750/Images-Deduplicator.git
   cd Images-Deduplicator

2. Installa in modalità sviluppo con tutte le dipendenze:

.. code-block:: bash

   # Crea e attiva un ambiente virtuale (consigliato)
   python -m venv venv
   source venv/bin/activate  # Su Windows: venv\Scripts\activate
   
   # Installa il pacchetto in modalità sviluppo con tutti gli extra
   pip install -e '.[dev,docs,packaging]'

3. Esegui l'applicazione:

.. code-block:: bash

   python main.py

Verifica dell'installazione
--------------------------

Per verificare che Wand riesca a trovare e utilizzare ImageMagick:

.. code-block:: python

   from wand.image import Image
   from wand.version import QUANTUM_DEPTH, MAGICK_VERSION
   
   print(f"Versione di ImageMagick: {MAGICK_VERSION}")
   print(f"Profondità quantica: {QUANTUM_DEPTH} bit")
   
   # Test delle operazioni di base sulle immagini
   with Image(filename='wizard:') as img:
       print(f'Dimensioni immagine: {img.size}')

Risoluzione dei problemi
-----------------------

**Wand non trova ImageMagick**

Se ricevi errori relativi a librerie mancanti:

1. Assicurati che ImageMagick sia installato correttamente e sia nel PATH di sistema
2. Su Windows, potrebbe essere necessario riavviare il terminale/IDE dopo l'installazione
3. Verifica l'installazione eseguendo ``magick --version`` nel terminale

**Errori di permessi**

Se incontri errori di permessi, prova:

.. code-block:: bash

   # Su Linux/macOS
   pip install --user images-deduplicator
   
   # Oppure usa un ambiente virtuale
   python -m venv venv
   source venv/bin/activate  # Su Windows: venv\Scripts\activate
   pip install -e .

**Problemi di memoria**

Per grandi collezioni di immagini, potrebbe essere necessario aumentare i limiti delle risorse di ImageMagick. Crea o modifica il file ``policy.xml``:

- Linux/macOS: ``/etc/ImageMagick-7/policy.xml``
- Windows: ``C:\Program Files\ImageMagick-7.1.1-Q16-HDRI\policy.xml``

E modifica questi valori:

.. code-block:: xml

   <policy domain="resource" name="width" value="16KP"/>
   <policy domain="resource" name="height" value="16KP"/>
   <policy domain="resource" name="area" value="128MB"/>
   <policy domain="resource" name="memory" value="4GiB"/>
   <policy domain="resource" name="map" value="8GiB"/>
   <policy domain="resource" name="disk" value="16GiB"/>
