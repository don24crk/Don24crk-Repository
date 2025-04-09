<script src="https://cdn.jsdelivr.net/npm/hls.js@latest"></script>

<button type="button" onclick="PlayVideo();">Play</button>
<video id="video" controls autoplay crossorigin="anonymous" ></video>

function PlayVideo() {
    var video = document.getElementById('video');
    var videoSrc = "http://line.myunityhost.com/play/live.php?mac=00:1A:79:D8:CE:85&stream=307908&extension=ts&play_token=GMUAfWCMqF";
    if (Hls.isSupported()) {
        // The following hlsjsConfig is required for live-stream
        var hlsjsConfig = {
            "maxBufferSize": 0,
            "maxBufferLength": 30,
            "liveSyncDuration": 30,
            "liveMaxLatencyDuration": Infinity
        }
        var hls = new Hls(hlsjsConfig);
        hls.loadSource(videoSrc);
        hls.attachMedia(video);
        hls.on(Hls.Events.MANIFEST_PARSED, function () {
            video.play();
        });
    } 
    else if (elementId.canPlayType('application/vnd.apple.mpegurl')) {
        elementId.src = videoSrc;
        elementId.addEventListener('loadedmetadata', function () {
            elementId.play();
        });
    }
}