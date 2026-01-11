from flask import Flask, request, jsonify
from sql_connection import get_sql_connection
import products_dao 

app = Flask(__name__)

connection = get_sql_connection()

def add_cors_headers(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

@app.route('/getUOM', methods=['GET'])
def get_uom():
    response = products_dao.get_uoms(connection)
    response = jsonify(response)
    return add_cors_headers(response)

@app.route('/getProducts', methods=['GET'])
def get_products():
    products = products_dao.get_all_products(connection)
    response = jsonify(products) 
    return add_cors_headers(response)

@app.route('/insertProduct', methods=['POST'])
def insert_product():
    request_payload = request.get_json()
    product_id = products_dao.insert_new_product(connection, request_payload)
    response = jsonify({
        'product_id': product_id
    })
    return add_cors_headers(response)

@app.route('/deleteProduct', methods=['POST'])
def delete_product():
    request_payload = request.get_json()
    product_id = request_payload['product_id']
    products_dao.delete_product(connection, product_id)
    response = jsonify({
        'product_id': product_id
    })
    return add_cors_headers(response)

if __name__ == "__main__":
    print() 
    app.run(port=5000)