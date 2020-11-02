function logKey(e) {
    /* Show shortcut */
    let visible_space = document.getElementById("shortcut-display");

    let text_to_display = "key:&nbsp;<b>" + e.key + "</b>&nbsp;&nbsp;&nbsp;&nbsp;";
    text_to_display += "code:&nbsp;<b>" + e.code + "</b>&nbsp;&nbsp;&nbsp;&nbsp;";
    text_to_display += "shiftKey:&nbsp;<b>" + e.shiftKey + "</b>&nbsp;&nbsp;&nbsp;&nbsp;";
    text_to_display += "ctrlKey:&nbsp;<b>" + e.ctrlKey + "</b>&nbsp;&nbsp;&nbsp;&nbsp;";
    text_to_display += "altKey:&nbsp;<b>" + e.altKey + "</b>";

    visible_space.innerHTML = text_to_display;

    /* Hide shortcut in hidden state in python format for copy */
    let hidden_space = document.getElementById("hidden-shortcut");
    let shiftKey = "False";
    let ctrlKey = "False";
    let altKey = "False";
    if (e.shiftKey) {
        shiftKey = "True";
    }
    if (e.ctrlKey) {
        ctrlKey = "True";
    }
    if (e.altKey) {
        altKey = "True";
    }

    let hidden_text = "{\"key\":\"" + e.key + "\",";
    hidden_text += " \"code\":\"" + e.code + "\",";
    hidden_text += " \"shift_key\":" + shiftKey + ",";
    hidden_text += " \"ctrl_key\":" + ctrlKey + ",";
    hidden_text += " \"alt_key\":" + altKey + "}";

    hidden_space.innerHTML = hidden_text;
}

function stopListener() {
    window.removeEventListener('keydown', logKey);
}

function copyToClipboard() {
    let hidden_space = document.querySelector("#hidden-shortcut");
    let range = document.createRange();
    let selection = window.getSelection();

    hidden_space.style.display = "block";

    range.selectNode(hidden_space);
    selection.removeAllRanges();
    selection.addRange(range);

    document.execCommand("copy");
    hidden_space.style.display = "none";
}

function startListener() {
    try {
        stopListener();
    } catch (err) {
        console.log(err);
    } finally {
        window.addEventListener('keydown', logKey);
    }
}

document.getElementsByClassName("stop_shortcut_button_class")[0].addEventListener("click", stopListener);
document.getElementsByClassName("copy_shortcut_button_class")[0].addEventListener("click", copyToClipboard);
document.getElementsByClassName("start_shortcut_button_class")[0].addEventListener("click", startListener);
startListener();