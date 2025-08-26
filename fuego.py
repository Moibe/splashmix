js = f"""
function funcion() {{
    console.log("Ésto es un console log normal desde fuego . js @ PRECARGA")        
    resultado = localStorage.getItem('uid');
    //console.log("Éste es el usuario que obtuvo fuego: ", resultado)
    
    // Verificar si resultado está vacío
    if (!resultado || resultado === "" || resultado === "null" || resultado === "undefined") {{
    console.log("Resultado está vacío o es null/undefined, redireccionando...");
    return null;
    }} else {{
    console.log("Resultado no está vacío, si hay user de firebase, no se redirecciona a login.");
    }}

    return resultado       
    }}

"""
