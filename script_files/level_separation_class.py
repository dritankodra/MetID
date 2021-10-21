# import needed libraries
import os

import pandas as pd
import ipywidgets as ipyw

from my_module import color, create_dir_options, add_counts_function, df_to_excel_function_new

#================================================================================
#================================================================================
#================================================================================


class LevelSeparation:

    #–––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
    
    def __init__(self, dir_in = None):

        #-----
        # set main directories to be used in code
        self.dir_in = dir_in

        if self.dir_in:
            self.cur_dir_report = self.dir_in
            self.main_dir = self.dir_in
        else:
            self.main_dir = './'
            self.cur_dir_report = self.main_dir

        #-----
        self.dir_options = create_dir_options(self.cur_dir_report)
        
        self.df_new = pd.DataFrame()
        
        #-----
        self.manual_index = 0
    
        self.df_data = pd.DataFrame()
        self.filter_regex = ''
        
        self.dir_in = dir_in
        

    #–––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
    
    def create_widgets(self):

        #---------------
        # create list of files and directories to select
        self.w_sel_dir_option_tit = ipyw.Label(value='Select directory or file:')
        self.w_sel_dir_option = ipyw.Select(options=self.dir_options,
                                            value=None,
                                            layout={'width': '350px', 'height': '340px'},
                                            disabled=False)
        # create button to press to go to selected directory or file
        self.w_but_goto_dir = ipyw.Button(description='Go to selection!',
                                          icon='chevron-circle-right',
                                          tooptip='Go to the selected directory or file',
                                          button_style='primary',
                                          style=ipyw.ButtonStyle(button_color='#1d598a'),
                                          layout={'width': '150px', 'height': '30px'})
        # apply function to add round corners and larger font weight to button
        self.w_but_goto_dir.add_class('cwhite').add_class('brad5').add_class('fw')
        # apply function to go to selected directory or file
        self.w_but_goto_dir.on_click(self._on_select_change_dir)

        #----------
        # create list of columns of dataframe to select
        self.w_show_values = ipyw.Select(options=[],
                                         layout={'width': '250px', 'height': '340px'},
                                         disabled=False)
        
        
        #----------
        flist = create_dir_options('./input_files/')
        self.w_sel_filter_file = ipyw.SelectMultiple(options = flist,
                                                     layout = {'width': '300px', 'height': '150px'}, 
                                                     disabled = False)
        self.w_sel_filter_file.observe(self._on_select_show_columns, names = 'value')
    
    
        self.w_sel_filter_columns = ipyw.SelectMultiple(options = [None],
                                                        value = [None],
                                                        layout = {'width': '300px', 'height': '150px'}, 
                                                        disabled = False)
        
        # create button to press to go to selected directory or file
        self.w_but_filter_data = ipyw.Button(description = 'Filter data!',
                                             icon = 'filter',
                                             tooptip = 'Filter data according to selected value',
                                             button_style = 'primary',
                                             style = ipyw.ButtonStyle(button_color = '#9e2b4a'),
                                             layout = {'width': '148px', 'height': '30px'})
        # apply function to add round corners and larger font weight to button
        self.w_but_filter_data.add_class('cwhite').add_class('brad5').add_class('fw').add_class('fsmedium')
        # apply function to go to selected directory or load selected excel file
        self.w_but_filter_data.on_click(self._on_click_filter_data)
        
        # create button to press to go to selected directory or file
        self.w_but_save_data = ipyw.Button(description = 'Save data!',
                                           icon = 'save',
                                           tooptip = 'Update data according to selected value',
                                           button_style = 'primary',
                                           style = ipyw.ButtonStyle(button_color = '#36849e'),
                                           layout = {'width': '148px', 'height': '30px'})
        # apply function to add round corners and larger font weight to button
        self.w_but_save_data.add_class('cwhite').add_class('brad5').add_class('fw').add_class('fsmedium')
        # apply function to go to selected directory or load selected excel file
        self.w_but_save_data.on_click(self._on_click_save_data)
        

    #–––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
    
    def _on_select_change_dir(self, change):

        self.out.clear_output()

        with self.out:
            #-----
            desired_dir = self.w_sel_dir_option.value
            self.cur_sel_report = self.cur_dir_report + f"{desired_dir}"

            print(color.BOLD, color.BLUE, 'selected directory: ', color.RED, self.cur_sel_report, color.END)

            if os.path.isdir(self.cur_sel_report):
                if self.cur_sel_report[-1] == '/':
                    self.cur_dir_report = self.cur_sel_report
                else:
                    self.cur_dir_report = self.cur_sel_report + '/'

                self.w_sel_dir_option.options = ['../'] + \
                    sorted([i for i in os.listdir(self.cur_dir_report)
                            if os.path.isdir(os.path.join(self.cur_dir_report, i))]) + \
                    sorted([i for i in os.listdir(self.cur_dir_report)
                            if not os.path.isdir(os.path.join(self.cur_dir_report, i))
                            and 'DS' not in i and '.ipynb' not in i and '.py' not in i])
                self.w_sel_dir_option.value = None

            elif os.path.isfile(self.cur_sel_report) and '.csv' in self.cur_sel_report:
                try:
                    self.df_new = pd.read_csv(self.cur_sel_report, 
                                                  header = 0, 
                                                  index_col = False, dtype = str).fillna('')
                except:
                    self.df_new = pd.read_csv(self.cur_sel_report, sep = '\s+', 
                                                  header = 0, 
                                                  engine = 'python', index_col = False, dtype = str).fillna('')
                
                if self.df_new.empty:
                    print('No data loaded!!!')
                else:
                    display(self.df_new.head())
                    self.w_show_values.options = [icol for icol in self.df_new.columns][2:]
                    
                    
    #–––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
    
    def _on_select_show_columns(self, b):
        
        self.out.clear_output()
        
        with self.out:
            #-----
            if self.w_sel_filter_file.value:
                
                self.filter_df = pd.read_excel(self.dir_in + '/input_files/' + \
                                               self.w_sel_filter_file.value[0], 
                                               sheet_name = 'wanted')
                
                self.w_sel_filter_columns.options =  [i for i in self.filter_df.columns]

    
    #–––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––

    def _on_click_filter_data(self, b):
        '''
        Function to add data to list

        Parameters:
        - b = not sure what this parameter does...

        Returns:
        - none (adds DOI entered to the list)
        '''
        # clear widget output so far
        self.out.clear_output()
        
        with self.out:
            #-----
            self.df_all = self.df_new.copy()
            if not self.df_new.empty and self.w_sel_filter_columns.value:
                self.df_new.drop_duplicates(inplace = True)
                
                if isinstance(self.df_new.columns, pd.MultiIndex):
                    new_col_list = [iword[0][:-2] if iword[0][-2:]=='s?' else iword[0] 
                                    for iword in self.df_new.columns[2:]]
                elif isinstance(self.df_new.columns, pd.Index):
                    new_col_list = [iword[:-2] if iword[-2:]=='s?' else iword 
                                    for iword in self.df_new.columns[2:]]
                
                self.df_new.columns = ['paper', 'doi'] + new_col_list
                
                
                self.word_list = ['paper', 'doi']
                for icol in self.w_sel_filter_columns.value:
                    self.word_list += [iword for iword in self.filter_df[icol].values 
                                       if str(iword) != 'nan' and iword in self.df_new.columns
                                      ]
                
                self.count_words_out = {ikey: [iword for iword in self.filter_df[ikey] 
                                               if str(iword)!='nan' and iword in self.df_new.columns]
                                        for ikey in self.w_sel_filter_columns.value
                                       }

                #---------------
                for ikey, ival in self.count_words_out.items():
                    idf = pd.concat([self.df_new[['paper', 'doi']], self.df_new[ival]], axis = 1)
                    
                    idf2 = add_counts_function(idf)
                    
                    print(f'{color.BOLD}{color.RED}   {ikey}   {color.END}')
                    print(f'{color.BOLD}{color.RED}{idf2.shape[0] - 1} {color.BLUE}rows × ' + 
                          f'{color.RED}{idf2.shape[1]} {color.BLUE}columns{color.END}')
                    
                    display(idf2)
                    
                    self.count_words_out[ikey] += [idf2]
                
                
                #---------------
                # print(f'{color.BOLD}{color.BLUE}{100*"-"}{color.END}')
                # print(f'{color.BOLD}{color.RED}   INTERSECTION   {color.END}')
                # sets = map(set, [[j for j in i[-1].index if j!='col_count'] for i in self.count_words_out.values()])
                # ind_intersect = sorted(list(set.intersection(*sets)))
                # self.df_intersection = self.df_new.loc[ind_intersect]#, self.word_list]
                # self.df_intersection = pd.concat([self.df_intersection[['paper', 'doi']], 
                #                                   self.df_intersection[[i for i in \
                #                                                         self.df_intersection.columns[2:]]]], 
                #                                  axis = 1)
                # df_intersect = add_counts_function(self.df_intersection[self.word_list].copy())
                # print(f'{color.BOLD}{color.RED}{df_intersect.shape[0] - 1} {color.BLUE}rows × ' + 
                #       f'{color.RED}{df_intersect.shape[1]} {color.BLUE}columns{color.END}')
                # display(df_intersect)#[['paper', 'doi']])
                # self.count_words_out[f'{self.w_sel_filter_columns.value[0]} - intersection'] = [df_intersect]
                
                
                #---------------
                print(f'{color.BOLD}{color.BLUE}{100*"-"}{color.END}')
                print(f'{color.BOLD}{color.RED}   UNION   {color.END}')
                sets = map(set, [[j for j in i[-1].index if j!='col_count'] for i in self.count_words_out.values()])
                ind_union = sorted(list(set.union(*sets)))
                self.df_union = self.df_new.loc[ind_union]#, self.word_list]
                self.df_union = pd.concat([self.df_union[['paper', 'doi']], 
                                           self.df_union[[i for i in self.df_union.columns[2:]]]], 
                                          axis = 1)
                df_uni = add_counts_function(self.df_union[self.word_list].copy())
                print(f'{color.BOLD}{color.RED}{df_uni.shape[0] - 1} {color.BLUE}rows × ' + 
                      f'{color.RED}{df_uni.shape[1]} {color.BLUE}columns{color.END}')
                display(df_uni)
                self.count_words_out[f'{self.w_sel_filter_columns.value[0]} - union'] = [df_uni]
    
    
    #–––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
    
    def _on_click_save_data(self, b):
        '''
        Function to add data to list

        Parameters:
        - b = not sure what this parameter does...

        Returns:
        - none (adds DOI entered to the list)
        '''
        # clear widget output so far
        self.out.clear_output()
        
        with self.out:
            #-----
            fname_used = '_'.join(str(list(self.count_words_out.keys())[0]).split())
            
            if all([str(i).isnumeric()
                    for i in self.count_words_out[list(self.count_words_out.keys())[0]][-1].iloc[1:,2].values]):
                fname_used += '_counts.xlsx'
                countif_used = '">0"'
            else:
                fname_used += '_sentences.xlsx'
                countif_used = '"<>"'
                
                
            for ikey, ival in self.count_words_out.items():
                
                idf = ival[-1]
                
                print(f'{color.BOLD}{color.RED}   {ikey}   {color.END}')
                print(f'{color.BOLD}{color.RED}{idf.shape[0] - 1} {color.BLUE}rows × ' + 
                      f'{color.RED}{idf.shape[1]} {color.BLUE}columns{color.END}')
                
                display(idf)
                
                alphabet_letters = 26
                #
                idf.loc[[i for i in idf.index if 'col_count' not in str(i)], 'row_count'] = \
                [f"=COUNTIF(D{j}:" + \
                 f"{(idf.shape[1]//alphabet_letters)*chr(ord('@') + 1)}" + \
                 f"{chr(ord('@') + (idf.shape[1]%alphabet_letters))}{j}"  + \
                 f', {countif_used})'
                 for j in range(3, idf.shape[0] + 2)]
                #
                idf.loc['col_count', [i for i in idf.columns 
                                        if all([j not in str(i) for j in ['paper', 'doi']])]] = \
                [f"=COUNTIF({(j//alphabet_letters)*chr(ord('@') + 1)}" + \
                 f"{chr(ord('@') + (j%alphabet_letters))}3:" + \
                 f"{(j//alphabet_letters)*chr(ord('@') + 1)}" + \
                 f"{chr(ord('@') + (j%alphabet_letters))}{idf.shape[0] + 1}"  + \
                 f', {countif_used})'
                 for j in range(4, idf.shape[1] + 2)]
                
                
                df_to_excel_function_new(f'{self.cur_dir_report}{fname_used}', ikey, idf)
            
            self.out.clear_output()
            print(color.BOLD, color.BLUE, 'Data saved to file!', color.END)
    
    
    #–––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
    
    def display_widgets(self):

        self.create_widgets()

        self.out = ipyw.Output()
        self.out.clear_output()

        #-----------------------------------------------------------------

        tabs = ipyw.Tab(layout=ipyw.Layout(width='100%', height='450px'))
        t_children = []
        tabs.children = t_children

        empty_space = ipyw.Label(value='')

        #---------------
        gb000 = ipyw.GridBox([self.w_sel_dir_option_tit, self.w_but_goto_dir],
                             layout=ipyw.Layout(width='100%',
                                                grid_template_rows='auto',
                                                grid_template_columns='45% 15%',
                                                align_items='center',
                                                grid_gap='0px 0px'))
        b000 = ipyw.Box([self.w_sel_dir_option])

        gb00 = ipyw.GridBox([gb000, b000],
                            layout=ipyw.Layout(width='100%',
                                               grid_template_rows='auto auto',
                                               grid_template_columns='100%',
                                               align_items='center',
                                               grid_gap='10px 0px'))
        
        #---------------
        gb01 = ipyw.GridBox([empty_space, self.w_show_values],
                            layout = ipyw.Layout(width ='100%',
                                                 grid_template_rows = 'auto auto',
                                                 grid_template_columns = '100%',
                                                 align_items = 'flex-end',
                                                 grid_gap = '40px 0px'))
        
        
        
        #---------------
        gb020 = ipyw.GridBox([self.w_sel_filter_file],
                             layout = ipyw.Layout(width ='100%',
                                                  grid_template_rows = 'auto',
                                                  grid_template_columns = '90%',
                                                  align_items = 'center',
                                                  grid_gap = '0px 0px'))

    
        
        gb021 = ipyw.GridBox([self.w_sel_filter_columns],
                             layout = ipyw.Layout(width ='100%',
                                                  grid_template_rows = 'auto',
                                                  grid_template_columns = '90%',
                                                  align_items = 'center',
                                                  grid_gap = '0px 0px'))

    
        
        gb022 = ipyw.GridBox([self.w_but_filter_data, self.w_but_save_data],
                             layout = ipyw.Layout(width ='100%',
                                                  grid_template_rows = 'auto',
                                                  grid_template_columns = '49% 49%',
                                                  align_items = 'center',
                                                  grid_gap = '0px 0px'))
        
        gb023 = ipyw.GridBox([gb020, gb021, gb022],
                            layout = ipyw.Layout(width ='100%',
                                                 grid_template_rows = 'auto auto auto',
                                                 grid_template_columns = '90%',
                                                 align_items = 'flex-end',
                                                 grid_gap = '0px 0px'))
    
        gb02 = ipyw.GridBox([empty_space, gb023],
                            layout = ipyw.Layout(width ='100%',
                                                 grid_template_rows = 'auto auto',
                                                 grid_template_columns = '100%',
                                                 align_items = 'flex-end',
                                                 grid_gap = '40px 0px'))

        #-----
        gb0 = ipyw.GridBox([gb00, gb01, gb02],
                           layout=ipyw.Layout(width='100%',
                                              grid_template_rows='auto',
                                              grid_template_columns='32% 30% 36%',
                                              align_items='center',
                                              grid_gap='0px 0px'))

        title0 = 'Select keywords'
        t_children += [gb0]
        tabs.children = t_children
        tabs.set_title(len(t_children) - 1, title0)

        #---------------

        display(tabs)

        #-----------------------------------------------------------------

        display(self.out)


#================================================================================
#================================================================================
#================================================================================
