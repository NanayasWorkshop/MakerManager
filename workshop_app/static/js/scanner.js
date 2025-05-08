/**
 * Workshop Management System - Scanner Functionality
 * Main entry point for the scanner component
 */

import { initScanner } from './scanner/scanner-main.js';

document.addEventListener('DOMContentLoaded', function() {
    // DOM Elements
    const elements = {
        video: document.getElementById('scanner-video'),
        canvas: document.getElementById('scanner-canvas'),
        loadingElement: document.getElementById('scanner-loading'),
        overlayElement: document.getElementById('scanner-overlay'),
        startButton: document.getElementById('startScanButton'),
        stopButton: document.getElementById('stopScanButton'),
        manualEntryLink: document.getElementById('manualEntryLink'),
        manualEntryForm: document.getElementById('manualEntryForm')
    };
    
    // Get CSRF token for AJAX requests
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    
    // Initialize scanner
    initScanner(elements, csrfToken);
});
