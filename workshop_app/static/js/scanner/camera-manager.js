/**
 * Camera Manager Module
 * Handles camera initialization, access and configuration
 */

// Camera variables
let videoStream = null;

/**
 * Initialize the camera and set up video stream
 * @param {HTMLVideoElement} videoElement - The video element to display the stream
 * @param {HTMLElement} loadingElement - Element showing loading status
 * @param {HTMLElement} overlayElement - Element for showing scanner guides overlay
 * @returns {Promise<boolean>} - Whether camera initialization was successful
 */
async function initializeCamera(videoElement, loadingElement, overlayElement) {
    try {
        // Request camera access - prefer back camera on mobile devices
        videoStream = await navigator.mediaDevices.getUserMedia({
            video: { 
                facingMode: "environment",
                width: { ideal: 1280 },
                height: { ideal: 720 }
            }
        });
        
        // Set video source
        videoElement.srcObject = videoStream;
        
        // Show video when ready
        videoElement.onloadedmetadata = function() {
            loadingElement.classList.add('d-none');
            videoElement.classList.remove('d-none');
            overlayElement.classList.remove('d-none');
            videoElement.play();
        };
        
        return true;
    } catch (error) {
        console.error('Camera access error:', error);
        loadingElement.innerHTML = `
            <div class="alert alert-danger">
                <p><strong>Camera access failed</strong></p>
                <p>${error.message}</p>
                <p>Please ensure you've granted camera permission and are using a supported browser.</p>
            </div>
        `;
        return false;
    }
}

/**
 * Stop the camera stream
 */
function stopCamera() {
    if (videoStream) {
        videoStream.getTracks().forEach(track => track.stop());
        videoStream = null;
    }
}

/**
 * Get the current video dimensions
 * @param {HTMLVideoElement} videoElement - The video element
 * @returns {Object} - The width and height of the video
 */
function getVideoDimensions(videoElement) {
    return {
        width: videoElement.videoWidth,
        height: videoElement.videoHeight
    };
}

/**
 * Check if camera is currently active
 * @returns {boolean} - Whether camera stream is active
 */
function isCameraActive() {
    return videoStream !== null;
}

export { 
    initializeCamera, 
    stopCamera, 
    getVideoDimensions, 
    isCameraActive 
};
