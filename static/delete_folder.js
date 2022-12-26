function delete_folder(workDir, folder_to_delete){
    alert(workDir);
    alert(folder_to_delete);
    if (confirm("Vous allez supprimer définitivement ce dossier!\nÊtes vous sur?")){
        window.location.replace("?path="+workDir+"&action=deleteFolder&workFile="+folder_to_delete);
    } else {
        window.location.replace("?path="+workDir+"&action=show");
    }
}