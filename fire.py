import fireconfig

js = f"""
function normal(a) {{

    console.log("Entré a fire.js @ BLOCKS y esto es a: ", a)
    resultado = localStorage.getItem('uid');
    console.log("1Éste es el usuario que obtuvo fuego cuando hay user auth desde afuera de fire: ", resultado);

    // Lógica para el manejo de recargas
    const urlParams = new URLSearchParams(window.location.search);
    const reloadKey = 'has_reloaded';

    // Prioriza el parámetro de URL sobre el localStorage
    if (urlParams.get('reload') === 'true') {{
        console.log("Parámetro 'reload=true' encontrado. Recargando la página en 0.5 segundos...");
        
        // 1. Elimina el parámetro 'reload' para prevenir un bucle infinito
        urlParams.delete('reload');
        
        // 2. Construye la URL sin el parámetro
        let newUrl;
        if (urlParams.toString()) {{
            newUrl = `${{window.location.pathname}}?${{urlParams.toString()}}${{window.location.hash}}`;
        }} else {{
            newUrl = `${{window.location.pathname}}${{window.location.hash}}`;
        }}
        
        // 3. Modifica la URL en la barra de direcciones sin recargar
        history.pushState(null, '', newUrl);
        
        // 4. Recarga la página con un retraso corto
        setTimeout(() => {{
            window.location.reload();
        }}, 500); 
        
    }} else if (!localStorage.getItem(reloadKey)) {{
        // Si no hay un parámetro 'reload' en la URL y es la primera visita...
        console.log("Primera visita a la página. Recargando en 0.5 segundos...");
        
        // Establece la clave en localStorage para evitar recargas futuras
        localStorage.setItem(reloadKey, 'true');
        
        // Recarga la página con un breve retraso
        setTimeout(() => {{
            window.location.reload();
        }}, 500); 
    }} else {{
        // Si la página ya se recargó y no hay parámetro, se limpia el localStorage para la próxima visita directa
        localStorage.removeItem(reloadKey);
    }}
    
    // El resto de tu código
    {fireconfig.firebase_config}
    firebase.initializeApp(firebaseConfig);
    const provider = new firebase.auth.GoogleAuthProvider();
    
    firebase.auth().onAuthStateChanged((user) => {{
        if (user) {{
        console.log("Hay usuario...", user)
            localStorage.setItem('estadoUsuario', 'Conectado');
            localStorage.setItem('uid', user.uid);
            localStorage.setItem('email', user.email);
            localStorage.setItem('name', user.displayName); 
            localStorage.setItem('photo', user.photoURL);
            resultado = localStorage.getItem('uid');
            console.log("Éste es el usuario que obtuvo fuego cuando hay user auth: ", resultado)  
        }} else {{
        console.log("No hay usuario...") 
        resultado = localStorage.getItem('uid');
        console.log("Éste es el usuario que obtuvo fuego cuando no hay usuario auth: ", resultado)      
            //Si el usuario se sale o no está. Importante: Revisar por que tengo comentado ésto.
            //localStorage.setItem('estadoUsuario', 'Desconectado');
            //localStorage.setItem('usuario', ""); 
        }}
    }})

    console.log("Estoy por retornar resultado...")
    return resultado

}}  

"""