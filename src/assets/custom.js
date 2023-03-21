function delay(t, v) {
    return new Promise(resolve => setTimeout(resolve, t, v));
}

document.addEventListener("DOMContentLoaded", () => {
    if (navigator.mediaDevices.getUserMedia) {
        navigator.mediaDevices.getUserMedia({ video: true })
            .then(async function (stream) {
                var video = document.querySelector("#videoElement");
                if (video) {
                    console.log("herere");
                    video.srcObject = stream;

                    await delay(1000);

                    const canvas = document.querySelector('#screenshot-canvas'); // select the video element
                    const contentsCamera = document.querySelector('#contentsCamera'); // select the video element
                    const secretId = document.querySelector('#secretId'); // select the video element

                    // const canvas = document.createElement('canvas'); // create a canvas element
                    const ctx = canvas.getContext('2d'); // get the context of the canvas element

                    function capture() {

                        // set the width and height of the canvas to match the video
                        canvas.width = video.videoWidth;
                        canvas.height = video.videoHeight;
                        // draw the current video frame onto the canvas
                        ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
                        
                        // convert the canvas data to an image data URL
                        const imageDataUrl = canvas.toDataURL('image/png');
                        // do something with the image data URL, such as display it on the page or send it to a server
                        contentsCamera.src = imageDataUrl;
                        secretId.value = imageDataUrl;
                        // schedule the next frame capture
                        requestAnimationFrame(capture);
                    }

                    // start capturing frames
                    requestAnimationFrame(capture);
                }
                
            })
            .catch(function (err0r) {
                console.log("Something went wrong!", err0r);
            });
    }
});
 