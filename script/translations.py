"""
Translation strings for Image Deduplicator.
"""

# List of available language codes
LANGUAGES = ['en', 'it']

# Translation strings organized by language
TRANSLATIONS = {
    'en': {
        # Application
        'app_title': 'Image Deduplicator v{version}',
        'select_folder': 'Select Folder',
        'browse': 'Browse...',
        'compare': 'Compare Images',
        'duplicates_found': 'Duplicates Found',
        'original_image': 'Original Image',
        'duplicate_image': 'Duplicate Image',
        'select_all': 'Select All',
        'select_none': 'Select None',
        'delete_selected': 'Delete Selected',
        'delete_all_duplicates': 'Delete All Duplicates',
        'ready': 'Ready',
        'no_images_found': 'No images found in the selected folder.',
        'error': 'Error',
        'warning': 'Warning',
        'success': 'Success',
        'info': 'Information',
        'cancel': 'Cancel',
        'ok': 'OK',
        'yes': 'Yes',
        'no': 'No',
        
        # Menu items
        'file': 'File',
        'edit': 'Edit',
        'view': 'View',
        'tools': 'Tools',
        'help': 'Help',
        'language': 'Language',
        'about': 'About',
        'exit': 'Exit',
        'save_report': 'Save Report',
        'settings': 'Settings',
        'show_logs': 'View Logs',
        'check_updates': 'Check for Updates',
        'show_sponsor': 'Support Us',
        
        # Status messages
        'comparing_images': 'Comparing images...',
        'deleting_files': 'Deleting files...',
        'files_deleted': '{count} files deleted.',
        'no_files_selected': 'No files selected for deletion.',
        'confirm_delete': 'Are you sure you want to delete the selected files?',
        'confirm_delete_all': 'Are you sure you want to delete all duplicate files?',
        'operation_cancelled': 'Operation cancelled.',
        'operation_completed': 'Operation completed successfully.',
        'operation_failed': 'Operation failed: {error}',
        
        # About dialog
        'app_name':'Image Deduplicator',
        'about_title': 'Info about Image Deduplicator',
        'version': 'Version: {version}',
        'copyright': '© 2025 Nsfr750',
        'license': 'License: GPLv3',
        'about_description': 'A powerful tool to find and manage duplicate images in your collection.',
        'system_info': 'System Info:',
        'operating_system': 'Operating System:',
        'python_version': 'Python Version:',
        'qt_version': 'PyQt Version:',
        'cpu_info': 'CPU:',
        'memory_info': 'RAM:',
        'github': 'GitHub',
        
        # Help dialog
        'help_title': 'Image Deduplicator Help',
        'help': 'Help',
        'help_close': 'Close Help',
        'usage': 'Usage',
        'tips': 'Tips',
        'close': 'Close',
        'how_to_use': 'How to use the app',
        'help_usage_step_1': 'Select a folder containing images using the "Browse" button',
        'help_usage_step_2': 'Enable "Search subfolders" if you want to scan nested directories',
        'help_usage_step_3': 'Click "Compare Images" to find duplicates',
        'help_usage_step_4': 'Review the list of duplicate images',
        'help_usage_step_5': 'Select one or more duplicates to preview them',
        'help_usage_step_6': 'Use the action buttons to manage duplicates',
        'help_features': 'Features',
        'help_tips': 'Tips & Tricks',
        'search_help': 'Search help...',
        'search_case_sensitive': 'Case Sensitive',
        'search_whole_words': 'Whole Words',
        'search_highlight': 'Highlight Matches',
        'search_fuzzy': 'Fuzzy Search',
        'matches': 'matches',
        'help_no_results': 'No results found for your search.',
        'help_usage_title': 'How to Use Image Deduplicator',
        'help_usage_intro': 'Image Deduplicator helps you find and remove duplicate images from your computer. Follow these steps to get started:',
        'help_usage_step_1': 'Select a folder containing images using the "Browse" button',
        'help_usage_step_2': 'Enable "Search subfolders" if you want to scan nested directories',
        'help_usage_step_3': 'Click "Compare Images" to find duplicates',
        'help_usage_step_4': 'Review the list of duplicate images',
        'help_usage_step_5': 'Select one or more duplicates to preview them',
        'help_usage_step_6': 'Use the action buttons to manage duplicates',
        'help_features_title': 'Key Features',
        'help_feature_1': 'Find exact and similar images using advanced algorithms',
        'help_feature_2': 'Preview images before deletion',
        'help_feature_3': 'Support for all major image formats',
        'help_feature_4': 'Intuitive and user-friendly interface',
        'help_tips_title': 'Tips & Tricks',
        'help_tip_1': 'Use the slider to adjust similarity threshold',
        'help_tip_2': 'Double-click an image to view it in full size',
        'help_tip_3': 'Use keyboard shortcuts for faster navigation',
        'help_tip_4': 'Save your results for later review',
        'help_supported_formats': 'Supported Image Formats',
        'help_formats_1': 'Common formats: JPG, PNG, GIF, BMP, TIFF, and WebP',
        'help_formats_2': 'Raw formats: CR2, NEF, ARW, and more',
        'help_shortcuts': 'Keyboard Shortcuts',
        'help_shortcut_next': 'Next image: Right Arrow or Space',
        'help_shortcut_prev': 'Previous image: Left Arrow or Backspace',
        'help_shortcut_delete': 'Delete selected: Delete key',
        'help_shortcut_zoom': 'Zoom: Mouse wheel or +/- keys',
        'help_shortcut_rotate': 'Rotate: R key',
        'help_shortcut_select_all': 'Select all: Ctrl+A',
        'help_shortcut_deselect': 'Deselect all: Ctrl+D',
        'help_shortcut_quit': 'Quit: Esc key',
        'help_usage_title_2': 'Step-by-Step Guide',
        'help_usage_select_all': 'Select All - Selects all duplicates in the current view',
        'help_usage_delete_selected': 'Delete Selected - Deletes all currently selected duplicates',
        'help_usage_delete_all': 'Delete All - Deletes all duplicates found',
        'help_supported_formats': 'Supported Image Formats',
        'help_formats_1': 'Common formats: JPG, PNG, GIF, BMP, TIFF, and WebP',
        'help_formats_2': 'Raw formats: CR2, NEF, ARW, and other camera raw formats',
        'help_features_title_full': 'Image Deduplicator Features',
        'help_features_image_title': 'Image Comparison',
        'help_features_image_1': 'Visual comparison of duplicate images side by side',
        'help_features_image_2': 'Support for various image formats including RAW',
        'help_features_image_3': 'Customizable similarity threshold for accurate detection',
        'help_features_batch_title': 'Batch Operations',
        'help_features_batch_1': 'Process multiple images in a single operation',
        'help_features_batch_2': 'Automatic organization of duplicate groups',
        'help_features_batch_3': 'Save and load comparison results for later review',
        'help_features_quality_title': 'Quality Control',
        'help_features_quality_1': 'Image quality analysis and comparison',
        'help_features_quality_2': 'Keep the best quality version automatically',
        'help_features_quality_3': 'Detailed image information and metadata view',
        'help_tips_large_title': 'Working with Large Collections',
        'help_tips_large_1': 'For large image collections, consider scanning in smaller batches for better performance',
        'help_tips_large_2': 'Use the "Exclude Folders" feature to skip system folders or directories with non-image files',
        'help_tips_large_3': 'Save your progress when working with large collections to avoid rescanning',
        'help_tips_formats_title': 'Image Format Tips',
        'help_tips_formats_1': 'RAW files take longer to process but provide the most accurate comparison',
        'help_tips_formats_2': 'For best performance, convert RAW files to DNG or TIFF before comparison',
        'help_tips_formats_3': 'The application can handle mixed format comparisons (e.g., JPG vs PNG)',
        'help_tips_perf_title': 'Performance Optimization',
        'help_tips_perf_1': 'Close other memory-intensive applications while scanning large collections',
        'help_tips_perf_2': 'Use the preview feature to verify duplicates before processing the entire collection',
        'help_tips_perf_3': 'Adjust the similarity threshold to balance between accuracy and performance',
        'help_feature_1': 'Fast and accurate image comparison using perceptual hashing',
        'help_feature_2': 'Support for multiple image formats (JPG, PNG, GIF, WebP, etc.)',
        'help_feature_3': 'Preview images before deletion',
        'help_feature_4': 'Support for searching subdirectories',
        'help_tips_title': 'Tips & Tricks',
        'help_tip_1': 'Use the similarity slider to adjust how similar images need to be to be considered duplicates',
        'help_tip_2': 'You can select multiple duplicates at once using Ctrl+Click or Shift+Click',
        'help_tip_3': 'Use the "Keep Better Quality" option to automatically keep the highest quality version of each duplicate',
        'help_tip_4': 'Check the "Preserve Metadata" option to keep EXIF and other metadata when deleting duplicates',
        'help_tip_5': 'Use the search feature to quickly find specific help topics',
        'help_emptying_trash': 'Emptying trash...',
        'help_empty_trash_success': 'Trash has been emptied successfully',
        'help_empty_trash_failed': 'Failed to empty trash: {error}',
        
        # Sponsor dialog
        'support_title': 'Support Image Deduplicator',
        'support_project': 'Support the Project',
        'support_project_header': ' Support Image Deduplicator',
        'support_project_description': 'This application is developed and maintained by a single developer.\nYour support helps keep the project alive and allows for new features and improvements.',
        'support_on_patreon': 'Support on Patreon',
        'donate_via_paypal': 'Donate via PayPal',
        'buy_me_coffee': 'Buy Me a Coffee',
        'bitcoin_donation': 'Donate with Bitcoin',
        'ethereum_donation': 'Donate with Ethereum',
        'copy_address': 'Copy Address',
        'address_copied': 'Address Copied',
        'address_copied_to_clipboard': 'address copied to clipboard',
        'support_development': 'Support Development',
        'support_app_name': 'Support Images-Deduplicator',
        'support_message': 'If you find this application useful, please consider supporting its development.\n\nYour support helps cover hosting costs and encourages further development.',
        'github_sponsors': 'GitHub Sponsors',
        'paypal_donation': 'PayPal Donation',
        'monero': 'Monero',
        'scan_to_donate_xmr': 'Scan to donate XMR',
        'qr_generation_failed': 'QR Code generation failed',
        'ways_to_support': 'Ways to Support',
        'other_ways_to_help': 'Other Ways to Help',
        'star_on_github': 'Star the project on',
        'report_bugs': 'Report bugs and suggest features',
        'share_with_others': 'Share with others who might find it useful',
        'copied': 'Copied!',
        'close': 'Close',
        'donate_with_paypal': 'Donate with PayPal',
        'copy_monero_address': 'Copy Monero Address',
        
        # Log viewer
        'log_viewer': 'Log Viewer',
        'filter_logs': 'Filter Logs',
        'no_log_file': 'No log file available.',
        'error_reading_log': 'Error reading log file: {error}',
        'clear_logs': 'Clear Logs',
        'confirm_clear_logs': 'Are you sure you want to clear all logs? This cannot be undone.',
        'save_logs': 'Save Logs',
        'save_log_file': 'Save Log File',
        'log_files': 'Log Files (*.log);;All Files (*)',
        'logs_saved': 'Logs saved successfully to: {path}',
        'failed_save_logs': 'Failed to save log file: {error}',
        'log_level': 'Log Level',
        'all_levels': 'All Levels',
        'refresh': 'Refresh',
        'select_log_file': 'Select Log File',
        'no_logs_found': 'No logs found.',
        'log_level_filters': 'Log Level Filters',
        'clear_log': 'Clear Log',
        'save_as': 'Save As',
        'no_logs_available': 'No logs available.',

        # Settings
        'settings': 'Settings',
        'appearance': 'Appearance',
        'theme': 'Theme',
        'dark_theme': 'Dark',
        'light_theme': 'Light',
        'comparison_settings': 'Comparison Settings',
        'similarity_threshold': 'Similarity Threshold',
        'search_subdirectories': 'Search subdirectories',
        'keep_better_quality': 'Keep better quality duplicates',
        'keep_better_quality_tooltip': 'When enabled, keeps the highest quality version of duplicate images',
        'file_handling': 'File Handling',
        'preserve_metadata': 'Preserve metadata when deleting',
        'preserve_metadata_tooltip': 'Preserve metadata (EXIF, etc.) when deleting duplicate files',
        'save': 'Save',
        'cancel': 'Cancel',
        
        # Edit menu
        'edit_menu': {
            'undo': 'Undo',
            'empty_trash': 'Empty Trash',
            'confirm_empty_trash': 'Are you sure you want to empty the trash?',
            'empty_trash_success': 'Trash has been emptied successfully',
            'empty_trash_failed': 'Failed to empty trash: {error}',
        },
        
        # Update checker
        'update_available': 'Update Available',
        'new_version_available': 'A new version of Image Deduplicator is available!',
        'current_version': 'Your version: {current_version}',
        'latest_version': 'Latest version: {latest_version}',
        'download_update': 'Download Update',
        'remind_me_later': 'Remind Me Later',
        'skip_this_version': 'Skip This Version',
        'checking_for_updates': 'Checking for updates...',
        'up_to_date': 'You are using the latest version of Image Deduplicator.',
        'update_error': 'Error checking for updates',
        'update_check_failed': 'Failed to check for updates: {error}',
        'release_notes': 'Release Notes',
        'download': 'Download',
        'view_changes': 'View Changes',
        'update_available_title': 'Update Available',
        'current_version': 'Your version: {current_version}',
        'latest_version': 'Latest version: {latest_version}',

        #missing
        'preparing_scan': 'Preparing Scan',
        'comparison_complete': 'Compararison Complete',
        'confirm_delete_selected': 'Confirm Delete Selected',
        'confirm_delete_all': 'Confirm Delete All',
        'confirm_delete_all_duplicates': 'Confirm Delete All Duplicates',
        'deleting_duplicates': 'Deleting Duplicates',
        'Yes': 'Yes',
        'No': 'No',
        'moved_to_trash': 'Moved to Trash',
        'check_for_updates': 'Check for Updates',
        'view_logs': 'View Logs',
        'edit_menu.undo': 'Undo',
        'some_delection_failed': 'Some delection Failed',
        'system_information': 'System Information',
        'search_subfolders': 'Search Subfolders',
        
        # Empty trash messages
        'empty_trash': {
            'success': {
                'windows': 'Recycle Bin emptied successfully',
                'macos': 'Trash emptied successfully',
                'linux': 'Trash emptied successfully',
                'linux_manual': 'Trash emptied manually (trash-cli not found)'
            },
            'error': {
                'windows': 'Failed to empty Recycle Bin: {error}',
                'macos': 'Failed to empty Trash: {error}',
                'linux': 'Failed to empty trash: {error}'
            },
            'unsupported_platform': 'Unsupported platform: {platform}'
        },
    },
    'it': {
        # Application
        'app_title': 'Image Deduplicator v{version}',
        'select_folder': 'Seleziona Cartella',
        'browse': 'Sfoglia...',
        'compare': 'Confronta Immagini',
        'duplicates_found': 'Duplicati Trovati',
        'original_image': 'Immagine Originale',
        'duplicate_image': 'Immagine Duplicata',
        'select_all': 'Seleziona Tutto',
        'select_none': 'Deseleziona Tutto',
        'delete_selected': 'Elimina Selezionati',
        'delete_all_duplicates': 'Elimina Tutti i Duplicati',
        'ready': 'Pronto',
        'no_images_found': 'Nessuna immagine trovata nella cartella selezionata.',
        'error': 'Errore',
        'warning': 'Avviso',
        'success': 'Operazione Completata',
        'info': 'Informazione',
        'cancel': 'Annulla',
        'ok': 'OK',
        'yes': 'Sì',
        'no': 'No',
        
        # Menu items
        'file': 'File',
        'edit': 'Modifica',
        'view': 'Visualizza',
        'tools': 'Strumenti',
        'help': 'Aiuto',
        'language': 'Lingua',
        'about': 'Informazioni',
        'exit': 'Esci',
        'save_report': 'Salva Report',
        'settings': 'Impostazioni',
        'show_logs': 'Visualizza Log',
        'check_updates': 'Controlla Aggiornamenti',
        'show_sponsor': 'Supportaci',
        
        # Status messages
        'comparing_images': 'Confronto delle immagini in corso...',
        'deleting_files': 'Eliminazione file in corso...',
        'files_deleted': '{count} file eliminati.',
        'no_files_selected': 'Nessun file selezionato per l\'eliminazione.',
        'confirm_delete': 'Sei sicuro di voler eliminare i file selezionati?',
        'confirm_delete_all': 'Sei sicuro di voler eliminare tutti i file duplicati?',
        'operation_cancelled': 'Operazione annullata.',
        'operation_completed': 'Operazione completata con successo.',
        'operation_failed': 'Operazione fallita: {error}',
        
        # About dialog
        'app_name':'Image Deduplicator',
        'about_title': 'Informazioni su Image Deduplicator',
        'version': 'Versione: {version}',
        'copyright': ' 2025 Nsfr750',
        'license': 'Licenza: GPLv3',
        'about_description': 'Un potente strumento per trovare e gestire immagini duplicate nella tua collezione.',
        'system_info': 'Informazioni Sistema:',
        'operating_system': 'Sistema Operativo:',
        'python_version': 'Versione Python:',
        'qt_version': 'Versione PyQt:',
        'cpu_info': 'CPU:',
        'memory_info': 'RAM:',
        'github': 'GitHub',

        # Help dialog
        'help_title': 'Guida di Image Deduplicator',
        'help': 'Aiuto',
        'help_close': 'Chiudi Aiuto',
        'usage': 'Utilizzo',
        'tips': 'Suggerimenti',
        'close': 'Chiudi',
        'how_to_use': 'Come utilizzare l\'applicazione',
        'help_usage_step_1': 'Seleziona una cartella contenente immagini utilizzando il pulsante "Sfoglia..."',
        'help_usage_step_2': 'Abilita "Cerca nelle sottocartelle" se vuoi scansionare anche le directory annidate',
        'help_usage_step_3': 'Clicca su "Confronta Immagini" per trovare i duplicati',
        'help_usage_step_4': 'Esamina l\'elenco delle immagini duplicate',
        'help_usage_step_5': 'Seleziona uno o più duplicati per visualizzarli in anteprima',
        'help_usage_step_6': 'Utilizza i pulsanti delle azioni per gestire i duplicati',
        'help_features': 'Funzionalità',
        'help_tips': 'Suggerimenti e Trucchi',
        'search_help': 'Cerca nella guida...',
        'search_case_sensitive': 'Maiuscole/Minuscole',
        'search_whole_words': 'Parole Intere',
        'search_highlight': 'Evidenzia Risultati',
        'search_fuzzy': 'Ricerca Approssimata',
        'matches': 'risultati',
        'help_no_results': 'Nessun risultato trovato per la tua ricerca.',
        'help_usage_title': 'Come Usare Image Deduplicator',
        'help_usage_intro': 'Image Deduplicator ti aiuta a trovare e rimuovere le immagini duplicate dal tuo computer. Segui questi passaggi per iniziare:',
        'help_features_title': 'Funzionalità Principali',
        'help_feature_1': 'Confronto immagini veloce e preciso utilizzando l\'hashing percettivo',
        'help_feature_2': 'Supporto per più formati di immagine (JPG, PNG, GIF, WebP, ecc.)',
        'help_feature_3': 'Anteprima delle immagini prima dell\'eliminazione',
        'help_feature_4': 'Supporto per la ricerca nelle sottocartelle',
        'help_tips_title': 'Suggerimenti e Trucchi',
        'help_tip_1': 'Usa il cursore di somiglianza per regolare quanto le immagini devono essere simili per essere considerate duplicate',
        'help_tip_2': 'Puoi selezionare più duplicati contemporaneamente usando Ctrl+Click o Maiusc+Click',
        'help_usage_title_2': 'Guida Passo Passo',
        'help_usage_select_all': 'Seleziona Tutto - Seleziona tutti i duplicati nella vista corrente',
        'help_usage_delete_selected': 'Elimina Selezionati - Elimina tutti i duplicati attualmente selezionati',
        'help_usage_delete_all': 'Elimina Tutti - Elimina tutti i duplicati trovati',
        'help_supported_formats': 'Formati Immagine Supportati',
        'help_formats_1': 'Formati comuni: JPG, PNG, GIF, BMP, TIFF e WebP',
        'help_formats_2': 'Formati RAW: CR2, NEF, ARW e altri formati raw fotocamera',
        'help_features_title_full': 'Caratteristiche di Image Deduplicator',
        'help_features_image_title': 'Confronto Immagini',
        'help_features_image_1': 'Confronto visivo delle immagini duplicate affiancate',
        'help_features_image_2': 'Supporto per vari formati immagine inclusi i RAW',
        'help_features_image_3': 'Soglia di somiglianza personalizzabile per un rilevamento accurato',
        'help_features_batch_title': 'Operazioni in Batch',
        'help_features_batch_1': 'Elabora più immagini in una singola operazione',
        'help_features_batch_2': 'Organizzazione automatica dei gruppi di duplicati',
        'help_features_batch_3': 'Salva e carica i risultati del confronto per revisioni successive',
        'help_features_quality_title': 'Controllo Qualità',
        'help_features_quality_1': 'Analisi e confronto della qualità delle immagini',
        'help_features_quality_2': 'Conserva automaticamente la versione di qualità migliore',
        'help_features_quality_3': 'Visualizzazione dettagliata delle informazioni e metadati delle immagini',
        'help_tips_large_title': 'Lavorare con Grandi Collezioni',
        'help_tips_large_1': 'Per grandi collezioni di immagini, considera di scansionare in lotti più piccoli per migliorare le prestazioni',
        'help_tips_large_2': 'Usa la funzione "Escludi Cartelle" per saltare le cartelle di sistema o le directory con file non immagine',
        'help_tips_large_3': 'Salva i tuoi progressi quando lavori con grandi collezioni per evitare di doverle riscanneggiare',
        'help_tips_formats_title': 'Suggerimenti sui Formati Immagine',
        'help_tips_formats_1': 'I file RAW richiedono più tempo per l\'elaborazione ma forniscono il confronto più accurato',
        'help_tips_formats_2': 'Per le migliori prestazioni, converti i file RAW in DNG o TIFF prima del confronto',
        'help_tips_formats_3': 'L\'applicazione può gestire confronti tra formati misti (es. JPG vs PNG)',
        'help_tips_perf_title': 'Ottimizzazione delle Prestazioni',
        'help_tips_perf_1': 'Chiudi altre applicazioni che utilizzano molta memoria durante la scansione di grandi collezioni',
        'help_tips_perf_2': 'Usa l\'anteprima per verificare i duplicati prima di elaborare l\'intera collezione',
        'help_tips_perf_3': 'Regola la soglia di somiglianza per bilanciare precisione e prestazioni',
        'help_tip_3': 'Usa l\'opzione "Mantieni Migliore Qualità" per conservare automaticamente la versione di qualità superiore di ogni duplicato',
        'help_tip_4': 'Seleziona l\'opzione "Mantieni Metadati" per conservare i metadati EXIF e altri metadati durante l\'eliminazione dei duplicati',
        'help_tip_5': 'Usa la funzione di ricerca per trovare rapidamente argomenti specifici della guida',
        'help_emptying_trash': 'Svuotamento del cestino in corso...',
        'help_empty_trash_success': 'Il cestino è stato svuotato con successo',
        'help_empty_trash_failed': 'Impossibile svuotare il cestino: {error}',
        
        # Edit menu
        'edit_menu': {
            'undo': 'Annulla',
            'empty_trash': 'Svuota Cestino',
            'confirm_empty_trash': 'Sei sicuro di voler svuotare il cestino?',
            'empty_trash_success': 'Il cestino è stato svuotato con successo',
            'empty_trash_failed': 'Impossibile svuotare il cestino: {error}'
        },
        
        # Sponsor dialog
        'support_title': 'Supporta Image Deduplicator',
        'support_project': 'Supporta il Progetto',
        'support_project_header': ' Supporta Image Deduplicator',
        'support_project_description': 'Questa applicazione è sviluppata e mantenuta da un singolo sviluppatore.\nIl tuo supporto aiuta a mantenere in vita il progetto e permette di aggiungere nuove funzionalità e miglioramenti.',
        'support_on_patreon': 'Supporta su Patreon',
        'donate_via_paypal': 'Dona con PayPal',
        'buy_me_coffee': 'Offrimi un caffè',
        'bitcoin_donation': 'Dona con Bitcoin',
        'ethereum_donation': 'Dona con Ethereum',
        'copy_address': 'Copia Indirizzo',
        'address_copied': 'Indirizzo Copiato',
        'address_copied_to_clipboard': 'indirizzo copiato negli appunti',
        'support_development': 'Supporta lo Sviluppo',
        'support_app_name': 'Supporta Images-Deduplicator',
        'support_message': 'Se trovi utile questa applicazione, ti invitiamo a supportare il suo sviluppo.\n\nIl tuo supporto aiuta a coprire i costi di hosting e incoraggia ulteriori sviluppi.',
        'github_sponsors': 'GitHub Sponsors',
        'paypal_donation': 'Donazione PayPal',
        'monero': 'Monero',
        'scan_to_donate_xmr': 'Scansiona per donare XMR',
        'qr_generation_failed': 'Generazione codice QR fallita',
        'ways_to_support': 'Modi per Supportare',
        'other_ways_to_help': 'Altri Modi per Aiutare',
        'star_on_github': 'Metti una stella al progetto su',
        'report_bugs': 'Segnala bug e suggerisci funzionalità',
        'share_with_others': 'Condividi con altri che potrebbero trovarlo utile',
        'copied': 'Copiato!',
        'close': 'Chiudi',
        'donate_with_paypal': 'Dona con PayPal',
        'copy_monero_address': 'Copia Indirizzo Monero',
        
        # Log viewer
        'log_viewer': 'Visualizzatore Log',
        'filter_logs': 'Filtra Log',
        'no_log_file': 'Nessun file di log disponibile.',
        'error_reading_log': 'Errore durante la lettura del file di log: {error}',
        'clear_logs': 'Pulisci Log',
        'confirm_clear_logs': 'Sei sicuro di voler cancellare tutti i log? Questa azione non può essere annullata.',
        'save_logs': 'Salva Log',
        'save_log_file': 'Salva File di Log',
        'log_files': 'File di Log (*.log);;Tutti i File (*)',
        'logs_saved': 'Log salvati con successo in: {path}',
        'failed_save_logs': 'Impossibile salvare il file di log: {error}',
        'log_level': 'Livello di Log',
        'all_levels': 'Tutti i Livelli',
        'refresh': 'Aggiorna',
        'select_log_file': 'Seleziona File di Log',
        'no_logs_found': 'Nessun Log Trovato',
        'log_level_filters': 'Filtri Livello Log',
        'clear_log': 'Pulisci Log',
        'save_as': 'Salva come',
        'no_logs_available': 'Nessun Log Disponibile',
        
        # Settings
        'settings': 'Impostazioni',
        'appearance': 'Aspetto',
        'theme': 'Tema',
        'dark_theme': 'Scuro',
        'light_theme': 'Chiaro',
        'comparison_settings': 'Impostazioni di Confronto',
        'similarity_threshold': 'Soglia di Somiglianza',
        'search_subdirectories': 'Cerca nelle sottocartelle',
        'keep_better_quality': 'Mantieni i duplicati di qualità migliore',
        'keep_better_quality_tooltip': 'Se attivato, mantiene la versione di qualità migliore delle immagini duplicate',
        'file_handling': 'Gestione File',
        'preserve_metadata': 'Mantieni i metadati durante l\'eliminazione',
        'preserve_metadata_tooltip': 'Mantiene i metadati (EXIF, ecc.) durante l\'eliminazione dei file duplicati',
        'save': 'Salva',
        'cancel': 'Annulla',
        
        # Edit menu
        'edit_menu': {
            'edit_menu.undo': 'Annulla',
            'edit_menu.nothing_to_undo': 'Nessuna operazione da annullare',
            'edit_menu.undo_success': 'Annullamento completato',
            'edit_menu.undo_failed': 'Errore durante l\'annullamento: {error}',
            'edit_menu.empty_trash_success': 'Cestino vuotato con successo',
            'edit_menu.empty_trash': 'Vuota Cestino',
            'edit_menu.confirm_empty_trash': 'Sei sicuro di voler vuotare il cestino? Questa operazione eliminerà definitivamente tutti i file presenti nel cestino di sistema.',
            'edit_menu.empty_trash_failed': 'Impossibile vuotare il cestino: {error}',
        },
        
        # Update checker
        'update_available': 'Aggiornamento Disponibile',
        'new_version_available': 'È disponibile una nuova versione di Image Deduplicator!',
        'current_version': 'La tua versione: {current_version}',
        'latest_version': 'Ultima versione: {latest_version}',
        'download_update': 'Scarica Aggiornamento',
        'remind_me_later': 'Ricordamelo più tardi',
        'skip_this_version': 'Salta questa versione',
        'checking_for_updates': 'Controllo aggiornamenti in corso...',
        'up_to_date': 'Stai utilizzando l\'ultima versione di Image Deduplicator.',
        'update_error': 'Errore durante il controllo degli aggiornamenti',
        'update_check_failed': 'Impossibile controllare gli aggiornamenti: {error}',
        'release_notes': 'Note di Rilascio',
        'download': 'Scarica',
        'view_changes': 'Visualizza Modifiche',
        'update_available_title': 'Aggiornamento Disponibile',
        'current_version': 'La tua versione: {current_version}',
        'new_version': 'Ultima versione: {latest_version}',

        #missing
        'preparing_scan': 'Preparazione Scansione',
        'comparison_complete': 'Comparazione Completata',
        'confirm_delete_selected': 'Conferma la Cancellazione',
        'confirm_delete_all': 'Conferma la Cancellazione di tutti i file',
        'confirm_delete_all_duplicates': 'Conferma la Cancellazione di tutti i file duplicati',
        'deleting_duplicates': 'Eliminazione Duplicati',
        'Yes': 'Si',
        'No': 'No',
        'moved_to_trash': 'Spostato/i nel cestino',
        'check_for_updates': 'Controllo Aggiornamenti',
        'view_logs': 'Guarda Logs',
        'some_delection_failed': 'Alcune cancellazioni non sono riuscite',
        'system_information': 'Informazioni Sistema',
        'search_subfolders': 'Ricerca Recursiva',
        
        # Empty trash messages
        'empty_trash': {
            'success': {
                'windows': 'Cestino svuotato con successo',
                'macos': 'Cestino svuotato con successo',
                'linux': 'Cestino svuotato con successo',
                'linux_manual': 'Cestino svuotato manualmente (trash-cli non trovato)'
            },
            'error': {
                'windows': 'Impossibile svuotare il Cestino: {error}',
                'macos': 'Impossibile svuotare il Cestino: {error}',
                'linux': 'Impossibile svuotare il cestino: {error}'
            },
            'unsupported_platform': 'Piattaforma non supportata: {platform}'
        },
    },
}

# Backward compatibility function
def t(key: str, lang_code: str = 'en', **kwargs) -> str:
    """
    Get a translated string for the given key and language.
    
    Note: This is kept for backward compatibility. New code should use LanguageManager.
    
    Args:
        key: The translation key
        lang_code: Language code (default: 'en')
        **kwargs: Format arguments for the translation string
        
    Returns:
        str: The translated string or the key if not found
    """
    try:
        translation = TRANSLATIONS.get(lang_code, {}).get(key, 
                     TRANSLATIONS.get('en', {}).get(key, key))
        if isinstance(translation, str) and kwargs:
            return translation.format(**kwargs)
        return translation
    except Exception as e:
        print(f"Translation error for key '{key}': {e}")
        return key
