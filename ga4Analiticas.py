import json
import bridges
import globales
import requests


def send_ga4_signup_event():
    """
    Función para enviar un evento de SIGN-UP a GA4 usando Measurement Protocol.
    
    Args:
        
    """
    url = f"https://www.google-analytics.com/mp/collect?measurement_id={globales.ga4ID}&api_secret={bridges.ga4Key}"
    
    # moneda = session['currency'].upper()
    # imagenes = session['metadata']['imagenes']
    # print(f"Imágenes es: {imagenes} y es del tipo {type(imagenes)}...")
    # valor = session['amount_total'] / 100.0
    # print(f"Valor es {valor} y es del tipo {type(valor)}...")
    # cxm = int(valor) / int(imagenes)  #costo por imagen
    # print(f"cxm es {cxm} y su tipo es {type(cxm)}...")
    
    # id_imagenes = str(imagenes) + 'i'
    # id_valor = str(int(valor)) + moneda
    # id_cxm = str(cxm) + moneda
    
    # item_id = id_imagenes + id_valor
    # item_name = id_cxm
    
    # Prepara los items (productos) para GA4
    # items = []
    
    # Simulación de obtención de items
    # En un caso real, esto sería más complejo.
    # items.append({
    #     "item_id": item_id, #1000i-1900mxn
    #     "item_name": item_name, #1.8mxn
    #     "price": int(valor),
    #     "quantity": 1
    # })

    payload = {
        "client_id": session['metadata']['gaCliente'], # Aquí deberías usar el Client ID o User ID del usuario
        "events": [
            {
                "name": "user_signup",
                "params": {
                    "debug_mode": True,
                    "method": "email"
                }
            }
        ]
    }

    try:
        response = requests.post(url, data=json.dumps(payload), headers={"Content-Type": "application/json"})
        response.raise_for_status() # Lanza una excepción si la respuesta no es 2xx
        print("Evento de compra enviado a GA4 con éxito.")
        return True
    except requests.exceptions.RequestException as e:
        print(f"Error al enviar el evento a GA4: {e}")
        return False