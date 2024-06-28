from flask import jsonify

def upload(file) : 

    if file.filename == '' : return (
        jsonify({'error' : 'No file selected for uploading'}) , 
        400
    )

    if file and (file.filename.endswith('pdf') or file.filename.endswith('json')) : 

        file.save(f'../Assets/uploads/{file.filename}')
        
        return (
            jsonify({
                'message' : 'File successfully uploaded' ,
                'filename' : file.filename
            }) , 
            200
        )

    else : return (
        jsonify({'error' : 'Allowed file types are pdf or json'}) , 
        400
    )
