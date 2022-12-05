function delete_file(workDir, file_to_delete){
    if (confirm("Vous allez supprimer définitivement ce fichier!\nÊtes vous sur?")){
        window.location.replace("?path="+workDir+"&action=delete&workFile="+file_to_delete);
        console.log('delete file nammed '+file_to_delete);
    } else {
        window.location.replace("?path="+workDir+"&action=show");
        console.log('don\'t delete the file');
    }
}