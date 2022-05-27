#import required packages
from bs4 import BeautifulSoup as Soup
from datetime import datetime
import lxml
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.edge.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from skimpy import clean_columns
import time
from urllib import request
from webdriver_manager.microsoft import EdgeChromiumDriverManager

#function to grab the panel urls#############################
def get_panel_urls():
    """Get a list of all panel urls available in  GotW panel search.
    
    This function automatically sets search settings for panels as far back as they can go. It also sets up the webdriver. 
    May be future functionality will be to add arguments to customise the timeframe.
    IMPORTANT: The function works using an Edge webdriver, so you need to be Windows for this to work, and have MS Edge isntalled.
    
    Returns
    -----
    A list of the panel urls.
    """
    #set the driver
    driver = webdriver.Edge(service = Service(EdgeChromiumDriverManager().install()))
    
    #set url
    start_url = "https://gow.epsrc.ukri.org/NGBOFindPanels.aspx"
    
    #load page
    driver.get(start_url)
    
    #first step is to set to search between dates - the ui defaults to 'in the last' 6 months
    driver.find_element(by = By.XPATH, value = '//*[@id="oplDates_0"]').click()
    
    #then we need to pick the first day, month, year
    day_xpath = '//*[@id="oUcStartDate_ddlDay"]/option[1]'
    mon_xpath = '//*[@id="oUcStartDate_ddlMonth"]/option[1]'
    yr_xpath = '//*[@id="oUcStartDate_ddlYear"]/option[1]'
    
    #now we have to click on those options
    driver.find_element(by = By.XPATH, value = '//*[@id="oUcStartDate_ddlDay"]').click() # open day slicer
    WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, day_xpath))).click() # choose the day
    
    driver.find_element(by = By.XPATH, value = '//*[@id="oUcStartDate_ddlMonth"]').click() # open day slicer
    WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, mon_xpath))).click() # choose the month
    
    driver.find_element(by = By.XPATH, value = '//*[@id="oUcStartDate_ddlYear"]').click() # open day slicer
    WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, yr_xpath))).click() # choose the year
    
    #so now all that's left to do is search
    driver.find_element(by = By.XPATH, value = '//*[@id="btnSearch"]').click()
    
    #get the page as a soup object
    page = Soup(driver.page_source, features = "html.parser")
    
    #from inspecting the page we can see the particular table of interest has id = "dgDetails"
    tbl = page.find(id = "dgDetails")
    
    #find all  the 'a' (hyperlink) elements
    hyperlinks = tbl.find_all("a", href = True)
    
    #extract the href arguments
    hrefs = [hyperlinks[h]["href"] for h in range(len(hyperlinks))]
    
    #now extract the panle ids - exclude the first two rows as these part of the table header
    panel_ids = [hrefs[h].split("PanelId=")[1] for h in range(2, len(hrefs), 1)]
    
    #identify if 'view panel', 'prior panel' or 'NGBO panel' - affects final URL
    types = []
    for h in range(2, len(hrefs), 1):
        if hrefs[h][:4] == "NGBO":
            type = "NGBO"
            types.append(type)
        elif hrefs[h][4:6] == "Pr": 
            type = "Prior"
            types.append(type)
        else:
            type = "View"
            types.append(type)

    #finally, turn these into urls
    panel_urls = []
    for i in range(len(panel_ids)):
        if types[i] == "NGBO":
            url = f"https://gow.epsrc.ukri.org/NGBOViewPanel.aspx?PanelId={panel_ids[i]}"
            panel_urls.append(url)
        elif types[i] == "Prior":
            url = f"https://gow.epsrc.ukri.org/ViewPriorPanel.aspx?PanelId={panel_ids[i]}"
            panel_urls.append(url)
        else:
            url = f"https://gow.epsrc.ukri.org/ViewPanel.aspx?PanelId={panel_ids[i]}"
            panel_urls.append(url)      
    
    #at this point I don't think the driver is needed any more, so we can quit
    driver.quit()
    
    #return the list of urls
    return panel_urls
    
#function to retrive details for each panel##########################################
def retrieve_panel_decsions(url):
    """Retrieve decision data for a specific panel.
    
    Once you have the URL for a page containing panel decisions, retrieve the data as a `pandas` DataFrame object.

    Args:
        url (str): The url for the panel page desired, as returned by `get_panel_urls`.
        
    Returns:
        A pandas dataframe with two rows, one showing the panel decisions by number, the other by value.
    """
    
    #panel page source
    panel_source = request.urlopen(url)
    
    #panel page
    panel_page = Soup(panel_source, features = "html.parser")
    
    #get the panel name
    panel_name = panel_page.find(id = "lblPanelName").text.strip()
    
    #get the meeting date
    meeting_date = panel_page.find(id = "lblDateOfPanel").text
    meeting_date = datetime.strptime(meeting_date, '%d %B %Y')
    
    #read tables to dataframe
    tables = pd.read_html(url) #we're using the first one as an example here
    
    #store relevant tables in a list
    tbl_list = [
        tables[3], #by number
        tables[5] #by value
        ]
    
    #internal function to make tidying up the tables easier
    def tidy_tables(df):  
            
        #headers
        df = df.rename(columns = df.iloc[0])
        df = clean_columns(df)   
        
        #remove unncessary rows
        df = df.drop([0, 2, 3, 4])   
        
        #add columns for panel, meeting date and year
        df["panel"] = panel_name
        df["year"] = meeting_date.year
        df["month"] = meeting_date.month
        df["day"] = meeting_date.day   
        
        #rename the funding rate column for conistency
        df = df.rename(columns = {df.columns[5]: "success_rate"})   
        
        return df
    
    #list for tidied dfs
    tidied_dfs = [tidy_tables(df) for df in tbl_list]
    
    #concat
    tidy_df = pd.concat(tidied_dfs)
    
    #add on data type
    tidy_df["data_type"] = ["number", "value"]
    
    return tidy_df