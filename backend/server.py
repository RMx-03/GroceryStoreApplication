from flask import Flask, request, jsonify
from sql_connection import get_sql_connection
import products_dao 

app = Flask(__name__)

connection = get_sql_connection()

@app.route('/getProducts', methods=['GET'])
def get_products():
    products = products_dao.get_all_products(connection)
    response = jsonify(products) 
    response.headers.add('Access-Control-Allow-Origin', '*')  # CORS policy 
    return response

if __name__ == "__main__":
    print() 
    app.run(port=5000)