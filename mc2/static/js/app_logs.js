var AppLog = function (target, cb) {
    this.target = $(target);
    this.cb = cb || function (log) {
        console.log('No callback: ' + log);
    };
};

AppLog.prototype.log = function (msg) {
    var scrollit = this.atBottom();
    this.cb(msg);
    if(scrollit) {
        this.scroll();
    }
}

AppLog.prototype.atBottom = function () {
    return (this.target.prop('scrollTop') + this.target.prop('offsetHeight')) >= this.target.prop('scrollHeight');
}

AppLog.prototype.scroll = function () {
    var height = this.target.get(0).scrollHeight;
    this.target.animate({
        scrollTop: height
    }, 10);
};
