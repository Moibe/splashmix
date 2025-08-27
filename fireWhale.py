import globales
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from firebase_admin import auth

if globales.firebase_auth == 'prod':
    cred = credentials.Certificate('config_prod.json')
    #app_name = 'fireWhale_app'
else: 
    cred = credentials.Certificate('config_dev.json')
    #app_name = 'fireWhale_app'

if not firebase_admin.get_app('default'):    
    firebase_admin.initialize_app(cred)

db = firestore.client()

def obtenDatosUIDFirebase(uid):
    """
    Verifica si un UID existe en Firebase Authentication.
    Esto con el fin de evitar que se cambié el id arbitrareamente desde localstorage.

    Args:
        uid (str): El User ID (UID) que se desea verificar.

    Returns:
        bool: True si el usuario con ese UID existe, False en caso contrario.
    """
    try:
        user = auth.get_user(uid) #Obtengo el objeto con todos los datos.
        print("Ésto es el user obtenido de la comprobación: ", user)
        email = user.email
        displayName = user.display_name
        
        # Si la operación es exitosa, el usuario existe
        print(f"✔️ Usuario con UID '{uid}' encontrado en Firebase Auth: {user.email or 'sin email'}")
        return email, displayName 
    except auth.UserNotFoundError:
        # Esta excepción se lanza específicamente si el UID no existe
        print(f"❌ Usuario con UID '{uid}' NO encontrado en Firebase Auth.")
        return None, None
    except Exception as e:
        # Captura cualquier otro error (ej. problemas de conexión, permisos)
        print(f"❌ Error al verificar usuario con UID '{uid}': {e}")
        return None, None    

def obtenDato(coleccion, dato, info):
    
    #Primero debemos definir la referencia al documento, o sea a la hoja de usuario.
    doc_ref = db.collection(coleccion).document(dato) 

    #Éste es el documento que tiene los datos de ella.
    documento = doc_ref.get()
          
    #Quizá éste segmento que comenté era el que producia nuevos documentos sin deber.
    if documento.exists:
        #Recuerda la conversión a diccionario.
        documento = doc_ref.get() 
        diccionario = documento.to_dict()
        print("Esto es el diccionario: ", diccionario)
        resultado = diccionario.get(info)
        print("Éste es el resultado...", resultado)
        return resultado
        pass #El documento si existe.        
    else:
        print("No existe el documento, es un nuevo usuario.")
        return None
        #No crees nada pero avisa que no existe.
        #creaDato(coleccion, dato, 'tokens', 5) #porque agregará 5 tokens.

def editaDato(coleccion, dato, info, contenido):

    #Primero debemos definir la referencia al documento, o sea a la hoja de usuario.
    doc_ref = db.collection(coleccion).document(dato)
    
    doc_ref.update({
        # 'quote': quote,
        info: contenido,
    })

def creaDato(coleccion, dato, info, contenido):

    #Primero debemos definir la referencia al documento, o sea a la hoja de usuario.
    doc_ref = db.collection(coleccion).document(dato)
    
    doc_ref.set({
        # 'quote': quote,
        info: contenido,
    })

def creaDatoMultiple(coleccion, dato, data_dict):
    """
    Crea un nuevo documento o sobrescribe uno existente en Firestore
    con múltiples pares de campo-contenido.

    Args:
        coleccion (str): El nombre de la colección donde se creará/actualizará el documento.
        dato (str): El ID del documento que se va a crear o sobrescribir.
        data_dict (dict): Un diccionario donde las claves son los nombres de los campos
                          y los valores son el contenido de esos campos.
                          Ej: {'nombre': 'Juan', 'edad': 30, 'activo': True}
    """
    # Primero definimos la referencia al documento
    doc_ref = db.collection(coleccion).document(dato)
    
    try:
        # Usamos .set() y le pasamos el diccionario completo.
        # Esto sobrescribirá el documento si ya existe con los nuevos datos.
        doc_ref.set(data_dict)
        
        print(f"✔️ Documento '{dato}' creado/sobrescrito en la colección '{coleccion}' con los siguientes datos:")
        for key, value in data_dict.items():
            print(f"  - {key}: {value}")
            
    except Exception as e:
        print(f"❌ Error al crear/sobrescribir documento '{dato}' en '{coleccion}': {e}")

def verificar_token(id_token):
    """Verifica el token de ID de Firebase."""
    try:
        # Verifica el token y decodifica la información del usuario
        decoded_token = auth.verify_id_token(id_token)
        uid = decoded_token['uid']
        return uid  # Retorna el UID del usuario si el token es válido
    except auth.InvalidIdTokenError as e:
        print(f"Token inválido: {e}")
        return None  # Retorna None si el token es inválido

def incrementar_campo_numerico(collection_name, document_id, field_name, amount=1):
    """
    Incrementa un campo numérico en un documento de Firestore de forma atómica.
    Si el documento no existe, lo crea e inicializa el campo con el 'amount'.
    Si el campo no existe en un documento existente, lo inicializa y aplica el incremento.

    Args:
        collection_name (str): El nombre de la colección.
        document_id (str): El ID del documento.
        field_name (str): El nombre del campo numérico a incrementar.
        amount (int/float): La cantidad por la cual incrementar (puede ser negativo para decrementar).
    """
    doc_ref = db.collection(collection_name).document(document_id)

    try:
        # Usamos .set() con merge=True para comportamiento de "upsert".
        # Si el documento no existe, lo crea.
        # Si el campo no existe, lo crea e inicializa con 'amount'.
        # Si el campo ya existe, lo incrementa con 'amount'.
        doc_ref.set(
            {field_name: firestore.Increment(amount)},
            merge=True  # Esta es la clave para que se cree si no existe y no sobrescriba otros campos
        )
        print(f"✔️ Campo '{field_name}' en el documento '{document_id}' actualizado/creado e incrementado en {amount}.")
    except Exception as e:
        print(f"❌ Error al operar en el campo '{field_name}' del documento '{document_id}': {e}")

def inhabilitaUsuarioProveedor(servidor):

    editaDato('quota', servidor, 'segundos', -5) 
