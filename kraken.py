import json # Used for pretty-printing the JSON response
import requests
import ambiente

def crear_cliente_stripe(email: str, firebase_user: str = None, site: str = None) -> dict:
    """
    Consumes the API Kraken to create a Stripe client.
    Correctly sends data as 'application/x-www-form-urlencoded' as per API spec.

    Args:
        email (str): The client's email address (required).
        firebase_user (str, optional): The Firebase user ID. Defaults to None.
        site (str, optional): The website associated with the client. Defaults to None.

    Returns:
        dict: The JSON response from the API if the request was successful,
              or a dictionary with error information if it failed.
    """
    api_url = f"https://moibe-stripe-kraken-{ambiente.firebase_auth}.hf.space/creaCliente/" # Asegúrate de que tenga la barra final si es necesario, la especificación la muestra.

    # Prepara los datos a enviar en el cuerpo de la petición.
    # Solo incluimos los campos si tienen un valor (no son None o cadena vacía).
    # Estos datos serán enviados como 'application/x-www-form-urlencoded'
    payload = {
        "email": email
    }
    if firebase_user:
        payload["firebase_user"] = firebase_user
    if site:
        payload["site"] = site

    # NOTA: Ya no es necesario especificar "Content-Type" explícitamente en los headers
    # cuando usas el parámetro 'data', requests lo hace automáticamente.
    # Si lo dejas, requests podría sobrescribirlo o causar un comportamiento inesperado.
    # headers = {
    #     "Content-Type": "application/x-www-form-urlencoded" # Esto es lo que requests pondría automáticamente
    # }

    try:
        # Realiza la petición POST a la API, usando 'data=payload'
        #print(f"Attempting to send data to API as x-www-form-urlencoded: {payload}")
        response = requests.post(api_url, data=payload) # <--- ¡Cambiado de 'json=data' a 'data=payload'!

        # Raise an HTTPError for bad responses (4xx or 5xx status codes).
        response.raise_for_status()

        # Parse and return the JSON response from the API.
        print("API call successful!")
        return response.json()

    except requests.exceptions.HTTPError as e:
        #print(f"HTTP Error: {e}")
        error_details = {"error": "HTTP Error", "status_code": e.response.status_code if e.response else "N/A"}
        if e.response and e.response.text:
            try:
                error_details["response_json"] = e.response.json()
            except json.JSONDecodeError:
                error_details["response_text"] = e.response.text
        return error_details
    except requests.exceptions.ConnectionError as e:
        print(f"Connection Error: {e}")
        return {"error": "Connection Error", "details": str(e)}
    except requests.exceptions.Timeout as e:
        print(f"Timeout Error: {e}")
        return {"error": "Timeout Error", "details": str(e)}
    except requests.exceptions.RequestException as e:
        print(f"An unexpected Request Error occurred: {e}")
        return {"error": "Unknown Request Error", "details": str(e)}
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return {"error": "Unexpected Error", "details": str(e)}