import os 
import time
import random
import bridges
import globales
import importlib
import powerWhale
import gradio as gr

from huggingface_hub import HfApi

def theme_selector():
    temas_posibles = [
        gr.themes.Base(),
        gr.themes.Default(),
        gr.themes.Glass(),
        gr.themes.Monochrome(),
        gr.themes.Soft(),
        gr.themes.Citrus(),
        gr.themes.Ocean(),
        gr.themes.Origin(),
        
    ]
    tema = random.choice(temas_posibles)
    return tema

def eligeAPI(opcion):
    #Elige API y usuario proveedor.
    print(opcion)
    funciones = {
        "eligeQuotaOCosto": eligeQuotaOCosto, #Ésta es la usada por mi InstantID.
        "eligeAOB": eligeAOB, #Se elige una u otra de un par determinado.
        "eligeGratisOCosto": eligeGratisOCosto #Cuando una instancia gratuita tiene el suficiente poder para operar y costo solo otorga ventajas adicionales como velocidad.
        #Contemplar otra opción triquota.
    }    
    if opcion in funciones:
        funcion_elegida = funciones[opcion]
        api, tipo_api, usuario_proveedor = funcion_elegida()
    else:
        print("Opción no válida")

    return api, tipo_api, usuario_proveedor

#Los tipos de elección son diferentes porque tienen diferentes reglas de negocio.

def eligeGratisOCosto():
#Se eligirá en los casos en los que sin costo funciona bien como Astroblend pero por si se quiere mejorar hacia Costo.
#Por ahora funcionará exactamente igual que eligeAoB, en el futuro se basará en reglas de membresía.
    apis = [globales.api_a, globales.api_b]
    api_elegida = random.choice(apis)
    print("Print api elegida: ", api_elegida)
    api, tipo_api = api_elegida
    return api, tipo_api

def eligeAOB():
#Se eligirá cuando se tenga un control sobre la cantidad en queu y se redirija hacia una segunda fuente alternativa.
    # Lista con las opciones
    apis = [globales.api_a, globales.api_b]
    api_elegida = random.choice(apis)
    #IMPORTANTE, aquí A o B por ahora siempre será A, porque queremos que lo haga con MP3.
    #api_elegida = globales.api_a
    print("Print api elegida: ", api_elegida)
    api, tipo_api = api_elegida
    return api, tipo_api

def eligeQuotaOCosto():
    #Importante, ahora habrá varios proveedores de segundos disponibles, y mientras cualquiera de ellos tenga segundos disponibles, nos quedamos en ésta.
    #Para que sea transparente para éste proceso, al final obtendremos quota_disponible y pasará el resto del proceso de forma transparente.
    usuario_proveedor = revisorCuotas()

    if usuario_proveedor == 'costo': 
        api, tipo_api = globales.api_cost 
        return api, tipo_api, usuario_proveedor
    else: 
        api, tipo_api = globales.api_zero 
        return api, tipo_api, usuario_proveedor

def revisorCuotas(): 
    proveedores_poder = globales.proveedores
    total_elementos = len(proveedores_poder)

    for indice, elemento in enumerate(proveedores_poder):
        print(elemento) 
        quota_disponible = powerWhale.obtenDato("power", elemento, "segundos")
        print(f"Servidor: {elemento}: segundos: {quota_disponible}.")
        if quota_disponible > globales.process_margin: 
            #Si la quota_disponible es mayor que lo que nos costará el proceso, selecciona ese servidor. 
            print(f"Servidor seleccionado: {elemento}, que tiene {quota_disponible} segundos disponibles.")
            if indice == total_elementos - 1: #Si el seleccionado es el último elemento, revisar si sus segundos quedaron al limite para hacer el encendido preventivo.
                print("¡Estamos en el último elemento, revisión de límite para encendido preventivo.")
                #print("If cuota disponible < globales.process_margin") #If cuota disponible después de la resta!
                print(f"Quota Disponible = {quota_disponible} y process margin = {globales.process_margin}")
                if quota_disponible - globales.process_cost < globales.process_margin:
                    initAPI(globales.api_cost) 
                   #proveedor, segundos disponibles.
            return elemento        
    #Si llegó aquí es porque ninguno de los procesos tuvo cuota suficiente para llevar a cabo el proceso. 
    #Por lo tanto encenderemos el de costo:
    initAPI(globales.api_cost) 
    return 'costo' #Regresa 'costo' si ninguno de los elementos tiene cuota disponible. 

def initAPI(api):
    print("Estoy en initAPI...")
    global result_from_initAPI
    try:
        repo_id = api[0]
        llave = HfApi(token=bridges.hug)
        runtime = llave.get_space_runtime(repo_id=repo_id)
        #"RUNNING_BUILDING", "APP_STARTING", "SLEEPING", "RUNNING", "PAUSED", "RUNTIME_ERROR"
        if runtime.stage == "SLEEPING":
            llave.restart_space(repo_id=repo_id)
            print("Hardware: ", runtime.hardware)
        result_from_initAPI = runtime.stage
    except Exception as e:
        #Aquí llegó porque se le dio una tupla y no un string con el nombre de la api.
        print("No api, encendiendo: ", e)
        result_from_initAPI = str(e)    
    return result_from_initAPI

def titulizaExcepDeAPI(e): 
    #Resume una excepción a un título manejable.
    print("Antes de titulizar la excepción es: ", e)

    if "RUNTIME_ERROR" in str(e):
        resultado = "RUNTIME_ERROR" #api mal construida tiene error.
    elif "PAUSED" in str(e):
        resultado = "PAUSED" 
    elif "The read operation timed out" in str(e): #IMPORTANTE, ESTO TAMBIÉN SUCEDE CUANDO LA DESPIERTAS Y ES INSTANTÁNEO.
        resultado = "STARTING"
    elif "GPU quota" in str(e): 
        resultado = "QUOTA"
        #resultado = recortadorQuota(str(e)) #Cuando se trata de quota regresa el resultado completo convertido a string.
    elif "handshake operation timed out" in str(e):
        resultado = "HANDSHAKE_ERROR"
    elif "File None does not exist on local filesystem and is not a valid URL." in str(e):
        resultado = "NO_FILE"
    elif "too many values to unpack (expected 2)" in str(e): #No es lo ideal pero instantid no envía mensaje tan específico, FUTURE: tendrías que modificarlo haya y no se si lo valga. 
        resultado = "NO_FACE" 
    #A partir de aquí son casos propios de cada aplicación.
    elif "Unable to detect a face" in str(e): #Al parecer solo imageblend y no instantID llegan aquí, porque InstID no te dice que no detectó rostro.
        resultado = "NO_FACE"
    elif "positions" in str(e):
        resultado = "NO_POSITION"
    elif "401" in str(e):
        resultado = "UNAUTHORIZED"
    elif "Error" in str(e):
        print("Si entré a la detección 182 de la excepción: ") #Se atraviesa con ésta antes de llegar a la de 401.
        resultado = "GENERAL"
    else: 
        resultado = "GENERAL"

    return resultado
    
def recortadorQuota(texto_quota):
    print("Esto es texto_quota:" , texto_quota)
    
    # Encontrar el índice de inicio (después de "exception:")
    indice_inicio = texto_quota.find("exception:") + len("exception:")
    print("Índice inicio es: ", indice_inicio)
    # Encontrar el índice de final (antes de "<a")
    indice_final = texto_quota.find("<a")
    print("Índice final es: ", indice_final)

    if indice_final == -1: #Significa que no encontró el texto "<a" entonces buscará Sign-Up.
        indice_final = texto_quota.find("Sign-up")
        print("Al encontrar indice_final fue buscando SignUp: ", indice_final)
    
    #Extraer la subcadena
    subcadena = texto_quota[indice_inicio:indice_final]

    #Y si el objetivo es nunca desplegar el texto Hugging Face, éste es el plan de escape final.
    if "requested vs." in subcadena: 
        nuevo_mensaje = "QUOTA"
        return nuevo_mensaje
    else:
        print(subcadena)
    
    return subcadena

def desTuplaResultado(resultado):
    #Procesa la tupla recibida y la convierte ya sea en imagen(path) o error(string)       
    if isinstance(resultado, tuple):

        ruta_imagen_local = resultado[0]
        print("Ésto es resultado ruta imagen local: ", ruta_imagen_local)
        return ruta_imagen_local       

    #NO PROCESO CORRECTAMENTE NO GENERA UNA TUPLA.
    #CORRIGE IMPORTANTE: QUE NO SE SALGA DEL CICLO DE ESA IMAGEN AL ENCONTRAR ERROR.
    else:
        #NO ES UNA TUPLA:
        print("El tipo del resultado cuando no fue una tupla es: ", type(resultado))                
        texto = str(resultado)
        segmentado = texto.split('exception:')
        #FUTURE: Agregar que si tuvo problemas con la imagen de referencia, agregue en un 
        #Log de errores porque ya no lo hará en el excel, porque le dará la oportunidad con otra 
        #imagen de posición.
        try:
            #Lo pongo en try porque si no hay segmentado[1], suspende toda la operación. 
            print("Segmentado[1] es: ", segmentado[1])
            mensaje = segmentado[1]
            return mensaje
        except Exception as e:
            print("Error en el segmentado: ", e)
            # mensaje = "concurrent.futures._base.CancelledError"
            # concurrents = concurrents + 1
        finally: 
            pass

def get_mensajes(idioma):
    """
    Obtiene el módulo de mensajes correspondiente al idioma especificado.
    Args:
        idioma (str): Código del idioma (ej: 'es', 'en').
    Returns:
        module: Módulo de mensajes cargado dinámicamente.
    """
    #Primero el módulo normal de mensajes.
    try:
        # Intenta cargar el módulo correspondiente
        module_mensajes = importlib.import_module(f"messages.{idioma}")
        
    except ImportError:
        # Si ocurre un error al importar, carga un módulo por defecto (opcional)
        print(f"Idioma '{idioma}' no encontrado. Cargando módulo por defecto.")
        module_mensajes = importlib.import_module("messages.en")  # Por ejemplo, inglés como defecto
    #Y después el módulo de Sulku.
    try:
        # Intenta cargar el módulo correspondiente
        module_sulku = importlib.import_module(f"messages_sulku.{idioma}")
        
    except ImportError:
        # Si ocurre un error al importar, carga un módulo por defecto (opcional)
        print(f"Idioma '{idioma}' no encontrado. Cargando módulo por defecto.")
        module_sulku = importlib.import_module("messages_sulku.en")  # Por ejemplo, inglés como defecto 
    
    return module_mensajes, module_sulku   

def renombra_imagen(hero, resultado):

    timestamp_segundos = int(time.time())
    print(timestamp_segundos)

    hero = hero.replace(" ", "")

    # 1. Obtener el directorio y el nombre del archivo original
    directorio = os.path.dirname(resultado)
    nombre_original = os.path.basename(resultado)

    # 2. Crear el nuevo nombre del archivo
    nuevo_nombre = f"{hero}-{timestamp_segundos}.jpg"
    nueva_ruta = os.path.join(directorio, nuevo_nombre)

    # 3. Renombrar el archivo
    try:
        os.rename(resultado, nueva_ruta)
    except FileNotFoundError:
        print(f"Error: El archivo '{resultado}' no existe.")
    except FileExistsError:
        print(f"Error: El archivo '{nueva_ruta}' ya existe.")
    except Exception as e:
        print(f"Error inesperado: {e}")

    # 4. (Opcional) Actualizar la variable 'resultado' con la nueva ruta
    resultado = nueva_ruta
   
    return resultado

def reducirQuota(tipo_api, usuario_proveedor):
            if tipo_api == "quota":
                powerWhale.incrementar_campo_numerico("power", usuario_proveedor, 'segundos', amount=-globales.process_cost)

def defineBotones(env):
    script = "() => window.location.href = " 

    if env == 'dev':
        base_url = "'https://app.targetvox.com/"
        script_logout = script + base_url + "logout'" 
        script_buy = script + base_url + "buy'"
        
    else:
        base_url = "'https://app.splashmix.ink/"
        script_logout = script + base_url + "logout'"
        script_buy = script + base_url + "buy'"

    return script_logout, script_buy


def process_request_with_cookie(name, request: gr.Request):
    """
    Processes a request and attempts to retrieve a cookie.
    """
    user_cookie = request.cookies.get("my_cookie_name")
    if user_cookie:
        return f"Hello, {name}! Your cookie value is: {user_cookie}"
    else:
        return f"Hello, {name}! No 'my_cookie_name' cookie found."
    
def obtener_gclid_exacto(cadena):
    """
    Toma un string con el formato "GA1.1.###.###" y regresa las últimas dos cifras.

    Args:
        cadena (str): El string de entrada.

    Returns:
        str: Las dos últimas cifras unidas por un punto, o None si el formato es incorrecto.
    """
    # 1. Dividir el string en partes usando el punto como delimitador
    partes = cadena.split('.')
    
    # 2. Verificar que el formato tiene al menos 4 partes (GA1, 1, cifra, cifra)
    if len(partes) >= 4:
        # 3. Unir las dos últimas partes con un punto y retornarlas
        return f"{partes[-2]}.{partes[-1]}"
    else:
        # Retornar None si el formato no es el esperado
        return None