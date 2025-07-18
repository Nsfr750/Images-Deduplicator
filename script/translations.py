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
        
        # Help dialog
        'help_title': 'Image Deduplicator Help',
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
            'nothing_to_undo': 'Nothing to undo',
            'undo_success': 'Undo successful',
            'undo_failed': 'Failed to undo operation: {error}',
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
        'copyright': '© 2025 Nsfr750',
        'license': 'Licenza: GPLv3',
        'about_description': 'Un potente strumento per trovare e gestire immagini duplicate nella tua collezione.',
        'system_info': 'Informazioni Sistema:',
        'operating_system': 'Sistema Operativo:',
        'python_version': 'Versione Python:',
        'qt_version': 'Versione PyQt:',
        'cpu_info': 'CPU:',
        'memory_info': 'RAM:',

        # Help dialog
        'help_title': 'Guida di Image Deduplicator',
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
            'undo': 'Annulla',
            'nothing_to_undo': 'Niente da annullare',
            'undo_success': 'Annullamento riuscito',
            'undo_failed': 'Impossibile annullare l\'operazione: {error}',
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
        'edit_menu.undo': 'Annulla',
        'some_delection_failed': 'Alcune cancellazioni non sono riuscite',
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
