"use strict";
function i(t, e) {
    var n = (65535 & t) + (65535 & e);
    return (t >> 16) + (e >> 16) + (n >> 16) << 16 | 65535 & n
}
function a(t, e, n, r, o, a) {
    return i((c = i(i(e, t), i(r, a))) << (u = o) | c >>> 32 - u, n);
    var c, u
}
function c(t, e, n, r, o, i, c) {
    return a(e & n | ~e & r, t, e, o, i, c)
}
function u(t, e, n, r, o, i, c) {
    return a(e & r | n & ~r, t, e, o, i, c)
}
function s(t, e, n, r, o, i, c) {
    return a(e ^ n ^ r, t, e, o, i, c)
}
function l(t, e, n, r, o, i, c) {
    return a(n ^ (e | ~r), t, e, o, i, c)
}
function hashCore(t, e) {
    var n, r, o, a, f;
    t[e >> 5] |= 128 << e % 32,
        t[14 + (e + 64 >>> 9 << 4)] = e;
    var p = 1732584193
        , d = -271733879
        , v = -1732584194
        , h = 271733878;
    for (n = 0; n < t.length; n += 16)
        r = p,
            o = d,
            a = v,
            f = h,
            p = c(p, d, v, h, t[n], 7, -680876936),
            h = c(h, p, d, v, t[n + 1], 12, -389564586),
            v = c(v, h, p, d, t[n + 2], 17, 606105819),
            d = c(d, v, h, p, t[n + 3], 22, -1044525330),
            p = c(p, d, v, h, t[n + 4], 7, -176418897),
            h = c(h, p, d, v, t[n + 5], 12, 1200080426),
            v = c(v, h, p, d, t[n + 6], 17, -1473231341),
            d = c(d, v, h, p, t[n + 7], 22, -45705983),
            p = c(p, d, v, h, t[n + 8], 7, 1770035416),
            h = c(h, p, d, v, t[n + 9], 12, -1958414417),
            v = c(v, h, p, d, t[n + 10], 17, -42063),
            d = c(d, v, h, p, t[n + 11], 22, -1990404162),
            p = c(p, d, v, h, t[n + 12], 7, 1804603682),
            h = c(h, p, d, v, t[n + 13], 12, -40341101),
            v = c(v, h, p, d, t[n + 14], 17, -1502002290),
            p = u(p, d = c(d, v, h, p, t[n + 15], 22, 1236535329), v, h, t[n + 1], 5, -165796510),
            h = u(h, p, d, v, t[n + 6], 9, -1069501632),
            v = u(v, h, p, d, t[n + 11], 14, 643717713),
            d = u(d, v, h, p, t[n], 20, -373897302),
            p = u(p, d, v, h, t[n + 5], 5, -701558691),
            h = u(h, p, d, v, t[n + 10], 9, 38016083),
            v = u(v, h, p, d, t[n + 15], 14, -660478335),
            d = u(d, v, h, p, t[n + 4], 20, -405537848),
            p = u(p, d, v, h, t[n + 9], 5, 568446438),
            h = u(h, p, d, v, t[n + 14], 9, -1019803690),
            v = u(v, h, p, d, t[n + 3], 14, -187363961),
            d = u(d, v, h, p, t[n + 8], 20, 1163531501),
            p = u(p, d, v, h, t[n + 13], 5, -1444681467),
            h = u(h, p, d, v, t[n + 2], 9, -51403784),
            v = u(v, h, p, d, t[n + 7], 14, 1735328473),
            p = s(p, d = u(d, v, h, p, t[n + 12], 20, -1926607734), v, h, t[n + 5], 4, -378558),
            h = s(h, p, d, v, t[n + 8], 11, -2022574463),
            v = s(v, h, p, d, t[n + 11], 16, 1839030562),
            d = s(d, v, h, p, t[n + 14], 23, -35309556),
            p = s(p, d, v, h, t[n + 1], 4, -1530992060),
            h = s(h, p, d, v, t[n + 4], 11, 1272893353),
            v = s(v, h, p, d, t[n + 7], 16, -155497632),
            d = s(d, v, h, p, t[n + 10], 23, -1094730640),
            p = s(p, d, v, h, t[n + 13], 4, 681279174),
            h = s(h, p, d, v, t[n], 11, -358537222),
            v = s(v, h, p, d, t[n + 3], 16, -722521979),
            d = s(d, v, h, p, t[n + 6], 23, 76029189),
            p = s(p, d, v, h, t[n + 9], 4, -640364487),
            h = s(h, p, d, v, t[n + 12], 11, -421815835),
            v = s(v, h, p, d, t[n + 15], 16, 530742520),
            p = l(p, d = s(d, v, h, p, t[n + 2], 23, -995338651), v, h, t[n], 6, -198630844),
            h = l(h, p, d, v, t[n + 7], 10, 1126891415),
            v = l(v, h, p, d, t[n + 14], 15, -1416354905),
            d = l(d, v, h, p, t[n + 5], 21, -57434055),
            p = l(p, d, v, h, t[n + 12], 6, 1700485571),
            h = l(h, p, d, v, t[n + 3], 10, -1894986606),
            v = l(v, h, p, d, t[n + 10], 15, -1051523),
            d = l(d, v, h, p, t[n + 1], 21, -2054922799),
            p = l(p, d, v, h, t[n + 8], 6, 1873313359),
            h = l(h, p, d, v, t[n + 15], 10, -30611744),
            v = l(v, h, p, d, t[n + 6], 15, -1560198380),
            d = l(d, v, h, p, t[n + 13], 21, 1309151649),
            p = l(p, d, v, h, t[n + 4], 6, -145523070),
            h = l(h, p, d, v, t[n + 11], 10, -1120210379),
            v = l(v, h, p, d, t[n + 2], 15, 718787259),
            d = l(d, v, h, p, t[n + 9], 21, -343485551),
            p = i(p, r),
            d = i(d, o),
            v = i(v, a),
            h = i(h, f);
    return [p, d, v, h]
}
function stringToByteArray(t) {
    var e, n = [];
    for (n[(t.length >> 2) - 1] = void 0, e = 0; e < n.length; e += 1)
        n[e] = 0;
    var r = 8 * t.length;
    for (e = 0; e < r; e += 8)
        n[e >> 5] |= (255 & t.charCodeAt(e / 8)) << e % 32;
    return n
}

function byteArrayToString(t) {
    var e, n = "", r = 32 * t.length;
    for (e = 0; e < r; e += 8)
        n += String.fromCharCode(t[e >> 5] >>> e % 32 & 255);
    return n
}

function stringToHex(t) {
    var e, n, r = "0123456789abcdef", o = "";
    for (n = 0; n < t.length; n += 1)
        e = t.charCodeAt(n),
        o += r.charAt(e >>> 4 & 15) + r.charAt(15 & e);
    return o
}

function encodeString(t) {
    return unescape(encodeURIComponent(t))
}

function generateHash(t) {
    return function(t) {
        return byteArrayToString(hashCore(stringToByteArray(t), 8 * t.length))
    }(encodeString(t))
}

function generateKeyedHash(t, e) {
    return function(t, e) {
        var n, r, o = stringToByteArray(t), i = [], a = [];
        for (i[15] = a[15] = void 0,
        o.length > 16 && (o = hashCore(o, 8 * t.length)),
        n = 0; n < 16; n += 1)
            i[n] = 909522486 ^ o[n],
            a[n] = 1549556828 ^ o[n];
        return r = hashCore(i.concat(stringToByteArray(e)), 512 + 8 * e.length),
        byteArrayToString(hashCore(a.concat(r), 640))
    }(encodeString(t), encodeString(e))
}

function encrypt(t, e, n) {
    return e ? n ? generateKeyedHash(e, t) : stringToHex(generateKeyedHash(e, t)) : n ? generateHash(t) : stringToHex(generateHash(t))
}

var d = function() {
    var t = arguments.length > 0 && void 0 !== arguments[0] ? arguments[0] : 8;
    return (Number((Math.random() + Math.random()).toString().substr(2, 13)) + Date.now()).toString(36).slice(-parseInt(t, 10))
}

// post
// 8b23k95p
// 1732112001039
// parking
// {"carNo":"57KkQUJDMTIzNQ==","carNoType":1,"iphone":"MTg4MTk2MjQzMTc=","sourceType":1,"verificationCode":"0329","oneId":"oDJ04uLFXG5-2l5iVRoDIqWpD_Kc"}
var n = "post"
var o = d()
o = "8b23k95p"
var ts = new Date(Date.now()).getTime();
ts = 1732112001039
// var r = {url: "https://smartum.sz.gov.cn/tcyy/parking/lot-mobile/main"}
var r = {"carNo":"57KkQUJDMTIzNQ==","carNoType":1,"iphone":"MTg4MTk2MjQzMTc=","sourceType":1,"verificationCode":"0329","oneId":"oDJ04uLFXG5-2l5iVRoDIqWpD_Kc"}
var e = "parking"
var t = function() { 
    return n + "\n" + o + "\n" + ts + "\n" + e + "\n" + (r ? JSON.stringify(r) : "")
}

var t1 = function(r, ts) { 
    return n + "\n" + o + "\n" + ts + "\n" + e + "\n" + r
}

function sign(r, ts) {
    return encrypt(t1(r, ts), undefined, undefined) + "_" + o
}