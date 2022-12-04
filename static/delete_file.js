function delete_file(file_to_delete){
    console.log("Hello World")
    if (confirm("Vous allez supprimer définitivement ce fichier!\nÊtes vous sur?")){
        console.log('delete file nammed '+file_to_delete)
    } else {
        console.log('don\'t delete the file')
    }
}