import logging
from datetime import datetime

# Constantes
TG_LOG_LEVEL = logging.INFO
MM_LOG_LEVEL = logging.INFO
LOG_DIR = 'log/'
LOG_FILE = LOG_DIR + 'sB0T_' + datetime.now().strftime("%Y_%m_%d__%Hh%Mm")+'.log'
LOG_DB_FILE = LOG_DIR + 'db_Manager.log'

ADMIN_INVALID = ""
ADMIN_LABELED = ""

# Mensajes

START_MESSAGE = """Bienvenido/a al Bot Sentimental

El propósito de este bot es recopilar un conjunto de frases etiquetadas para entrenar una Inteligencia Artificial experta en sentimientos.

Se te irán mostrando frases aleatorias y debes indicar, pulsando en el botón correspondiente, si crees que la frase es positiva, negativa o neutra.

Intenta ser objetivo. Es decir, aunque no estés de acuerdo con la frase, intenta entender la intención de quien la escribiese.

Si crees que la frase no tiene sentido completo (por ejemplo muchos hashtags o un solo link) puedes pulsar el botón de Invalida

¡Pulsa en el botón de VOTAR para empezar a etiquetar frases!

Si necesitas ayuda con ejemplos, pulsa aquí -> /ejemplos

(Opciones de administrador restringidas)

¡Gracias por tu ayuda!"""

HELP_MESSAGE = """
EJEMPLOS DE FRASES ETIQUETADAS:

<b>Ejemplos Positiva:</b>
· @VaqueraSur Alegría amistad cariño y con esa imagen que más puedo pedir??Aah también paciencia.. un gracias por todo vaquerita 👌💞🍀🌄un excelente día para ti
· Tomarte un café con amigas y hablar es literalmente de las actividades más productivas que se me pueden ocurrir.

<b>Ejemplos Neutra:</b>
· Necesito que alguien me haga un cafecito por las mañanas
· Una nueva noche fría en el barrio

<b>Ejemplos Negativa:</b>
· Menudo nivel. Tú sí eres un atentado contra el humor y también  contra el respeto hacia tantas víctimas del País Vasco y del resto de España. Ni puñetera gracia.
· Me encanta que alguien como @Trecet me bloquee porque es la prueba de que algo estoy haciendo bien. Gente así sobra en el baloncesto español. #OtroBaloncestoEsNecesario

<b>Ejemplos Inválida:</b> 
· @Yaritza43389945 @Edinsonvh @2021Luchadora @Mozkovo2021 @KattyPSUV @MorenoCrezz @Maida11169691 @7chiz @20Venceremos @Rafito_Herrera @chikderoja @CarlosG86569847 @will6942 @alvarado_rudys @GHA80633107 @Ramn50633957 @Thais64101031 @arianamatoss51 @Mippcivzla #18Mar ETIQUETAS DEL DÍA! ▶️ 1️⃣ #DaleUnParaoALaCovid192️⃣ #HitoBicentenario3millones500mil
· @ElwndelG @Shadow3Lord2 @NuncaMas___ Claro xD

<b>NOTA PARA INVÁLIDAS:</b>
Una frase a votar con muchas menciones o hashtags puede contener otra frase que sí tenga sentimiento. Por ejemplo:

@apijimenez @canalfiesta @vanesamartin_ @manuelcarrasco_ @rosalia @bombaioficial @soyRayden @flaviofdzz @SebastianYatra @alfredgarcia @Nestior_Oficial @martaot2018 @pabloalboran @polgranch @CycloMusic Buenos días a mi querido @antonioaras 😘😘❤️ 

En este caso, la frase debería marcarse como Positiva, dado el extracto: "Buenos días a mi querido @antonioaras 😘😘❤️"

Sin embargo, en el segundo ejemplo de inválidas el extracto sería: "Claro xD", que no tiene sentimiento real, por lo que es correctamente marcada como inválida.

En caso de no tener claro si la frase es positiva, negativa o neutra no te comas la cabeza. ¡Márcala como inválida y yo me encargo!
"""


CHOSE_MESSAGE = "Elige una opción"

UNKNOWN_MESSAGE = "¡Vaya, que embarazoso! Solo entiendo los botones y el comando /start, lo siento"

NO_PERMISSION = "¡Lo siento! Opción restringida para el administrador"

NO_SENTENCES = """En este momento no hay frases disponibles para votar

Por favor, contacta con el administrador @alvarito_lml y escribe o pulsa en /start cuando haya más frases disponibles

¡Lo siento!"""

NO_INVALID_SENTENCES = """En este momento no hay frases invalidas disponibles para evaluar

Por favor, contacta con el administrador @alvarito_lml y escribe o pulsa en /start cuando haya más frases disponibles

¡Lo siento!"""

NO_LABELED_SENTENCES = """En este momento no hay frases etiquetadas disponibles para evaluar

Por favor, contacta con el administrador @alvarito_lml y escribe o pulsa en /start cuando haya más frases disponibles

¡Lo siento!"""

FILL_INSTRUCTIONS = "Escribe [n_frases]@[keyword] respetando la arroba"

FILL_COMMAND_ERROR = "No se introdujo el patrón correctamente.\n Ejemplo:\t20@coches\nsacará 20 frases que traten de 'coches'"

INFO_DB_MESSAGE = "INFORMACION DE LA BASE DE DATOS\n---------------------------------------------------------------\n"
INFO_DB_MESSAGE += "Unlabeled:\n\t· Elementos: {}\n\n"
INFO_DB_MESSAGE += "Invalid:\n\t· Elementos: {}\n\n"
INFO_DB_MESSAGE += "Labeled:\n\t· Elementos: {}\n\t· Positivas: {}%\n\t· Neutras: {}%\n\t· Negativas: {}%\n\n"
INFO_DB_MESSAGE += "Dataset:\n\t· Elementos: {}\n\t· Positivas: {}%\n\t· Neutras: {}%\n\t· Negativas: {}%"
