head = """
<script src="https://www.gstatic.com/firebasejs/10.7.0/firebase-app-compat.js"></script>
    <script src="https://www.gstatic.com/firebasejs/10.7.0/firebase-auth-compat.js"></script>
    <script src="https://www.gstatic.com/firebasejs/10.7.0/firebase-firestore-compat.js"></script>  
    <script>
    console.log("Hola estoy en HEAD.js de firehead.py @ BLOCKS")  
    </script>
    <!-- Google Tag Manager -->
<script>
(function(w,d,s,l,i){w[l]=w[l]||[];w[l].push({'gtm.start':
new Date().getTime(),event:'gtm.js'});var f=d.getElementsByTagName(s)[0],
j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;j.src=
'https://www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);
})(window,document,'script','dataLayer','GTM-585LHZXF');


window.dataLayer.push = (function(originalPush) {
      return function() {
        for (var i = 0; i < arguments.length; i++) {
          var event = arguments[i];
          if (event.event === 'clientIDLoaded' && event.gaClientID) {
            // Guarda el Client ID en una variable global
            window.gaClientID = extraeClienteID(event.gaClientID);
            console.log('Client ID guardado en la variable global:', window.gaClientID);
          }
        }
        return originalPush.apply(this, arguments);
      };
    })(window.dataLayer.push);

    for (var i = 0; i < window.dataLayer.length; i++) {
      var event = window.dataLayer[i];
      if (event && event.event === 'clientIDLoaded' && event.gaClientID) {        
        window.gaClientID = extraeClienteID(event.gaClientID);
        console.log('Client ID encontrado en dataLayer:', window.gaClientID);
        break;
      }
    }

</script>
<!-- End Google Tag Manager --> 
<script>document.documentElement.setAttribute('translate', 'no');</script>    
"""