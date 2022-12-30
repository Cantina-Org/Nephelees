function updateClipboard(newClip) {
  navigator.clipboard.writeText(newClip).then(function() {
    console.log('All is fine!')
  }, function() {
    console.log('Fail Paste To CopyBoard!')
  });
}

function share_file(workDir, file_to_share){
    
    if (confirm("Voulez vous partager ce fichier avec toute les personnes qui ont le lien? ")) {
        if (confirm("Voulez vous protéger ce fichier avec un mot de passe? ")) {
            let passwd = prompt("Qu'elle est le mot de passe? ");
            window.location.replace("?path="+workDir+"&action=shareFile&workFile="+file_to_share+"&loginToShow=0&password=" + passwd);
        } else {
            window.location.replace("?path=" + workDir + "&action=shareFile&workFile=" + file_to_share + "&loginToShow=0");
        }
    } else {
        window.location.replace("?path="+workDir+"&action=shareFile&workFile="+file_to_share+"&loginToShow=1");
    }
}