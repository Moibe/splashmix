js = f"""
function funcion() {{
    console.log("Ésto es un console log normal desde fuego . js @ PRECARGA")        
    usuario_firebase = localStorage.getItem('uid');
    console.log("Éste es el usuario que obtuvo fuego: ", usuario_firebase)
    
    // Verificar si resultado está vacío
    if (!usuario_firebase || usuario_firebase === "" || usuario_firebase === "null" || usuario_firebase === "undefined") {{
    console.log("Resultado está vacío o es null/undefined, redireccionando...");
    return null;
    }} else {{
    console.log("Resultado no está vacío, si hay user de firebase, no se redirecciona a login.");
    }}
    console.log("En resultado que se está enviando es:", window.gaClientID)
    console.log(usuario_firebase)
    arreglo = [usuario_firebase, window.gaClientID]
    console.log("El arreglo que se está enviando es:" )
    console.log(arreglo)   
    return arreglo     
    }}
"""