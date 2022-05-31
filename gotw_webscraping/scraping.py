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
import time
from urllib import request
from webdriver_manager.microsoft import EdgeChromiumDriverManager

#function to grab the panel urls#############################
def get_panel_urls(year, month, day, search_term = None):
    """Get a list of all panel urls available in  GotW panel search.
    
    This function searches for all panels listed from a user-specified start date until the date of running. It also sets up the webdriver. 
    The function may be enhanced in future to customise the end date.
    IMPORTANT: The function works using an Edge webdriver, so you need to be Windows for this to work, and have MS Edge isntalled.
    
    Args:
        year (int): Year from which to start searching.
        month (int): Month in year from which to start searching
        day (int): Day in month from which to start searching.
        search_term: (str): Optionally, pass through a search term to further filter the list. 
    
    Returns
    -----
    A list of the panel urls.
    """
    #error checking
    
    #convert year to match xpath option number
    year_converted = year - 1999 #first year is 2000 and is option 1
    
    #set the driver
    driver = webdriver.Edge(service = Service(EdgeChromiumDriverManager().install()))
    
    #set url
    start_url = "https://gow.epsrc.ukri.org/NGBOFindPanels.aspx"
    
    #load page
    driver.get(start_url)
    
    #first step is to set to search between dates - the ui defaults to 'in the last' 6 months
    driver.find_element(by = By.XPATH, value = '//*[@id="oplDates_0"]').click()
    
    #then we need to pick the first day, month, year
    day_xpath = f'//*[@id="oUcStartDate_ddlDay"]/option[{day}]'
    mon_xpath = f'//*[@id="oUcStartDate_ddlMonth"]/option[{month}]'
    yr_xpath = f'//*[@id="oUcStartDate_ddlYear"]/option[{year_converted}]'
    
    #now we have to click on those options
    driver.find_element(by = By.XPATH, value = '//*[@id="oUcStartDate_ddlDay"]').click() # open day slicer
    WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, day_xpath))).click() # choose the day
    
    driver.find_element(by = By.XPATH, value = '//*[@id="oUcStartDate_ddlMonth"]').click() # open day slicer
    WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, mon_xpath))).click() # choose the month
    
    driver.find_element(by = By.XPATH, value = '//*[@id="oUcStartDate_ddlYear"]').click() # open day slicer
    WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, yr_xpath))).click() # choose the year
    
    #if search term is given, look for it
    if search_term is not None:
        panel_search = driver.find_element(by = By.XPATH, value = '//*[@id="txtPanelName"]') #click on the panel search webform
        panel_search.send_keys(search_term)
    
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
def retrieve_panel_decisions(url):
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
    tables = pd.read_html(url, match = "Funding Priority List") 
    
    #store relevant tables in a list
    tbl_list = [
        tables[0], #by number
        tables[1] #by value
        ]
    
    #internal function to make tidying up the tables easier
    def tidy_tables(df):  
        
        #remove trailing column if there is one
        if(df.shape[1]) == 7:
            df = df.drop(df.columns[6], axis = 1)
            
        #headers
        df = df.rename(columns = df.iloc[0])
        
        #tidy up headers
        def tidy_columns(c):
            stripped = c.strip()
            lower = stripped.lower()
            nospace = lower.replace(" ", "_")
            nopct = nospace.replace("%", "pct")
            nochr = nopct.translate ({ord(c): "" for c in "!@#$%^&*()[]{};:,./<>?\|`~-=+"})
            return nochr  
        
        df.columns = [tidy_columns(c) for c in df.columns.values.tolist()]
        
        #rename success rate field if applicable
        if df.shape[1] > 3:
            df = df.rename(columns = {df.columns[5]: "success_rate"})
        
        #remove unncessary rows
        if df.shape[1] > 3:
             filter_out = ["Funding Priority List", "Standard", "Including:", "Please click on relevant Funding Priority List for a full rank ordered list."]
             df = df.loc[~df.funding_priority_list.isin(filter_out)]
        else:
            df = df.iloc[[1]] 
        
        #add columns for panel, meeting date and year
        df["panel"] = panel_name
        df["panel_id"] = url.split("PanelId=")[1]
        df["year"] = meeting_date.year
        df["month"] = meeting_date.month
        df["day"] = meeting_date.day  
        
        #change column types
        if df.shape[1] > 8:
            for c in ["funded", "unfunded", "referred_to_a_later_panel", "decision_still_awaited", "success_rate"]:
                df[c] = pd.to_numeric(df[c])
        else:
            for c in ["full_proposals_invited", "full_proposals_declined"]:
                df[c] = pd.to_numeric(df[c])        
     
        #calculate sr if needed
        if df.shape[1] <= 8: 
            df["success_rate"] = 100 * df["full_proposals_invited"] / (df["full_proposals_invited"] + df["full_proposals_declined"])
            
        return df
    
    #list for tidied dfs
    tidied_dfs = [tidy_tables(df) for df in tbl_list]
    
    #concat
    tidy_df = pd.concat(tidied_dfs)
    
    #get entries for data type field
    numbers = ["number" for r in list(range(int(len(tidy_df) / 2)))]
    values = ["value" for r in list(range(int(len(tidy_df) / 2)))]
    
    #add data type field
    tidy_df["data_type"] = numbers + values

    return tidy_df