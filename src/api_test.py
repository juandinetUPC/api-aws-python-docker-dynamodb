#API unit test
# By: Juandinet
from decimal import Decimal
import unittest
import requests
import custom_encoder

base_url='http://localhost/'
# base_url='http://52.15.78.75/'

#Prueba el constructor de la respuesta de la API (HTTP)
class TestBuildResponse(unittest.TestCase):
    def test_buildResponse(self):
        response = custom_encoder.buildResponse(200,{'mensaje':'hola', 'age':Decimal(5)})
        self.assertEqual(response['statusCode'],200)
        self.assertEqual(response['body'],'{"mensaje": "hola", "age": 5}')

#Prueba el método create
class TestCreate(unittest.TestCase):
    def test_create_user(self):
        userid = 1
        payload = {
            "userid": userid,
            "username": "Pepito Perez",
            "age": 29
        }
        response = requests.post(f'{base_url}user', json=payload)
        if response.status_code == 201:
            self.assertEqual(sorted(response.json()), sorted({'Message': 'Usuario creado', 'User': payload}))
        elif response.status_code == 202:
            self.assertEqual(sorted(response.json()), sorted({'Message': 'Usuario ya existe', 'User': payload}))

#Prueba el método read
class TestRead(unittest.TestCase):
    def test_read_user(self):
        userid=111111111
        response = requests.get(f'{base_url}user/{userid}')
        if response.status_code == 200:
            self.assertEqual(response.status_code,200)
            self.assertEqual(sorted(response.json()), sorted({'username': 'Pepito Perez', 'userid': str(userid), 'age': (29)}))
        elif response.status_code == 404:
            self.assertEqual(response.status_code,404)
            self.assertEqual(response.json(), {'Message': f'userid:{userid} not found'})
       
    def test_read_user_fail(self):
        response = requests.get(f'{base_url}user/99999999')
        self.assertEqual(response.status_code,404)
        self.assertEqual(response.json(), {'Message': 'userid:99999999 not found'})
        
#Prueba el método update
class TestUpdate(unittest.TestCase):
    #Prueba el método update con un usuario existente
    def test_update_user(self):
        userid = 123456
        # Generamos un usuario para luego editarlo
        payload = {
            "userid": userid,
            "username": "Pepito Perez",
            "age": 29
        }
        response = requests.post(f'{base_url}user', json = payload)
        payload2 = {
            "username": "Juan Diego Cubillos editado",
            "age": 35
        }
        response = requests.put(f'{base_url}user/{userid}', json=payload2)
        if response.status_code == 200:
            self.assertEqual(response.status_code,200)
            # payload2['userid']=userid
            # self.assertEqual(response.json()['Message'], 'Usuario actualizado')
        else:
            self.assertEqual(response.status_code,404)
            self.assertEqual(response.json()['Message'],  'Usuario no encontrado')
    #Prueba el método update con un userid que no existe
    
    def test_update_user_notfound(self):
        userid=999999999
        payload = {
            "username": "Juan Diego Cubillos",
            "age": 35
        }
        response = requests.put(f'{base_url}user/{userid}', json=payload)
        if response.status_code == 200:
            self.assertEqual(response.status_code,200)
            payload['userid']=userid
            self.assertEqual(response.json()['Message'], 'Usuario actualizado')
        elif response.status_code == 404:
            self.assertEqual(response.status_code,404)
            self.assertEqual(response.json()['Message'],  'Usuario no encontrado')

#Prueba el método delete
class TestDelete(unittest.TestCase):
    #Prueba el método delete con un usuario existente
    def test_delete_user(self):
        userid = 9999998
        # Generamos un usuario para luego eliminarlo
        payload = {
            "userid": userid,
            "username": "Pepito Perez",
            "age": 29
        }
        response = requests.post(f'{base_url}user', json=payload)
        response = requests.delete(f'{base_url}user/{userid}')
        if response.status_code == 200:
            self.assertEqual(response.status_code,200)
            self.assertEqual(response.json()['Message'], 'success')
            print("Usuario eliminado")
        else:
            self.assertEqual(response.status_code,404)
            self.assertEqual(response.json()['Message'],  'Usuario no encontrado')
            print("Usuario no encontrado")
    #Prueba el método delete con un userid que no existe
    def test_delete_user_notfound(self):
        userid=999999999
        response = requests.delete(f'{base_url}user/{userid}')
        if response.status_code == 200:
            self.assertEqual(response.status_code,200)
            self.assertEqual(response.json()['Message'], 'Usuario eliminado')
            print("Usuario eliminado")
        elif response.status_code == 404:
            self.assertEqual(response.status_code,404)
            self.assertEqual(response.json()['Message'],  'Usuario no encontrado')
            print("Usuario no encontrado")
            
#Prueba el método list
class TestList(unittest.TestCase):
    #Prueba el método listar todos los usuarios
    def test_list_user(self):
        userid=1
        response = requests.get(f'{base_url}users')
        #Solo se comprueba el status code porque el body es una lista variable
        if response.status_code == 200:
            self.assertEqual(response.status_code,200)
        else:
            self.assertEqual(response.status_code,204)
            self.assertEqual(response.json()['Message'], 'La tabla está vacía')
    