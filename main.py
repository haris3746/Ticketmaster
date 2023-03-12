import logging
import undetected_chromedriver as uc
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
import ssl
from email.message import EmailMessage
import smtplib
from pymongo import MongoClient
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from re import search

SCRAPPER = False


# def driverInit():
# setting options for undetected chrome driver
#   options = Options()
#  options.add_argument("--headless")
# options.add_argument("window-size=1400,1500")


# driverr = webdriver.Chrome(options=options)

# return driverr



def driverInit():
    option = uc.ChromeOptions()
    useragentstr = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.84 Safari/537.36"
    option.add_argument("--log-level=3")
    option.add_argument("--disable-infobars")
    option.add_argument("--disable-extensions")
    option.add_argument("--headless")
    prefs = {"credentials_enable_service": False,
             "profile.password_manager_enabled": False,
             "profile.default_content_setting_values.notifications": 2
             }
    option.add_experimental_option("prefs", prefs)

    option.add_argument(f"user-agent={useragentstr}")
    driverr = uc.Chrome(options=option)
    return driverr



def scroll_down(driver):
    SCROLL_PAUSE_TIME = 1
    # Get scroll height
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        # Scroll down to bottom
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # Wait to load page
        time.sleep(SCROLL_PAUSE_TIME)

        # Calculate new scroll height and compare with last scroll height
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height
        time.sleep(2)


def send_email(body, email):
    with open("email_credentials.txt", "r") as f:
        lines = [line.rstrip() for line in f]
        email_sender = lines[0]
        email_password = lines[1]

    email_receiver = str(email)
    subject = "Notification: Tickets Available in Tickets Master"
    em = EmailMessage()
    em['From'] = email_sender
    em['To'] = email_receiver
    em['subject'] = subject
    em.set_content(body)
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
        smtp.login(email_sender, email_password)
        smtp.sendmail(email_sender, email_receiver, em.as_string())


def add_cart(driver, price, url, email, in_url, input_price):
    try:

        driver.find_element(By.XPATH, "//div[@class='session-price-cat']//button[" + str(price) + "]")



    except:
        try:
            driver.find_element(By.XPATH, "//h3[@class='session-price-cat-title']/following-sibling::button[" + str(price) + "]"
                                "/html/body/div[1]/div/div/main/div/div[6]/div[2]/div/div[3]/div[1]/ul/li[" + str(
                                    price) + "]/div[1]/button").click()

        except:
            try:
                driver.find_element(By.XPATH, "/html/body/div[1]/div/div/main/div/div[6]/div[1]/div/div[3]/div[1]/ul/li[" + str(
                                    price) + "]/div[1]/button").click()
            except:
                driver.find_element(By.XPATH, "/html/body/div[1]/div/div/main/div/div[6]/div[2]/div/div[4]/div[1]/ul/li[" + str(price) + "]/div[1]/button").click()


    body = "Tickets are available for Url " + in_url + " for price of " + str(
        input_price[0]) + " Euros \nTicket Url :    " + url
    print("yes, tickets are available in this category in url : ", url)
    try:
        send_email(body, email)
    except:
        pass
        #logging.exception('msg')
    print("Email Sent")
    return "found"


try:
    print("Turn")
    cluster = MongoClient("mongodb+srv://user1:yes321@cluster0.m6tusxx.mongodb.net/?retryWrites=true&w=majority")
    db = cluster["ticketmaster"]
    collection = db["datafield"]
    data = list(collection.find())
    en = len(data)
    output = data[en - 1]
    temp = output
    url = output['url']
    quantity = output['quantity']
    input_price = output['price']
    notification_email = output['email']
    for i in range(0, len(url)):
        if url[i] == url[i-1]:
            continue
        if search("www.ticketmaster.fr", url[i]):
            print("in")
            driver = driverInit()
            driver.get(url[i])
            time.sleep(3)
            driver.find_element(By.ID, "onetrust-accept-btn-handler").click()
            # driver.find_element(By.XPATH, "//a[@class='header-my-account-link']//span[1]").click()
            # time.sleep(3)
            # driver.find_element(By.ID, "login-email").send_keys("muhammadharis3746@gmail.com")
            # driver.find_element(By.ID, "login-password").send_keys("Yes54321" + Keys.ENTER)
            time.sleep(2)
            scroll_down(driver)
            try:
                n = int(driver.find_element(By.XPATH, "//h2[@class='results-filter-info']//strong[1]").text)
            except:
                n = 0
            href = []
            for u in range(1, n + 1):
                href.append(
                    driver.find_element(By.XPATH,
                                        "(//a[@class='event-result-title-link'])[" + str(u) + "]").get_attribute(
                        "href"))
            if len(href) == 0:
                href.append(url[i])

            for num in range(0, len(href)):
                try:
                    status = ""
                    driver.get(href[num])
                    time.sleep(3)
                    scroll_down(driver)
                    try:
                        driver.find_element(By.XPATH, "/html/body/div[1]/div/div/main/div/div[5]/div[1]/button").click()
                    except:
                        # logging.exception('msg')
                        pass
                    time.sleep(2)
                    try:
                        driver.find_element(By.XPATH,
                                        "//button[contains(@class,'session-price-foldall-btn btn')]//span[1]").click()
                    except:
                        pass
                    time.sleep(2)
                    scroll_down(driver)
                    time.sleep(2)
                    print(input_price[i])
                    for price in range(1, 25):
                        try:
                            prc = driver.find_element(By.XPATH,
                                                      "(//span[@class='session-price-cat-title-price'])[" + str(
                                                          price) + "]").text
                            if search("Dès ", prc):
                                prc = int(float(prc.split(" ")[1]))
                            else:
                                prc = int(float(prc.split(" ")[0]))



                            print(prc)

                            if prc <= int(input_price[i]):
                                status = add_cart(driver, price, href[num], notification_email[i], url[i], input_price)
                                del temp['url'][i]
                                del temp['quantity'][i]
                                del temp['price'][i]
                                del temp['email'][i]
                                del temp['_id']
                                print(temp)
                                collection.insert_one(temp)

                                break
                        except:
                            # logging.exception('msg')
                            continue
                    if status == "found":
                        break
                except:
                    #logging.exceotion('msg')
                    continue
            driver.quit()
        else:
            continue




except:
    #logging.exception('msg')
    pass
