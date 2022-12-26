function create_file(workDir){
    alert(workDir)
    let fileName = prompt("Quelle est le nom du fichier? ")
    window.location.replace("?path="+workDir+"&action=createFile&workFile="+fileName);
}