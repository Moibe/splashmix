import ambiente
import gradio as gr

#Ambiente.py
app_path = ambiente.app_path
server_port=ambiente.server_port
version = ambiente.version
firebase_auth = ambiente.firebase_auth 

nombre_diccionario = "datos_superheroe"

#Aquí se elije el tipo de selección, no la api en si.
seleccion_api = "eligeQuotaOCosto" #eligeQuotaOCosto , eligeAOB o eligeGratisOCosto
max_size = 20

#Quota o Costo
api_zero = ("Moibe/InstantID2", "quota") #Indíca la url del api y su tipo.
api_cost = ("Moibe/InstantID2-Turbo", "costo")

api_zero_backup = "InstantX/InstantID"

interface_api_name = "/generate_image" #El endpoint al que llamará client.

seto = "splashmix"
#work = "picswap" #Se usaba para definir el tipo de trabajo para diferentes cobros.

process_cost = 12 #Los segundos que cuesta el procesamiento.
process_margin = 60 #Aunque solo requiere 12, arranca con 60 disponibles si no, no funciona (comprobar)
costo_work = 1 #Esto es el costo en créditos para el usuario. 

tema = gr.themes.Base()
flag = "never"

neural_wait = 4
mensajes_lang = "es"

credits_visibility = False

posicion_marker = False

proveedores = ['irina', 'moibe', 'servidoria', 'desarrolloia', 'sun', 'sosa', 'buzzword']