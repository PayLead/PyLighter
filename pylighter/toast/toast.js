var snackbar = document.getElementById("snackbar");
snackbar.classList.add("show");

var snackbar_text = document.getElementById("snackbar-text");
snackbar_text.classList.add("snackbar-<% success_type %>");
snackbar_text.innerHTML = "<% toast_msg %>";

setTimeout(function () { snackbar.classList.remove("show"); }, 3000);