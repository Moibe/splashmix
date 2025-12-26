import random
import kraken
import tools
import globales
import fireWhale
import gradio as gr
import ga4Analiticas
from firebase_admin import firestore
mensajes, sulkuMessages = tools.get_mensajes(globales.mensajes_lang) #import modulo_correspondiente

result_from_displayTokens = None 
result_from_initAPI = None    

def displayTokens(usuario):
    
    global result_from_displayTokens

    print("Entré a dipslay tokens, y ésto es usuario: ", usuario)

    #Obtengamos los datos hardcodeados del usuario mio, que no existe en las colecciones: 
    tokens = fireWhale.obtenDato('usuarios', usuario, 'tokens')  
    
    novelty = fireWhale.obtenDato('usuarios', usuario, 'novelty' )
        
    if novelty == "new_user": 
        display = gr.Textbox(visible=False)
    else:
        tokens = fireWhale.obtenDato('usuarios', usuario, 'tokens') 
        #tokens = sulkuPypi.getTokens(sulkuPypi.encripta(request.username).decode("utf-8"), globales.env)
        display = visualizar_creditos(tokens, usuario) 
    
    result_from_displayTokens = display

def precarga(arreglo):    
    
    #Habrá casos en que regrese null porque entro a la app directo pero no había nadie logueado.
    print(f"En estos casos arreglo es: {arreglo} y su tipo es {type(arreglo)}.")
    
    uid = arreglo.get('uid')
    gaClient = arreglo.get('gaClient', '')
    country_ip = arreglo.get('country_ip', '')
    country_geolocation = arreglo.get('country_geolocation', '')
    country_header = arreglo.get('country_header', '')
    traffic_source = arreglo.get('traffic_source', '')
    documento_id = None  # Se asignará cuando se encuentre el documento del usuario
    #uid = '3iKefol3ZWc7ypsseFKRmXsbDAA3' #Sebas Dev. (En local no se actualiza bien firesbase :(  ))
    
    if uid == None:
        #Aquí tenemos que hacer el redireccionamiento si no hay uid.
        mensaje = 'Necesitas loguearte al sistema.'
        mensaje2 = ''
        
        return uid, gr.Accordion(label=mensaje, open=True), gr.Button(value="Login 👋🏻"), gr.Accordion(label=mensaje2, open=False)
    
    else: #Si si hubo uid continuas el camino normal.       
        #Agrega que cuando si haya uid, y cheque el user agrege el country_ip y demás si no los tenía
        #porque puede haber obtenido esos valores posteriormente.
        #Inicialización de mensajes en éste punto. 
        mensaje = 'Refresca la página con F5 por favor.'
        mensaje2 = ''
        try:
            email, displayName = fireWhale.obtenDatosUIDFirebase(uid)
            print(f"Email: {email}, displayName: {displayName}.")
            
            #Encontró un usuairo de firebase auth.
            if email or displayName: #Si encontró a cualquiera de los dos significa que si existe en firebase auth.  
                print("Estoy dentro del IF de email o displayName...")
                # Obtiene el ID del documento del usuario (puede ser diferente al UID si se creó con timestamp-uid-email)
                documento_id = fireWhale.obtenerDocumentoIDPorUID('usuarios', uid)
                
                if documento_id:  # Si encontró el documento
                    print("Si hubo documento_id... y es: ", documento_id)
                    documento_completo = fireWhale.obtenDocumento('usuarios', documento_id)
                    #EL USUARIO SI EXISTE EN FIRESTORE.
                    #Si el usuario si existe en Firestore aquí debería checar si tiene las vars country_ip y demás, si no las tiene agrégaselas.
                    print("Chequeando country vars...")
                    tools.countryChecker(documento_id, country_ip, country_geolocation, country_header)
                    if documento_completo: #Si el documento existió...
                        tokens = documento_completo.get('tokens', None)
                        despliego = documento_completo.get('despliega_creditos', True)
                        #Y los tokens existieron....
                        #El usuario tiene tokens.
                        if tokens is not None: #Significa que el usuario si tiene un registro previo en firebase.
                            print("Camino 1: Si hubo un usuario.") 
                            display_banner = False
                            display_credits = True
                            print("Por evaluuar despliego que es: ", despliego)
                            if despliego is False: #o sea si no ha comprado.
                                print("Despliego es False.")
                                #Si no ha comprado, no le muestres cuantos créditos tiene.
                                #Por alguna razón está como al revés, o aquí llega si no ha comprado :S 
                                display_credits = False
                                display_banner = True
                                #Configura el banner de mensajes y promociones solo para usuarios que no han comprado.
                            #Ahora los mensajes van a varias de forma random. Antes ->lbl_info_welcome  ahora-> 
                            print("Por poner num_mensaje...")
                            num_mensaje = random.randint(0, 5)
                            gr.Info(title="¡Bienvenido!", message=mensajes.mensajes_usuario[num_mensaje], duration=None, visible=display_banner)
                    
                        print(f"Tokens: {tokens}.")
                        mensaje = f"🐙Usuario: {email} "
                        mensaje2 = f"💶Créditos Disponibles: {tokens}."
                        
                        # Registra movimiento de "visita al sitio" si han pasado 3 horas
                        tools.registrar_visita_sitio(documento_id, tokens)
                
                else: #USUARIO NO EXISTE EN FIRESTORE, HAY QUE CREARLO.
                    #Crear usuario nuevo en firestore, con 5 tokens y guarda su info de email y displayname.
                    print("Camino 2: Usuario Nuevo:") #Aquí tmb registraremos el evento de ga4 y ahora country_ip.                 
                    # Genera el ID del documento con formato: timestamp-uid-correo
                    id_documento = tools.generar_id_documento_usuario(uid, email)
                    documento_id = id_documento  # Asigna el nuevo ID para retornarlo después
                    
                    datos_perfil = {
                    'displayName': displayName,
                    'email': email,
                    'tokens': 5,
                    'fecha_registro': firestore.SERVER_TIMESTAMP, # Para un timestamp del servidor
                    'compro': False,
                    'despliega_creditos': False,
                    'uid': uid,  # Agregamos el UID como campo para referencia
                    'country_ip': country_ip,  # Agregamos country_ip como campo para referencia
                    'country_geolocation': country_geolocation,  # Agregamos country_geolocation como campo para referencia
                    'country_header': country_header,  # Agregamos country_header como campo para referencia
                    'traffic_source': traffic_source, # Agregamos traffic_source como campo para referencia
                    'gaClient': gaClient # Agregamos gaClient como campo para referencia
                    }
                    fireWhale.creaDatoMultipleConMovimiento('usuarios', id_documento, datos_perfil) #Ésta es la creación del usuario en Firestore con el nuevo ID.
                    ga4Analiticas.send_ga4_signup_event(gaClient)
                    mensaje = f"🐙Usuario: {email} "
                    mensaje2 = f"💶Creditos Disponibles: 5." #Analizar si está bien dejarlo fijo y todo funciona bien.
                    #Una vez creado, crea de una vez su usuario de Stripe.
                    site = "splashmix"
                    respuesta = kraken.crear_cliente_stripe(email, uid, site)
                    print("Respuesta de Kraken es: ")
                    print(respuesta)
                    if 'error' in respuesta:
                        #Aquí hubo un error de Kraken, principalmente por no estar disponible, por ende no podrá crear el usuario. 
                        #Podrías ignorarlo si al momento de hacer pagos lo vuelve intentar crear.
                        print("Kraken está apagado, prendiendo...")
                        pass
                    else: #Si no hubo error continua con el proceso normal. 
                        pass #Al parecer si le da tiempo suficiente de prender. 
                        #Checar si al hacer compra se vuelve a crear el usuario.    
                    customer_id = respuesta.get('customer_id')
                    # Actualiza el campo 'cus' con el ID del cliente de Stripe usando id_documento (usuario nuevo)
                    fireWhale.editaDato('usuarios', id_documento, 'cus', customer_id)
                    # print("cus agregado")
            else: #Si no existe en FIREBASE AUTH, es un usuario inválido. FutureImportante: ¿Debería regresarlo a login? 
                mensaje = "Usuario inválido."
                mensaje2 = "Recarga la página si no puedes ver tus créditos." #Future,¿éste mensaje puede ser un link a login más que un texto?
        except Exception as e:
            print(f"Excepción: {e}")
        print("Display credits es: ", display_credits)
        # Retorna documento_id si existe (para usuarios existentes), sino uid (para usuarios nuevos o inválidos)
        usuario_a_retornar = documento_id if documento_id else uid
        print("A punto de terminar, mensaje es:", mensaje)
        return usuario_a_retornar, gr.Accordion(label=mensaje, open=False), gr.Button(), gr.Accordion(label=mensaje2, open=False, visible=display_credits)  

def visualizar_creditos(nuevos_creditos, usuario):

    html_credits = f"""
    <div>
    <div style="text-align: left;">👤<b>{mensajes.lbl_username}: </b> {usuario}</div><div style="text-align: right;">💶<b>{mensajes.lbl_credits}: </b> {nuevos_creditos}</div>
    </div>
                    """    
     
    return html_credits

#Controla lo que se depliega en el frontend y que tiene que ver con llamados a Sulku.
def noCredit():
    info_window = sulkuMessages.out_of_credits
    path = 'images/no-credits.png'
    return path, info_window 

def aError(excepcion):
    #print("La excepción es:", excepcion)
    info_window = manejadorExcepciones(excepcion)
    path = 'images/error.png'      
    return path, info_window

def manejadorExcepciones(excepcion):
    #El parámetro que recibe es el texto despliega ante determinada excepción:
    if excepcion == "PAUSED": 
        info_window = sulkuMessages.PAUSED
    elif excepcion == "RUNTIME_ERROR":
        info_window = sulkuMessages.RUNTIME_ERROR
    elif excepcion == "STARTING":
        info_window = sulkuMessages.STARTING
    elif excepcion == "HANDSHAKE_ERROR":
        info_window = sulkuMessages.HANDSHAKE_ERROR
    elif excepcion == "GENERAL":
        info_window = sulkuMessages.GENERAL
    elif excepcion == "NO_FACE":
        info_window = sulkuMessages.NO_FACE
    elif excepcion == "NO_FILE":
        info_window = sulkuMessages.NO_FILE
    elif excepcion == "NO_POSITION": #Solo aplíca para Splashmix.
        info_window = sulkuMessages.NO_POSITION
    elif excepcion == "UNAUTHORIZED": #Solo aplíca para Splashmix.
        info_window = sulkuMessages.UNAUTHORIZED
    elif excepcion == "QUOTA": #Solo aplíca para Splashmix.
        info_window = sulkuMessages.QUOTA
    # elif "quota" in excepcion: #Caso especial porque el texto cambiará citando la cuota.
    #     info_window = excepcion
    else:
        info_window = sulkuMessages.ELSE

    return info_window

def evaluaResultadoUsuario(resultado, personaje): 

    if "image.webp" in resultado:
        #Si es imagen, debitarás.
        resultado = tools.renombra_imagen(personaje, resultado)
        #accion = "no-debitar" if globales.acceso == "libre" else "debita"
        info_window = sulkuMessages.result_ok
    else: #CUANDO NO TRAE IMAGEN EL ERROR QUE PODRÍA TRAER ES NO_FACE O GENERAL (y ambos significarían que no detecto rostro).
        #Si no es imagen es un texto que nos dice algo.
        resultado, info_window = aError(excepcion = resultado)
        return resultado, info_window         
           
    return resultado, info_window

def actualizador_navbar(usuario, result, info_window, genero=None, personaje=None, api_tipo=None):
    
    apertura = False #Cerrado es el valor default del acordeón.
    
    #Dependiendo del resultado obtenido deberé debitar o no:     
    #Cuando no hay imagen (Error directo de mass): error.png
    if "jpg" in result: #Cuando la imagen es correcta. El resultado es un archivo .jpg
        #Debita uno de la cuota de ese usuario y despliegalo.
        fireWhale.cobrar_token('usuarios', usuario, 'tokens', amount=-globales.costo_work)
        documento_completo = fireWhale.obtenDocumento('usuarios', usuario) 
        tokens = documento_completo.get('tokens', None)
        despliega_creditos = documento_completo.get('despliega_creditos', None)
        visibilidad = despliega_creditos
        
        # Agrega el movimiento de consumo de token con campos opcionales
        kwargs_movimiento = {}
        if genero:
            kwargs_movimiento['genero'] = genero
        if personaje:
            kwargs_movimiento['personaje'] = personaje
        if api_tipo:
            kwargs_movimiento['api_usada'] = api_tipo
        
        fireWhale.agregaMovimiento('usuarios', usuario, 'consumo de token', tokens, **kwargs_movimiento)
        
    elif "error.png" in result:
        # Error en la generación de imagen - registrar movimiento de error
        documento_completo = fireWhale.obtenDocumento('usuarios', usuario)
        tokens = documento_completo.get('tokens', None)
        despliega_creditos = documento_completo.get('despliega_creditos', None)
        visibilidad = despliega_creditos
        
        # Agrega el movimiento de error con el mensaje
        kwargs_error = {'mensaje_error': info_window}
        if genero:
            kwargs_error['genero'] = genero
        if personaje:
            kwargs_error['personaje'] = personaje
        if api_tipo:
            kwargs_error['api_usada'] = api_tipo
        
        fireWhale.agregaMovimiento('usuarios', usuario, 'error', tokens, **kwargs_error)
        
    else: 
        #Controla si se abre el botón de recargar créditos.
        if "no-credits" in result:
            apertura = True
            visibilidad = True
            fireWhale.agregaMovimiento('usuarios', usuario, 'sin_credito', 0)
            tokens = 0 
        else:
            apertura = False
            visibilidad = despliega_creditos #Si el asunto no fue de los créditos, despliega como indique el firestore del usuario. 
        
        # tokens = fireWhale.obtenDato('usuarios', usuario, 'tokens') #obtienes
        # print("Estos son los tokens que tiene actualmente el usuario:", tokens)
        #Por ahora no debites.
    return gr.Accordion(label=f"💶Creditos Disponibles: {tokens}", open=apertura, visible=visibilidad) 