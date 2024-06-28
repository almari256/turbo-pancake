import os 
import json
import PyPDF2

from langchain.schema.document import Document
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings.openai import OpenAIEmbeddings
from halo import Halo

def process() : 

    files = os.listdir('../Assets/uploads')
    files = [f'../Assets/uploads/{file}' for file in files]

    documents = []

    pdf_files = [
        file 
        for file 
        in files 
        if file.endswith('pdf')
    ]

    json_file = [
        file 
        for file 
        in files 
        if file.endswith('json')
    ]

    spinner = Halo(
        text = f'Creating Vector Store for PDF Files' , 
        spinner = 'dots'
    )

    spinner.start()

    for file in pdf_files : 

        pdf = PyPDF2.PdfReader(file)

        for page_number in range(len(pdf.pages)) : 

            text = pdf.pages[page_number].extract_text()

            chunks = [
                text[index : index + 1024]
                for index 
                in range(0 , len(text) , 1024)
            ]

            for chunk in chunks :

                documents.append(
                    Document(
                        page_content = chunk , 
                        metadata = {
                            'source_type' : 'pdf' , 
                            'source_name' : file , 
                            'iter_number' : page_number , 
                            'type' : 'text' , 
                            'url' : ''    
                        }
                    ))

        vc =  FAISS.from_documents(
            documents , 
            embedding = OpenAIEmbeddings(model="text-embedding-3-large")
        )

        vc.save_local('../Assets/vectorstore/text_vc')

    spinner.stop()

    spinner = Halo(
        text = f'Creating Vector Store for JSON Files' , 
        spinner = 'dots'
    )

    spinner.start()

    documents = []

    for file in json_file : 

        for doc in json.load(open(file)) : 

            documents.append(Document(
                page_content = doc['page_content'] , 
                metadata = {
                    'source_type' : 'json' , 
                    'source_name' : file ,
                    'iter_number' : 0 ,
                    'type' : doc['type'] , 
                    'url' : doc['url']
                }
            ))

    vc =  FAISS.from_documents(
        documents , 
        embedding = OpenAIEmbeddings(model="text-embedding-3-large")
    )

    vc.save_local('../Assets/vectorstore/img_vc')

    spinner.stop()
