Riferimento API
============

Questa sezione fornisce la documentazione dettagliata per l'API di Images Deduplicator. L'applicazione è costruita con un'architettura modulare, dove ogni modulo gestisce funzionalità specifiche.

Moduli Principali
-----------------

.. automodule:: main
   :members:
   :undoc-members:
   :show-inheritance:
   :exclude-members: QMainWindow, QApplication

   Punto di ingresso principale dell'applicazione e funzionalità di base.

Elaborazione Immagini
--------------------

.. automodule:: script.image_processor
   :members:
   :undoc-members:
   :show-inheritance:
   :noindex:

   Gestisce tutte le operazioni di elaborazione delle immagini utilizzando Wand/ImageMagick.

   Caratteristiche principali:
   - Supporta tutti i principali formati immagine (JPEG, PNG, WEBP, PSD, ecc.)
   - Hashing percettivo per il rilevamento dei duplicati
   - Elaborazione efficiente della memoria per immagini di grandi dimensioni
   - Gestione di EXIF e metadati

Interfaccia Utente
-----------------

.. automodule:: script.UI
   :members:
   :undoc-members:
   :show-inheritance:
   :exclude-members: Ui_MainWindow

   Finestra principale e componenti dell'interfaccia utente costruiti con PyQt6.

.. automodule:: script.menu
   :members:
   :undoc-members:
   :show-inheritance:

   Funzionalità del menu e della barra degli strumenti dell'applicazione.

.. automodule:: script.image_dialog_preview
   :members:
   :undoc-members:
   :show-inheritance:

   Finestra di dialogo per l'anteprima e il confronto delle immagini.

Funzionalità di Base
-------------------

.. automodule:: script.workers
   :members:
   :undoc-members:
   :show-inheritance:

   Processi in background per operazioni non bloccanti dell'interfaccia utente.

.. automodule:: script.undo_manager
   :members:
   :undoc-members:
   :show-inheritance:

   Gestisce le operazioni di annulla/ripeti per le operazioni sui file.

Internazionalizzazione
---------------------

.. automodule:: script.translations
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: script.language_manager
   :members:
   :undoc-members:
   :show-inheritance:

   Gestisce il cambio lingua e le traduzioni delle stringhe.

Utilità
-------

.. automodule:: script.logger
   :members:
   :undoc-members:
   :show-inheritance:

   Funzionalità di logging centralizzate.

.. automodule:: script.version
   :members:
   :undoc-members:
   :show-inheritance:

   Gestione della versione e controllo aggiornamenti.

.. automodule:: script.about
   :members:
   :undoc-members:
   :show-inheritance:

   Finestra "Informazioni su" e informazioni sull'applicazione.

.. automodule:: script.help
   :members:
   :undoc-members:
   :show-inheritance:

   Sistema di aiuto e visualizzatore della documentazione.

.. automodule:: script.sponsor
   :members:
   :undoc-members:
   :show-inheritance:

   Funzionalità per sponsor e donazioni.

.. automodule:: script.styles
   :members:
   :undoc-members:
   :show-inheritance:

   Tema e stile dell'applicazione.

Integrazione Wand/ImageMagick
---------------------------

L'applicazione utilizza la libreria Wand (un binding Python per ImageMagick) per tutte le operazioni di elaborazione delle immagini. Le caratteristiche principali includono:

- Supporto per oltre 200 formati immagine
- Funzionalità avanzate di manipolazione delle immagini
- Gestione dei profili colore e dei metadati
- Elaborazione efficiente della memoria

Esempio di utilizzo:

.. code-block:: python

   from wand.image import Image
   
   def get_image_size(image_path):
       with Image(filename=image_path) as img:
           return img.width, img.height

Per ulteriori informazioni, consulta la `documentazione di Wand <https://docs.wand-py.org/>`_ e la `documentazione di ImageMagick <https://imagemagick.org/script/documentation.php>`_.

Note
----

- Tutte le operazioni sui file vengono eseguite in modo thread-safe
- Le operazioni di elaborazione delle immagini sono ottimizzate per le prestazioni
- L'applicazione include una gestione completa degli errori e il logging
- Per un utilizzo avanzato, molte funzioni accettano argomenti aggiuntivi che vengono passati alle funzioni sottostanti di Wand/ImageMagick

Per una documentazione API più dettagliata, consulta direttamente il codice sorgente o utilizza l'opzione "Mostra codice" nella documentazione generata.
