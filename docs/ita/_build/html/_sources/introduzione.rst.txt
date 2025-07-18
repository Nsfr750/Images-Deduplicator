Introduzione
============

Images Deduplicator è un'applicazione Python progettata per la gestione e la rimozione efficiente di immagini duplicate. Utilizzando la libreria Wand (basata su ImageMagick) per l'elaborazione delle immagini, questo strumento offre tecniche avanzate di confronto visivo per identificare e gestire i duplicati con elevata precisione.

Caratteristiche principali:
------------------------

* **Elaborazione avanzata delle immagini**: Basata su Wand/ImageMagick per un supporto superiore dei formati
* **Rilevamento duplicati visivi**: Hashing percettivo per identificare immagini visivamente simili
* **Supporto completo dei formati**: Gestisce tutti i principali formati tra cui JPEG, PNG, WEBP, PSD e altri
* **Interfaccia intuitiva**: Interfaccia utente amichevole con supporto per temi scuro/chiaro
* **Supporto multilingua**: Internazionalizzazione integrata con italiano e inglese
* **Elaborazione in batch**: Processa efficientemente migliaia di immagini
* **Anteprima e confronto**: Confronto affiancato prima di intraprendere azioni
* **Operazioni sicure**: Spostamento nel cestino invece di cancellazione permanente
* **Log dettagliati**: Registrazione completa delle operazioni per la tracciabilità

Requisiti di sistema:
-------------------

* **Python**: 3.8 o superiore (3.10+ consigliato)
* **ImageMagick**: Richiesto per l'elaborazione con Wand
  - Windows: Scarica da [ImageMagick Windows](https://imagemagick.org/script/download.php#windows)
  - macOS: `brew install imagemagick`
  - Linux: `sudo apt-get install libmagickwand-dev`
* **Memoria**: Minimo 4GB, 8GB+ consigliato per grandi collezioni di immagini
* **Spazio su disco**: Sufficiente per le immagini da elaborare + file temporanei
* **Sistemi operativi**: Windows 10/11, macOS 10.15+, Linux con X11/Wayland

Perché Wand/ImageMagick?
----------------------

Images Deduplicator utilizza Wand (un binding Python per ImageMagick) per diversi vantaggi:

* Supporto più ampio per formati inclusi PSD, GIF e BMP
* Migliore gestione della memoria per immagini di grandi dimensioni
* Comportamento più coerente tra diverse piattaforme
* Funzionalità avanzate di manipolazione delle immagini
* Manutenzione attiva e aggiornamenti di sicurezza
