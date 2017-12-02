import random, string
import datetime
from bottle import get, post, run, response, request, redirect, default_app
from tinydb import TinyDB, Query

DATABASE = 'database.json'

application = default_app()

def clean_db():
    db = TinyDB(DATABASE)
    query = Query()
    d = datetime.timedelta(days=2)
    r = datetime.datetime.utcnow() - d
    res = db.search(query.date < r.timestamp())
    db.remove(doc_ids=[x.doc_id for x in res])

@get('/')
@get('/<token>')
def index(token=None):
    if not token:
        response.status = 400
        return {
                "message": "What are you doing, son?",
                "endpoins": {
                    "/short": {
                        "method": "POST",
                        "params": "uri",
                        "description": "short uri"
                        }
                    "/<token>": {
                        "method": "GET",
                        "description": "redirect to uri identified by <token>"
                        }
                    }
                }
    db = TinyDB(DATABASE)
    query = Query()
    res = db.search(query.token == token.upper())
    
    if not res:
        response.status = 404
        return {"message": "Link not found!"}
    
    if len(res) > 1:
        return {
        "message": "You are lucky! A colision occurred. There is more than one URL with {} as id."
        .format(token),
        "uris": ", ".join([x['uri'] for x in res])
        }
    
    return redirect(res[0]['uri'])


@post('/short/')
def short():
    uri = request.params.get('uri') or request.json.get('uri')
    if not uri:
        response.status = 400
        return {"message": "'uri' parameter is required you dumb!"}
    token = "".join([random.choice(string.hexdigits) for n in range(4)]).upper()
    db = TinyDB(DATABASE)
    link = "https://{}/{}".format(request.get_header('host'), token)
    db.insert({'token': token, 'uri': uri, 'date': datetime.datetime.utcnow().timestamp()})
    
    clean_db()
    return {"link": link}

if __name__ == "__main__":
    run(host='localhost', port=8080)