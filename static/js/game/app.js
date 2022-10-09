//map data
// const noteInfo = eval("{{data[ 'noteInfo']}} ");
// const stackLeniency = eval("{{data[ 'stackLeniency']}} ");
// const previewTime = eval("{{data[ 'previewTime']}} ");
// const countdown = eval("{{data[ 'countdown']}} ");
// const songName = "{{data[ 'songName']}} ";
// const songWriter = "{{data[ 'songWriter']}} ";

const music = document.querySelector('#music');

const c = document.querySelector("canvas");
const ctx = c.getContext("2d");

let speed = 4;
let HP = 10;

// notes
var lane1 = [];
var lane2 = [];
var lane3 = [];
var lane4 = [];

var noteInScreen = [];

let lane1ptr = 0;
let lane2ptr = 0;
let lane3ptr = 0;
let lane4ptr = 0;

// Class
class Note {
    constructor(x, y, color) {
        this.x = x;
        this.y = y;

        this.color = color;
    }

    draw() {
        ctx.beginPath();
        ctx.fillRect(this.x, this.y, 100, 20);
        ctx.fillStyle = this.color;
        ctx.fill();
    }
    update() {
        this.draw();
        this.y = this.y + speed;
    }
}

//functions

function noteGenerate() {

    for (let i = 0; i < noteInfo.length; i++) {
        if (noteInfo[i][0] == 64) {
            lane1.push(noteInfo[i][1]);
        } else if (noteInfo[i][0] == 192) {
            lane2.push(noteInfo[i][1]);
        } else if (noteInfo[i][0] == 320) {
            lane3.push(noteInfo[i][1]);
        } else if (noteInfo[i][0] == 448) {
            lane4.push(noteInfo[i][1]);
        }
    }
    lane1.push(-1);
    lane2.push(-1);
    lane3.push(-1);
    lane4.push(-1);
}

function gamePlay() {
    music.volume = 0.2;
    music.play();
}

function init() {
    noteGenerate();
    animate();
}

/**
 * 매 프레임 반복구간(주 실행구간)
 */
function animate() {
    animationId = requestAnimationFrame(animate);

    for (let i = 0; i < noteInScreen.length; i++) {
        noteInScreen[i].update();
        if (noteInScreen[i].y > 700) {
            // 
        }
    }

    const musicTime = music.currentTime * 1000; //ms 단위이므로 1000곱함.

    if (musicTime >= lane1[lane1ptr]) {
        var note1 = new Note(100, 0, 'white');
        note1.draw();
        noteInScreen.push(note1);
        lane1ptr++;
    }
    if (musicTime >= lane2[lane2ptr]) {
        var note2 = new Note(200, 0, 'white');
        note2.draw();
        noteInScreen.push(note2);
        lane2ptr++;
    }
    if (musicTime >= lane3[lane3ptr]) {
        var note3 = new Note(300, 0, 'white');
        note3.draw();
        noteInScreen.push(note3);
        lane3ptr++;
    }
    if (musicTime >= lane4[lane4ptr]) {
        var note4 = new Note(400, 0, 'white');
        note4.draw();
        noteInScreen.push(note4);
        lane4ptr++;
    }
}

// event listeners
window.addEventListener("keydown", (e) => {
    if (e.code == 'Enter') { // 시작
        gamePlay();
    } else if (e.code == 'Escape') { // esc
        music.pause();
    } else if (e.code == 'KeyD') {
        console.log("D");
    } else if (e.code == 'KeyF') {
        console.log("f");
    } else if (e.code == 'KeyJ') {
        console.log("j");
    } else if (e.code == 'KeyK') {
        console.log("k");
    }
});

init();