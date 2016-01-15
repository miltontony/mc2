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
