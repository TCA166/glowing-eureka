function editBox(btn){
    comment = btn.parentElement;
    btn.style.display = "none";
    commentTextEl = comment.querySelector("#commentText");
    commentTextEl.style.display = "none";
    div = commentTextEl.parentElement;
    newInput = document.createElement("input");
    newInput.setAttribute("type", "text");
    newInput.classList.add("form-control");
    newInput.style.display = "inline-block";
    newInput.style.width = "fit-content";
    newInput.value = commentTextEl.innerHTML;
    newInput.addEventListener("keypress", function(event) {
        if (event.key === "Enter") {
            event.preventDefault();
            commentTextEl.innerHTML = newInput.value;
            commentTextEl.style.display = "";
            newInput.remove();
            var xhttp = new XMLHttpRequest();
            url = new URL(window.location.href);
            url.pathname = url.pathname + "/comment/edit";
            xhttp.open("POST", url.href, true);
            xhttp.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
            xhttp.send(JSON.stringify({"commentId":comment.id, "description":commentTextEl.innerHTML}));
            btn.style.display = "";
        }
    }); 
    div.insertBefore(newInput, commentTextEl.nextSibling);
}