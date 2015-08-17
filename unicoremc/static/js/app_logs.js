$(document).ready(function() {
    var stdout = new AppLog('#logs', function (msg) {
        $("<div class='entry stdout'/>").text(msg).appendTo(this.target);
    });

    stdout_es = new EventSource('/es/');
    stdout_es.addEventListener("message", function (event) {
        stdout.log(event.data);
    });

    var stderr = new AppLog('#logs', function (msg) {
        $("<div class='entry stderr'/>").text(msg).appendTo(this.target);
    });

    stderr_es = new EventSource('/es/');
    stderr_es.addEventListener("message", function (event) {
        stderr.log(event.data);
    });
});

var AppLog = function (target, cb) {
    this.target = $(target);
    this.cb = cb || function (log) {
        console.log('No callback: ' + log);
    };
};

AppLog.prototype.log = function (msg) {
    this.cb(msg);
    this.scroll();
}

AppLog.prototype.scroll = function () {
    var height = this.target.get(0).scrollHeight;
    this.target.animate({
        scrollTop: height
    }, 500);
};
