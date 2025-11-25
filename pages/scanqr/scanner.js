const video = document.getElementById("video");
const canvas = document.createElement("canvas");
const ctx = canvas.getContext("2d");

// Start camera
async function startCamera() {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({
      video: { facingMode: "environment" }
    });

    video.srcObject = stream;
    video.play();

    requestAnimationFrame(tick);
  } catch (err) {
    console.error("Camera error:", err);
    alert("Cannot access camera. Please allow camera permission.");
  }
}

function tick() {
  if (video.readyState === video.HAVE_ENOUGH_DATA) {
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

    const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
    const code = jsQR(imageData.data, canvas.width, canvas.height);

    if (code && code.data) {
      console.log("QR detected:", code.data);

      // Expecting the QR content to be a FULL URL:
      // e.g. http://127.0.0.1:5500/pages/scanqr/index.html?tableId=12
      // Let the browser navigate to it. Then qr.js will set cookies & redirect to /menu.
      window.location.href = code.data;
      return; // stop scanning after success
    }
  }

  requestAnimationFrame(tick);
}

startCamera();
