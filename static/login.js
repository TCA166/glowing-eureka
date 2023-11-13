function handleLogin(e){
    e.preventDefault();
    username = document.getElementById("usernameInput").value;
    password = document.getElementById("passwordInput").value;
    var xhttp = new XMLHttpRequest();
    xhttp.onload = function() {
        if(xhttp.status == 200){
            auth = this.responseText;
            document.cookie = "auth=" + auth;
            window.location.replace("/");
        }
    };
    xhttp.open("POST", "./login", true);
    xhttp.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
    xhttp.send(JSON.stringify({"username":username, "password":password}));
}