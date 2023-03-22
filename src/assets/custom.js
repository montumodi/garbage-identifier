// function delay(t, v) {
//     return new Promise(resolve => setTimeout(resolve, t, v));
// }

// document.addEventListener("DOMContentLoaded", () => {
//     if (navigator.mediaDevices.getUserMedia) {
//         navigator.mediaDevices.getUserMedia({ video: {
//             facingMode: 'environment'
//         }})
//             .then(async function (stream) {
//                 var video = document.querySelector("#videoElement");
//                 if (video) {
//                     console.log("herere");
//                     video.srcObject = stream;

//                 }
                
//             })
//             .catch(function (err0r) {
//                 console.log("Something went wrong!", err0r);
//             });
//     }
// });
 