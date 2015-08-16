$(document).ready(function() {
    var al = new AppLog('#logs', function (msg) {
        $("<div class='entry'/>").text(msg).appendTo(this.target);
    });

    window.setInterval(function () {
        al.log(new Date());
    }, 500);
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
