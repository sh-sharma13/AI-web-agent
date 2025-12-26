console.log("BlueLays: Content script loaded");

let trackedVideo = null;

function notifyBackground(action, data) {
    try {
        chrome.runtime.sendMessage({ action: action, data: data });
    } catch (e) {
        console.log("BlueLays: Background disconnected");
    }
}

if (location.hostname.includes("youtube.com")) {
    let currentUrl = location.href;

    function attachYouTubeListener() {
        if (location.href !== currentUrl) {
            console.log("BlueLays: URL changed, resetting tracker");
            currentUrl = location.href;
            if (trackedVideo) {
                delete trackedVideo.dataset.logged;
                trackedVideo = null;
            }
        }

        const video = document.querySelector("video");
        if (video && video !== trackedVideo) {
            console.log("BlueLays: Tracking new YouTube video");
            trackedVideo = video;
            delete video.dataset.logged;

            video.addEventListener("timeupdate", () => {
                if (video.duration > 0 && video.currentTime >= video.duration - 2) {
                    if (!video.dataset.logged) {
                        console.log("BlueLays: Video Limit Reached (Timeupdate)");
                        video.dataset.logged = "true";
                        notifyBackground("VIDEO_COMPLETED", {
                            url: location.href,
                            title: document.title,
                            platform: "YouTube"
                        });
                    }
                }
            });

            video.addEventListener("ended", () => {
                if (!video.dataset.logged) {
                    console.log("BlueLays: Video Finished (Ended Event)");
                    video.dataset.logged = "true";
                    notifyBackground("VIDEO_COMPLETED", {
                        url: location.href,
                        title: document.title,
                        platform: "YouTube"
                    });
                }
            });
        }
    }

    setInterval(attachYouTubeListener, 2000);
}

if (location.hostname.includes("udemy.com")) {
    function attachUdemyListener() {
        const video = document.querySelector("video");
        if (video && video !== trackedVideo) {
            console.log("BlueLays: Tracking new Udemy video");
            trackedVideo = video;

            video.addEventListener("ended", () => {
                console.log("BlueLays: Lecture Finished");
                notifyBackground("VIDEO_COMPLETED", {
                    url: location.href,
                    title: document.title,
                    platform: "Udemy"
                });
            });
        }
    }
    setInterval(attachUdemyListener, 3000);
}
