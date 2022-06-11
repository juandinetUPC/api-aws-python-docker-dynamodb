from flask import Flask, jsonify, request
from decimal import Decimal
from custom_encoder import buildResponse
import controller as dynamodb
import logging
logger=logging.getLogger()
logger.setLevel( logging.INFO )

app =Flask(__name__)

@app.route( '/' ) # prueba de ruta
def index():
    numero = Decimal(1.6)
    mensaje = f'API by Juandinet { numero }'
    return jsonify( { f'Message': mensaje} ), 200

@app.route( '/createTable' ) # crear tabla
def create_table():
    dynamodb.create_table()
    return jsonify( { f'Message': 'Tabla creada'} ), 200    


@app.route( '/user', methods=['POST'] )  # Agregar un usuario
def create_user():
    userId = int( request.json.get( 'userid' ) )
    username = request.json.get( 'username' )
    age = int( request.json.get( 'age' ) )

    if not userId or not username:
        return jsonify( { 'error': 'Debe ingresar un "userid", "username" y "age"' } ), 400
    
    item={ "userid": userId, "username": username, "age": age }
    table = dynamodb.table()

    try:
        ifExist = table.get_item( Key = { "userid": Decimal(userId) } )
        
        if 'Item' in ifExist:
            #Si existe el usuario, envía el mensaje de error
            body={ 'Message':'Usuario ya existe',
                  "User":ifExist['Item'] }
            return jsonify( body ), 202
        else:
            #Si no existe el usuario, lo inserta en la tabla    
            table.put_item( Item=item )
            body = {
                "Message": "Usuario creado",
                "User": item
            }
            return jsonify( body ), 201
    except:
        logger.exception( f'Error al tratar de conectarse a la base de datos !! {userId}' )
        return buildResponse( 500,{'Message':'Error al tratar de crear el usuario'} )
    

@app.route( '/users' ) # Listar todos los usuarios
def list_users():
    """Devuelve una lista de usuarios"""
    
    table = dynamodb.table()
    #Obtiene todos los usuarios
    result = table.scan()
    
    if result['Items'] != []:
        #Si hay usuarios, devuelve la lista
        body = {
            "Message": "Usuarios",
            "datos":result['Items']
        }
        response = jsonify( body ), 200
        
    else:
        #Si no hay usuarios, devuelve el mensaje de error
        body = {
            "Message": "La tabla está vacía",
            "datos": result['Items']
        }
        response = jsonify( body ), 200

    return response

@app.route( '/user/<int:userid>' ) # Leer un usuario 
def read_user( userid ):
    """Devuelve un usuario"""
    table = dynamodb.table()
    userId = userid
    try:
        """Por ser el indice userid tipo 'N'(numero), se debe convertir el parametro(userId) a Decimal
        Para poder hacer la busqueda en la tabla"""
        
        response = table.get_item( Key = { "userid": Decimal(userId) } )

        if 'Item' in response:
            #Si existe el usuario, lo devuelve
            return jsonify( response['Item'] ), 200
        
        else:
            #Si no existe el usuario, devuelve el mensaje de error
            return jsonify( {'Message':f'userid:{userId} not found'} ), 404
    
    except:
        #Si no se puede consultar la tabla, se devuelve un error
        logger.exception( f'Error al tratar de consultar la base de datos !! {userId}' )
        return jsonify( {'Message':'Error al tratar de conectar con la base de datos'} ), 500


@app.route( '/user/<int:userid>', methods=['PUT'] ) # Actualizar un usuario
def update_user( userid ):
    """Recibe un userid y un json con los datos a actualizar
    Args:
        userid (int): Identificador del usuario
        json (json): Datos a actualizar
        {
        "username":"Ronny Tobillos", (string)
        "age":5 (int)
        }
    Returns:
        http: 200 si el usuario existe y se actualizaron los datos
    """
    userId = userid #int(request.json.get('userid'))
    username = request.json.get( 'username' )
    age = int( request.json.get('age') )
    if not age or not username:
        return jsonify( {'error': 'Debe ingresar un "username" y "age"'} ), 400
    
    table = dynamodb.table()
    
    try:
        #Si existe el usuario, procede a actualizarlo
        antes = table.get_item( Key = { "userid": Decimal(userId) } )
        if 'Item' in antes:
            antes = antes['Item']
            result = table.update_item(
                Key={
                    'userid': Decimal(userId)
                },
            ExpressionAttributeNames={
                '#todo_username': 'username',
                '#todo_age': 'age'
                },
            ExpressionAttributeValues={
                ':username': username,
                ':age': age
                },
                UpdateExpression='SET #todo_username = :username, #todo_age = :age',
                ReturnValues='UPDATED_NEW'
                )
            despues = table.get_item( Key = { "userid": Decimal(userId) } )['Item']
            body = {
                "Message": "Usuario actualizado",
                "ANTES": antes,
                "DESPUES": despues,
                "result": result
            }
            response = jsonify( body ), 200
        else:
            #Si no existe el usuario, devuelve el mensaje de error
            body = {
                "Message": "Usuario no encontrado",
                "userid": userId
            }
            response = jsonify( body ), 404

        return response

    except:
        logger.exception( f'Error al tratar de consultar la base de datos !! {userId}' )
        return buildResponse( 500,{'Message':'Error al tratar de actualizar el usuario'} )


@app.route( '/user/<int:userid>', methods=[ 'DELETE' ] ) # Eliminar un usuario
def delete_user( userid ):
    """Recibe un userid Y lo elimina de la tabla
    Args:
        userid (int): Identificador del usuario
        
    Returns:
        http: 200 si el usuario lo elimina
    """
    userId = userid 
    table = dynamodb.table()
    
    try:
        #Si existe el usuario, procede a eliminarlo
        antes = table.get_item( Key = { "userid": Decimal(userId) } )
        if 'Item' in antes:
            #Porcedemos a eliminar el usuario
            deleted = table.delete_item( Key = {'userid': Decimal(userId)} )
            body = {
            "operación": "delete_item",
            "Message": "success",
            'deleted': deleted,
            'userid': userId }
            response = jsonify( body ), 200
        else:
            #Si no existe el usuario, devuelve el mensaje de error
            body = {
                "Message": "Usuario no encontrado",
                "userid": userId
            }
            response = jsonify( body ), 404

        return response

    except:
        #Si ocurre un error lo mandamos al log de AWS
        logger.exception( f'Error al tratar de consultar la base de datos !! {userId}' )
        #Si encuentra un error, retorna un 500
        return buildResponse( 500,{'Message':'Error al tratar de eliminar el usuario'} )


if __name__ == "__main__":
    # port = 4000  Para que salga por el puerto 4000
    # host = '0.0.0.0' Para que salga por todos las IPs
    # debug = True Para que se vea el cambio en el servidor sin reiniciar
    app.run( port = 4000,debug = True, host = '0.0.0.0' )