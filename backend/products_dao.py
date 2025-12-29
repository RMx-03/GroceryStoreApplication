from sql_connection import get_sql_connection
def get_all_products(connection):

    # for database operations
    cursor = connection.cursor()


    query = ("SELECT products.product_id, products.name, products.uom_id, products.price_per_unit, uom.uom_name " 
            "FROM products inner join uom on products.uom_id=uom.uom_id;")
    cursor.execute(query)

    # array to store the results
    response = []
    for (product_id, name, uom_id, price_per_unit, uom_name) in cursor:
        response.append(
            {
                'product_id': product_id,
                'name': name,
                'uom_id': uom_id,
                'price_per_unit': price_per_unit,
            }
        )

    return response

if __name__=='__main__':
    connection = get_sql_connection()
    print(get_all_products(connection))