js = f"""
function funcion() {{
    console.log("Ésto es un console log normal desde fuego . js @ PRECARGA")        
    usuario_firebase = localStorage.getItem('uid');
    country_ip = localStorage.getItem('country_ip');
    country_geolocation = localStorage.getItem('country_geolocation');
    country_header = localStorage.getItem('country_header');
    traffic_source = localStorage.getItem('traffic_source');
    console.log("Éste es el usuario que obtuvo fuego: ", usuario_firebase)
    console.log("Éste es el country_ip que obtuvo fuego: ", country_ip)
    
    // Verificar si resultado está vacío
    if (!usuario_firebase || usuario_firebase === "" || usuario_firebase === "null" || usuario_firebase === "undefined") {{
    console.log("Resultado está vacío o es null/undefined, redireccionando...");
    arreglo = {{gaClient: window.gaClientID, uid: null, country_ip: country_ip}}
    return arreglo;
    }} else {{
    console.log("Resultado no está vacío, si hay user de firebase, no se redirecciona a login.");
    }}
    console.log("En resultado que se está enviando es:", window.gaClientID)
    console.log(usuario_firebase)
    arreglo = {{gaClient: window.gaClientID, uid: usuario_firebase, country_ip: country_ip, country_geolocation: country_geolocation, country_header: country_header, traffic_source: traffic_source}}
    console.log("El arreglo que se está enviando es:" )
    console.log(arreglo)   
    return arreglo     
    }}
"""