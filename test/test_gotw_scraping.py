import unittest

from gotw_webscraping import get_panel_urls
from gotw_webscraping import retrieve_panel_decisions

#test you get a list from the get_panel_list function
class TestScrape(unittest.TestCase):
    def test_get_panel_list(self):
        result = get_panel_urls(2021, 1, 1)
        result_type = isinstance(result, list)
        expected = True
        self.assertEqual(result_type, expected)
        
#check you get the expected data frame for a specific url
class TestRetrieve(unittest.TestCase):
    def test_retrive_panel_decisions(self):
        result = retrieve_panel_decisions("https://gow.epsrc.ukri.org/NGBOViewPanel.aspx?PanelId=1-3S0O1")
        #check column returns expected data
        expected_funded = [3, 5911461]
        self.assertListEqual(result["funded"].tolist(), expected_funded)
        
        
if __name__ == "__main__":
    unittest.main()