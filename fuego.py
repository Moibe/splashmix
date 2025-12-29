js = f"""
function funcion() {{
    console.log("Ésto es un console log normal desde fuego . js @ PRECARGA")        
    usuario_firebase = localStorage.getItem('uid');
    country_ip = localStorage.getItem('country_ip');
    country_geolocation = localStorage.getItem('country_geolocation');
    country_header = localStorage.getItem('country_header');
    traffic_source = localStorage.getItem('traffic_source');
    
    // Extrae el vid de window.gaGlobal
    ga_vid = '';
    if (window.gaGlobal && window.gaGlobal.vid) {{
        ga_vid = window.gaGlobal.vid;
    }}
    
    // Extrae los parámetros de Google Ads (gclid y adgroupid)
    ads_gclid = '';
    ads_adgroupid = '';
    if (window.marketing_gclid) {{
        ads_gclid = window.marketing_gclid;
    }}
    if (window.marketing_adgroupid) {{
        ads_adgroupid = window.marketing_adgroupid;
    }}
    
    console.log("Éste es el usuario que obtuvo fuego: ", usuario_firebase)
    console.log("Éste es el country_ip que obtuvo fuego: ", country_ip)
    console.log("Éste es el GA vid que obtuvo fuego: ", ga_vid)
    console.log("Éste es el ads_gclid que obtuvo fuego: ", ads_gclid)
    console.log("Éste es el ads_adgroupid que obtuvo fuego: ", ads_adgroupid)
    
    // Verificar si resultado está vacío
    if (!usuario_firebase || usuario_firebase === "" || usuario_firebase === "null" || usuario_firebase === "undefined") {{
    console.log("Resultado está vacío o es null/undefined, redireccionando...");
    arreglo = {{gaClient: ga_vid, uid: null, country_ip: country_ip, ads_gclid: ads_gclid, ads_adgroupid: ads_adgroupid}}
    return arreglo;
    }} else {{
    console.log("Resultado no está vacío, si hay user de firebase, no se redirecciona a login.");
    }}
    console.log("En resultado que se está enviando es:", ga_vid)
    console.log(usuario_firebase)
    arreglo = {{gaClient: ga_vid, uid: usuario_firebase, country_ip: country_ip, country_geolocation: country_geolocation, country_header: country_header, traffic_source: traffic_source, ads_gclid: ads_gclid, ads_adgroupid: ads_adgroupid}}
    console.log("El arreglo que se está enviando es:" )
    console.log(arreglo)   
    return arreglo     
    }}
"""