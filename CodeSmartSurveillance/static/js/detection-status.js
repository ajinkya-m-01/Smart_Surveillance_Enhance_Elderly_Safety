// Simple Video Manager - Fullscreen only
class VideoManager {
    constructor() {
        this.init();
    }

    init() {
        const fullScreenBtn = document.querySelector('[title="Full Screen"]');
        if (fullScreenBtn) {
            fullScreenBtn.addEventListener('click', this.toggleFullScreen);
        }
    }

    toggleFullScreen() {
        const videoStream = document.getElementById('videoStream');
        if (!videoStream) return;
        
        if (!document.fullscreenElement) {
            videoStream.requestFullscreen().catch(err => {
                console.error(`Error attempting to enable full-screen mode: ${err.message}`);
            });
        } else {
            document.exitFullscreen();
        }
    }
}

document.addEventListener('DOMContentLoaded', () => {
    new VideoManager();
});
