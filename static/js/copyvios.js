function copyvio_toggle_details(details) {
    link = document.getElementById("cv-result-detail-link");
    details = document.getElementById("cv-result-detail");
    
    if (link.innerHTML == "Show details:") {
        details.style.display = "block";
        link.innerHTML = "Hide details:";
    } else {
        details.style.display = "none";
        link.innerHTML = "Show details:";
    }
}
