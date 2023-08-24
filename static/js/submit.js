const submitButton = document.getElementById("submitButton");

if (submitButton) {
    submitButton.addEventListener("click", function(event) {
        event.preventDefault();

        event.target.classList.add("loading");

        setTimeout(function() {
            event.target.closest('form').submit();
        }, 500);
    });
}
