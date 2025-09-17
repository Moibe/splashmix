import json
import tools
import bridges
import globales
import requests


def send_ga4_signup_event(gaCliente):
    """
    Función para enviar un evento de SIGN-UP a GA4 usando Measurement Protocol.
    
    Args:
        
    """

    print("Estoy en send sign up y gaCliente es: ", gaCliente)

    gclid_exacto = tools.obtener_gclid_exacto(gaCliente)
    url = f"https://www.google-analytics.com/mp/collect?measurement_id={globales.ga4ID}&api_secret={bridges.ga4Key}"
    
    payload = {
        "client_id": gclid_exacto, # Aquí deberías usar el Client ID o User ID del usuario
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
        print("Evento de sign up enviado a GA4 con éxito.")
        return True
    except requests.exceptions.RequestException as e:
        print(f"Error al enviar el evento a GA4: {e}")
        return False