function clone_repository(workDir){
    let repoLink = prompt("Quelle est le lien du dépots distants? ")
    window.location.replace("?path="+workDir+"&action=cloneRepo&repoLink="+repoLink);
}