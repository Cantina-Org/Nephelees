function create_folder(workDir){
    let fileName = prompt("Quelle est le nom du dossier? ")
    window.location.replace("?path="+workDir+"&action=createFolder&workFile="+fileName);
}