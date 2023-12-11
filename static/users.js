
function deleteUser(btn){
    id = btn.parentElement.parentElement.querySelector("#id").innerHTML;
    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", "./users/delete", true);
    xhttp.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
    xhttp.send(JSON.stringify({"id":id}));
}

function changePerms(input){
    level = input.value;
    id = input.parentElement.parentElement.querySelector("#id").innerHTML;
    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", "./users/edit", true);
    xhttp.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
    xhttp.send(JSON.stringify({"id":id, "level":level}));
}
