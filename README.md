# BotBuscameCasa
Bot en python / jupyter notebook para encontrar casa

Instalar anaconda (Windows o Linux):
	https://docs.anaconda.com/anaconda/install/windows/
	https://docs.anaconda.com/anaconda/install/linux/
	
Instalar Chrome driver y colocarlo en una ubicación conocida o en el Path de Windows:
https://chromedriver.chromium.org/downloads

Luego poner la ubicación del "chromedriver.exe" en la variable WEB_DRIVER_LOCATION
con el formato: 'C:/Users/user/Downloads/chromedriver_win32/'

Abrir una consola de anaconda en Windows (o setear el entorno virtual conda en linux)
y hacer: pip install -r requirements.txt

Abrir el jupyter notebook BotBuscameCasa.ipynb, y sustituir WEB_DRIVER_LOCATION
En la lista listUrls añadir los urls de los barrios o pueblos principales de la pagina de
idealista que se quiere extraer, mirar ejemplo.
A continuacion ir ejecutando cada celda hasta llegar a Main Bot Script, ahi empieza el Bot a funcionar,
tarda muchos minutos ya que el script es amable con el servidor y asi no nos bloquea
idealista.