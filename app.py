from flask import Flask, request, render_template, redirect, url_for, jsonify
from pymongo import MongoClient
import requests
from datetime import datetime


app = Flask(__name__)


cxn_str = 'mongodb+srv://sitanasalwa:25Januari2002@cluster0.g1jnsmp.mongodb.net/?retryWrites=true&w=majority'
client = MongoClient(cxn_str)

db = client.project02

@app.route('/')
def main():
    words_result = db.words.find({}, {'_id': False})
    words = []
    for word in words_result:
        definition = word['definitions'][0]['shortdef']
        definition = definition if type(definition) is str else definition[0]
        words.append({
            'word' : word['word'],
            'definition' : definition,
        })
    
    return render_template('index.html', words=words)

@app.route('/detail/<keyword>')
def detail(keyword):
    api_key = 'ce8fec5a-0280-41e8-9e8e-88d8b3f0f6df'
    url = f'https://www.dictionaryapi.com/api/v3/references/collegiate/json/{keyword}?key={api_key}'
    response=requests.get(url)
    definitions = response.json()

    if not definitions:
        return redirect(url_for(
            'error',
            msg = f'Could not find the word, "{keyword}"' 
        ))
    
    if type(definitions[0]) is str:
        suggestions = ', '.join(definitions)
        return redirect(url_for(
            'error',
            msg = f'Could not find the word, "{keyword}", did you mean one of these words' ,
            suggestions = suggestions
        ))

    status = request.args.get('status_give', 'new')
    return render_template(
        'detail.html',
        word = keyword,
        definitions = definitions,
        status = status
    )

@app.route('/error')
def error():
    msg= request.args.get('msg')
    items = request.args.get('suggestions', '').split(',')
    
    return render_template('eror.html', msg=msg, items=items)


@app.route('/api/save_word', methods=['POST'])
def save_word():
    json_data = request.get_json()
    word = json_data.get('word_give')
    definitions = json_data.get('definitions_give')

    doc = {
        'word' : word,
        'definitions' : definitions,
        'date' : datetime.now().strftime('%Y-%m-%d')
    }

    db.words.insert_one(doc)

    return jsonify({
        'result' : 'success',
        'msg' : f'the, {word}, was saved!!!',
        
    })

@app.route('/api/delete_word', methods=['POST'])
def delete_word():
    word = request.form.get('word_give')
    db.words.delete_one({'word' : word})
    return jsonify({
        'result' : 'success',
        'msg' : f'the word, {word}, was deleted'
    })
   

if __name__ == '__main__':
    app.run('0.0.0.0', port = 5000, debug=True)