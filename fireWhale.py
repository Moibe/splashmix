import globales
import firebase_admin
from firebase_admin import auth
from firebase_admin import firestore
from firebase_admin import credentials

if globales.firebase_auth == 'prod':
    cred = credentials.Certificate('config_prod.json')
    app_name = 'splashmix-prod'
else: 
    cred = credentials.Certificate('config_dev.json')
    app_name = 'splashmix-dev'

#if not firebase_admin.get_app(name=app_name):    
firebase_admin.initialize_app(cred, name=app_name)

app_instance = firebase_admin.get_app(name=app_name)
db = firestore.client(app=app_instance)

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
        user = auth.get_user(uid, app=app_instance) #Obtengo el objeto con todos los datos.
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

def obtenerDocumentoIDPorUID(coleccion, uid):
    """
    Busca y retorna el ID del documento que contiene el UID especificado.
    Útil cuando el ID del documento es diferente al UID de Firebase.
    
    Args:
        coleccion (str): El nombre de la colección (ej: 'usuarios').
        uid (str): El UID de Firebase a buscar.
    
    Returns:
        str: El ID del documento si lo encuentra, None si no existe.
    """
    try:
        # Busca en la colección documentos que tengan el campo 'uid' igual al UID especificado
        query = db.collection(coleccion).where('uid', '==', uid).limit(1)
        resultados = query.stream()
        
        for doc in resultados:
            return doc.id  # Retorna el ID del documento encontrado
        
        # Si no encontró nada
        print(f"❌ No se encontró documento con UID '{uid}' en la colección '{coleccion}'")
        return None
        
    except Exception as e:
        print(f"❌ Error al buscar documento por UID: {e}")
        return None

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

def obtenDocumento(coleccion, dato):
    """
    Obtiene todos los datos de un documento de Firestore como un diccionario.

    Args:
        coleccion (str): El nombre de la colección.
        dato (str): El ID del documento a obtener.

    Returns:
        dict or None: El diccionario completo del documento si existe, o None si no existe.
    """
    # Define la referencia al documento
    doc_ref = db.collection(coleccion).document(dato) 

    # 1. Obtiene el documento (una sola lectura)
    documento = doc_ref.get()
    
    # 2. Verifica si el documento existe
    if documento.exists:
        # Convierte el snapshot del documento a un diccionario
        diccionario = documento.to_dict()
        
        print("✔️ Documento encontrado. Esto es el diccionario completo: ", diccionario)
        
        # 3. Retorna el diccionario completo
        return diccionario
    else:
        print(f"❌ Documento '{dato}' no existe en la colección '{coleccion}'.")
        return None

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

def creaDatoMultipleConMovimiento(coleccion, dato, data_dict):
    """
    Crea un nuevo documento y registra automáticamente su primer movimiento.
    Ideal para crear usuarios por primera vez.

    Args:
        coleccion (str): El nombre de la colección (ej: 'usuarios').
        dato (str): El ID del documento (ej: uid del usuario).
        data_dict (dict): Diccionario con los datos del documento principal.
    """
    from datetime import date
    
    # Primero definimos la referencia al documento
    doc_ref = db.collection(coleccion).document(dato)
    
    try:
        # 1. Crea el documento principal
        doc_ref.set(data_dict)
        
        print(f"✔️ Documento '{dato}' creado en la colección '{coleccion}' con los siguientes datos:")
        for key, value in data_dict.items():
            print(f"  - {key}: {value}")
        
        # 2. Obtiene la fecha y timestamp actual
        from datetime import datetime
        import pytz
        
        # Obtiene la zona horaria UTC-6
        tz_mexico = pytz.timezone('America/Mexico_City')
        ahora = datetime.now(tz_mexico)
        
        # Formatea la fecha en formato: 19 de noviembre de 2025, 8:54:14 p.m. UTC-6
        meses = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']
        mes_nombre = meses[ahora.month - 1]
        am_pm = 'a.m.' if ahora.hour < 12 else 'p.m.'
        hora_12 = ahora.hour if ahora.hour <= 12 else ahora.hour - 12
        if hora_12 == 0:
            hora_12 = 12
        fecha_formateada = f"{ahora.day} de {mes_nombre} de {ahora.year}, {hora_12}:{ahora.minute:02d}:{ahora.second:02d} {am_pm} UTC-6"
        
        timestamp = int(datetime.now(tz_mexico).timestamp() * 1000)  # Timestamp en milisegundos
        
        # 3. Crea el primer movimiento (creación del usuario) con ID: timestamp-creacion
        doc_id = f"{timestamp}-creacion"
        movimiento_ref = doc_ref.collection('movimientos').document(doc_id)
        print("Cree la colección de movimientos.")
        movimiento_ref.set({
            'fecha': fecha_formateada,
            'movimiento': 'creación'
        })
        
        print(f"✔️ Movimiento de 'creación' registrado en la subcolección 'movimientos' (fecha: {fecha_formateada})")
        
    except Exception as e:
        print(f"❌ Error al crear documento y movimiento: {e}")

def agregaMovimiento(coleccion, documento_id, tipo_movimiento, tokens):
    """
    Agrega un documento a la subcolección 'movimientos' de un documento existente.
    Ideal para registrar acciones del usuario como consumo de tokens, compras, etc.

    Args:
        coleccion (str): El nombre de la colección (ej: 'usuarios').
        documento_id (str): El ID del documento principal (ej: uid del usuario).
        tipo_movimiento (str): Descripción del movimiento (ej: 'consumo de token', 'visito página compras', 'compro paquete 1').
        tokens (int): Número de tokens que el usuario tiene en ese momento.
    """
    from datetime import date, datetime
    import pytz

    #print("El document_id es: ", documento_id)
    
    try:
        # Obtiene la referencia al documento principal
        doc_ref = db.collection(coleccion).document(documento_id)
        
        # Obtiene la zona horaria UTC-6
        tz_mexico = pytz.timezone('America/Mexico_City')
        ahora = datetime.now(tz_mexico)
        
        # Formatea la fecha en formato: 19 de noviembre de 2025, 8:54:14 p.m. UTC-6
        meses = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']
        mes_nombre = meses[ahora.month - 1]
        am_pm = 'a.m.' if ahora.hour < 12 else 'p.m.'
        hora_12 = ahora.hour if ahora.hour <= 12 else ahora.hour - 12
        if hora_12 == 0:
            hora_12 = 12
        fecha_formateada = f"{ahora.day} de {mes_nombre} de {ahora.year}, {hora_12}:{ahora.minute:02d}:{ahora.second:02d} {am_pm} UTC-6"
        
        timestamp = int(datetime.now(tz_mexico).timestamp() * 1000)  # Timestamp en milisegundos
        
        # Convierte el tipo_movimiento a una palabra única en minúsculas para el ID
        # Ejemplos: "consumo de token" -> "consumo", "compra paquete 1" -> "compra"
        accion = tipo_movimiento.split()[0].lower()
        
        # Crea un nuevo documento en la subcolección 'movimientos' con ID: timestamp-accion
        doc_id = f"{timestamp}-{accion}"
        movimiento_ref = doc_ref.collection('movimientos').document(doc_id)
        movimiento_ref.set({
            'fecha': fecha_formateada,
            'movimiento': tipo_movimiento,
            'tokens': tokens
        })
        
        print(f"✔️ Movimiento '{tipo_movimiento}' registrado para el documento '{documento_id}' (fecha: {fecha_formateada})")
        
    except Exception as e:
        print(f"❌ Error al agregar movimiento: {e}")

def verificar_token(id_token):
    """Verifica el token de ID de Firebase."""
    try:
        # Verifica el token y decodifica la información del usuario
        decoded_token = auth.verify_id_token(id_token, app=app_instance)
        #uid = decoded_token['uid']
        uid = decoded_token.get('uid')
        return uid  # Retorna el UID del usuario si el token es válido
    except auth.InvalidIdTokenError as e:
        print(f"Token inválido: {e}")
        return None  # Retorna None si el token es inválido

def cobrar_token(collection_name, document_id, field_name, amount=1):
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