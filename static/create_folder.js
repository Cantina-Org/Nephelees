function create_folder(workDir){
    let fileName = prompt("Quelle est le nom du fichier? ")
    window.location.replace("?path="+workDir+"&action=createFolder&workFile="+fileName);
}