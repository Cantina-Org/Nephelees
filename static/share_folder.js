function share_folder(workDir, folder_to_share){
    if (/iPhone/i.test(navigator.userAgent)) {
        window.setTimeout(function() {
            if (confirm("Voulez vous partager ce dossier (bientôt une archive) avec toute les personnes qui ont le lien? ")) {
                if (confirm("Voulez vous protéger ce fichier avec un mot de passe? ")) {
                    let passwd = prompt("Qu'elle est le mot de passe? ");
                    window.open("?path=" + workDir + "&action=shareFolder&workFolder=" + folder_to_share + "&loginToShow=0&password=" + passwd);
                } else {
                    window.open("?path=" + workDir + "&action=shareFolder&workFolder=" + folder_to_share + "&loginToShow=0");
                }
            } else {
                window.open("?path=" + workDir + "&action=shareFolder&workFolder=" + folder_to_share + "&loginToShow=1");
            }
        })
    } else{
        if (confirm("Voulez vous partager ce dossier (bientôt une archive) avec toute les personnes qui ont le lien? ")) {
            if (confirm("Voulez vous protéger ce fichier avec un mot de passe? ")) {
                let passwd = prompt("Qu'elle est le mot de passe? ");
                window.open("?path=" + workDir + "&action=shareFolder&workFolder=" + folder_to_share + "&loginToShow=0&password=" + passwd);
            } else {
                window.open("?path="+workDir+"&action=shareFolder&workFolder="+folder_to_share+"&loginToShow=0");
            }
        } else {
            window.open("?path="+workDir+"&action=shareFolder&workFolder="+folder_to_share+"&loginToShow=1");
        }
    }

}