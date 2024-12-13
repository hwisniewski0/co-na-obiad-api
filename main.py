from flask import Flask, jsonify, render_template, request

from modules.obiadowe.podziel_obiad import podziel_obiad
from modules.obiadowe.przeksztalc_json import przeksztalc_json
from modules.obiadowe.get_obiad import get_obiad
from modules.obiadowe.send_email import send_email
from modules.database.db_post import post_content


app = Flask(__name__)


################################################################
######################## API OBIADOWE ##########################
################################################################
@app.route('/get_obiad', methods=['GET'])
def obiady():
    # Wywołanie funkcji i zwrócenie danych w formacie JSON
    menu_data = get_obiad()

    converted_menu = przeksztalc_json(menu_data)

    return jsonify(podziel_obiad(converted_menu))


################################################################
@app.route('/version', methods=['GET'])
def version():
    return "1.0"


################################################################
@app.route('/', methods=['GET'])
def main():
    return render_template('index.html')


################################################################
@app.route('/send_email', methods=['GET'])
def send_email_api():
    # Odczytanie parametrów zapytania
    content = request.args.get('content')
    sender_email = request.args.get('sender')

    if not content or not sender_email:
        return jsonify({"error": "Brakuje argumentów 'content' lub 'sender'"}), 400

    # Wywołanie funkcji wysyłającej e-mail
    success = send_email(content, sender_email)
    
    if success:
        return jsonify({"message": "200"}), 200
    else:
        return jsonify({"error": "Wystąpił błąd podczas wysyłania e-maila"}), 500
    

################################################################
################### API - OCENY OBIADOW ########################
################################################################

@app.route('/api/post',methods=['GET'])
def post():
    nickname=request.args.get('nickname')
    tresc = request.args.get('content')
    result = post_content()
    if result == "succes":
        return "200"
    else:
        return "500"




if __name__ == '__main__':
    app.run(host="0.0.0.0",port=8080)