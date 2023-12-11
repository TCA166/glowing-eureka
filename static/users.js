
function deleteUser(e, btn){
    e.preventDefault();
    id = btn.parentElement.parentElement.querySelector("#id").innerHTML;
    var xhttp = new XMLHttpRequest();
    xhttp.onload = function() {
        if(xhttp.status == 200){
            auth = this.responseText;
            document.cookie = "auth=" + auth;
            window.location.replace("/");
        }
    };
    xhttp.open("POST", "./users/delete", true);
    xhttp.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
    xhttp.send(JSON.stringify({"id":id}));
}
