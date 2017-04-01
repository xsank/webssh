function openTerminal(options) {
    var client = new WSSHClient();
    var term = new Terminal({cols: 80, rows: 24, screenKeys: true, useStyle:true});
    term.on('data', function (data) {
        client.sendClientData(data);
    });
    term.open();
    $('.terminal').detach().appendTo('#term');
    term.write('Connecting...');
    client.connect({
        onError: function (error) {
            term.write('Error: ' + error + '\r\n');
            console.debug('error happened');
        },
        onConnect: function () {
            client.sendInitData(options);
            client.sendClientData('\r');
            console.debug('connection established');
        },
        onClose: function () {
            term.write("\rconnection closed")
            console.debug('connection reset by peer');
        },
        onData: function (data) {
            term.write(data);
            console.debug('get data:' + data);
        }
    })
}

function store(options) {
    window.localStorage.host = options.host
    window.localStorage.port = options.port
    window.localStorage.username = options.username
    window.localStorage.password = options.password
}

function check() {
    var result = $("#host").val() && $("#port").val() && $("#username").val() && $("#password").val()
    if (result) {
        var spans = $("fieldset").find("span")
        // do not check the password
        for (var i = 0; i < spans.length-1; i++) {
            if (spans[i].innerHTML.trim() != "correct") {
                return false
            }
        }
    }
    return result
}

function connect() {
    var remember = $("#remember").is(":checked")
    var options = {
        host: $("#host").val(),
        port: $("#port").val(),
        username: $("#username").val(),
        password: $("#password").val()
    }
    if (remember) {
        store(options)
    }
    if (check()) {
        openTerminal(options)
    } else {
        alert("please check the form!")
    }
}