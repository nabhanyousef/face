const video = document.getElementById('video');
const canvas = document.getElementById('canvas');
const captureBtn = document.getElementById('capture-btn');
const imageInput = document.getElementById('image-input');
const uploadForm = document.getElementById('upload-form');

// Access the camera
navigator.mediaDevices.getUserMedia({ video: true })
    .then(stream => {
        video.srcObject = stream;
    })
    .catch(err => {
        console.error("Error accessing the camera: ", err);
    });

// Draw ellipse overlay on the video
const drawEllipse = () => {
    const context = canvas.getContext('2d');
    context.clearRect(0, 0, canvas.width, canvas.height); // Clear the canvas

    // Draw ellipse
    context.beginPath();
    context.ellipse(canvas.width / 2, canvas.height / 2, 200, 250, 0, 0, 2 * Math.PI); // Adjust ellipse size
    context.strokeStyle = 'rgba(255, 255, 255, 0.8)';
    context.lineWidth = 4;
    context.stroke();
};

// Capture image and crop to ellipse
captureBtn.addEventListener('click', () => {
    const context = canvas.getContext('2d');
    context.drawImage(video, 0, 0, canvas.width, canvas.height);

    // Create a temporary canvas to crop the image to the ellipse
    const tempCanvas = document.createElement('canvas');
    const tempContext = tempCanvas.getContext('2d');
    tempCanvas.width = canvas.width;
    tempCanvas.height = canvas.height;

    // Draw the ellipse on the temporary canvas
    tempContext.beginPath();
    tempContext.ellipse(tempCanvas.width / 2, tempCanvas.height / 2, 200, 250, 0, 0, 2 * Math.PI);
    tempContext.clip(); // Clip to the ellipse
    tempContext.drawImage(canvas, 0, 0); // Draw the captured image inside the ellipse

    // Convert the cropped image to base64
    const croppedImageData = tempCanvas.toDataURL('image/png');
    imageInput.value = croppedImageData;
    uploadForm.submit();
});

// Continuously draw the ellipse overlay
video.addEventListener('play', () => {
    function draw() {
        drawEllipse();
        requestAnimationFrame(draw);
    }
    draw();
});