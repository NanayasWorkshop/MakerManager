/**
 * Code Detector Module
 * Handles QR code detection from video frames
 */

/**
 * Process a video frame to detect QR codes
 * @param {HTMLVideoElement} videoElement - The video element to capture frames from
 * @param {HTMLCanvasElement} canvasElement - Canvas element for processing the frame
 * @returns {Object|null} - The decoded QR code object or null if none detected
 */
function detectCodeInFrame(videoElement, canvasElement) {
    if (!videoElement || !canvasElement) return null;
    
    const context = canvasElement.getContext('2d');
    
    // Ensure canvas dimensions match video
    if (canvasElement.width !== videoElement.videoWidth || 
        canvasElement.height !== videoElement.videoHeight) {
        canvasElement.width = videoElement.videoWidth;
        canvasElement.height = videoElement.videoHeight;
    }
    
    // Draw the current video frame to the canvas
    context.drawImage(videoElement, 0, 0, canvasElement.width, canvasElement.height);
    
    // Get image data for processing
    const imageData = context.getImageData(0, 0, canvasElement.width, canvasElement.height);
    
    try {
        // Use jsQR to detect QR codes
        // This assumes jsQR is loaded globally via a script tag
        const code = jsQR(imageData.data, imageData.width, imageData.height, {
            inversionAttempts: "dontInvert",
        });
        
        return code;
    } catch (error) {
        console.error('Error detecting QR code:', error);
        return null;
    }
}

/**
 * Create a highlight effect on detected code
 * @param {Object} code - The detected code object from jsQR
 * @param {CanvasRenderingContext2D} context - Canvas context for drawing
 */
function highlightDetectedCode(code, context) {
    if (!code || !context) return;
    
    // Draw bounding box around detected code
    context.lineWidth = 4;
    context.strokeStyle = "#FF3B58";
    context.beginPath();
    
    // Draw each corner of the QR code
    const { topLeftCorner, topRightCorner, bottomLeftCorner, bottomRightCorner } = code.location;
    context.moveTo(topLeftCorner.x, topLeftCorner.y);
    context.lineTo(topRightCorner.x, topRightCorner.y);
    context.lineTo(bottomRightCorner.x, bottomRightCorner.y);
    context.lineTo(bottomLeftCorner.x, bottomLeftCorner.y);
    context.lineTo(topLeftCorner.x, topLeftCorner.y);
    
    context.stroke();
    
    // Draw data text
    context.font = "16px Arial";
    context.fillStyle = "#FF3B58";
    context.fillText(code.data.substring(0, 20) + (code.data.length > 20 ? '...' : ''), 
                    topLeftCorner.x, topLeftCorner.y - 10);
}

export { 
    detectCodeInFrame, 
    highlightDetectedCode 
};
