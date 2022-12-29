function share_folder(workDir, folder_to_share){

    if (confirm("Voulez vous partager ce dossier (bientôt une archive) avec toute les personnes qui ont le lien? ")) {
        window.location.replace("?path="+workDir+"&action=shareFolder&workFolder="+folder_to_share+"&loginToShow=0");
    } else {
        window.location.replace("?path="+workDir+"&action=shareFolder&workFolder="+folder_to_share+"&loginToShow=1");
    }
}