
import json

from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from openai import OpenAI
from halo import Halo

def run_llm(prompt) :

    client = OpenAI()

    stream = client.chat.completions.create(
        model = 'gpt-4o' , 
        messages = [
            {
                'role' : 'user' , 
                'content' : prompt
            }
        ] , 
        stream = True
    )
    response = ''

    for chunk in stream : 

        if chunk.choices[0].delta.content : response += chunk.choices[0].delta.content

    return response

def split_prompt_to_n(query , time_to_run = 5) : 

    spinner = Halo(
        text = f'Generating {time_to_run} different questions for {query}' , 
        spinner = 'dots'
    )

    spinner.start()

    question_llm_prompt = open('../Assets/prompt/n_split_prompt.txt').read().format(time_to_run , query)
    questions = run_llm(question_llm_prompt).split('\n')

    spinner.stop()

    n_response = ''

    for q_index , question in enumerate(questions) : 

        spinner = Halo(
            text = f'Generating response for {q_index} Query : {question}' , 
            spinner = 'dots'
        )

        spinner.start()

        n_response += answer(question , retain_history = False) + '\n\n'

        writable = f'''
Original Question : {query} 

Times to Run : {time_to_run}

{q_index} Qeury : {question}

{q_index} Response : {n_response}
        '''

        open('../Assets/Saved/n_variations.txt' , 'a').write(writable)

        print(f'------------------------{q_index}-----------------------')
        print(n_response)
        print('---------------------------------------------------------')

        spinner.stop()

    n_prompt = open('../Assets/prompt/n_prompt.txt').read()

    spinner = Halo(
        text = f'Generating response for original query : {query}' , 
        spinner = 'dots'
    )

    spinner.start()

    response = run_llm(n_prompt.format(n_response , query))

    spinner.stop()

    open('../Assets/Logs/chat_logs.json' , 'a').write(json.dumps({
        'query' : query , 
        'response' : response
    }) + '\n')

    return response

def get_images(query) : 

    vc = FAISS.load_local(
        '../Assets/vectorstore/img_vc' , 
        embeddings = OpenAIEmbeddings(model = 'text-embedding-3-large') ,  
        allow_dangerous_deserialization = True
    ) 

    similar_docs = vc.similarity_search(query)

    images = [doc.metadata['url'] for doc in similar_docs if doc.metadata['type'] == 'image']

    return images

def answer(query , retain_history = True) : 

    vc = FAISS.load_local(
        '../Assets/vectorstore/text_vc' , 
        embeddings = OpenAIEmbeddings(model = 'text-embedding-3-large') ,  
        allow_dangerous_deserialization = True
    ) 
    client = OpenAI()

    similar_docs = vc.similarity_search(query)

    context = ' '

    for doc in similar_docs : 

        context += f'''
        Page Content : {doc.page_content}

        source_type : {doc.metadata['source_type']}

        source_name : {doc.metadata['source_name']}

        iter_number : {doc.metadata['iter_number']}        
        '''

    images = [doc.metadata['url'] for doc in similar_docs if doc.metadata['type'] == 'image']

    if retain_history : 

        prompt = open('../Assets/prompt/main_prompt.txt').read()

        history = open('../Assets/Logs/chat_logs.json').read()
        history = history.split('\n')
        history = history[-6 :]
        history = '\n'.join(history)
        
        prompt = prompt.format(history , context , query)

        response = run_llm(prompt)

    else :

        prompt = open('../Assets/prompt/prompt_without_history.txt').read()

        prompt = prompt.format(context , query)

        response = run_llm(prompt)

    return response