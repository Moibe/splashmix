import tools
import random
import bridges
import globales
import fireWhale
import sulkuFront
import gradio as gr
import gradio_client
import splashmix.prompter as prompter
import splashmix.splash_tools as splash_tools
import splashmix.configuracion as configuracion
mensajes, sulkuMessages = tools.get_mensajes(globales.mensajes_lang)
import time

btn_buy = gr.Button("Get Credits", visible=False, size='lg')

def perform(input1, gender, personaje, usuario):

    gender = gender or "superhero" #default es superhero.
    #Los tokens se checan dentro de perform para estar seguros de que cuenta con los tokens para ejecutar esa operación en particular.
    tokens = fireWhale.obtenDato('usuarios', usuario['uid'], 'tokens')
    
    #1: Reglas sobre autorización si se tiene el crédito suficiente.
    if tokens >= globales.costo_work: #Lo hará solo si tiene el crédito suficiente.
        try:
            #La API se elige ahora afuera de mass.
            api, tipo_api, usuario_proveedor = tools.eligeAPI(globales.seleccion_api) #Aquí ya elegiste al usuario proveedor pero no haz elegido su hf token.             
            resultado = mass(input1, gender, personaje, api, usuario_proveedor)
            #Importante: La cuota solo se debita aquí, después de hacer el client.predict.
            tools.reducirQuota(tipo_api, usuario_proveedor) #Si estamos en sistema de quotas. Aplica un IF.
        
        except Exception as e:           
            if "401" in str(e): #Inhabilitará el server si tiene un 401, para evitar el problema con otros usuarios.        
                fireWhale.inhabilitaUsuarioProveedor(usuario_proveedor)
            print("Excepción de mass...")    
            resultado, info_window  = sulkuFront.aError(excepcion = tools.titulizaExcepDeAPI(e))
            
            #SI EL ERROR ES UN RUNTIME_ERROR: 
            print("Llegada al IF de la segunda vuelta, donde e es: ", e)
            if "RUNTIME_ERROR" in str(e):
                print("Estoy dentro del IF del segundo intento...")                                 
                #Segundo intento
                try:
                    resultado = mass(input1, gender, personaje, globales.api_zero_backup, usuario_proveedor)
                    tools.reducirQuota(tipo_api, usuario_proveedor)
                except Exception as e:           
                    if "401" in str(e): #Inhabilitará el server si tiene un 401, para evitar el problema con otros usuarios.        
                        fireWhale.inhabilitaUsuarioProveedor(usuario_proveedor)
                    print("Excepción de mass...")    
                    resultado, info_window  = sulkuFront.aError(excepcion = tools.titulizaExcepDeAPI(e))
            
            else: #O sea si el error de la excepción no fue RUNTIME_ERROR (aun siendo error.)
                #print("No caí en el if del segundo intento, estoy en el else.")
                return resultado, info_window          
    else: #Aquí es si no fue error y ya salimos del try más externo, es el else de si tuviste suficientes tokens.
        #Si no hubo autorización.
        resultado, info_window = sulkuFront.noCredit()
        return resultado, info_window

    #AQUÍ LLEGARA CUANDO NO ES ERROR DE SISTEMA Y ES DE USUARIO (O LOGRO LA IMAGEN O PUSO UNA SIN ROSTRO DETECTABLE)
    resultado, info_window = sulkuFront.evaluaResultadoUsuario(resultado, personaje) #No fue frenado por falta de crédito o or imagen vacía, paso a la API (se debita)
    return resultado, info_window

def mass(input1, gender, hero, api, usuario_proveedor):

    print("Estoy dentro de mass y api es: ", api)
    #Aquí es donde se usará el server elegido.
    token_usuario = getattr(bridges, usuario_proveedor)
    client = gradio_client.Client(api, hf_token=token_usuario)
    
    #Adquisición Databank Particular para ese objeto y género....
    nombre_databank = gender
    datos = getattr(configuracion, nombre_databank)
    
    #Posición
    imagenSource = gradio_client.handle_file(input1)
    carpeta_positions = datos["positions_path"]  
    imagenPosition = gradio_client.handle_file(splash_tools.getPosition(carpeta_positions)) 

    #nombre_posicion = imagenPosition['path']    
    #Ésta parte es para obtener el nombre de la posición y guardarla en el log.
    #nombre_posicion = imagenPosition['path'].rsplit("\\", 1)[1] 

    prompt = prompter.fraseador(hero, gender)

    try:
        result = client.predict(
                imagenSource,
                imagenPosition,
                prompt=prompt,
                #negative_prompt="(lowres, low quality, worst quality:1.2), (text:1.2), watermark, (frame:1.2), deformed, ugly, deformed eyes, blur, out of focus, blurry, deformed cat, deformed, photo, anthropomorphic cat, monochrome, pet collar, gun, weapon, 3d, drones, drone, buildings in background",
                style_name="(No style)", #ver lista en styles.txt
                num_steps=30,
                identitynet_strength_ratio=0.8,
                adapter_strength_ratio=0.8,
                #pose_strength=0.4,
                canny_strength=0.4,
                depth_strength=0.4,
                controlnet_selection=["depth"], #pueden ser ['pose', 'canny', 'depth'] #Al parecer pose ya no.
                guidance_scale=5,
                seed=random.randint(0, 2147483647), 
                scheduler="EulerDiscreteScheduler",
                enable_LCM=False,
                enhance_face_region=True,
                api_name=globales.interface_api_name
        )

        #IMPORTANTE: cuando InstantID no detecta un rostro, no dice que eso fue el error. 
        #Así es que por ahora asumiré que la única forma en la que InstantID regresa error es porque no detecto un rostro...
        #Y de ahí partiré. 
            
        result = tools.desTuplaResultado(result)
        return result

    except Exception as e:
        print("Excepción de client.predict...")
        #La no detección de un rostro es mandado aquí?! Siempre? SI SIEMPRE, porque instantID es diferente y no reporta ese error integramente, pero aquí llega. 
        mensaje = tools.titulizaExcepDeAPI(e)        
        return mensaje