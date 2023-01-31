function clone_repository(workDir){
    let repoLink = prompt("Quelle est le lien du dépots Github? ")
    window.location.replace("?path="+workDir+"&action=cloneRepo&repoLink="+repoLink);
}