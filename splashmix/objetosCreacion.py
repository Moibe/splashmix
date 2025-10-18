import random
import importlib
import splashmix.splash_tools as splash_tools
import splashmix.configuracion as configuracion
#import splashmix.static_databanks as static_databanks

#DATA GENERAL: 
folder_data = "data."
importable_general = folder_data + configuracion.general_databank 
databank_general = importlib.import_module(importable_general)

#DATA PARTICULAR (HG o SH):
def inicializador(archivo_databank):
    #Regresa el módulo que contiene el databank correspondiente al Objeto (Superhero o Superheroine seleccionado.)
    importable_particular = "data." + archivo_databank
    databank_particular = importlib.import_module(importable_particular)
    return databank_particular

class Prompt:
    
    def __init__(self, style=None):  #Ése style=None al parecer no se usa pq todo viene de la creación de un hijo.            
        #Aquí pondrás cada atributo que contenga ese objeto general:
        try: 
            self.style = style or random.choice(databank_general.lista_estilos) 
        except Exception as e: 
            print("Excepción: ", e)
class Superhero(Prompt):
    def __init__(self,
                 archivo_databank,
                 subject=None, 
                 ):
        super().__init__()  # Call the parent class constructor                          
        databank_particular = inicializador(archivo_databank)       
        self.subject = subject or splash_tools.randomNull(0.2, databank_particular.lista_subjects)

class Superheroine(Prompt):
    def __init__(self,
                 archivo_databank,
                 subject=None, 
                 ):
        super().__init__()  # Call the parent class constructor
        databank_particular = inicializador(archivo_databank)
        self.subject = subject or splash_tools.randomNull(0.2, databank_particular.lista_subjects)
                        
class Hotgirl(Prompt):
    def __init__(self,
                 archivo_databank,
                 #Aquí pondrás cada atributo que contenga ese objeto general:
                 style=None,
                 subject=None,
                 adjective=None,
                 type_girl=None,
                 hair_style=None,
                 boobs=None,
                 wardrobe_top=None,
                 wardrobe_accesories=None,
                 wardrobe_bottom=None,
                 wardrobe_shoes=None,
                 situacion=None,
                 place=None,
                 complemento=None,
                 ):
       
        super().__init__(style)  # Call the parent class constructor

        databank_particular = inicializador(archivo_databank)
        self.subject = subject or splash_tools.randomNull(0.2, databank_particular.lista_subjects)
        self.adjective = adjective or splash_tools.randomNull(0.2, databank_particular.lista_adjective)
        self.type_girl = type_girl or splash_tools.randomNull(0.2, databank_particular.lista_type_girl)
        self.hair_style = hair_style or splash_tools.randomNull(0.2, databank_particular.lista_hair_style)
        self.boobs = boobs or splash_tools.randomNull(0.2, databank_particular.lista_boobs)
        self.wardrobe_top = wardrobe_top or splash_tools.randomNull(0.2, databank_particular.lista_wardrobe_top)
        self.wardrobe_accesories = wardrobe_accesories or splash_tools.randomNull(0.2, databank_particular.lista_wardrobe_accesories)
        self.wardrobe_bottom = wardrobe_bottom or splash_tools.randomNull(0.2, databank_particular.lista_wardrobe_bottom)
        self.wardrobe_shoes = wardrobe_shoes or splash_tools.randomNull(0.2, databank_particular.lista_wardrobe_shoes)
        self.situacion = situacion or splash_tools.randomNull(0.2, databank_particular.lista_situacion)
        self.place = place or splash_tools.randomNull(0.2, databank_particular.lista_place)
        self.complemento = complemento or splash_tools.randomNull(0.2, databank_particular.lista_complemento)                  