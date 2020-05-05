import bs4, requests
from selenium import webdriver
# from selenium.webdriver.firefox.options import Options
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from datetime import datetime


CJParcelNumber = '630200846612'
def getCJParcelStatus(parcelNumber):

    CJTEKBAEurl = r'https://www.cjlogistics.com/ko/tool/parcel/tracking'
    

    options = Options()
    options.add_argument("--headless") # This opens headless (windowless) Chrome/ium
    
    try: # This covers the pi and win computers keeping Chrome path in different places. Could Pi work without it?
        print('Trying Pi Path:')
        driver = webdriver.Chrome('/usr/lib/chromium-browser/chromedriver', options=options)
    except:
        print('Trying Win Path:')
        driver = webdriver.Chrome(options=options)

    driver.get(CJTEKBAEurl)
    print('Headless Chrome Initialised...')
    CJEnterParcelNumberForm = driver.find_element_by_id("paramInvcNo") #Tracking number input box
    print('Located parcel number input box')
    CJEnterParcelNumberForm.send_keys(parcelNumber)
    CJEnterParcelNumberForm.send_keys(Keys.ENTER) # Enter the number and press enter
    print('Entered parcel number')
    element = WebDriverWait(driver, 10).until( # Wait until it loads
            EC.presence_of_element_located((By.ID, "statusDetail")) #This table appears when loaded
        )
    print('Detail table loaded')

    CJParcelTable = element.get_attribute('innerHTML')

    CJSoup = bs4.BeautifulSoup(CJParcelTable, features="html.parser")

    driver.quit()

    CJParcelTable_BottomRow = CJSoup.findAll('tr')[-2] # The bottom row is a blank row, so use -2
    CJParcelCells = CJParcelTable_BottomRow.findAll('td')

    results = [cell.get_text() for cell in CJParcelCells]

    try:
        datetimeObj = None
        try:
            datetimeObj = datetime.strptime(results[1], "%Y-%m-%d %H:%M:%S.%f") #Create versatile datetime object out of date provided
        except:
            print(f'CJ Tracking produced erroneous datetime: {results[1]}')

        if '완료' in results[0]:
            results[0] = '배달완료'

        resultsDict = {
                        'status' : results[0],
                        'dateTime' : datetimeObj,
                        'location' : results[3],
                        'extra': results[2]
                        }
        return resultsDict
    except:
        print('Failed to extract data. Data gathered:')
        print(results)
        return False


LotteParcelNumber = '402175371732'
def getLotteParcelStatus(parcelNumber):

    LotteTekbaeUrl = r'https://www.lotteglogis.com/home/reservation/tracking/index'

    options = Options()
    options.add_argument("--headless")
    
    try: #This allows the script to find Chromedriver on both PI and Win. Need to attempt without specified path on PI too.
        print('Trying Pi Path:')
        driver = webdriver.Chrome('/usr/lib/chromium-browser/chromedriver', options=options)
    except:
        print('Trying Win Path:')
        driver = webdriver.Chrome(options=options)

    driver.get(LotteTekbaeUrl)
    print('Headless Chrome Initialised...')
    LotteEnterParcelNumberForm = driver.find_element_by_id("InvNo")
    print('Located parcel number input box')
    LotteEnterParcelNumberForm.send_keys(parcelNumber)

    LotteSubmitButton = driver.find_element_by_class_name('btnGL')
    print('Found button')
    LotteSubmitButton.click()
    print('Clicked button')
    element = WebDriverWait(driver, 10).until( # The XPATH for the results table
            EC.presence_of_element_located((By.XPATH, "/html/body/div[2]/div[2]/div[3]/div/div[2]/table[2]"))
            )


    print('Detail table loaded')

    LotteParcelTable = element.get_attribute('innerHTML')


    LotteSoup = bs4.BeautifulSoup(LotteParcelTable, features="html.parser")
    driver.quit()
    LotteParcelTable_BottomRow = LotteSoup.findAll('tr')[-1] #Lotte's results are in the bottom row.
    LotteParcelCells = LotteParcelTable_BottomRow.findAll('td')

    results = [cell.get_text() for cell in LotteParcelCells]
    strippedDateCell = results[1].strip()
    try:
        datetimeObj = None
        try:

            if strippedDateCell.endswith('\xa0--:--'): #The bottom row can have an oddly formatted date. This cuts it off.
                timeLessDate = results[1].strip()[:-6]
                datetimeObj = datetime.strptime(timeLessDate, "%Y-%m-%d")
            else:
                try:
                    datetimeObj = datetime.strptime(strippedDateCell, "%Y-%m-%d %H:%M:%S.%f")
                except:
                    print(f'Lotte Tracking produced erroneous datetime: {strippedDateCell}')

        except:
            print(f'Lotte Tracking produced erroneous datetime: {strippedDateCell}')

        if '완료' in results[0]:
            results[0] = '배달완료'

        resultsDict = {
            'status' : results[0],
            'dateTime' : datetimeObj,
            'location' : results[2].strip(),
            'extra': results[3]
        }
        return resultsDict
    except: #This covers Lotte's expired tracking number result
        if len(results) == 1 and results[0] == '화물추적 내역이 없습니다.':
            print('Parcel number has expired!')
            return {
                'status' : results[0],
                'dateTime': 'Expired',
                'location' : 'Expired',
                'extra': 'Expired'
            }
        else:
            print('Failed to extract data. Data gathered:')
            print(results)
            return False


# HanJinParcelNumber = '507897901630'
HanJinParcelNumber = 	'507901323591'
def getHanJinParcelStatus(parcelNumber):
    BS4headers = {'User-Agent' : 'Chrome/70.0.3538.77'}


    HanJinURL = r'https://www.hanjin.co.kr/Delivery_html/inquiry/result_waybill.jsp?wbl_num='

    res = requests.get(HanJinURL + parcelNumber, headers=BS4headers)

    res.raise_for_status()

    resultsPageSOUP = bs4.BeautifulSoup(res.text, features="html.parser")

    resultsTable_entire = resultsPageSOUP.findAll('tbody')[1] #The first table [0] is some sort of invoice for the parcel service.

    resultsTable_rows = resultsTable_entire.findAll('tr')

    finalResultRow = resultsTable_rows[-2] # Row -1 tells about who receives but not the status of the parcel.

    resultCells = finalResultRow.findAll('td')

    results = [cell.get_text() for cell in resultCells]

    splitFinalCell = results[-1].splitlines() # The final cell is formatted poorly. Separate this into a list.
    splitFinalCell = [cell.strip() for cell in splitFinalCell] #Strip excess whitespace chars
    splitFinalCell = [cell for cell in splitFinalCell if cell] #Remove blank list entries

    results = results[:-1] # Remove poorly formatted final cell
    results.extend(splitFinalCell) # Add usable data from final cell.

    if '완료' in results[3]:
        results[3] = '배달완료'

    try:
        datetimeObj = None
        try:
            datetimeObj = datetime.strptime(f'{results[0]} {results[1]}', "%Y-%m-%d %H:%M")
        except:
            print(f'HanJin Tracking produced erroneous datetime: {results[0]} {results[1]}')

        resultsDict = {
            'dateTime' : datetimeObj,
            'location' : results[2],
            'status' : results[3],
            'extra' : results[4]
        }

        return resultsDict
    except:
        print('Failed to extract data. Data gathered:')
        print(results)
        return False
    
# print(getCJParcelStatus(CJParcelNumber))

# print(getLotteParcelStatus(LotteParcelNumber))

# print(getHanjinParcelStatus(HanJinParcelNumber))
