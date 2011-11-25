var audio = null;
var reverseTime = false;

function initSoundManagerPlayer() {
    soundManager.url = 'js/';
    soundManager.flashLoadTimeout = 10000;

    soundManager.onready(function() {
        info("soundManager ready");
        audioReady();
    });

    soundManager.ontimeout(function(status) {
        error("SM2 error. Is flash blocked or missing? The status is "  
            + status.success + ', the error type is ' + status.error.type);
    });
}

function toggleReverseTime() {
    reverseTime = !reverseTime;
}

function audioPlay(mp3) {
    if (mp3 != null) {
        audioCleanup();               // stop the previous play
        var track_time = $("#track-time");
        var lastPosition = 0;
        audio = soundManager.createSound({
            id: 'sound',
            url: mp3,
            onfinish: nextTrack,
            whileplaying: function () {
              var position = this.position;
              if (position - lastPosition > 1000) {
                  lastPosition = position;
                  if (reverseTime) {
                       if (this.duration > this.position) {
                           position = this.duration - this.position; 
                       }
                  }
                  track_time.text(fmtTime(position));
              }
            }
        });
        setPlaying(true);
        audio.play();
    } 
}

function audioCleanup() {
    if (audio) {
        audio.pause();
        audio.destruct();
        audio = null;
    }
}



function audioStop() {
    setPlaying(false);
}

function audioPause() {
    setPlaying(false);
    if (audio) {
        audio.pause();
    }
}

function audioResume() {
    setPlaying(true);
    if (audio) {
        audio.resume();
    }
}

function audioMute() {
    soundManager.mute();
}

function audioUnMute() {
    soundManager.unmute();
}

// Reverses how we display time. When reversed we
// show the amount of time remaining in the song
//
function toggleReverseTime() {
    reverseTime = !reverseTime;
}

function fmtTime(position) {
    position = position / 1000;
    var mins = Math.floor(position / 60);
    var secs = Math.floor(position - mins * 60);

    if (mins < 10) {
        mins = "0" + mins;
    }

    if (secs < 10) {
        secs = "0" + secs;
    }
    return mins + ":" + secs;
}
