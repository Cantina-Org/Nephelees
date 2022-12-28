function share_file(workDir, file_to_share){
    if (confirm("Voulez vous partager ce fichier avec toute les personnes qui ont le lien? ")) {
        window.location.replace("?path="+workDir+"&action=shareFile&workFile="+file_to_share+"&loginToShow=0");
    } else {
        window.location.replace("?path="+workDir+"&action=shareFile&workFile="+file_to_share+"&loginToShow=1");
    }
}