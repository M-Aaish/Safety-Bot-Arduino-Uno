document.addEventListener("DOMContentLoaded", () => {
    
    // Motor Buttons
    const btnForward = document.getElementById('btn-forward');
    const btnReverse = document.getElementById('btn-reverse');
    const btnLeft = document.getElementById('btn-left');
    const btnRight = document.getElementById('btn-right');
    const btnStop = document.getElementById('btn-stop');
    
    // Camera Pan/Tilt Buttons
    const btnCamUp = document.getElementById('btn-cam-up');
    const btnCamDown = document.getElementById('btn-cam-down');
    const btnCamLeft = document.getElementById('btn-cam-left');
    const btnCamRight = document.getElementById('btn-cam-right');
    
    // UI Elements
    const statusText = document.getElementById('status-text');
    const statusDot = document.getElementById('status-dot');
    
    // Camera Feed Elements
    const cameraFeed = document.getElementById('camera-feed');
    const btnToggleCam = document.getElementById('btn-toggle-cam');
    const videoOverlay = document.getElementById('video-overlay');
    const overlayMsg = document.getElementById('overlay-msg');
    const loadingSpinner = document.getElementById('loading-spinner');

    let cameraEnabled = true;
    let firstFrameReceived = false;

    // ==========================================
    // 1. ROBOT MOVEMENT EVENTS
    // ==========================================
    btnForward.addEventListener('click', () => ui.sendMessage('motor_forward', {}));
    btnReverse.addEventListener('click', () => ui.sendMessage('motor_reverse', {}));
    btnLeft.addEventListener('click', () => ui.sendMessage('motor_left', {}));
    btnRight.addEventListener('click', () => ui.sendMessage('motor_right', {}));
    
    btnStop.addEventListener('click', () => {
        ui.sendMessage('motor_stop', {});
        updateMotorStatus("MOTOR IS STOPPED", true); // Optimistic UI update
    });

    // ==========================================
    // 2. CAMERA PAN/TILT EVENTS
    // ==========================================
    btnCamUp.addEventListener('click', () => ui.sendMessage('camera_up', {}));
    btnCamDown.addEventListener('click', () => ui.sendMessage('camera_down', {}));
    btnCamLeft.addEventListener('click', () => ui.sendMessage('camera_left', {}));
    btnCamRight.addEventListener('click', () => ui.sendMessage('camera_right', {}));

    // ==========================================
    // 3. CAMERA TOGGLE LOGIC
    // ==========================================
    btnToggleCam.addEventListener('click', () => {
        cameraEnabled = !cameraEnabled;
        
        if (cameraEnabled) {
            btnToggleCam.innerText = "Disable Camera Feed";
            btnToggleCam.style.borderColor = "#3E4663";
            btnToggleCam.style.color = "#E2E8F0";
            
            // Show loading overlay again until the next frame arrives
            cameraFeed.style.display = "none";
            videoOverlay.style.display = "flex";
            loadingSpinner.style.display = "block";
            overlayMsg.innerHTML = "Resuming secure camera feed...<br>Please hold tight.";
            firstFrameReceived = false;
        } else {
            btnToggleCam.innerText = "Enable Camera Feed";
            btnToggleCam.style.borderColor = "#FF3366";
            btnToggleCam.style.color = "#FF3366";
            
            // Show disabled message and hide the image
            cameraFeed.style.display = "none";
            videoOverlay.style.display = "flex";
            loadingSpinner.style.display = "none"; // Hide spinner when intentionally disabled
            overlayMsg.innerHTML = "Camera Feed Offline.<br>Click 'Enable' to resume.";
        }
    });

    // ==========================================
    // 4. RECEIVE LIVE CAMERA FRAMES
    // ==========================================
    ui.onMessage('camera_frame', (data) => {
        // Ignore frames if the user intentionally turned the camera off
        if (!cameraEnabled || !cameraFeed) return;

        // Hide overlay and show image on the very first frame
        if (!firstFrameReceived) {
            videoOverlay.style.display = "none";
            cameraFeed.style.display = "block";
            firstFrameReceived = true;
        }

        // Parse and render the image
        if (typeof data === 'string') {
            if (data.includes("data:image")) {
                let match = data.match(/data:image[^'"]+/);
                if (match) cameraFeed.src = match[0];
            }
        } else if (data && data.image) {
            cameraFeed.src = data.image;
        }
    });

    // ==========================================
    // 5. STATUS INDICATOR HELPER
    // ==========================================
    function updateMotorStatus(text, isStopped) {
        statusText.innerText = text;
        if (isStopped) {
            statusText.style.color = "#FF3366"; // Red
            statusDot.style.background = "#FF3366";
            statusDot.style.boxShadow = "0 0 10px #FF3366";
        } else {
            statusText.style.color = "#00E5FF"; // Cyan
            statusDot.style.background = "#00E5FF";
            statusDot.style.boxShadow = "0 0 10px #00E5FF";
        }
    }

    // Listen for motor status updates from python
    ui.onMessage('motor_status_update', (data) => {
        if (data && data.status_text) {
            const isStopped = data.status_text.toUpperCase().includes('STOP');
            updateMotorStatus(data.status_text, isStopped);
        }
    });

    // Request initial state on load
    ui.sendMessage('get_initial_state', {});
});