from selenium import webdriver
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import time
import logging
import json
import os
import smtplib, ssl
import email
from email.message import Message
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


class ConfigData:
    WEB_DRIVER_FILE_LOCATION = ''
    NEXT_PAGE_DELAY = 0
    NEXT_ZONE_DELAY = 0
    listUrls = []
    Version = ""
    recipients = []
    emailFrom = ""
    sec = ""
    
    def __init__(self):
        self.GetConfigData()

    def GetConfigData(self):
        if os.path.isfile( "config.json" ):
            with open('config.json') as json_file:
                data = json.load(json_file)
            self.WEB_DRIVER_FILE_LOCATION = data['ChromeDriverLocation'] + 'chromedriver.exe'
            self.Version = data["Version"]
            self.listUrls = data['Targets']
            self.NEXT_PAGE_DELAY = int( data["NEXT_PAGE_DELAY"] )
            self.NEXT_ZONE_DELAY = int( data["NEXT_ZONE_DELAY"] )
            self.recipients = data['Recipients']
            self.emailFrom = data['Sender']
            self.sec = data['Secret']
        else:   #default
            self.NEXT_PAGE_DELAY = 20
            self.NEXT_ZONE_DELAY = 120
            self.WEB_DRIVER_FILE_LOCATION = 'C:/Users/myuser/path/to/chromedriver.exe'
            self.listUrls = ["https://www.idealista.com/venta-viviendas/madrid/hortaleza/apostol-santiago/",
                        "https://www.idealista.com/venta-viviendas/madrid/hortaleza/pinar-del-rey/"]
            self.recipients = []
            sef.emailFrom = "example3@example.com"
            self.sec = "xxx"

class DbPage:
    idList = []
    platformList = []
    titleList =  []
    priceList =  []
    parkingList = []
    habList = []
    nbanosList = []
    supList = []
    plantaList = []
    telefoneList =  []
    listHrefs = []
    listBarrio = []
    listZona = []
    listYear = []
    listMonth = []
    listDay = []
    listActive = []
    listYearInac = []
    listMonthInac = []
    listDayInac = []
    listCaract = []
    listComent = []
    
    
    def __init__(self):
        self.reset()
    
    def reset(self):
        self.idList = []
        self.platformList = []
        self.titleList =  []
        self.priceList =  []
        self.parkingList = []
        self.habList = []
        self.nbanosList = []
        self.supList = []
        self.plantaList = []
        self.telefoneList =  []
        self.listHrefs = []
        self.listBarrio = []
        self.listZona = []
        self.listYear = []
        self.listMonth = []
        self.listDay = []
        self.listActive = []
        self.listYearInac = []
        self.listMonthInac = []
        self.listDayInac = []
        self.listCaract = []
        self.listComent = []

def getDf():
    df = pd.DataFrame(columns=['IdPlat','Plat','Titulo','Precio','Hab','N_Banos','Sup','Planta','Garaje','Telefono','Url','Barrio','Zona','Year','Month', 'Day', 'Active', 'YearInact','MonthInact', 'DayInact', 'Caract', 'Comentario'])
    df = df.astype({"IdPlat": int})
    return df

class DfDbContainer:
    df_Db_in = getDf()
    df_today = getDf()
    df_Db_out = getDf()
    df_new = getDf()
    df_Inactive = getDf()
    df_InactConf = getDf()
    
    def __init__(self):
        self.reset()
    
    def reset(self):
        self.df_Db_in = getDf()
        self.df_today = getDf()
        self.df_Db_out = getDf()
        self.df_new = getDf()
        self.df_Inactive = getDf()
        self.df_InactConf = getDf()
        
def setTitlePriceTelef(page, soup):
    page.titleList = soup.select("div.item-info-container > a.item-link")
    page.priceList = soup.select("div.item-info-container > div.price-row > span.item-price")
    
    for elem in soup.select("div.item-info-container > div.item-toolbar"):
        try:
            page.telefoneList.append( elem.select("span.icon-phone")[0].get_text() ) 
        except IndexError as error:
            page.telefoneList.append( "NA" )

def setIdealista(page, soup): #Encontrar id Idealista del piso
    date =  datetime.now()
    for elem in soup.select("div.item-info-container > a.item-link"):
        page.idList.append( int(elem["href"].split("/")[2]) )
        page.platformList.append("idealista")
        page.listYear.append( date.year )
        page.listMonth.append( date.month )
        page.listDay.append( date.day )
        
def setHabSupPl(page, soup):  #Encontrar Habitaciones, superficie y planta
    isHab = lambda a : True if "hab" in a else False
    isSup = lambda a : True if "m²" in a else False
    isPlanta = lambda a : True if ("planta".lower() in a.lower() or "Bajo".lower() in a.lower() or "exterior".lower() in a.lower() ) else False
    set_bit = lambda value, bit : value | (1<<bit)  #zero index

    for elem in soup.select("div.item-info-container"):
        auxStr = ""
        bitmap = 0  # hab,sup,planta as bits 000, 101, etc
        for subelem in elem.select("span.item-detail"):
            auxStr = subelem.get_text()
            if isHab(auxStr):
                page.habList.append( auxStr )
                bitmap = set_bit(bitmap, 2)
            if isSup(auxStr):
                page.supList.append( auxStr )
                bitmap = set_bit(bitmap, 1)
            if isPlanta(auxStr):
                page.plantaList.append( auxStr )
                bitmap = set_bit(bitmap, 0)
        if (bitmap & 0x1) == False:
            page.plantaList.append( "NA" )
        elif (bitmap & 0x2)>>1 == False:
            page.supList.append( "NA" )
        elif (bitmap & 0x4)>>2 == False:
            page.habList.append( "NA" )

def setParking(page, soup):  # Encontrar datos Garaje
    for elem in soup.select("div.item-info-container > div.price-row"):
        auxStr = ""
        parkingElem = elem.select("span.item-parking")
        if( not parkingElem):
            auxStr += "No Garaje "
        else:
            auxStr += parkingElem[0].get_text()
        page.parkingList.append( auxStr )

def setUrl(page, soup):  #Encontrar URL
    for elem in soup.select("div.item-info-container > a.item-link"):
        page.listHrefs.append( "https://www.idealista.com" + elem['href'] )
        
def insertPageInDf(page, df):
    for i in range(0,len(page.titleList)-1):
        row = [page.idList[i],
               page.platformList[i],
               page.titleList[i].get_text(),
               page.priceList[i].get_text(),
               page.habList[i],
               'NA',
               page.supList[i],
               page.plantaList[i],
               page.parkingList[i],
               page.telefoneList[i],
               page.listHrefs[i],
               page.listBarrio[i],
               page.listZona[i],
               page.listYear[i],
               page.listMonth[i],
               page.listDay[i],
               'Yes',
               'NA',
               'NA',
               'NA',
               'NA',
               'NA'
               ]
        if (df.IdPlat == int(page.idList[i])).any() :  #Evaluar tambien en caso de que si el precio es distinto, actualizar
            continue
        df.loc[len(df)] = row

def getNextPageUrl(soup, mainUrl): #compute next page URL
    out = ""
    try:
        out = mainUrl + soup.select("div.pagination > ul > li.next > a")[0]["href"]
    except IndexError as error:
        printAndLog("Last page in entry")
        out = "Last page in entry"
    return out

def setBarrioZona(Barrio, url, soup, page):
    Zona = url.split('/')[-2]
    for elem in soup.select("div.item-info-container > a.item-link"):
        page.listBarrio.append( Barrio )
        page.listZona.append( url.split('/')[-2].capitalize() )

def OpenBrowserAndFetchData(url, config):
    #Open webpage with selenium webdriver, extract page source, and close webdriver in order to avoid scaring target website 
    #with the multiple repeated requests that webdrive does.
    options = webdriver.ChromeOptions()
    options.page_load_strategy = 'eager'
    options.add_argument("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36")
    driver = webdriver.Chrome(r"{}".format(config.WEB_DRIVER_FILE_LOCATION), options=options)
    driver.get(url)
    content = driver.page_source
    driver.quit()

    #Get Beautiful Soup Html object to work with
    soup = BeautifulSoup(content, 'html.parser')    
    return soup




def WorkZona(df, listUrls_entry, mainUrl, config):
    maxLoopCounts = 20
    counter = 0

    url = listUrls_entry
    Barrio = listUrls_entry.split('/')[-3].replace('-', ' ').title()
    
    while url != 'Last page in entry':
        if counter >= maxLoopCounts:
            break

        page = DbPage()

        printAndLog("Working.. url: " + url + ", counter: " + str(counter))
        soup = OpenBrowserAndFetchData(url, config)

        setTitlePriceTelef(page, soup)
        setIdealista(page, soup)
        printAndLog(page.idList)
        setHabSupPl(page, soup)
        setParking(page, soup)
        setUrl(page, soup)
        setBarrioZona(Barrio, url, soup, page)
        insertPageInDf(page, df)

        print(df[['IdPlat', 'Titulo']])
        url = getNextPageUrl(soup, mainUrl)
        
        printAndLog("Next Url: " + url)
        if url == 'Last page in entry':
            break
        time.sleep( config.NEXT_PAGE_DELAY ) # NEXT_PAGE_DELAY seconds delay after request
        counter += 1
        
def BuildOutputDb(df_Db_in, df_today):
    df_Db_out = pd.concat([df_Db_in,df_today]).drop_duplicates(subset = ['IdPlat'], keep='first')
    df_Db_out = df_Db_out.reset_index(drop=True)
    printAndLog(df_Db_out)
    return df_Db_out

#-------------------------------------------------------------------
#Spetial functions to find new and inactive entrys

def FindNewDf(df_Db_in, df_today):
    return df_today[df_today.IdPlat.isin(df_Db_in.IdPlat)==False]

def FindInactiveDf(df_Db_in, df_today):
    df_Inactive = df_Db_in[df_Db_in.IdPlat.isin(df_today.IdPlat)==False]
    inactiveFromDb = df_Db_in[ df_Db_in['Active'] == 'No' ]
    return df_Inactive[df_Inactive.IdPlat.isin(inactiveFromDb.IdPlat)==False]

def MarkInactiveDf(df_InactConf, df_Db_out):
    index = df_Db_out[df_Db_out['IdPlat'].isin(df_InactConf.IdPlat)].index
    date =  datetime.now()
    
    for elem in index:
        InsertInCell(df_Db_out, elem, 'Active', "No")
        InsertInCell(df_Db_out, elem, 'YearInact', date.year)
        InsertInCell(df_Db_out, elem, 'MonthInact', date.month)
        InsertInCell(df_Db_out, elem, 'DayInact', date.day)
    df_InactConf.Active = 'No'
    df_InactConf.YearInact = date.year
    df_InactConf.MonthInact = date.month
    df_InactConf.DayInact = date.day
        
def getInactConf(df_Inactive, config):
    list = []
    printAndLog("Evaluating Inactive List: ")
    for i, elem in enumerate(df_Inactive.Url):
        printAndLog(elem)
        soup = OpenBrowserAndFetchData(elem, config)
        try:
            inactiveString = soup.select("div.deactivated-detail_container > h1")[0].get_text().strip()
            if inactiveString == 'Lo sentimos, este anuncio ya no está publicado':
                list.append(i)
                printAndLog("True Positive")
        except IndexError as error:
            printAndLog("False Positive")
        printAndLog("--------")
        time.sleep(15)

    return df_Inactive.iloc[ list ].reset_index(drop=True)

def InsertInCell(df_Db_out, row, Col, Value):
    df_Db_out.loc[df_Db_out.index[row], Col] = Value

def printAndLog(string):
    print(string)
    logging.info(string)
    
def setUpLogs():
    if not os.path.exists('RealEstateInfo.log'):
        open('RealEstateInfo.log', 'w').close() 
    if not os.path.exists('RealEstateDebug.log'):
        open('RealEstateDebug.log', 'w').close() 
    logging.basicConfig(filename='RealEstateInfo.log', level=logging.INFO, format='%(levelname)s-%(asctime)s: %(message)s')
    logging.basicConfig(encoding='utf-8')
    logging.basicConfig(filename='RealEstateDebug.log', level=logging.DEBUG, format='%(levelname)s-%(asctime)s: %(message)s')
    logging.basicConfig(encoding='utf-8')
    logging.info('Opening new log session')
    logging.debug('Opening new Debug log session')
    
def loadDb(name):
    #load pandas db
    df_Db_in = getDf()
    try:
        df_Db_in = pd.read_csv(name, encoding='cp1252', index_col=False, keep_default_na=False)
    except FileNotFoundError:
        printAndLog("First do one round of botting, to generate initial dbPisos.csv")

    df_Db_in = df_Db_in.astype({"IdPlat": int})
    printAndLog(df_Db_in)
    return df_Db_in

def executeBot(config,mainUrl):
    currentDateTime = lambda: datetime.now().strftime("%Y/%m/%d/ %H:%M:%S")

    printAndLog( "Starting job: " + currentDateTime() )  
    df_today = getDf()

    for elem in config.listUrls:
        printAndLog( currentDateTime() + ", Current Url: " + elem  ) 
        WorkZona(df_today, elem, mainUrl, config)
        printAndLog( "Sleeping 2 min to be nice to servers: " + str(currentDateTime())   ) 
        time.sleep( config.NEXT_ZONE_DELAY )
        
    return df_today

def displayLoadedUrls(config):
    printAndLog("List of loaded urls:")
    for elem in config.listUrls:
        printAndLog(elem)
        
def writeResults(Dfcont):
    if not os.path.exists('history'):
        os.makedirs('history')

    date =  datetime.now()

    todaysDirName = str(date.year) + date.strftime("%b") +  date.strftime('%d')
    todaysDirNameLocation = 'history'+ '/' + todaysDirName

    if not os.path.exists( todaysDirNameLocation ):
        os.makedirs( todaysDirNameLocation )

    Dfcont.df_Db_in.to_csv( todaysDirNameLocation + '/' + 'dbIn_Pisos.csv', encoding='cp1252',index=False)
    Dfcont.df_today.to_csv( todaysDirNameLocation + '/' + 'dbToday_Pisos.csv', encoding='cp1252',index=False)
    Dfcont.df_Db_out.to_csv( todaysDirNameLocation + '/' + 'dbOut_Pisos.csv', encoding='cp1252',index=False)
    Dfcont.df_new.to_csv( todaysDirNameLocation + '/' + 'dbNew_Pisos.csv', encoding='cp1252',index=False)
    Dfcont.df_Inactive.to_csv( todaysDirNameLocation + '/' + 'dbInactive_Pisos.csv', encoding='cp1252',index=False)
    Dfcont.df_InactConf.to_csv( todaysDirNameLocation + '/' + 'dbInactiveConf_Pisos.csv', encoding='cp1252',index=False)

    os.replace("RealEstateInfo.log", todaysDirNameLocation + '/RealEstateInfo.log')  #Send log to proper dir
    
    #Write out df to overwrite standard input file
    Dfcont.df_Db_out.to_csv('dbPisos.csv', encoding='cp1252',index=False)
    
def sendEmail(df_new, config):
    msg = MIMEMultipart()
    msg['Subject'] = "Nuevos pisos de Idealista"
    msg['From'] = config.emailFrom
    recp= ""
    for elem in config.recipients:
        recp = recp + elem + ", "
    recp = recp[:-2]
    msg['To'] = recp

    html = """\
    <html>
      <head></head>
      <body>
        {0}
      </body>
    </html>
    """.format(df_new.to_html())

    part1 = MIMEText(html, 'html')
    msg.attach(part1)

    port = 465  # For SSL
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
        server.login(config.emailFrom, config.sec)
        server.sendmail(msg['From'], config.recipients, msg.as_string())

logging.basicConfig(filename='RealEstateInfo.log', level=logging.INFO, format='%(levelname)s-%(asctime)s: %(message)s')
logging.basicConfig(encoding='utf-8')

def main():
    mainUrl = "https://www.idealista.com"
    config = ConfigData()
    setUpLogs()
    displayLoadedUrls(config)
    Dfcont = DfDbContainer()
    Dfcont.df_Db_in = loadDb('dbPisos.csv')
    Dfcont.df_today = executeBot(config,mainUrl)
    Dfcont.df_Db_out = BuildOutputDb(Dfcont.df_Db_in, Dfcont.df_today)
    Dfcont.df_Db_out.to_csv('dbPisosTemp.csv', encoding='cp1252',index=False)  #Write pandas df to temp db
    #Get new and inactive entries
    Dfcont.df_new = FindNewDf(Dfcont.df_Db_in, Dfcont.df_today).reset_index(drop=True)
    Dfcont.df_Inactive = FindInactiveDf(Dfcont.df_Db_in, Dfcont.df_today).reset_index(drop=True)
    Dfcont.df_InactConf = getInactConf(Dfcont.df_Inactive, config)
    MarkInactiveDf(Dfcont.df_InactConf, Dfcont.df_Db_out)
    writeResults(Dfcont)
    sendEmail(Dfcont.df_new, config)


if __name__ == "__main__":
    main()