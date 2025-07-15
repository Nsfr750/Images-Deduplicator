Configurazione
=============

Opzioni principali
-----------------

1. **Precisione del confronto**
   - Livello di precisione (1-100):
     * Valori più bassi trovano più duplicati
     * Valori più alti trovano solo duplicati quasi identici

2. **Dimensioni minime**
   - Ignora immagini sotto:
     * Larghezza minima (pixel)
     * Altezza minima (pixel)
     * Dimensione minima (KB)

3. **Formati supportati**
   - Estensioni consentite:
     * .jpg, .jpeg
     * .png
     * .gif
     * .bmp
     * .webp

4. **Cartelle escluse**
   - Lista di cartelle da ignorare:
     * Cartelle di sistema
     * Cartelle temporanee
     * Cartelle specifiche

5. **Opzioni di elaborazione**
   - Numero di thread:
     * Aumenta per migliorare le prestazioni
     * Riduce per risparmiare risorse
   - Cache dimensione:
     * Memoria massima per cache (MB)

6. **Opzioni di output**
   - Genera report:
     * PDF
     * CSV
     * JSON
   - Salva log:
     * Livello di dettaglio
     * Posizione file

7. **Interfaccia utente**
   - Lingua:
     * Italiano
     * Inglese
   - Tema:
     * Light
     * Dark

8. **Avanzate**
   - Algoritmo di confronto:
     * Average Hash
     * Perceptual Hash
     * Difference Hash
   - Ottimizzazioni:
     * Pre-caricamento immagini
     * Buffering risultati

Consigli di configurazione
------------------------

1. **Prestazioni**
   - Usa più thread su sistemi multi-core
   - Aumenta la cache su sistemi con RAM abbondante

2. **Precisione**
   - Livello 70-80 per un buon equilibrio
   - Livello 90+ per confronti molto rigorosi

3. **Memoria**
   - Monitora l'uso della RAM
   - Riduci la cache se necessario

4. **Backup**
   - Salva sempre le configurazioni
   - Esporta i report prima di eliminare immagini
