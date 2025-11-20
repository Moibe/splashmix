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
    #uid = '3iKefol3ZWc7ypsseFKRmXsbDAA3' #Sebas Dev. (En local no se actualiza bien firesbase :(  ))
    
    if uid == None:
        #Aquí tenemos que hacer el redireccionamiento si no hay uid.
        mensaje = 'Necesitas loguearte al sistema.'
        mensaje2 = ''
        
        return uid, gr.Accordion(label=mensaje, open=True), gr.Button(value="Login 👋🏻"), gr.Accordion(label=mensaje2, open=False)
    
    else: #Si si hubo uid continuas el camino normal.       
        
        try:
            email, displayName = fireWhale.obtenDatosUIDFirebase(uid)
            print(f"Email: {email}, displayName: {displayName}.")
            
            #Encontró un usuairo de firebase auth.
            if email or displayName: #Si encontró a cualquiera de los dos significa que si existe en firebase auth.  
                documento_completo = fireWhale.obtenDocumento('usuarios', uid)
                #EL USUARIO SI EXISTE EN FIRESTORE.
                if documento_completo: #Si el documento existió...
                    tokens = documento_completo.get('tokens', None)
                    compro = documento_completo.get('compro', True)
                    #Y los tokens existieron....
                    #El usuario tiene tokens.
                    if tokens is not None: #Significa que el usuario si tiene un registro previo en firebase.
                        #print("Camino 1: Si hubo un usuario.") 
                        display_banner = False
                        display_credits = True
                        if compro is False: #o sea si no ha comprado.
                            #Si no ha comprado, no le muestres cuantos créditos tiene.
                            #Por alguna razón está como al revés, o aquí llega si no ha comprado :S 
                            display_credits = False
                            display_banner = True
                            #Configura el banner de mensajes y promociones solo para usuarios que no han comprado.
                            #Ahora los mensajes van a varias de forma random. Antes ->lbl_info_welcome  ahora-> 
                            num_mensaje = random.randint(0, 5)
                            gr.Info(title="¡Bienvenido!", message=mensajes.mensajes_usuario[num_mensaje], duration=None, visible=display_banner)
                    
                        print(f"Tokens: {tokens}.")
                        mensaje = f"🐙Usuario: {email} "
                        mensaje2 = f"💶Créditos Disponibles: {tokens}."
                
                else: #USUARIO NO EXISTE EN FIRESTORE, HAY QUE CREARLO.
                    #Crear usuario nuevo en firestore, con 5 tokens y guarda su info de email y displayname.
                    print("Camino 2: Usuario Nuevo:") #Aquí tmb registraremos el evento de ga4.                    
                    datos_perfil = {
                    'displayName': displayName,
                    'email': email,
                    'tokens': 5,
                    'fecha_registro': firestore.SERVER_TIMESTAMP, # Para un timestamp del servidor
                    'compro': False
                    }
                    fireWhale.creaDatoMultipleConMovimiento('usuarios', uid, datos_perfil) #Ésta es la creación del usuario en Firestore.
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
                    fireWhale.editaDato('usuarios', uid, 'cus', customer_id)
                    # print("cus agregado")
            else: #Si no existe en FIREBASE AUTH, es un usuario inválido. FutureImportante: ¿Debería regresarlo a login? 
                mensaje = "Usuario inválido."
                mensaje2 = "Recarga la página si no puedes ver tus créditos." #Future,¿éste mensaje puede ser un link a login más que un texto?
        except Exception as e:
            print(f"Excepción: {e}")
        print("Display credits es: ", display_credits)
        return uid, gr.Accordion(label=mensaje, open=False), gr.Button(), gr.Accordion(label=mensaje2, open=False, visible=display_credits)  

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

def actualizador_navbar(usuario, result, info_window, sin_creditos):
    
    #Controla si se abre el botón de recargar créditos.
    # Abre el acordeón si: 1) no hay créditos detectado en perform() O 2) resultado contiene "no-credits"
    if sin_creditos or "no-credits" in result:
        apertura = True
    else:
        apertura = False

    #Dependiendo del resultado obtenido deberé debitar o no:     
    #Cuando no hay imagen (Error directo de mass): error.png
    if "jpg" in result: #Cuando la imagen es correcta. El resultado es un archivo .jpg
        #Debita uno de la cuota de ese usuario y despliegalo.
        fireWhale.cobrar_token('usuarios', usuario, 'tokens', amount=-globales.costo_work)
        tokens = fireWhale.obtenDato('usuarios', usuario, 'tokens') #A pesar de la maniobra para obtener y restar, para poder desplegarlo de todas formas necesitaremos hacer otra lectura de firebase.
        print(f"Después de debitar tienes {tokens} tokens.")
        fireWhale.agregaMovimiento('usuarios', usuario, 'consumo de token', tokens)
        
    else: 
        #Lo demás debería ser un error.
        print("Resultado incorrecto e incobrable...")
        #Future, también podrías no hacer la ida a firebase y obtenerlo de valor previo.
        tokens = fireWhale.obtenDato('usuarios', usuario, 'tokens') #obtienes
        print("Estos son los tokens que tiene actualmente el usuario:", tokens)
        #Por ahora no debites.
    return gr.Accordion(label=f"💶Creditos Disponibles: {tokens}", open=apertura) 