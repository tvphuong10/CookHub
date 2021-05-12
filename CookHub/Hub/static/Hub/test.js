document.getElementById("body").onscroll = function scrollFunction() {
    var to_top = document.scrollingElement.scrollTop;
    var x = "center";
    var factor = 0.5;
    var y = to_top * factor;
    document.getElementById("bg").style.backgroundPosition = x + " " + y + "px";
}

function search() {
        var s = document.getElementById('search_id').value;
        var encode = encodeURI(s);
        window.location.href = 'search/' + encode;
}

function search(e) {
    if (e.keyCode == 13) {
        var s = document.getElementById('search_id').value;
        var encode = encodeURI(s);
        window.location.href = 'search/' + encode;
    }
}

function goTop() {
    document.body.scrollTop = 0;
    document.documentElement.scrollTop = 0;
}

function goCreate() {
    window.location.href = 'create/'
}