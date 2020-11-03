
if (
    e.shiftKey == <% shift_key %>
    && e.altKey == <% alt_key %>
    && e.ctrlKey == <% ctrl_key %>
    && e.key == "<% key %>"
) {
    let button = document.getElementsByClassName("<% class_name %>")[0];
    button.click();
}