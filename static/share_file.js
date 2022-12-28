function share_file(workDir, file_to_share){
    window.location.replace("?path="+workDir+"&action=shareFile&workFile="+file_to_share);
}