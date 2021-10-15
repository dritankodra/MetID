# import needed libraries
import time
import os
import re

import numpy as np
import pandas as pd

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver import DesiredCapabilities

from bs4 import BeautifulSoup

#================================================================================
#================================================================================
#================================================================================


class color:
    '''
    class to print out colored, bold and underlined text
    '''
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    BLUE = '\033[34m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

#================================================================================
#================================================================================
#================================================================================


def wait_for_downloads(dir_in='/Users/drk36/Downloads', list_in=None):

    print(5 * ' ' + "Waiting for downloads", end="")

    list_new = os.listdir(dir_in)

    if list_in:
        while list_new == list_in:
            time.sleep(2)
            list_new = os.listdir(dir_in)
            print(".", end="")

    while any([filename.endswith(".crdownload") for filename in list_new]):
        time.sleep(2)
        print(".", end="")

    print(" Done!")

#================================================================================
#================================================================================
#================================================================================


def search_wos(all_db_in=None,
               search_string_in=None,
               start_date_in=None,
               end_date_in=None,
               filter_in=None,
               doctype_in=None,
               save_recs_in=None,
               fout_type_in=None,
               wait_click_in=3
               ):

    #------------------------------------------------------------
    # start timing code
    ti = time.time()

    url_in = 'http://apps.webofknowledge.com/'

    wait_click = wait_click_in  # time in seconds to wait for elements to be found by selenium
    stop_option = False  # option for process repeat until successful try
    try_number = 1  # starting try number
    print(f'\n{color.BOLD}{color.BLUE}Starting try: {color.RED}{try_number}{color.END}')
    print(f'\n{color.BOLD}{color.BLUE}output file type: {color.RED}{fout_type_in}{color.END}')

    while not stop_option and try_number <= 3:
        #-----------------------------------
        # start try to find and extract desired records
        try:
            # set options for webdriver
            optionz = webdriver.ChromeOptions()
            optionz.add_argument('--ignore-certificate-errors')
            optionz.add_argument('--incognito')
            capabilities = DesiredCapabilities.CHROME.copy()
            capabilities['acceptSslCerts'] = True
            capabilities['acceptInsecureCerts'] = True

            # start webdriver
            browser = webdriver.Chrome(options=optionz, desired_capabilities=capabilities)
            browser.get(url_in)

            # close popups at the beginning
            close_xpath = '//button[text()="×"]'
            wait = WebDriverWait(browser, 10)
            try:
                wait.until(EC.element_to_be_clickable((By.XPATH, close_xpath)))
                time.sleep(wait_click)
                browser.find_element_by_xpath(close_xpath).click()

                try:
                    wait.until(EC.element_to_be_clickable((By.XPATH, close_xpath)))
                    time.sleep(wait_click)
                    browser.find_element_by_xpath(close_xpath).click()
                except:
                    pass

            except:
                pass

            #-----
            # select option to search in all available databases
            # and not just the default option which is WOS core database
            if all_db_in:
                database_xpath = '//*[@id="global-select"]/div/div[2]/div[1]'
                wait = WebDriverWait(browser, 10)
                wait.until(EC.element_to_be_clickable((By.XPATH, database_xpath)))
                time.sleep(wait_click)
                browser.find_element_by_xpath(database_xpath).click()

            #-----
            # go to advanced search tab
            adv_search_xpath = '//*[@id="snSearchType"]/div[2]/a'
            wait.until(EC.element_to_be_clickable((By.XPATH, adv_search_xpath)))
            time.sleep(wait_click)
            browser.find_element_by_xpath(adv_search_xpath).click()
            time.sleep(2)

            #-----
            # set filter for start year of publications
            if start_date_in:

                add_date_xpath = '//span[text()=" Add date range "]'
                browser.find_element_by_xpath(add_date_xpath).click()
                time.sleep(1)

                try:
                    date_type_xpath = '//span[text()="Index Date"]'
                    browser.find_element_by_xpath(date_type_xpath).click()
                    time.sleep(1)
                except:
                    pass

                date_type_xpath2 = '//span[text()="Publication Date"]'
                browser.find_element_by_xpath(date_type_xpath2).click()
                time.sleep(1)

                try:
                    custom_date_xpath = '//span[text()="Custom"]'
                    browser.find_element_by_xpath(custom_date_xpath).click()
                    time.sleep(1)
                except:
                    pass

                start_date_box_xpath = '/html/body/app-wos/div/div/main/div/app-input-route/' + \
                                       'app-search-home/div[2]/div/app-input-route/app-search-advanced/' + \
                                       'app-advanced-search-form/form/div[4]/div[1]/div[1]/' + \
                                       'app-search-timespan/div/div[2]/input[1]'

                start_date_box = browser.find_element_by_xpath(start_date_box_xpath)
                start_date_box.send_keys(start_date_in)
                time.sleep(1)

                # set filter for end year of publications
                if end_date_in:

                    end_date_box_xpath = '/html/body/app-wos/div/div/main/div/app-input-route/' + \
                                         'app-search-home/div[2]/div/app-input-route/app-search-advanced/' + \
                                         'app-advanced-search-form/form/div[4]/div[1]/div[1]/' + \
                                         'app-search-timespan/div/div[2]/input[2]'

                    end_date_box = browser.find_element_by_xpath(end_date_box_xpath)
                    end_date_box.send_keys(end_date_in)
                    time.sleep(1)

            #-----
            # find and clear search box
            search_xpath = '//*[@id="advancedSearchInputArea"]'
            search_box = browser.find_element_by_xpath(search_xpath)
            search_box.clear()

            # enter search string in search box
            search_box.send_keys(search_string_in)
            search_box.submit()

            try:
                wait.until(EC.element_to_be_clickable((By.XPATH, close_xpath)))
                time.sleep(wait_click)
                browser.find_element_by_xpath(close_xpath).click()

            except:
                pass

            # filter for highly cited publications
            if filter_in != 'All':
                filter_in_xpath = f'//span[text()="{filter_in}"]'
                wait.until(EC.element_to_be_clickable((By.XPATH, filter_in_xpath)))
                browser.find_element_by_xpath(filter_in_xpath).click()

                refine_xpath = '//span[text()="Refine"]'
                wait.until(EC.element_to_be_clickable((By.XPATH, refine_xpath)))
                browser.find_element_by_xpath(refine_xpath).click()

                time.sleep(5)

            # filter for document type
            if doctype_in != 'All':
                doctype_in_xpath = f'//span[text()="{doctype_in}"]'
                wait.until(EC.element_to_be_clickable((By.XPATH, doctype_in_xpath)))
                browser.find_element_by_xpath(doctype_in_xpath).click()

                refine_xpath = '//span[text()="Refine"]'
                wait.until(EC.element_to_be_clickable((By.XPATH, refine_xpath)))
                browser.find_element_by_xpath(refine_xpath).click()

                time.sleep(5)

            # get the number of results after filtering (if any...)
            hits_element_xpath = '/html/body/app-wos/div/div/main/div/app-input-route/app-base-summary-component/' + \
                                 'app-search-friendly-display/div[1]/app-general-search-friendly-display/h1/span'
            hits_element_final = browser.find_element_by_xpath(hits_element_xpath)
            num_results = int(hits_element_final.text.replace(',', ''))

            #------------------------------
            # set list of records' batches to download
            # (only 1000 records to download at a time is allowed)
            #------------------------------
            steps_used = 1000
            if save_recs_in == 'all':
                if num_results % steps_used:
                    recs_used = [i for i in range((num_results // steps_used) + 1)]
                else:
                    recs_used = [i for i in range(num_results // steps_used)]

            elif '-' in save_recs_in:
                save_recs_in = save_recs_in.split('-')
                save_recs_in = [int(i.strip()) if i.strip() else 0 for i in save_recs_in]
                recs_min = save_recs_in[0]
                recs_max = save_recs_in[1]

                while recs_max * steps_used > num_results:
                    recs_max -= 1

                recs_used = [i for i in range(recs_min, recs_max + 1)]

            else:
                recs_used = [0]

            # find number of total pages with results
            total_pages_xpath = '/html/body/app-wos/div/div/main/div/app-input-route/app-base-summary-component/' + \
                                'div/div[2]/app-page-controls[1]/div/form/div/span'
            total_pages_final = browser.find_element_by_xpath(total_pages_xpath)
            num_pages = int(total_pages_final.text.replace(',', ''))

            print(f" - Number of results: {color.BOLD}{color.RED}{num_results}{color.END}, " +
                  f"in {color.BOLD}{color.RED}{num_pages}{color.END} pages")

            # ================================
            # OUTPUT RESULTS IN FILE
            # ================================
            # loop over desired batches of records
            for irec, rec in enumerate(recs_used):
                element_number = irec * 2

                export_continue = True
                while export_continue:
                    markFrom = rec * steps_used + 1
                    if markFrom < num_results:
                        markTo = (rec + 1) * steps_used
                        if markTo > num_results:
                            markTo = num_results

                        print(f' - Exporting records: {markFrom} – {markTo}')

                        export_continue = False
                    else:
                        rec -= 1

                # open up export popup window and make selections
                export_type_xpath = '//span[text()=" Export "]'
                browser.find_element_by_xpath(export_type_xpath).click()
                time.sleep(0.5)

                if fout_type_in == '.xls':
                    # select other format of output file
                    xls_format_xpath = '//button[text()=" Excel "]'
                    browser.find_element_by_xpath(xls_format_xpath).click()
                else:
                    # select other format of output file
                    other_format_xpath = '//button[text()=" Tab delimited file "]'
                    browser.find_element_by_xpath(other_format_xpath).click()

                # select option to save all results
                time.sleep(1)

                save_option_xpath = '//*[@id="radio3"]/label'
                browser.find_element_by_xpath(save_option_xpath).click()

                # input starting record to be exported to file
                markFrom_box = browser.find_element_by_id('mat-input-' + str(element_number))
                markFrom_box.clear()
                markFrom_box.send_keys(markFrom)

                # input ending record to be exported to file
                markTo_box = browser.find_element_by_id('mat-input-' + str(element_number + 1))
                markTo_box.clear()
                markTo_box.send_keys(markTo)

                time.sleep(0.5)
                record_xpath = '//span[text()="Author, Title, Source"]'
                browser.find_element_by_xpath(record_xpath).click()

                time.sleep(0.5)
                record_xpath2 = '//span[text()="Full Record"]'
                browser.find_element_by_xpath(record_xpath2).click()

                time.sleep(0.5)
                export_xpath = '//span[text()="Export"]'
                browser.find_element_by_xpath(export_xpath).click()

                # select option to save all results
                time.sleep(0.5)

                init_list = os.listdir('/Users/drk36/Downloads/')
                wait_for_downloads(list_in=init_list)

            #--------------------
            # end process after successful extraction of records and close webdriver
            stop_option = True
            print(f'{color.BOLD}{color.BLUE}Try: ' +
                  f'{color.RED}{try_number}' +
                  f'{color.BLUE} Successful!!!{color.END}'
                  )
            browser.close()

        #-----------------------------------
        # handles case of falied attempt and repeats process...
        except:
            # close window in  the case of an error
            print(f'{color.BOLD}{color.BLUE}Try ' +
                  f'{color.RED}{try_number} ' +
                  f'{color.BLUE}Failed!!!\n\n' +
                  f'{color.BLUE}Starting try: ' +
                  f'{color.RED}{try_number + 1}{color.END}'
                  )
            try_number += 1

    #--------------------------------------------------
    # end timing code
    tf = time.time()
    print(f'\n{color.BOLD}{color.BLUE}Total time: ' +
          f'{color.RED}{round(tf-ti, 1)} ' +
          f'{color.BLUE}seconds{color.END}\n')

#================================================================================
#================================================================================
#================================================================================


def create_regex_function(df_in, regexin = None):
    
    search_regex = ''
    
    if not df_in.empty:
        
        if type(df_in.columns) == pd.MultiIndex:
            df_out = df_in[['search text']].copy()
        else:
            wanted_cols = list(df_in.columns)
            df_out = df_in[wanted_cols[wanted_cols.index('search text'):]].copy()
        df_out.dropna(axis = 'index', how = 'all', inplace = True)
        
        if regexin == 'text':
            df_used = df_out[('search text', regexin)].copy()
            search_text_words = [i[0] for i in df_used.values if str(i[0]) != 'nan']
            
            search_text_regex = '|'.join(search_text_words)
            search_text_regex = search_text_regex.replace('(', '\(').replace(')', '\)')
            search_text_regex = search_text_regex.replace('[', '\[').replace(']', '\]')
            search_text_regex = search_text_regex.replace(',', '\,').replace('.', '\.')
            search_text_regex = search_text_regex.replace('%', '\%').replace(':', '\:')
            search_text_regex = search_text_regex.replace('/', '\/')
            
            if search_regex:
                search_regex += f'|{search_text_regex}'
            else:
                search_regex += search_text_regex
                
        if regexin == 'values':
            df_used = df_out[('search text', regexin)].copy()
            search_values_numbers = '(-|−)?' + ''.join([str(i) for i in df_used['numbers'] if str(i) != 'nan'])
            search_values_connect = '|'.join([i for i in df_used['connect'] if str(i) != 'nan'])
            search_values_connect = search_values_connect.replace('+', '\+')#.replace('±', '\±')
            search_values_prefix = '|'.join([i for i in df_used['prefix'] if str(i) != 'nan'])
            search_values_units = '|'.join([i for i in df_used['units'] if str(i) != 'nan'])
            search_all_units = f'({search_values_prefix})?({search_values_units})' + \
                               f'(\s)?(GAE)?(/)?({search_values_prefix})?({search_values_units})?((-|−)1)?'
            
            search_values_regex1 = f'({search_values_numbers})(\s)?({search_values_connect})?(\s)?' + \
                                   f'({search_values_numbers})?(\s)?({search_all_units})'
            search_values_regex2 = f'({search_values_numbers})(\s)?({search_values_connect})(\s)?' + \
                                   f'({search_values_numbers})'
            search_values_regex = f'({search_values_regex1}|{search_values_regex2})'
            
            
            if search_regex:
                search_regex += f'|{search_values_regex}'
            else:
                search_regex += search_values_regex
            
    return(df_out, search_regex)

#================================================================================
#================================================================================
#================================================================================


def read_tables_functions(options_in = None,
                          paper_parts_in = None, 
                          doi_in = None,
                          product_name_in = None,
                          db_name_in = None,
                          file_version_in = None,
                          tables_out = False,
                          hide_webdriver_in = True,
                          highlight_regex_in = None,
                          html_dir_out = None):

    #---------------------------------------------
    if doi_in:
        doi_used = doi_in[doi_in.find('-') + 2:]
    else:
        doi_used = doi_in

    prefix_used = ''
    if 'm_' in doi_in[:2]:
        doi_index = int(doi_in[2:doi_in.find('-') - 1])
        prefix_used = 'm_'
    else:
        doi_index = int(doi_in[:doi_in.find('-') - 1])
    
    main_url = f"http://doi.org/{doi_used}"
    
    product_dir = f'./output_files/_{product_name_in}/'
    input_xlfiles_dir = product_dir + '01_read_xlfiles/'
    # input_xlfiles_dir = product_dir + 'input_xlfiles/'
    input_xlfile_name = f'{product_name_in}_v{file_version_in}_{db_name_in}_' + \
                        f'Paper_{prefix_used}%03d.xlsx'%(doi_index)


    if not options_in:
        options_in = webdriver.ChromeOptions()
        if hide_webdriver_in:
            options_in.add_argument('-headless')
        options_in.add_argument('--ignore-certificate-errors')
        options_in.add_argument('--incognito')

    table_soups = []
    tables_list = []
    
    #------------------------------------------------
    # Get soup of paper from the publisher's website
    #------------------------------------------------
    success_option = False

    print(color.BOLD, color.BLUE, 100*'-', color.END)
    print(f'{color.BOLD}{color.BLUE}  Starting try to read paper {prefix_used}{doi_index}!{color.END}\n')

    #---------------------------------------------
    driver = webdriver.Chrome(options = options_in)
    driver.get(main_url)
    time.sleep(3)

    #---------------------------------------------
    accept_xpath = '//a[text()="Accept"]'
    if driver.find_elements_by_xpath(accept_xpath):
        try:
            wait = WebDriverWait(driver, 10)
            wait.until(EC.element_to_be_clickable((By.XPATH, accept_xpath)))
            driver.find_element_by_xpath(accept_xpath).click()
        except:
            pass

    #---------------------------------------------
    accept2_xpath = '//button[text()="Accept Cookies"]'
    if driver.find_elements_by_xpath(accept2_xpath):
        try:
            wait = WebDriverWait(driver, 10)
            wait.until(EC.element_to_be_clickable((By.XPATH, accept2_xpath)))
            driver.find_element_by_xpath(accept2_xpath).click()
        except:
            pass

    #---------------------------------------------
    allow_xpath = '//a[class="optanon-allow-all"]'
    if driver.find_elements_by_xpath(allow_xpath):
        wait = WebDriverWait(driver, 10)
        wait.until(EC.element_to_be_clickable((By.XPATH, allow_xpath)))
        driver.find_element_by_xpath(allow_xpath).click()
    #---------------------------------------------
    view_xpath = '//a[text()="View Full-Text"]'
    if driver.find_elements_by_xpath(view_xpath):
        wait = WebDriverWait(driver, 10)
        wait.until(EC.element_to_be_clickable((By.XPATH, view_xpath)))
        driver.find_element_by_xpath(view_xpath).click()

    view2_xpath = '//a[text()="Full Text"]'
    if driver.find_elements_by_xpath(view2_xpath):
        wait = WebDriverWait(driver, 10)
        wait.until(EC.element_to_be_clickable((By.XPATH, view2_xpath)))
        driver.find_element_by_xpath(view2_xpath).click()


    time.sleep(2)    


    #-----------------------------------------------------------------
    #-----------------------------------------------------------------
    #-----------------------------------------------------------------

    soup_url = driver.current_url
    print(f'\t{color.BOLD}{color.BLUE}URL: {color.END}', soup_url, '\n')
    # if '.pdf' in soup_url:
    #     comment_output = 'pdf_file'

    #---------------------------------------------
    if 'oeno-one' in soup_url:
        expand_css = 'a[class*="tab-expand"]'
        tab_ex_els = driver.find_elements_by_css_selector(expand_css)
        if tab_ex_els:
            for itabex in range(len(tab_ex_els)):
                tab_ex_els[itabex].click()
                time.sleep(0.5)

    #---------------------------------------------
    soup_html = driver.execute_script('return document.documentElement.outerHTML')
    soup_paper = BeautifulSoup(soup_html, "html.parser")
    
    #---------------------------------------------
    publisher_list = [ikey for ikey in paper_parts_in.keys() if ikey in soup_url]
    if not publisher_list:
        publisher_list = ['general']
    paper_parts_temp = paper_parts_in[publisher_list[0]].fillna('')
    
    paper_parts_temp['temp_col'] = 'temp'
    paper_parts_new = \
    paper_parts_temp.groupby('temp_col', sort = False, as_index = False).agg(', '.join)
    paper_parts_new.drop(columns = 'temp_col', inplace = True)
    paper_parts_new.replace(regex = r'\, \, \, $', value = '', inplace = True)
    
    # if tables_out:
    #     success_option = True
    
    #---------------------------------------------
    #---------------------------------------------
    if highlight_regex_in and html_dir_out:
        title_temp = soup_paper.select(paper_parts_new['title'][0])
        abstract_temp = soup_paper.select(paper_parts_new['abstract'][0])
        main_paper_temp = soup_paper.select(paper_parts_new['body'][0])
        #
        paper_temp = title_temp + abstract_temp + main_paper_temp
        soup_temp = BeautifulSoup('\n\n'.join(str(part) for part in paper_temp), 'html.parser')
        #
        html_out = False

        for par in soup_temp.select(paper_parts_new['paragraph'][0]):
            # highlight_regex_in = '(((-|−)?\\d+(?:\\.\\d+)?)(\\s)?(-|–|—|\\+|\\±|to|and|or)?(\\s)?((-|−)?\\d+(?:\\.\\d+)?)?(\\s)?((m|μ|n|k)?(g|l|ppm|ppb|min)(\\s)?(GAE)?(/)?(m|μ|n|k)?(g|l|ppm|ppb|min)?((-|−)1)?)|((-|−)?\\d+(?:\\.\\d+)?)(\\s)?(-|–|—|\\+|\\±|to|and|or)(\\s)?((-|−)?\\d+(?:\\.\\d+)?))'
            if re.search(f'({highlight_regex_in})', par.text):
                html_out = True
                highlighted_text = \
                BeautifulSoup(re.sub(f'({highlight_regex_in})', 
                                     r'<mark>\1</mark>', 
                                     par.text, 
                                     flags = re.I), 
                              'html.parser')
                par.replace_with(highlighted_text)
        #
        if html_out:
            html_file_out = f'{html_dir_out}/' + \
                            f'{product_name_in}_v{file_version_in}_{db_name_in}_' + \
                            f'Paper_{prefix_used}%03d.html'%(doi_index)
            with open(html_file_out, 'w') as file:
                file.write(str(soup_temp))
    
    #---------------------------------------------
    #---------------------------------------------
    if tables_out:
        try:
            main_paper = soup_paper.select(paper_parts_new['body'][0])[0]
            #------------------------------
            if 'springer' in soup_url or 'nature' in soup_url:
                # close webdriver
                driver.close()
                # get the links for all the tables found
                hrefs_all = main_paper.find_all(href = True)
                tab_urls = [soup_url[:soup_url.find('/article')] + hr['href'] 
                            for hr in hrefs_all if '/table' in hr['href']]
                # print(tab_urls)
                # keep only unique links of tables
                tab_urls = list(np.unique(tab_urls))
                #-----
                # loop over links of tables to read info with BeautifulSoup
                if tab_urls:
                    print(f'\t{color.BOLD}{color.BLUE}Tables found!!!{color.END}')
                    for itab, tab_url in enumerate(tab_urls):
                        tab_driver = webdriver.Chrome(options = options_in)
                        tab_driver.get(tab_url)

                        time.sleep(3)

                        # get soup of table
                        try:
                            tab_html = tab_driver.execute_script('return document.documentElement.outerHTML')
                            tab_soup_temp = BeautifulSoup(tab_html, "html.parser")
                            tab_soup = tab_soup_temp.select(paper_parts_new['table'][0])[0]
                            table_soups.append(tab_soup)
                            tab_driver.close() # close table webdriver and continue to next one
                        except:
                            # close table webdriver and continue to next one
                            tab_driver.close()
                            continue

            #------------------------------
            elif 'hindawi' in soup_url:
                driver.close()
                # get the links for the tables found
                hrefs_all = main_paper.find_all(href = True)
                tab_urls = [soup_url + hr['href'] for hr in hrefs_all
                            if 'tab' in hr['href'] and len(hr['href']) <=6]
                # keep only unique links of tables
                tab_urls = list(np.unique(tab_urls))
                #-----
                # loop over links of tables to read info with BeautifulSoup
                if tab_urls:
                    print(f'\t{color.BOLD}{color.BLUE}Tables found!!!{color.END}')
                    for itab, tab_url in enumerate(tab_urls):
                        tab_driver = webdriver.Chrome(options = options_in)
                        tab_driver.get(tab_url)

                        time.sleep(3)

                        # get soup of table
                        tab_html = tab_driver.execute_script('return document.documentElement.outerHTML')
                        tab_soup_temp = BeautifulSoup(tab_html, "html.parser")
                        tab_soup = tab_soup_temp.select(paper_parts_new['table'][0])[0]
                        table_soups.append(tab_soup)

                        # close table webdriver and continue to next one
                        tab_driver.close()

            #------------------------------
            elif 'mdpi.com' in soup_url:
                # get all table elements from paper soup to click on
                tab_css = 'img[alt="Table"]'
                tab_els = driver.find_elements_by_css_selector(tab_css)
                #-----
                # loop over table elements to read info with BeautifulSoup
                if tab_els:
                    print(f'\t{color.BOLD}{color.BLUE}Tables found!!!{color.END}')
                    for itab in range(len(tab_els)):
                        # click on table element to read its info with BeautifulSoup
                        tab_els[itab].click()
                        time.sleep(1) 
                        tab_html = driver.execute_script('return document.documentElement.outerHTML')
                        tab_soup_temp = BeautifulSoup(tab_html, "html.parser")
                        tab_soup = tab_soup_temp.select(paper_parts_new['table'][0])[0]
                        table_soups.append(tab_soup)

                        # close table tab to continue to next element
                        close_tab = 'button[class*="mfp-close"]'
                        if driver.find_elements_by_css_selector(close_tab):
                            wait = WebDriverWait(driver, 10)
                            wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, close_tab)))
                            driver.find_element_by_css_selector(close_tab).click()
                            time.sleep(1)
                # close webdriver
                driver.close()

            #------------------------------
            elif 'tandfonline' in soup_url:

                tab_xpath = '//a[text()="Display Table"]'
                tab_els = driver.find_elements_by_xpath(tab_xpath)

                close_css = 'i[title="Close Table Viewer"]'

                #-----
                if tab_els:
                    print(f'\t{color.BOLD}{color.BLUE}Tables found!!!{color.END}')
                    for itab in range(len(tab_els)):
                        tab_els[itab].click()
                        time.sleep(1)

                        tab_html = driver.execute_script('return document.documentElement.outerHTML')
                        tab_soup_temp = BeautifulSoup(tab_html, "html.parser")
                        tab_soup = tab_soup_temp.select(paper_parts_new['table'][0])[0]

                        table_soups.append(tab_soup)

                        if driver.find_elements_by_css_selector(close_css):
                            wait = WebDriverWait(driver, 10)
                            wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, close_css)))
                            driver.find_element_by_css_selector(close_css).click()
                            time.sleep(1)
                driver.close()

            #------------------------------
            else:
                driver.close()
                table_soups = main_paper.select(paper_parts_new['table'][0])
                #-----
                if table_soups:
                    print(f'\t{color.BOLD}{color.BLUE}Tables found!!!{color.END}')


            #-----------------------------------------------------------------
            #-----------------------------------------------------------------
            #-----------------------------------------------------------------

            if table_soups:
                print()
                for itab, tab_soup in enumerate(table_soups):
                    try:
                        tab_dict = {}
                        tab_temp = pd.read_html(str(tab_soup))
                        tab_new = pd.DataFrame()
                        for tab in tab_temp:
                            if type(tab.columns) == pd.MultiIndex:
                                cols_new = [' - '.join(np.unique([j.replace('\xa0', ' ') 
                                                                    for j in i 
                                                                    if 'Unnamed' not in j])[::-1]) 
                                            for i in tab.columns]
                                tab.columns = cols_new
                            tab_new = pd.concat([tab_new, tab], axis = 0)
                        tab_dict['data'] = tab_new
                    except:
                        continue

                    try:
                        header_soup = tab_soup.select(paper_parts_new['table_header'][0])
                        header_text = [i.text.replace('\n', ' ').replace('\xa0', ' ')\
                                       .replace('\u2009', ' ').replace('            ', '').strip()
                                       for i in header_soup]
                        tab_dict['title'] = header_text[0]
                    except:
                        tab_dict['title'] = 'NO TITLE'

                    try:
                        footer_soup = tab_soup.select(paper_parts_new['table_footer'][0])
                        footer_text = [i.text.replace('\n', ' ').replace('\xa0', ' ')\
                                       .replace('\u2009', ' ').replace('            ', '').strip()
                                       for i in footer_soup]
                        tab_dict['footer'] = footer_text[0]
                    except:
                        tab_dict['footer'] = 'NO FOOTER'

                    tables_list.append(tab_dict)
            else:
                print(f'\t{color.BOLD}{color.RED}NO Tables found!!! ' + \
                      f'Make sure you have full access!!!{color.END}\n')
                
            extras = soup_paper.select('div[class="Extras"]')
            if extras:
                print(f'\t{color.BOLD}{color.RED}Extra files found in paper!!!{color.END}')
                # comment_output = 'extra_files'

            success_option = True

        except:
            driver.close()
            print(f'{color.BOLD}{color.RED}  Try Failed!!!{color.END}')
            # comment_output = 'retry'


        #============================================================

        if tables_list:

            for itab, table_used in enumerate(tables_list):

                #======
                tab_temp = df_remove_row_col_names_function(table_used, display_option = False)

                #======
                if tab_temp.size == 1:
                    continue

                #======
                if doi_used:
                    tab_temp.rename_axis(doi_used, axis = "index", inplace = True)

                results_df = tab_temp.copy()
                # display(results_df)

                #======
                # df_to_excel_function(f'{input_xlfiles_dir}/v{file_version_in}/{input_xlfile_name}', 
                #                      results_df, 
                #                      sheet_name_in = f'Table_{itab}')

                df_to_excel_function_new(io_in = f'{input_xlfiles_dir}/v{file_version_in}/{input_xlfile_name}', 
                                         sheetname_in = f'Table_{itab}',
                                         df_in = results_df)

            print(f'\t{color.BOLD}{color.RED}Tables exported successfully!!!{color.END}\n')
    
    else:
        driver.close()

    if success_option:
        print(f'{color.BOLD}{color.BLUE}  Try Successful!!!{color.END}\n')

    if len(table_soups) == 0 and '.pdf' in soup_url:
        comment_output = 'pdf_file'
    elif len(table_soups) > 0 and len(table_soups) == len(tables_list):
        comment_output = 'successful'
    else:
        comment_output = 'retry'
    if 'extras' in locals() and extras:
        comment_output = 'extra_files'
        
    #============================================================
    
    return(input_xlfile_name, doi_used, success_option, len(table_soups), len(tables_list), 
           soup_paper, comment_output)


#================================================================================
#================================================================================
#================================================================================

