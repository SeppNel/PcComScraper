from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
from bs4 import BeautifulSoup
import requests
import time

def readTelegramKey():
    try:
        f = open("telegramKey.txt", "r")
        return f.read()
    except:
        print("Exception reading telegramKey.txt, creating blank file...")
        f = open("telegramKey.txt", "w")
        f.write("PASTE YOUR API KEY HERE")
        f.close()
        exit()


def sendTelegram(name, price):
    token = readTelegramKey()
    url = f"https://api.telegram.org/bot{token}"
    params = {"chat_id": "6425902651", "text": f"Lowest Price for {name} of: {price}"}
    r = requests.get(url + "/sendMessage", params=params)


def writePriceTxt(price):
    f = open("priceHistory.txt", "w")
    f.write(str(price))
    f.close()

def readPriceTxt():
    f = open("priceHistory.txt", "r")
    return float(f.read())


url = "https://www.pccomponentes.com/discos-duros/500-gb/512-gb/conexiones-m-2/disco-ssd?price_from=27&price_to=45"

try:
   lowestEver = readPriceTxt()
   print(f"Lowest Price: {lowestEver}")
except:
    lowestEver = 1000000

while True:
    print("Scraping...")
    # Configure the WebDriver for Firefox
    service = Service(executable_path='geckodriver.exe')
    firefox_options = Options()
    firefox_options.add_argument("--headless")
    firefox_options.headless = True  # Run Firefox in headless mode (no GUI)
    driver = webdriver.Firefox(options=firefox_options, service=service)
    driver.implicitly_wait(30)

    # Load the webpage
    driver.get(url)

    # Get the page source after the content has loaded
    page_source = driver.page_source

    # Parse the HTML content
    soup = BeautifulSoup(page_source, 'html.parser')

    # Find all elements with the specified class for product names
    product_names = soup.find_all('h3', class_='product-card__title')
    print(f"Productos: {len(product_names)}")

    print("")

    # Find all elements with the specified class for product prices
    product_prices = soup.find_all('div', class_='product-card__price-container')

    i = 0
    for nan in product_names:
        product_names[i] = product_names[i].text.strip()
        price = product_prices[i].text.strip()
        price = price.split('€', 1)[0]
        price = float(price.replace(',', '.'))
        product_prices[i] = price
        i += 1

    ordered = [-1, -1, -1, -1, -1]
    for i in range(5):
        lowest = 1000000
        j = 0
        for price in product_prices:
            if price < lowest and j not in ordered and "SATA" not in product_names[j]:
                ordered[i] = j
                lowest = price
            j += 1

    i = 1
    for p in ordered:
        name = product_names[p]
        price = product_prices[p]
        print(f"{i}. {name} - Price: {price}")
        i += 1

    index = ordered[0]

    if product_prices[index] < lowestEver:
        lowestEver = product_prices[index]
        writePriceTxt(lowestEver)
        sendTelegram(product_names[index], product_prices[index])

    # Close the WebDriver
    driver.quit()
    print("--------------------------------------------------------------")
    time.sleep(1800) #30 min