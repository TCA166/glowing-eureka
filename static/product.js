function editBox(btn){
    commentTextEl = document.getElementById("commentText");
    commentTextEl.style.display = "none";
    div = commentTextEl.parentElement;
    newInput = document.createElement("input");
    newInput.setAttribute("type", "text");
    newInput.classList.add("form-control");
    newInput.style.display = "inline-block";
    newInput.style.width = "";
    newInput.value = commentTextEl.innerHTML;
    newInput.addEventListener("keypress", function(event) {
        if (event.key === "Enter") {
            event.preventDefault();
            commentTextEl.innerHTML = newInput.value;
            commentTextEl.style.display = "";
            newInput.remove();
            var xhttp = new XMLHttpRequest();
            xhttp.open("POST", window.location.href + "/comment/edit", true);
            xhttp.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
            xhttp.send(JSON.stringify({"commentId":div.parentElement.id, "description":commentTextEl.innerHTML}));
        }
    }); 
    div.insertBefore(newInput, commentTextEl.nextSibling);
}