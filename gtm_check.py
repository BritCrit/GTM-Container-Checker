from datetime import date
import pandas as pd 
from requests_html import HTMLSession
import re


GTM_Code = "YOUR-GTMCODE" 
google_cache = 'http://webcache.googleusercontent.com/search?q=cache:'


def test_site(url):
  confirmed = False
  correct_url = False
  codes = []
  gtm_code_list = []
  try:
    session = HTMLSession()
    r = session.get(google_cache+url+'&strip=0&vwsrc=1')
    correct_url = True
  except:
    print(f"Invalid URL: {url}")
    return "Invalid URL"
  if correct_url:
    GTM_locations = [m.start() for m in re.finditer('GTM', r.text)]
    for location in GTM_locations:
      found_gtm_code = r.text[location:(location+11)]
      gtm_code_list.append(found_gtm_code)
      gtm_code_list = list(set(gtm_code_list))
    print(f"There were {len(gtm_code_list)} GTM tags found for {url}. GTM code(s): {', '.join([str(x) for x in gtm_code_list]) }")
    if GTM_Code in gtm_code_list:
      print(f"Our GTM code was found! on {url}")
      confirmed = True
      codes = ', '.join(gtm_code_list)
    else:
      print(f"Our GTM code was NOT found on {url}.")
      codes = 'No GTM found'
    return codes

def test_site_no_cache(url):
  confirmed = False
  correct_url = False
  codes = []
  gtm_code_list = []
  try:
    session = HTMLSession()
    r = session.get(url)
    correct_url = True
  except:
    print(f"Invalid URL: {url}")
    return "Invalid URL"
  if correct_url:
    GTM_locations = [m.start() for m in re.finditer('GTM', r.text)]
    for location in GTM_locations:
      found_gtm_code = r.text[location:(location+11)]
      gtm_code_list.append(found_gtm_code)
      gtm_code_list = list(set(gtm_code_list))
    print(f"There were {len(gtm_code_list)} GTM tags found for {url}. GTM code(s): {', '.join([str(x) for x in gtm_code_list]) }")
    if GTM_Code in gtm_code_list:
      print(f"Our GTM code was found! on {url}")
      confirmed = True
      codes = ', '.join(gtm_code_list)
    else:
      print(f"Our GTM code was NOT found on {url}.")
      codes = 'No GTM found'
    return codes

def confirm_gtm(df):
  df['verified'] = df.gtm_codes.str.contains(GTM_Code)
  return df


today = date.today().strftime("%m_%d_%y")

df = pd.read_csv(fn,header=None)
df.columns = ['site']
df['gtm_codes'] = df['site'].apply(lambda x: test_site(x))
df = confirm_gtm(df)

cached_df = df.loc[df.gtm_codes != 'No GTM found'].copy()

print("Performing double check against GTM's not found...")
new_df = df.loc[df.gtm_codes == 'No GTM found'].copy()
new_df = new_df.reset_index(drop=True).drop(['gtm_codes', 'verified'], axis=1)
new_df['gtm_codes'] = new_df['site'].apply(lambda x: test_site_no_cache(x))
new_df = confirm_gtm(new_df)

print("Combining final results into single dataframe...")
final_df = pd.concat([cached_df, new_df]).reset_index(drop=True)

final_df.to_csv(f"{fn.split('.')[0]}_gtm_check{today}.csv")
