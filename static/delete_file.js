function delete_file(workDir, file_to_delete){
    if (confirm("Vous allez supprimer définitivement ce fichier!\nÊtes vous sur?")){
        window.location.replace("?path="+workDir+"&action=deleteFile&workFile="+file_to_delete);
    } else {
        window.location.replace("?path="+workDir+"&action=show");
    }
}