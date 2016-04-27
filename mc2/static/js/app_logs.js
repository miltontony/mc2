var AppLog = function (target, cb) {
    this.init_scroll = true;
    this.target = $(target);
    this.cb = cb || function (log) {
        console.log('No callback: ' + log);
    };
};

AppLog.prototype.log = function (msg) {
    var scrollit = this.atBottom();
    this.cb(msg);
    if(scrollit || this.init_scroll) {
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
    this.init_scroll = false;
};
