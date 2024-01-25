function addTagToSearch(event, searchBarId) {
    const search = document.getElementById(searchBarId);
    search.value = event.target.value
}