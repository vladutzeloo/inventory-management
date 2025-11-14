/**
 * Warehouse UX Enhancements
 * - Keyboard shortcuts
 * - Barcode scanner support
 * - Confirmation dialogs
 * - Visual feedback
 */

(function() {
    'use strict';

    // ===== KEYBOARD SHORTCUTS =====
    const shortcuts = {
        'n': { url: null, description: 'New (context-dependent)', handler: handleNewShortcut },
        'r': { url: '/receipts/new', description: 'New Receipt' },
        't': { url: '/transfers/new', description: 'New Transfer' },
        'a': { url: '/adjustments/new', description: 'New Adjustment' },
        's': { url: '/scraps/new', description: 'New Scrap' },
        'd': { url: '/dashboard', description: 'Dashboard' },
        '/': { description: 'Search', handler: focusSearch },
        '?': { description: 'Show Shortcuts', handler: showShortcutsHelp },
        'Escape': { description: 'Cancel/Close', handler: handleEscape }
    };

    // Initialize keyboard shortcuts
    document.addEventListener('keydown', function(e) {
        // Don't trigger if typing in input/textarea
        if (e.target.tagName === 'INPUT' ||
            e.target.tagName === 'TEXTAREA' ||
            e.target.tagName === 'SELECT') {
            return;
        }

        const key = e.key.toLowerCase();
        const shortcut = shortcuts[e.key] || shortcuts[key];

        if (shortcut) {
            e.preventDefault();
            if (shortcut.handler) {
                shortcut.handler();
            } else if (shortcut.url) {
                window.location.href = shortcut.url;
            }
        }
    });

    function handleNewShortcut() {
        // Try to find "Add" or "New" button on current page
        const newBtn = document.querySelector('a[href*="/new"]') ||
                      document.querySelector('.btn-primary[href*="/new"]');
        if (newBtn) {
            newBtn.click();
        }
    }

    function focusSearch() {
        const searchInput = document.querySelector('input[name="search"]') ||
                          document.querySelector('input[type="search"]');
        if (searchInput) {
            searchInput.focus();
        }
    }

    function handleEscape() {
        // Close any open modals or dialogs
        const dialog = document.querySelector('.confirm-dialog.show');
        if (dialog) {
            dialog.classList.remove('show');
        }
    }

    function showShortcutsHelp() {
        let helpText = '<div style="text-align: left; color: #1e293b !important;"><h4>Keyboard Shortcuts</h4><ul>';
        for (let key in shortcuts) {
            if (shortcuts[key].description) {
                helpText += `<li><kbd>${key.toUpperCase()}</kbd> - ${shortcuts[key].description}</li>`;
            }
        }
        helpText += '</ul></div>';
        showAlert(helpText, 'info', false, 0);
    }

    // ===== BARCODE SCANNER SUPPORT =====
    let barcodeBuffer = '';
    let barcodeTimeout = null;

    document.addEventListener('keypress', function(e) {
        // Barcode scanners typically send input very quickly
        // We'll capture rapid keystrokes as potential barcode input

        if (e.target.tagName === 'INPUT' && e.target.classList.contains('barcode-input')) {
            return; // Let the input handle it normally
        }

        // Clear timeout if still typing
        if (barcodeTimeout) {
            clearTimeout(barcodeTimeout);
        }

        // Add character to buffer
        if (e.key && e.key.length === 1) {
            barcodeBuffer += e.key;
        }

        // Process buffer after 100ms of no input (scanner finished)
        barcodeTimeout = setTimeout(function() {
            if (barcodeBuffer.length >= 4) { // Minimum barcode length
                processBarcodeInput(barcodeBuffer);
            }
            barcodeBuffer = '';
        }, 100);
    });

    function processBarcodeInput(barcode) {
        // Find barcode input field and populate it
        const barcodeInput = document.querySelector('.barcode-input') ||
                           document.querySelector('input[name*="barcode"]') ||
                           document.querySelector('input[name*="batch"]');

        if (barcodeInput) {
            barcodeInput.value = barcode;
            barcodeInput.classList.add('success-state');
            setTimeout(() => barcodeInput.classList.remove('success-state'), 500);

            // Try to submit or move to next field
            const form = barcodeInput.closest('form');
            if (form) {
                // Focus next input
                const inputs = Array.from(form.querySelectorAll('input, select'));
                const currentIndex = inputs.indexOf(barcodeInput);
                if (currentIndex >= 0 && currentIndex < inputs.length - 1) {
                    inputs[currentIndex + 1].focus();
                }
            }
        }
    }

    // ===== CONFIRMATION DIALOGS =====

    // Create confirmation dialog HTML
    const confirmDialogHTML = `
        <div id="confirmDialog" class="confirm-dialog">
            <div class="confirm-content">
                <h3 id="confirmTitle">Confirm Action</h3>
                <p id="confirmMessage">Are you sure?</p>
                <div class="confirm-buttons">
                    <button type="button" class="btn btn-secondary" onclick="window.closeConfirmDialog()">
                        Cancel
                    </button>
                    <button type="button" class="btn btn-danger" id="confirmBtn">
                        Confirm
                    </button>
                </div>
            </div>
        </div>
    `;

    // Add dialog to page
    document.addEventListener('DOMContentLoaded', function() {
        if (!document.getElementById('confirmDialog')) {
            document.body.insertAdjacentHTML('beforeend', confirmDialogHTML);
        }

        // Add confirmation to all delete buttons
        addDeleteConfirmations();

        // Add visual enhancements
        enhanceFormInputs();

        // Add shortcut hints to buttons
        addShortcutHints();
    });

    function addDeleteConfirmations() {
        // Find all delete buttons/forms
        const deleteButtons = document.querySelectorAll('button[type="submit"][class*="danger"],' +
                                                       'form[action*="/delete"] button[type="submit"],' +
                                                       '.btn-danger[onclick*="delete"]');

        deleteButtons.forEach(btn => {
            const form = btn.closest('form');
            if (form && form.action.includes('/delete')) {
                form.addEventListener('submit', function(e) {
                    e.preventDefault();

                    const itemType = form.dataset.itemType || 'this item';
                    const itemName = form.dataset.itemName || '';

                    showConfirmDialog(
                        'Confirm Deletion',
                        `Are you sure you want to delete ${itemName ? '"' + itemName + '"' : itemType}? This action cannot be undone.`,
                        function() {
                            form.submit();
                        }
                    );
                });
            }
        });
    }

    window.showConfirmDialog = function(title, message, onConfirm) {
        const dialog = document.getElementById('confirmDialog');
        const titleEl = document.getElementById('confirmTitle');
        const messageEl = document.getElementById('confirmMessage');
        const confirmBtn = document.getElementById('confirmBtn');

        titleEl.textContent = title;
        messageEl.textContent = message;

        // Remove old listeners
        const newConfirmBtn = confirmBtn.cloneNode(true);
        confirmBtn.parentNode.replaceChild(newConfirmBtn, confirmBtn);

        // Add new listener
        newConfirmBtn.addEventListener('click', function() {
            window.closeConfirmDialog();
            if (onConfirm) onConfirm();
        });

        dialog.classList.add('show');
    };

    window.closeConfirmDialog = function() {
        const dialog = document.getElementById('confirmDialog');
        dialog.classList.remove('show');
    };

    // ===== FORM ENHANCEMENTS =====

    function enhanceFormInputs() {
        // Make primary inputs larger for warehouse workers
        const forms = document.querySelectorAll('form');
        forms.forEach(form => {
            // Find quantity and barcode inputs
            const qtyInputs = form.querySelectorAll('input[name*="quantity"]');
            const barcodeInputs = form.querySelectorAll('input[name*="batch"], input[name*="barcode"]');

            qtyInputs.forEach(input => {
                if (!input.classList.contains('form-control-lg')) {
                    input.classList.add('form-control-lg');
                }
            });

            barcodeInputs.forEach(input => {
                input.classList.add('barcode-input');
            });
        });

        // Add enter key support for forms
        const inputs = document.querySelectorAll('input:not([type="submit"])');
        inputs.forEach((input, index) => {
            input.addEventListener('keydown', function(e) {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();

                    // Move to next input or submit
                    const allInputs = Array.from(document.querySelectorAll('input:not([type="submit"]), select, textarea'));
                    const currentIndex = allInputs.indexOf(input);

                    if (currentIndex < allInputs.length - 1) {
                        allInputs[currentIndex + 1].focus();
                    } else {
                        // Submit form
                        const submitBtn = input.closest('form')?.querySelector('button[type="submit"]');
                        if (submitBtn) submitBtn.click();
                    }
                }
            });
        });
    }

    function addShortcutHints() {
        // Add keyboard shortcut hints to navigation items
        const navLinks = document.querySelectorAll('.navbar-nav .nav-link');
        navLinks.forEach(link => {
            const href = link.getAttribute('href');
            if (href) {
                for (let key in shortcuts) {
                    if (shortcuts[key].url && href.includes(shortcuts[key].url)) {
                        if (!link.querySelector('.shortcut-hint')) {
                            link.insertAdjacentHTML('beforeend',
                                ` <span class="shortcut-hint">${key.toUpperCase()}</span>`);
                        }
                        break;
                    }
                }
            }
        });
    }

    // ===== UTILITY FUNCTIONS =====

    function showAlert(message, type = 'info', autoClose = true, duration = 3000) {
        const alertHTML = `
            <div class="alert alert-${type} alert-lg alert-dismissible fade show" role="alert"
                 style="position: fixed; top: 80px; right: 20px; z-index: 9999; min-width: 300px;">
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        `;

        document.body.insertAdjacentHTML('beforeend', alertHTML);

        if (autoClose) {
            setTimeout(() => {
                const alert = document.querySelector('.alert-dismissible');
                if (alert) {
                    alert.remove();
                }
            }, duration);
        }
    }

    // Expose utility functions globally
    window.warehouseUtils = {
        showAlert,
        showConfirmDialog: window.showConfirmDialog,
        closeConfirmDialog: window.closeConfirmDialog
    };

    // ===== VISUAL FEEDBACK =====

    // Add success/error feedback on form submissions
    document.addEventListener('DOMContentLoaded', function() {
        const forms = document.querySelectorAll('form');
        forms.forEach(form => {
            form.addEventListener('submit', function() {
                const submitBtn = form.querySelector('button[type="submit"]');
                if (submitBtn && !submitBtn.disabled) {
                    submitBtn.disabled = true;
                    submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Processing...';

                    // Show loading overlay
                    const loadingHTML = `
                        <div class="warehouse-loading">
                            <div class="spinner-border text-primary" role="status"></div>
                            <div class="mt-3" style="color: #1e293b;">Processing...</div>
                        </div>
                    `;
                    document.body.insertAdjacentHTML('beforeend', loadingHTML);
                }
            });
        });
    });

    // Auto-focus first input on page load
    document.addEventListener('DOMContentLoaded', function() {
        const firstInput = document.querySelector('form input:not([type="hidden"]):not([disabled])');
        if (firstInput && !document.querySelector('input:focus')) {
            setTimeout(() => firstInput.focus(), 100);
        }
    });

    console.log('Warehouse UX enhancements loaded successfully');
})();
