import json
import tools
import bridges
import requests
import ambiente
import time 



def send_ga4_signup_event(gaCliente):
    """
    Función para enviar un evento de SIGN-UP a GA4 usando Measurement Protocol.
    
    Args: _ga
        
    """

    gclid_exacto = tools.obtener_gclid_exacto(gaCliente)
    # print("Glid exacto: ", gclid_exacto)
    # print(f"Ambiente: {ambiente.ga4ID}, ga4Key: {bridges.ga4Key}")
    url = f"https://www.google-analytics.com/mp/collect?measurement_id={ambiente.ga4ID}&api_secret={bridges.ga4Key}"
    # print("Url total: ", url)
    
    payload = {
        "client_id": gclid_exacto, # Aquí deberías usar el Client ID o User ID del usuario
        "events": [
            {
                "name": "user_signup",
                "params": {
                    #"debug_mode": True,
                    "method": "Google"
                }
            }
        ]
    }

    try:
        response = requests.post(url, data=json.dumps(payload), headers={"Content-Type": "application/json"})
        response.raise_for_status() # Lanza una excepción si la respuesta no es 2xx
        print("Evento de sign up enviado a GA4 con éxito.")
        return True
    except requests.exceptions.RequestException as e:
        print(f"Error al enviar el evento a GA4: {e}")
        return False