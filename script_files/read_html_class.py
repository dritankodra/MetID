# import needed libraries
import os, re, csv, time

import pandas as pd
import ipywidgets as ipyw

from bs4 import BeautifulSoup

from my_module import color, create_dir_options, create_regex_function, read_soup_function


#================================================================================
#================================================================================
#================================================================================

class ReadHTML():
    
    #––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
    def __init__(self, 
                 doi_in = None,
                 db_name_in = None,
                ):
        #-------------------------
        if doi_in:
            
            #---------------
            if ' - ' in doi_in:
                self.doi = doi_in[doi_in.find(' - ') + 3:]
                #-----
                if 'm_' in doi_in[:2]:
                    self.doi_index = int(doi_in[2:doi_in.find(' - ')])
                    self.doi_prefix = 'm_'
                #-----
                else:
                    self.doi_index = int(doi_in[:doi_in.find(' - ')])
                    self.doi_prefix = ''
            
            #---------------
            else:
                self.doi = doi_in
                self.doi_index = 0
                self.doi_prefix = ''
                
                
            self.paper_name = ''
            self.product_name = ''
            self.file_version = ''
            self.db_name = ''
            
            #---------------
            if db_name_in:
                self.db_name = db_name_in
                self.paper_name += f'{db_name_in}_'
            self.paper_name += f'Paper_{self.doi_prefix}%03d'%(self.doi_index)
            
            #---------------
            self.success_out = False
            self.comment_out = ''
            self.tables_found = 0
            self.tables_retrieved = 0
            
        #-------------------------
        else:
            print('Please enter appropriate DOI of publication!!!')
            
            
    #––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
    def hl_count_html_function(self,
                               options_in = None,
                               hide_webdriver_in = False,
                               pp_dict_in = None,
                               pp_select_in = None,
                               search_regex_dict_in = None,
                               count_word_list_in = None,
                               count_option = False,
                               highlight_text_option = False,
                               highlight_values_option = False,
                              ):
        
        self.soup_url, self.soup_found, self.success_out = \
        read_soup_function(self.doi, 
                           web_options_in = options_in, 
                           hide_webdriver_in = hide_webdriver_in, 
                          )
    
        self.soup_body = None
        self.soup_html = None
        self.comment_out = ''
        self.dict_word_count = None
        self.s_wanted = []

        #-------------------------
        if self.success_out:

            if self.soup_found and pp_dict_in:
                
                
                if self.soup_url:
                    publisher_list = [ikey for ikey in pp_dict_in.keys() if ikey in self.soup_url]
                    if not publisher_list:
                        publisher_list = ['general']
                else:
                    publisher_list = ['general']
                #
                self.paper_parts_used = pd.DataFrame(pp_dict_in[publisher_list[0]]\
                                                     .apply(lambda x: ', '.join(x.dropna()), axis = 0)).T

                self.soup_body = self.soup_found.select(self.paper_parts_used['body'][0])
            
            
            if count_word_list_in:
                self.dict_word_count = {i: None for i in count_word_list_in}
            
            
            #----------
            # start procedure for word counting
            if self.soup_found:
                if pp_select_in:
                    if count_option or highlight_text_option or highlight_values_option:
                        for s_part in pp_select_in:
                            if len(self.soup_found.select(self.paper_parts_used[s_part][0])) > 0:
                                for i_soup in self.soup_found.select(self.paper_parts_used[s_part][0]):
                                    if i_soup not in self.s_wanted and not any([i_soup in i for i in self.s_wanted]) \
                                    and 'Availability of Data and Materials'.lower() not in str(i_soup).lower():
                                        self.s_wanted.append(i_soup)

                    else:
                        self.success_out = False
                        self.comment_out += 'no_count_no_highlight | '

                else:
                    self.success_out = False
                    self.comment_out += 'no_paper_parts_selected | '


                if self.s_wanted:

                    self.soup_wanted = BeautifulSoup('\n\n'.join(str(sc_part) for sc_part in self.s_wanted), 
                                                    'html.parser')

                    # count desired words
                    if count_word_list_in:
                        for word_used in count_word_list_in:
                            count = len(re.findall(r'(?i)\b(%s)\b'%word_used, str(self.soup_wanted.text), 
                                                   re.IGNORECASE))
                            self.dict_word_count[f'{word_used}'] = count


                    # highlight desired words
                    if search_regex_dict_in and highlight_text_option:
                        
                        #-----
                        if 'values' in search_regex_dict_in.keys():
                            highlight_unwanted = search_regex_dict_in['values']
                            for par in self.soup_wanted.select(self.paper_parts_used['paragraph'][0]):
                                if highlight_unwanted and re.search(f'({highlight_unwanted})', par.text):
                                    highlighted_text = \
                                    BeautifulSoup(re.sub(r'(?<!-|–|—|/)\b(%s)\b'%highlight_unwanted, 
                                                         r"<mark style='background-color:green;color:white'>" + \
                                                         r"<b>\1</b></mark>", 
                                              str(par), flags = re.I), 
                                              'html.parser')
                                    par.replace_with(highlighted_text)

                        #-----
                        if 'unwanted' in search_regex_dict_in.keys():
                            highlight_unwanted = search_regex_dict_in['unwanted']
                            for par in self.soup_wanted.select(self.paper_parts_used['paragraph'][0]):
                                if highlight_unwanted and re.search(f'({highlight_unwanted})', par.text):
                                    highlighted_text = \
                                    BeautifulSoup(re.sub(r'(?<!-|–|—|/)\b(%s)\b'%highlight_unwanted, 
                                                         r"<mark style='background-color:red;color:white'>" + \
                                                         r"<b>\1</b></mark>", 
                                              str(par), flags = re.I), 
                                              'html.parser')
                                    par.replace_with(highlighted_text)

                        #-----
                        if 'wanted' in search_regex_dict_in.keys():
                            highlight_wanted = search_regex_dict_in['wanted']
                            for par in self.soup_wanted.select(self.paper_parts_used['paragraph'][0]):
                                if re.search(f'({highlight_wanted})', par.text):
                                    highlighted_text = \
                                    BeautifulSoup(re.sub(r'(?<!-|–|—|/)\b(%s)\b'%highlight_wanted, 
                                                         r"<mark style='background-color:blue;color:white'>" + \
                                                         r"<b>\1</b></mark>", 
                                              str(par), flags = re.I), 
                                              'html.parser')
                                    par.replace_with(highlighted_text)

                    #----------
                    self.soup_html = BeautifulSoup('\n\n'.join(str(html_part) 
                                                               for html_part in self.soup_wanted), 
                                                   'html.parser')

            else:
                self.success_out = False
                self.comment_out += 'no_soup_found | '
            
    
    #––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
    def read_tables_function(self,
                             tables_out_option = False,
                            ):
        
        self.table_list_initial = []
        self.table_list_final = []
        
        #-------------------------
        if tables_out_option and self.success_out:
            
            #--------------------
            try:
                if self.soup_body:
                    main_paper = self.soup_body[0]
                elif self.soup_found:
                    main_paper = self.soup_found
                
                #---------------
                if any([i in self.soup_url for i in ['springer', 'nature', 'hindawi']]):
                    # get the links for all the tables found
                    hrefs_all = main_paper.find_all(href = True)
                    
                    if 'hindawi' in self.soup_url:
                        tab_urls = [self.soup_url + hr['href'] for hr in hrefs_all
                                        if 'tab' in hr['href'] and len(hr['href']) <=6]
                    else:
                        tab_urls = [self.soup_url[:self.soup_url.find('/article')] + hr['href'] 
                                        for hr in hrefs_all if 'table' in hr['href']]
                    
                    # keep only unique links of tables
                    tab_urls = [i for i in list(np.unique(tab_urls)) if i.startswith(self.soup_url)]
                    
                    #-----
                    # loop over links of tables to read info with BeautifulSoup
                    if tab_urls:
                        print(f'\t{color.BOLD}{color.BLUE}Tables found!!!{color.END}')
                        for itab, tab_url in enumerate(tab_urls):
                            tab_driver = webdriver.Chrome(options = self.webdriver_options)
                            tab_driver.get(tab_url)

                            time.sleep(3)

                            # get soup of table
                            try:
                                tab_html = tab_driver.execute_script('return document.documentElement.outerHTML')
                                tab_soup_temp = BeautifulSoup(tab_html, "html.parser")
                                tab_soup = tab_soup_temp.select(self.paper_parts_used['table'][0])[0]
                                # print('So far so good!')
                                self.table_list_initial.append(tab_soup)
                                tab_driver.close() # close table webdriver and continue to next one
                            except:
                                print('Table read failed! Continue to next one!')
                                # close table webdriver and continue to next one
                                tab_driver.close()
                                continue

                #---------------
                elif 'mdpi.com' in self.soup_url:
                    # get all table elements from paper soup to click on
                    tab_css = 'img[alt="Table"]'
                    tab_els = self.driver.find_elements_by_css_selector(tab_css)
                    #-----
                    # loop over table elements to read info with BeautifulSoup
                    if tab_els:
                        print(f'\t{color.BOLD}{color.BLUE}Tables found!!!{color.END}')
                        for itab in range(len(tab_els)):
                            # click on table element to read its info with BeautifulSoup
                            tab_els[itab].click()
                            time.sleep(1) 
                            
                            tab_html = self.driver.execute_script('return document.documentElement.outerHTML')
                            tab_soup_temp = BeautifulSoup(tab_html, "html.parser")
                            tab_soup = tab_soup_temp.select(self.paper_parts_used['table'][0])[0]
                            self.table_list_initial.append(tab_soup)

                            # close table tab to continue to next element
                            close_tab = 'button[class*="mfp-close"]'
                            if self.driver.find_elements_by_css_selector(close_tab):
                                wait = WebDriverWait(self.driver, 10)
                                wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, close_tab)))
                                self.driver.find_element_by_css_selector(close_tab).click()
                                time.sleep(1)
                    
                    self.driver.close()

                #---------------
                elif 'tandfonline' in self.soup_url:

                    tab_xpath = '//a[text()="Display Table"]'
                    tab_els = self.driver.find_elements_by_xpath(tab_xpath)
                    
                    #-----
                    if tab_els:
                        print(f'\t{color.BOLD}{color.BLUE}Tables found!!!{color.END}')
                        for itab in range(len(tab_els)):
                            tab_els[itab].click()
                            time.sleep(1)

                            tab_html = self.driver.execute_script('return document.documentElement.outerHTML')
                            tab_soup_temp = BeautifulSoup(tab_html, "html.parser")
                            tab_soup = tab_soup_temp.select(self.paper_parts_used['table'][0])[0]

                            self.table_list_initial.append(tab_soup)
                            
                            close_css = 'i[title="Close Table Viewer"]'
                            if self.driver.find_elements_by_css_selector(close_css):
                                wait = WebDriverWait(self.driver, 10)
                                wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, close_css)))
                                self.driver.find_element_by_css_selector(close_css).click()
                                time.sleep(1)
                    
                    self.driver.close()

                #---------------
                else:
                    self.comment_out += 'SO FAR SO GOOD3!!! | '
                    self.table_list_initial = main_paper.select(self.paper_parts_used['table'][0])
                    #-----
                    if self.table_list_initial:
                        print(f'\t{color.BOLD}{color.BLUE}Tables found!!!{color.END}')
                        
                        self.tables_found = len(self.table_list_initial)

                    
                #---------------
                if self.table_list_initial:
                    print()
                    for itab, tab_soup in enumerate(self.table_list_initial):
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
                            print(f'\t{color.BOLD}{color.RED}Table not read properly from html! ' + \
                                  f'Continue to next!{color.END}')
                            self.comment_out += 'table_not_read_properly | '
                            continue

                        try:
                            header_soup = tab_soup.select(self.paper_parts_used['table_header'][0])
                            header_text = [i.text.replace('\n', ' ').replace('\xa0', ' ')\
                                           .replace('\u2009', ' ').replace('            ', '').strip()
                                           for i in header_soup]
                            tab_dict['title'] = header_text[0]
                        except:
                            tab_dict['title'] = 'NO TITLE'

                        try:
                            footer_soup = tab_soup.select(self.paper_parts_used['table_footer'][0])
                            footer_text = [i.text.replace('\n', ' ').replace('\xa0', ' ')\
                                           .replace('\u2009', ' ').replace('            ', '').strip()
                                           for i in footer_soup]
                            tab_dict['footer'] = footer_text[0]
                        except:
                            tab_dict['footer'] = 'NO FOOTER'

                        self.table_list_final.append(tab_dict)
                        
                    self.tables_retrieved = len(self.table_list_final)
                    
                    self.comment_out += 'tables_read | '
                
                #---------------
                else:
                    print(f'\t{color.BOLD}{color.RED}NO Tables found!!! ' + \
                          f'Make sure you have full access!!!{color.END}\n')
                    self.comment_out += 'no_tables_found | '

                extras = self.soup_found.select('div[class="Extras"]')
                if extras:
                    print(f'\t{color.BOLD}{color.RED}Extra files found in paper!!!{color.END}')
                    
                    self.comment_out += 'extra_files | '

            #--------------------
            except:
                print(f'\t{color.BOLD}{color.RED}Table read failed!!! ' + \
                      f'Please make sure you have full access and try again!{color.END}')
                
                self.success_out = False
                self.comment_out += 'no_tables_read | '

        #-------------------------
        else:
            print(f'\t{color.BOLD}{color.RED}No tables were found!!!{color.END}')
            
            self.comment_out += 'no_tables_found | '
#


#================================================================================
#================================================================================
#================================================================================

class ExtractInfo():
    #
    #––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
    def __init__(self, dir_in = None, 
                 hide_webdriver_in = True, comment_in = False, search_text_regex_in = None):
        
        #-----
        if dir_in:
            self.main_dir = dir_in
        else:
            self.main_dir = './'
        
        #-----
        self.main_dir_rec = self.main_dir
        self.cur_dir_rec = self.main_dir_rec
        
        self.dir_options = create_dir_options(self.cur_dir_rec)
        
        #-----
        self.doi_list_checked = []
        self.doi_list_old = []
        self.doi_list = []
        self.doi_list_manual = []
        
        #-----
        self.df_dict_used = {}
        
        self.header_list = list(range(1,11))
        self.header = 1
        
        #-----
        self.hide_webdriver = hide_webdriver_in
        self.comment_out = comment_in
        
        #-----
        self.regex_options_list = []
        self.search_regex_dict = None
        
        self.count_word_list = None
        
        self.html_options_list = []
        
        self.pparts_options_list = ['title', 'abstract', 'body', 'introduction', 
                                    'experiment', 'methods', 'materials', 'results', 
                                    'discussion', 'conclusions', 'references']
        
        self.report_header = ['file_name', 'doi', 'success', 
                              'tables_found', 'tables_retrieved', 'comments']
        
        self.ignore_comments_list = ['pdf_file', 'not_found', 'no_access', 
                                     'no_tables', 'image_tables', 
                                     'foreign', 'new_publisher', 
                                     'exported_html']
        
    
    #––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
    def create_widgets(self):

        #--------------------
        self.w_sel_dir_option_tit = ipyw.Label(value = 'Select directory or file:', 
                                          layout = {'width': '140px'})
        self.w_sel_dir_option = ipyw.SelectMultiple(options = self.dir_options,
                                               value = ['../'],
                                               layout = {'width': '300px', 'height': '270px'},
                                               disabled = False)
        # create button to press to go to selected directory or file
        self.w_but_goto_dir = ipyw.Button(description = 'Go to selection!',
                                     icon = 'chevron-circle-right',
                                     tooptip = 'Go to the selected directory or file',
                                     button_style = 'primary',
                                     style = ipyw.ButtonStyle(button_color = '#1d598a'),
                                     layout = {'width': '160px', 'height': '30px'})
        # apply function to add round corners and larger font weight to button
        self.w_but_goto_dir.add_class('cwhite').add_class('brad5').add_class('fw')
        # apply function to go to selected directory or load selected excel file
        self.w_but_goto_dir.on_click(self._on_click_change_dir)
        
        #----------
        self.w_sel_dois_tit = ipyw.Label(value = 'Select DOIs of papers to read:', 
                                    layout = {'visibility': 'hidden'})
        self.w_sel_dois = ipyw.SelectMultiple(options = [None],
                                         value = [None],
                                         layout = {'width': '350px', 'height': '270px'}, 
                                         disabled = False)
        
        #--------------------
        self.w_sel_highlight = ipyw.Checkbox(value = False, 
                                        description = 'Highlight and/or Count',
                                        layout = {'width': '170px', 'visibility': 'hidden'},
                                        disabled = False,
                                        indent = False)
        self.w_sel_highlight.observe(self._on_select_change_regex_dir_options, names = 'value')
        
        #----------
        self.w_sel_regex_dir_option_tit = ipyw.Label(value = 'Select directory or file:',
                                                layout = {'visibility': 'hidden'})
        # create button to press to go to selected directory or file
        self.w_but_goto_regex_dir = ipyw.Button(description = 'Go to selection!',
                                           icon = 'chevron-circle-right',
                                           tooptip = 'Go to the selected directory or file',
                                           button_style = 'primary',
                                           style = ipyw.ButtonStyle(button_color = '#1d598a'),
                                           layout = {'width': '200px', 'height': '30px', 
                                                     'visibility': 'hidden'})
        # apply function to add round corners and larger font weight to button
        self.w_but_goto_regex_dir.add_class('cwhite').add_class('brad5').add_class('fw')
        # apply function to go to selected directory or load selected excel file
        self.w_but_goto_regex_dir.on_click(self._on_select_change_regex_dir)       
        
        self.w_sel_regex_dir_option = ipyw.Select(options = self.regex_options_list,
                                             value = None,
                                             layout = {'width': '350px', 'height': '250px', 
                                                       'visibility': 'hidden'},
                                             disabled = False)
        
        #----------
        self.w_sel_highlight_values = ipyw.Checkbox(value = False, 
                                               description = 'Highlight values!',
                                               layout = {'width': '150px', 'visibility': 'hidden'},
                                               disabled = False,
                                               indent = False)
        self.w_sel_highlight_values.observe(self._on_select_change_regex, names = 'value')
        self.w_sel_highlight_values.observe(self._on_select_change_html_dir_options, names = 'value')
        
        self.w_sel_highlight_text = ipyw.Checkbox(value = False, 
                                             description = 'Highlight text!',
                                             layout = {'width': '150px', 'visibility': 'hidden'},
                                             disabled = False,
                                             indent = False)
        self.w_sel_highlight_text.observe(self._on_select_change_regex, names = 'value')
        self.w_sel_highlight_text.observe(self._on_select_change_html_dir_options, names = 'value')
        
        self.w_sel_count_text = ipyw.Checkbox(value = False, 
                                             description = 'Count text!',
                                             layout = {'width': '150px', 'visibility': 'hidden'},
                                             disabled = False,
                                             indent = False)
        self.w_sel_count_text.observe(self._on_select_change_regex, names = 'value')
        
        #----------
        self.w_sel_export_html = ipyw.Checkbox(value = False, 
                                        description = 'Export HTML',
                                        layout = {'width': '100px', 'visibility': 'hidden'},
                                        disabled = False,
                                        indent = False)
        self.w_sel_export_html.observe(self._on_select_change_html_dir_options, names = 'value')
        
        self.w_sel_html_dir_options_tit = ipyw.Label(value = 'Select directory for html files:',
                                               layout = {'visibility': 'hidden'})
        # create button to press to go to selected directory or file
        self.w_but_goto_html_dir = ipyw.Button(description = 'Go to selection!',
                                          icon = 'chevron-circle-right',
                                          tooptip = 'Go to the selected directory or file',
                                          button_style = 'primary',
                                          style = ipyw.ButtonStyle(button_color = '#1d598a'),
                                          layout = {'width': '150px', 'height': '30px', 
                                                    'visibility': 'hidden'})
        # apply function to add round corners and larger font weight to button
        self.w_but_goto_html_dir.add_class('cwhite').add_class('brad5').add_class('fw')
        # apply function to go to selected directory
        self.w_but_goto_html_dir.on_click(self._on_select_change_html_dir)       
        
        self.w_sel_html_dir_options = ipyw.Select(options = self.html_options_list,
                                            value = None,
                                            layout = {'width': '330px', 'height': '250px', 
                                                      'visibility': 'hidden'},
                                            disabled = False)

        #--------------------
        self.w_sel_pparts_options_tit = ipyw.Label(value = 'Select paper parts for highlights/counts:',
                                               layout = {'visibility': 'visible'})
        
        self.w_sel_pparts_options = ipyw.SelectMultiple(options = self.pparts_options_list,
                                            layout = {'width': '280px', 'height': '260px',  
                                                      'visibility': 'visible'},
                                            disabled = False)


        self.w_sel_webdriver = ipyw.Checkbox(value = False, 
                                        description = 'Hide webdriver!',
                                        layout = {'width': '150px', 'visibility': 'visible'},
                                        disabled = False,
                                        indent = False)
        self.w_but_load_dois = ipyw.Button(description = 'Load DOIs!',
                                      icon = 'spinner',
                                      button_style = 'primary',
                                      style = ipyw.ButtonStyle(button_color = '#0d5f7a'),
                                      layout = {'width': '140px', 'height': '40px', 
                                                'visibility': 'visible'})
        # apply function to add round corners and larger font weight to button
        self.w_but_load_dois.add_class('cwhite').add_class('brad5').add_class('fw').add_class('fsmedium')
        # apply function to go to selected directory or load selected doi file
        self.w_but_load_dois.on_click(self._on_click_load_dois)
        
    
    #––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
    def _on_click_change_dir(self, change):

        self.out.clear_output()

        with self.out:
            #---------------
            desired_dir_rec = self.w_sel_dir_option.value[0]
            self.cur_sel_rec = self.cur_dir_rec + f"{desired_dir_rec}"
            
            print(color.BOLD, color.BLUE, 'selected directory: ', 
                  color.RED, self.cur_sel_rec, color.END, '\n')

            #---------------
            if os.path.isdir(self.cur_sel_rec):
                self.w_sel_highlight.layout.visibility = 'hidden'
                self.w_sel_export_html.layout.visibility = 'hidden'
                self.w_sel_webdriver.layout.visibility = 'hidden'
                self.w_but_load_dois.layout.visibility = 'hidden'
                
                self.cur_dir_rec = self.cur_sel_rec + '/'
                self.cur_dir_rec = self.cur_dir_rec.replace('//', '/')
                
                self.w_sel_dir_option.options = create_dir_options(self.cur_dir_rec)
                self.w_sel_dir_option.value = ['../']
            
            #---------------
            elif any([i in self.cur_sel_rec for i in ['savedrecs', 'scopus', 'pubmed']]):
                self.w_sel_highlight.layout.visibility = 'visible'
                self.w_sel_export_html.layout.visibility = 'visible'
                self.w_sel_webdriver.layout.visibility = 'visible'
                self.w_but_load_dois.layout.visibility = 'visible'
                
                #-----
                fname_list = desired_dir_rec.split('_')
                version = [i for i in fname_list if 'v' == i[0]]
                if version:
                    self.version_name = version[0][1:]
                    self.product_name = '_'.join(fname_list[:fname_list.index(version[0])])
                else:
                    self.version_name = ''
                    self.product_name = ''

                #----------
                self.record_file_selected = self.w_sel_dir_option.value[0]
                #-----
                if 'savedrecs' in self.record_file_selected:
                    self.db_name = 'wos'
                    if '.txt' in self.record_file_selected:
                        df_results = pd.read_csv(self.cur_sel_rec, sep = '\t', 
                                                 index_col = False).fillna('None')
                    elif '.xls' in self.record_file_selected:
                        df_results = pd.read_excel(self.cur_sel_rec, index_col = None).fillna('None')
                #-----
                elif 'scopus' in self.record_file_selected:
                    self.db_name = 'scopus'
                    df_results = pd.read_csv(self.cur_sel_rec, sep = ',', index_col = False).fillna('None')
                
                #-----
                elif 'pubmed' in self.record_file_selected:
                    self.db_name = 'pubmed'
                    df_results = pd.read_csv(self.cur_sel_rec, sep = ',', index_col = False).fillna('None')
                
                #-----
                self.df_results = df_results.rename(columns = {'DI':'DOI', 'TI':'Title', 'AB':'Abstract'})
                
                self.doi_list_initial = [(doi.Index, doi.DOI) for doi in self.df_results.itertuples() 
                                                              if doi.DOI != 'None']
                self.doi_list = [(doi.Index, doi.DOI) for doi in self.df_results.itertuples() 
                                                      if doi.DOI != 'None']
                #----------
                if self.doi_list_manual:
                    self.w_sel_dois.options = \
                    ['None', 'All'] + [f'm_{idoi} - {doi}' for idoi, doi in enumerate(self.doi_list_manual)]
                    if self.doi_list:
                        self.w_sel_dois.options += tuple(f'{idoi} - {doi}' for idoi, doi in self.doi_list)
                else:
                    self.w_sel_dois.options = ['None', 'All'] + \
                    [f'{idoi} - {doi}' for idoi, doi in self.doi_list]
                
                self.w_sel_dois.value = ['None']
                print(f'{color.BOLD}{color.BLUE}Total number of DOIs to check: ' + 
                      f'{color.RED}{len(self.w_sel_dois.options) - 2}{color.END}\n')
                
            #---------------
            elif 'report.csv' in self.cur_sel_rec:
                self.w_sel_report_file.layout.visibility = 'visible'
                self.w_sel_highlight.layout.visibility = 'visible'
                self.w_sel_dois.layout.visibility = 'visible'
                self.w_sel_webdriver.layout.visibility = 'visible'
                self.w_but_load_dois.layout.visibility = 'visible'
                
                self.product_name = \
                self.cur_sel_rec[self.cur_sel_rec.rfind('/')+1:self.cur_sel_rec.find('_automatic')]
                
                self.df_reports = pd.DataFrame()
                
                for idir in self.w_sel_dir_option.value:
                    idf = pd.read_csv(self.cur_dir_rec + idir, sep = ',', index_col = False).fillna('None')
                    self.df_reports = pd.concat([self.df_reports, idf], axis = 0, sort = False).fillna('')
                
                self.w_sel_report_file.options = sorted(list(set([iname[iname.find('_v')+1:iname.find('_Paper')] 
                                                              for iname in self.df_reports['xlfile_name']])))
                
                self.w_sel_report_file.value = None
                                
                
    #––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
    def _on_select_change_regex_dir_options(self, change):
        '''
            Function to change options of directories/files with regex/words to highlight/count
        '''
        self.out.clear_output()
        
        with self.out:
            #-----
            self.cur_dir_regex = self.main_dir
            
            if self.w_sel_highlight.value:
                self.w_sel_regex_dir_option_tit.layout.visibility = 'visible'
                self.w_but_goto_regex_dir.layout.visibility = 'visible'
                self.w_sel_regex_dir_option.layout.visibility = 'visible'
                
                self.regex_options_list = create_dir_options(self.cur_dir_regex)
                
            else:
                self.w_sel_regex_dir_option_tit.layout.visibility = 'hidden'
                self.w_but_goto_regex_dir.layout.visibility = 'hidden'
                self.w_sel_regex_dir_option.layout.visibility = 'hidden'
                
                self.w_sel_highlight_values.layout.visibility = 'hidden'
                self.w_sel_highlight_text.layout.visibility = 'hidden'
                self.w_sel_count_text.layout.visibility = 'hidden'
                
                self.w_sel_html_dir_options_tit.layout.visibility = 'hidden'
                self.w_but_goto_html_dir.layout.visibility = 'hidden'
                self.w_sel_html_dir_options.layout.visibility = 'hidden'
                
                self.regex_options_list = []
            
            #-----
            self.w_sel_regex_dir_option.options = self.regex_options_list
            self.w_sel_regex_dir_option.value = None
            
    
    #––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
    def _on_select_change_regex_dir(self, change):
        '''
            Function to change directory/select input file with regex/words to highlight/count
        '''
        self.out.clear_output()

        with self.out:
            #-----
            selected_dir = self.w_sel_regex_dir_option.value
            self.cur_sel_regex = self.cur_dir_regex + f"/{selected_dir}"
            print(color.BOLD, color.BLUE, 'selected directory: ', 
                  color.RED, self.cur_sel_regex, color.END, '\n')
                
            if os.path.isdir(self.cur_sel_regex):
                self.w_sel_highlight_values.layout.visibility = 'hidden'
                self.w_sel_highlight_text.layout.visibility = 'hidden'
                self.w_sel_count_text.layout.visibility = 'hidden'
                
                self.w_sel_pparts_options_tit.layout.visibility = 'hidden'
                self.w_sel_pparts_options.layout.visibility = 'hidden'
                
                self.w_sel_html_dir_options_tit.layout.visibility = 'hidden'
                self.w_but_goto_html_dir.layout.visibility = 'hidden'
                self.w_sel_html_dir_options.layout.visibility = 'hidden'
                
                self.cur_dir_regex += f"/{selected_dir}"
                
                regex_options_list = create_dir_options(self.cur_dir_regex)
                
                self.w_sel_regex_dir_option.options = regex_options_list
                self.w_sel_regex_dir_option.value = None
            
            elif '.xls' in (self.cur_sel_regex):
                self.w_sel_highlight_values.layout.visibility = 'visible'
                self.w_sel_highlight_text.layout.visibility = 'visible'
                self.w_sel_count_text.layout.visibility = 'visible'
                
                self.w_sel_pparts_options_tit.layout.visibility = 'visible'
                self.w_sel_pparts_options.layout.visibility = 'visible'

                self.w_sel_html_dir_options_tit.layout.visibility = 'visible'
                self.w_but_goto_html_dir.layout.visibility = 'visible'
                self.w_sel_html_dir_options.layout.visibility = 'visible'

                self.df_dict = pd.read_excel(self.cur_sel_regex, sheet_name = None, index_col = None,
                                            header = [i for i in range(self.header)])
                
                self.search_regex_dict, self.count_word_list = create_regex_function(self.df_dict)
    
                print(f'{color.BOLD}{color.RED}search text:{color.END}  ', self.search_regex_dict['wanted'], '\n')
                print(f'{color.BOLD}{color.RED}count word list:{color.END}', self.count_word_list)
            
                display(self.df_dict['wanted'])
                
                self.cur_dir_regex = self.main_dir
            
            
    #––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
    def _on_select_change_regex(self, change):
        '''
            Function to change header of dataframe with regex/words to highlight/count
        '''
        self.out.clear_output()
        
        with self.out:
            #-----
            self.search_regex_dict, self.count_word_list = \
                create_regex_function(self.df_dict, 
                                       highlight_values_option = self.w_sel_highlight_values.value,
                                       highlight_text_option = self.w_sel_highlight_text.value,
                                       count_text_option = self.w_sel_count_text.value,
                                      )
            
            print(f'{color.BOLD}{color.RED}Select directory for html files! \n\n' + 
                  f'search text:{color.END}  ', self.search_regex_dict['wanted'], '\n')
            print(f'{color.BOLD}{color.RED}count word list:{color.END}', self.count_word_list)
            display(self.df_dict['wanted'])
            
                
    #––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
    def _on_select_change_html_dir_options(self, change):
        
        self.out.clear_output()
        
        with self.out:
            #-----
            
            self.cur_dir_html = f'{self.main_dir}output_files/'
            
            if self.w_sel_highlight_text.value or self.w_sel_highlight_values.value \
            or self.w_sel_export_html.value:
                self.w_sel_html_dir_options_tit.layout.visibility = 'visible'
                self.w_but_goto_html_dir.layout.visibility = 'visible'
                self.w_sel_html_dir_options.layout.visibility = 'visible'
                
                self.w_sel_html_dir_options.options = create_dir_options(self.cur_dir_html)
                
            else:
                self.w_sel_html_dir_options_tit.layout.visibility = 'hidden'
                self.w_but_goto_html_dir.layout.visibility = 'hidden'
                self.w_sel_html_dir_options.layout.visibility = 'hidden'
                
                self.w_sel_html_dir_options.options = []
            
            #-----
            self.w_sel_html_dir_options.value = None
            
            try:
                print(f'{color.BOLD}{color.RED}Select directory for html files! \n\n' + 
                      f'search text:{color.END}  ', self.search_regex_dict['wanted'], '\n')
                print(f'{color.BOLD}{color.RED}count word list:{color.END}', self.count_word_list)
                display(self.df_dict['wanted'])
            except:
                print(f'{color.BOLD}{color.RED}Select directory for html files!{color.END}')
            
    
    #––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
    def _on_select_change_html_dir(self, change):

        self.out.clear_output()

        with self.out:
            #-----
            selected_dir = self.w_sel_html_dir_options.value
            self.cur_sel_html = f'{self.cur_dir_html}/{selected_dir}'
            print(color.BOLD, color.BLUE, 'selected directory: ', color.RED, self.cur_sel_html, color.END, '\n')
                
            if os.path.isdir(self.cur_sel_html):
                self.cur_dir_html += f"/{selected_dir}"
                
                html_options_list = create_dir_options(self.cur_dir_html)
                
                self.w_sel_html_dir_options.options = html_options_list
                self.w_sel_html_dir_options.value = None
                
            #-----
            try:
                print(f'{color.BOLD}{color.RED}Select directory for html files! \n\n' + 
                      f'search text:{color.END}  ', self.search_regex_dict['wanted'], '\n')
                print(f'{color.BOLD}{color.RED}count word list:{color.END}', self.count_word_list)
                display(self.df_dict['wanted'])
            except:
                print(f'{color.BOLD}{color.RED}Select directory for html files!{color.END}')
            
            
    #––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
    def _on_click_load_dois(self, change):

        self.out.clear_output()

        with self.out:
            #-----
            try:
                desired_dois = []
                if 'All' in [*self.w_sel_dois.value]:
                    desired_dois = [f'{idoi} - {doi}' for idoi, doi in self.doi_list]
                elif 'None' in [*self.w_sel_dois.value]:
                    print(color.BOLD, color.RED, 
                          "You didn't select any DOIs! Please select one now!", 
                          color.END)
                else:
                    desired_dois = [*self.w_sel_dois.value]
                    
            except:
                pass
            
            #-----
            if desired_dois:
                self.pp_dict = pd.read_excel(self.main_dir + '/input_files/paper_parts_css.xlsx', 
                                             sheet_name = None)
                
                #-----
                for doi in desired_dois:
                                
                    self.read_doi = ReadHTML(doi_in = doi, db_name_in = self.db_name)
            
                    #-----
                    if self.w_sel_highlight_text.value or self.w_sel_highlight_values.value \
                    or self.w_sel_count_text.value or self.w_sel_export_html.value:
                
                        self.read_doi.hl_count_html_function(hide_webdriver_in = \
                                                             self.w_sel_webdriver.value,
                                                             pp_dict_in = self.pp_dict,
                                                             pp_select_in = \
                                                             list(self.w_sel_pparts_options.value),
                                                             count_word_list_in = self.count_word_list,
                                                             search_regex_dict_in = self.search_regex_dict,
                                                             count_option = self.w_sel_count_text.value,
                                                             highlight_text_option = \
                                                             self.w_sel_highlight_text.value,
                                                             highlight_values_option = \
                                                             self.w_sel_highlight_values.value,
                                                            )
                        
                        #-----
                        # export highlighted text to html file
                        if self.w_sel_highlight_text.value or self.w_sel_highlight_values.value \
                        or self.w_sel_export_html.value:
                            html_file_out = f'{self.cur_dir_html}/{self.read_doi.paper_name}.html'
                            with open(html_file_out, 'w') as file:
                                file.write(str(self.read_doi.soup_html))
                        
                        #-----
                        # export word counts to csv file
                        if self.count_word_list and self.read_doi.dict_word_count:
                            count_dir_out = f'./output_files/'

                            if self.product_name:
                                count_file_out = f'{self.product_name}_'
                            else:
                                count_file_out = ''

                            cf_name_end = 'word_count_report.csv'
                            count_file_out += cf_name_end

                            if not any(fname == count_file_out for fname in os.listdir(count_dir_out)):
                                with open(count_dir_out + count_file_out, 'w', newline = '') as myfile:
                                    csv_writer = csv.writer(myfile)
                                    csv_writer.writerow(['paper', 'doi'] + \
                                                        list(self.read_doi.dict_word_count.keys()))
                                    csv_writer.writerow([self.read_doi.paper_name, self.read_doi.doi] + \
                                                        list(self.read_doi.dict_word_count.values()))
                            else:
                                with open(count_dir_out + count_file_out, 'a', newline = '') as myfile:
                                    csv_writer = csv.writer(myfile)
                                    csv_writer.writerow([self.read_doi.paper_name, self.read_doi.doi] + \
                                                        list(self.read_doi.dict_word_count.values()))
                            
                    #-----
                    
                    try:
                        self.read_doi.driver.close()
                    except:
                        pass
                        
                                
                    print(f'{color.BOLD}{color.BLUE}  Finished!!!{color.END}\n')
                        

    #––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
    def _on_click_add_comment(self, change):
        
        self.out.clear_output()
        
        with self.out:
            #-----
            mylist2 = [self.read_doi.paper_name, self.read_doi.doi, self.read_doi.success_out, 
                       self.read_doi.tables_found, self.read_doi.tables_retrieved, self.read_doi.comment_out]
            
            report_dir_out = f'./output_files/'

            if self.product_name:
                report_file_out = f'{self.product_name}_'
            else:
                report_file_out = ''

            cf_name_end = 'manual_read_report.csv'
            report_file_out += cf_name_end
            
            #-----
            if not any(fname.endswith(report_file_out) for fname in os.listdir(report_dir_out)):
                with open(report_dir_out + report_file_out, 'w', newline = '') as myfile:
                    csv_writer = csv.writer(myfile)
                    
                    csv_writer.writerow(self.report_header)
                    csv_writer.writerow(mylist2)
            else:
                with open(report_dir_out + report_file_out, 'a', newline = '') as myfile:
                    csv_writer = csv.writer(myfile)
                    csv_writer.writerow(mylist2)
    
    
    #––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
    #––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
    #––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
    def display_widgets(self):

        self.create_widgets()

        self.out = ipyw.Output()
        self.out.clear_output()

        #-----------------------------------------------------------------
        
        tabs = ipyw.Tab(layout = ipyw.Layout(width = '100%', height = '380px'))
        t_children = []
        tabs.children = t_children
        
        empty_space = ipyw.Label(value = '')
        empty_space2 = ipyw.Label(value = '\n\n')
        
        #--------------------
        gb000 = ipyw.GridBox([self.w_sel_dir_option_tit, self.w_but_goto_dir],
                      layout = ipyw.Layout(width ='100%',
                                      grid_template_rows = 'auto',
                                      grid_template_columns = '44% 30%',
                                      align_items = 'center',
                                      grid_gap = '0px 0px'))
        b000 = ipyw.Box([self.w_sel_dir_option])
        #-----
        gb00 = ipyw.GridBox([gb000, b000],
                      layout = ipyw.Layout(width ='100%',
                                      grid_template_rows = 'auto auto',
                                      grid_template_columns = '100%',
                                      align_items = 'flex-end',
                                      grid_gap = '0px 0px'))
        
        #----------
        gb01 = ipyw.GridBox([empty_space, self.w_sel_dois],
                      layout = ipyw.Layout(width ='100%',
                                      grid_template_rows = 'auto auto',
                                      grid_template_columns = '90%',
                                      align_items = 'flex-end',
                                      grid_gap = '30px 0px'))
        
        
        #----------
        gb0 = ipyw.GridBox([gb00, gb01],
                      layout = ipyw.Layout(width ='100%',
                                      grid_template_rows = 'auto',
                                      grid_template_columns = '33% 37% 25%',
                                      align_items = 'center',
                                      grid_gap = '0px 20px'))
        #-----
        title0 = 'Make your selections!'
        t_children += [gb0]
        tabs.children = t_children
        tabs.set_title(len(t_children) - 1, title0)
        
        #--------------------
        gb200 = ipyw.GridBox([empty_space, self.w_sel_highlight],
                        layout = ipyw.Layout(width ='100%',
                                        grid_template_rows = 'auto',
                                        grid_template_columns = '20% 50%',
                                        align_items = 'center',
                                        grid_gap = '0px 0px'))
        
        hb200 = ipyw.HBox([self.w_sel_regex_dir_option_tit, self.w_but_goto_regex_dir],
                     layout = ipyw.Layout(width = '100%',
                                     align_items = 'center'))
        
        b200 = ipyw.Box([self.w_sel_regex_dir_option])
        
        gb20 = ipyw.GridBox([gb200, hb200, b200],
                       layout = ipyw.Layout(width ='100%',
                                       grid_template_rows = 'auto auto',
                                       grid_template_columns = '100%',
                                       align_items = 'center',
                                       grid_gap = 'px 0px'))
        #-----
        vb212 = ipyw.VBox([self.w_sel_highlight_values, 
                      self.w_sel_highlight_text, self.w_sel_count_text],
                     layout = ipyw.Layout(width ='100%', align_items = 'center'))
        
        gb21 = ipyw.GridBox([vb212],
                       layout = ipyw.Layout(width ='100%',
                                       grid_template_rows = 'auto auto',
                                       grid_template_columns = '100%',
                                       align_items = 'center',
                                       grid_gap = '30px 0px'))
        
        #-----
        gb220 = ipyw.GridBox([empty_space, self.w_sel_export_html],
                        layout = ipyw.Layout(width ='100%',
                                        grid_template_rows = 'auto',
                                        grid_template_columns = '20% 60%',
                                        align_items = 'center',
                                        grid_gap = '0px 0px'))
        
        hb220 = ipyw.HBox([self.w_sel_html_dir_options_tit, self.w_but_goto_html_dir],
                     layout = ipyw.Layout(width = '100%',
                                     align_items = 'center'))
        
        b220 = ipyw.Box([self.w_sel_html_dir_options])
        
        gb22 = ipyw.GridBox([gb220, hb220, b220],
                       layout = ipyw.Layout(width ='100%',
                                       grid_template_rows = 'auto auto',
                                       grid_template_columns = '100%',
                                       align_items = 'center',
                                       grid_gap = 'px 0px'))
        

        gb2 = ipyw.GridBox([gb20, gb21, gb22],
                      layout = ipyw.Layout(width ='100%',
                                      grid_template_rows = 'auto',
                                      grid_template_columns = '40% 20% 40%',
                                      align_items = 'center',
                                      grid_gap = '0px 0px'))
        
        #-----
        title2 = 'Highlight text!'
        t_children += [gb2]
        tabs.children = t_children
        tabs.set_title(len(t_children) - 1, title2)
        
        #--------------------
        gb30 = ipyw.GridBox([empty_space, self.w_sel_dois],
                      layout = ipyw.Layout(width ='100%',
                                      grid_template_rows = 'auto auto',
                                      grid_template_columns = '100%',
                                      align_items = 'center',
                                      grid_gap = '20px 0px'))
        #-----

        vb310 = ipyw.VBox([self.w_sel_pparts_options_tit, self.w_sel_pparts_options],
                     layout = ipyw.Layout(width ='100%', align_items = 'center'))
        
        vb311 = ipyw.VBox([self.w_sel_webdriver, self.w_but_load_dois],
                     layout = ipyw.Layout(width ='100%'))
        
        #-----

        gb3 = ipyw.GridBox([gb30, vb310, vb311],
                      layout = ipyw.Layout(width ='100%',
                                      grid_template_rows = 'auto',
                                      grid_template_columns = '38% 35% 27%',
                                      align_items = 'flex-end',
                                      grid_gap = '0px 0px'))
        
        #-----
        title3 = 'Find & Read DOIs!'
        t_children += [gb3]
        tabs.children = t_children
        tabs.set_title(len(t_children) - 1, title3)
        
        #--------------------
        
        display(tabs)
        
        #––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
        display(self.out)


#================================================================================
#================================================================================
#================================================================================
