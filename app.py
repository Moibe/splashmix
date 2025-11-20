import tools
import inputs
import ambiente
import globales
import funciones
import sulkuFront
import gradio as gr
import firehead, fire, fuego
import fireWhale

def iniciar():    
    app_path = globales.app_path
    main.queue(max_size=globales.max_size)
    main.launch(root_path=app_path, server_port=ambiente.server_port)

#Credit Related Elements
html_credits = gr.HTML(visible=globales.credits_visibility)
lbl_console = gr.Label(label="AI Terminal " + globales.version +  " messages", value="Hola", container=True)

#Customizable Inputs and Outputs
input1, gender, personaje, result = inputs.inputs_selector(globales.seto)
boton_comprar = gr.Button("Comprar Créditos ⚡", variant="primary", visible=False)    

#Otros Controles y Personalizaciones
nombre_posicion = gr.Label(label="Posición", visible=globales.posicion_marker)

enviar_btn=gr.Button("Enviar", variant="primary"),
despejar_btn=gr.Button("Borrar", variant="secondary")
script_logout, script_buy = tools.defineBotones(globales.firebase_auth)


def welcome(): 
    pass
    #botones = ['huggingface', 'primary', 'secondary', 'stop']
    #return gr.Button(value="Cerrar Sesión", size='md', variant=random.choice(botones))

def marca_click_compra(): 
    fireWhale.agregaMovimiento('usuarios', 'uid123', 'visito página compras')

#fire provee las partes de javascript que se requieren para correr el chequeo de firebase.
with gr.Blocks(theme=globales.tema, title="Splashmix App", head=firehead.head, js=fire.js, css="footer {visibility: hidden}") as main:
    
    arreglo = gr.JSON(visible=False) #Espacio para almacenar el usuario de firebase 
    usuario_firebase = gr.Text(visible=False)
    
    acheteemeele = gr.HTML("""
<!-- Google Tag Manager (noscript) -->
<noscript><iframe src="https://www.googletagmanager.com/ns.html?id=GTM-585LHZXF"
height="0" width="0" style="display:none;visibility:hidden"></iframe></noscript>
<!-- End Google Tag Manager (noscript) -->
                           """, visible=False)

    with gr.Row(variant='compact', show_progress=False):
        with gr.Column():
            acordeon = gr.Accordion(label = "Splashmix IA", open=False)
            with acordeon:   
             btn_logout = gr.Button(value="Cerrar Sesión 👋🏻", size='lg', variant='primary')
        with gr.Column():
            acordeon2 = gr.Accordion(label = "Por favor refresca la página (F5)...", open=False)
            with acordeon2: 
                compra = gr.Button(value="Recargar Créditos ⚡", size='lg', variant='primary')
 
    with gr.Row():
        demo = gr.Interface(
            fn=funciones.perform,
            inputs=[input1, gender, personaje, usuario_firebase], 
            outputs=[result, lbl_console, boton_comprar], 
            flagging_mode=globales.flag,
            js=fuego.js,        
            )        
    
    result.change(sulkuFront.actualizador_navbar, [usuario_firebase, result, lbl_console], acordeon2)

    btn_logout.click(
            fn=welcome,  # Una función Python, aunque no haga nada relevante para la redirección
            inputs=[],
            outputs=[],
            js=script_logout
            )
    compra.click(
            fn=marca_click_compra,  #Ahora la función anotará el movimiendo, revisar si lo hace antes de la redirección.
            inputs=[usuario_firebase],
            outputs=[],
            js=script_buy #Quizá aquí en el futuro necesite un reload con params.
            )
    main.load(sulkuFront.precarga, arreglo, [usuario_firebase, acordeon, btn_logout, acordeon2], js=fuego.js)
iniciar()