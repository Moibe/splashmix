import kraken
import tools
import globales
import fireWhale
import gradio as gr
from firebase_admin import firestore
mensajes, sulkuMessages = tools.get_mensajes(globales.mensajes_lang) #import modulo_correspondiente
import time
import ga4Analiticas

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
    
    uid = arreglo['uid']
    gaClient = arreglo.get('gaClient', '')

    #uid = 'uQDteq2ezQP6S1KNh1mf80wMYPg1' #Asumimos que ya lo traemos de auth y que aún no se guarda en firestore.
        
    if uid == None:
        #Aquí tenemos que hacer el redireccionamiento si no hay uid.
        mensaje = 'Necesitas loguearte al sistema.'
        mensaje2 = ''
        return uid, gr.Accordion(label=mensaje, open=True), gr.Button(value="Login 👋🏻"), gr.Accordion(label=mensaje2, open=False)
    
    else: #Si si hubo uid continuas el camino normal. 
        try:
            email, displayName = fireWhale.obtenDatosUIDFirebase(uid)
            print(f"Email: {email}, displayName: {displayName}.")
            
            if email or displayName: #Si encontró a cualquiera de los dos significa que si existe en firebase auth.  
                tokens = fireWhale.obtenDato('usuarios', uid, 'tokens') #En firestore los usuarios estarán identificados por su uid de auth.
                if tokens is not None: #Significa que el usuario si tiene un registro previo en firebase.
                    print("Camino 1: Si hubo un usuario.") 
                #La lógica de crear un usuario nuevo debería estar afuera, aquí.
                    print(f"Tokens: {tokens}.")
                    mensaje = f"🐙Usuario: {email} "
                    mensaje2 = f"💶Creditos Disponibles: {tokens}."
                else: #Si no se encontró significa que el usuario no existe en Firestore y deberíamos crear uno nuevo.
                    #Crear usuario nuevo en firestore, con 5 tokens y guarda su info de email y displayname.
                    print("Camino 2: Usuario Nuevo:") #Aquí tmb registraremos el evento de ga4.
                    gr.Info(title="¡Bienvenido!", message=mensajes.lbl_info_welcome, duration=None, visible=True)
                    datos_perfil = {
                    'diplayName': displayName,
                    'email': email,
                    'tokens': 5,
                    'fecha_registro': firestore.SERVER_TIMESTAMP # Para un timestamp del servidor
                    }
                    fireWhale.creaDatoMultiple('usuarios', uid, datos_perfil) #Ésta es la creación del usuario en Firestore.
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
                    fireWhale.editaDato('usuarios', uid, 'cus', respuesta['customer_id'])
                    # print("cus agregado")
            else: #Si no existe en FIREBASE AUTH, es un usuario inválido. FutureImportante: ¿Debería regresarlo a login? 
                mensaje = "Usuario inválido."
                mensaje2 = "Recarga la página si no puedes ver tus créditos." #Future,¿éste mensaje puede ser un link a login más que un texto?
        except Exception as e:
            f"Excepción: {e}"
  
        return uid, gr.Accordion(label=mensaje, open=False), gr.Button(), gr.Accordion(label=mensaje2, open=False)  

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

def actualizador_navbar(usuario, result, info_window):
    
    # print("Ésto es usuario: ", usuario)
    # print("Ésto es result: ", result)
    # print("Ésto es info_window: ", info_window)
    
    #Controla si se abre el botón de recargar créditos.
    if "no-credits" in result:
        apertura = True
    else:
        apertura = False

    #Dependiendo del resultado obtenido deberé debitar o no:     
    #Cuando no hay imagen (Error directo de mass): error.png
    if "jpg" in result: #Cuando la imagen es correcta. El resultado es un archivo .jpg
        #Debita uno de la cuota de ese usuario y despliegalo.
        fireWhale.incrementar_campo_numerico('usuarios', usuario, 'tokens', amount=-globales.costo_work)
        tokens = fireWhale.obtenDato('usuarios', usuario, 'tokens') #A pesar de la maniobra para obtener y restar, para poder desplegarlo de todas formas necesitaremos hacer otra lectura de firebase.
        print(f"Después de debitar tienes {tokens} tokens.")
    else: 
        #Lo demás debería ser un error.
        print("Resultado incorrecto e incobrable...")
        #Future, también podrías no hacer la ida a firebase y obtenerlo de valor previo.
        tokens = fireWhale.obtenDato('usuarios', usuario, 'tokens') #obtienes
        print("Estos son los tokens que tiene actualmente el usuario:", tokens)
        #Por ahora no debites.
    return gr.Accordion(label=f"💶Creditos Disponibles: {tokens}", open=apertura)