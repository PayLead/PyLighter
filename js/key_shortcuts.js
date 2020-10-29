document.dispatchEvent(new KeyboardEvent('keydown', {
    "shiftKey": <% cancel_shortcuts_shift_key %>,
    "altKey": <% cancel_shortcuts_alt_key %>,
    "ctrlKey": <% cancel_shortcuts_ctrl_key %>,
    "key": "<% cancel_shortcuts_key %>"
}));


function shortcut_handler(e) {
    if (
        e.shiftKey == <% cancel_shortcuts_shift_key %> 
        && e.altKey == <% cancel_shortcuts_alt_key %> 
        && e.ctrlKey == <% cancel_shortcuts_ctrl_key %>
        && e.key == "<% cancel_shortcuts_key %>"
    ) {
        document.removeEventListener('keydown', shortcut_handler);
    }

    <% custom_key_shortcuts %>

}

document.addEventListener('keydown', shortcut_handler);