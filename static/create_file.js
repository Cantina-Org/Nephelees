function create_file(workDir){
    let fileName = prompt("Quelle est le nom du fichier? ")
    window.location.replace("?path="+workDir+"&action=createFile&repoLink="+fileName);
}