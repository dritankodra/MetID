# import needed libraries
import os

import pandas as pd
import ipywidgets as ipyw

from my_module import color, wait_for_downloads, search_wos

#================================================================================
#================================================================================
#================================================================================


class FindLiterature:

    #---------------------------------------------------------------------------
    def __init__(self, dir_in=None):

        #-----
        # set main directories to be used in code
        self.dir_in = dir_in
        self.download_dir = '/Users/drk36/Downloads/'

        if self.dir_in:
            self.cur_dir_kw = self.dir_in
            self.main_dir = self.dir_in
        else:
            self.main_dir = './'
            self.cur_dir_kw = self.main_dir

        #-----
        # create list of directories and files in the "main directory"
        # which will be displayed in the first selection box
        # it contains sorted list of directories as well as sorted list of files included in "current directory"
        # (leaving out all python notebook or python script files)
        self.dir_options = ['../'] + \
            sorted([i for i in os.listdir(self.cur_dir_kw)
                    if os.path.isdir(os.path.join(self.cur_dir_kw, i))]) + \
            sorted([i for i in os.listdir(self.cur_dir_kw)
                    if not os.path.isdir(os.path.join(self.cur_dir_kw, i))
                    and 'DS' not in i and '.ipynb' not in i and '.py' not in i])

        # create list of dataframes to be read from excel file
        self.df_list = []
        self.df_name = None

        # create list of options for number of rows to be used as header of dataframe
        # default option set as 1
        self.df_header_list = list(range(1, 11))
        self.df_header = 1

        # set default option of database used for search in WOS!
        # default set as None for All Databases
        # meaning WOS Core Databases is used
        self.all_db = None

        #-----
        # create list of record files to be combined if and when needed
        # self.rec_file_list = []
        # self.rec_file = None

    #---------------------------------------------------------------------------
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
        # create list of sheets from excel file to select
        self.w_sel_df_tit = ipyw.Label(value='Select sheet:')
        self.w_sel_df = ipyw.Dropdown(options=self.df_list,
                                      value=self.df_name,
                                      layout={'width': '180px'},
                                      disabled=False)
        # apply function to select existing dataframe from selected sheet
        self.w_sel_df.observe(self._on_change_select_df, names='value')
        #-----
        # create list of number of rows to select as header for dataframe
        self.w_sel_header_tit = ipyw.Label(value='Select header rows:')
        self.w_sel_header = ipyw.Dropdown(options=self.df_header_list,
                                          value=self.df_header,
                                          layout={'width': '130px'},
                                          disabled=False)
        # apply function to set new header to dataframe
        self.w_sel_header.observe(self._on_change_select_new_df, names='value')
        #-----
        # create list of columns of dataframe to select
        self.w_sel_cols = ipyw.Select(options=[],
                                      layout={'width': '350px', 'height': '320px'},
                                      disabled=False)
        #-----
        # create list of topic field name to use in search performed
        # ALL = All fields (i.e. including Institutions, Authors, etc.)
        self.w_sel_field_tit = ipyw.Label(value='Select search field:')
        self.w_sel_field = ipyw.Dropdown(options=['TS', 'ALL'],
                                         value=None,
                                         layout={'width': '118px'})

        # create list of options to join strings in rows of same column
        self.w_sel_rjoin_options_tit = ipyw.Label(value='Select row join type:')
        self.w_sel_rjoin_options = ipyw.Dropdown(options=['OR', 'AND'],
                                                 value=None,
                                                 layout={'width': '110px'})

        # create list of options to join columns together
        self.w_sel_cjoin_options_tit = ipyw.Label(value='Select join type:')
        self.w_sel_cjoin_options = ipyw.Dropdown(options=['START', 'AND', 'OR', 'NOT', 'RESET'],
                                                 value=None,
                                                 layout={'width': '135px'})
        # apply function to change the search string with each new column selected
        self.w_sel_cjoin_options.observe(self._on_select_change_string, names='value')

        #---------------
        # create list of databases to use for search on WOS
        # WOS Core Database (default option) or All Databases
        self.w_sel_dbtype_tit = ipyw.Label(value='Select db type:')
        self.w_sel_dbtype = ipyw.Dropdown(options=['WOS Core Database', 'All Databases'],
                                          value='WOS Core Database',
                                          layout={'width': '140px'},
                                          disabled=False)

        # create input for start year of search
        # (in Scopus you only select one year that interest you)
        self.w_ent_start_year = ipyw.Textarea(placeholder='Start date (e.g. 1999-12-31)',
                                              layout={'width': '113px', 'height': '50px'},
                                              disabled=False)
        # create input for end year of search
        self.w_ent_end_year = ipyw.Textarea(placeholder='End date (e.g. 1999-12-31)',
                                            layout={'width': '113px', 'height': '50px'},
                                            disabled=False)
        #-----
        # create list of filters for results based on their accessibility
        # (i.e. Open Acess, Highly Cited, etc.)
        self.w_sel_filter_options_tit = ipyw.Label(value='Filter results by:')
        self.w_sel_filter_options = ipyw.Dropdown(options=['All', 'Highly Cited Papers', 'Review Articles',
                                                           'Early Access', 'Open Access'],
                                                  value='All',
                                                  layout={'width': '133px', 'height': '30px'})

        # create list of filters for results based on the type of document
        # (i.e. Article, Review, etc.)
        self.w_sel_doctype_options_tit = ipyw.Label(value='Document type:')
        self.w_sel_doctype_options = ipyw.Dropdown(options=['All', 'Articles', 'Book Chapters', 'Data Papers'],
                                                   value='All',
                                                   layout={'width': '133px', 'height': '30px'})
        #-----
        # create input for number of records to be exported to file(s) from WOS
        # (Scopus doesn't need this)
        self.w_ent_save_recs = ipyw.Textarea(placeholder='Save records (1 = 1-1000, 2 = 1001-2000)',
                                             layout={'width': '230px', 'height': '30px'},
                                             disabled=False)
        #-----
        # create list of types for output files with records to be saved
        self.w_sel_fout_type_tit = ipyw.Label(value='Select output file type:')
        self.w_sel_fout_type = ipyw.Dropdown(options=['.csv', '.xls'],
                                             value='.csv',
                                             layout={'width': '95px'},
                                             disabled=False)
        #-----
        # create button to press and go to selected directory or file
        self.w_but_search_bib = ipyw.Button(description='Search for papers!',
                                            icon='search',
                                            tooptip='Search for papers with selections',
                                            button_style='primary',
                                            style=ipyw.ButtonStyle(button_color='#36849e'),
                                            layout={'width': '230px', 'height': '40px'})
        # apply function to add round corners and larger font weight to button
        self.w_but_search_bib.add_class('cwhite').add_class('brad5').add_class('fw').add_class('fsmedium')
        # apply function to perform search on WOS
        self.w_but_search_bib.on_click(self._on_click_search_bib)

    #---------------------------------------------------------------------------
    def _on_select_change_dir(self, change):

        self.out.clear_output()

        with self.out:
            #-----
            desired_dir = self.w_sel_dir_option.value
            self.cur_sel_kw = self.cur_dir_kw + f"{desired_dir}"

            print(color.BOLD, color.BLUE, 'selected directory: ', color.RED, self.cur_sel_kw, color.END)

            if os.path.isdir(self.cur_sel_kw):
                if self.cur_sel_kw[-1] == '/':
                    self.cur_dir_kw = self.cur_sel_kw
                else:
                    self.cur_dir_kw = self.cur_sel_kw + '/'

                self.w_sel_dir_option.options = ['../'] + \
                    sorted([i for i in os.listdir(self.cur_dir_kw)
                            if os.path.isdir(os.path.join(self.cur_dir_kw, i))]) + \
                    sorted([i for i in os.listdir(self.cur_dir_kw)
                            if not os.path.isdir(os.path.join(self.cur_dir_kw, i))
                            and 'DS' not in i and '.ipynb' not in i and '.py' not in i])
                self.w_sel_dir_option.value = None

            elif '.xls' in (self.cur_sel_kw):
                self.df_dict = pd.read_excel(self.cur_sel_kw, sheet_name=None, index_col=None,
                                             header=[i for i in range(self.df_header)])

                self.w_sel_df.options = [i for i in self.df_dict.keys()]

    #---------------------------------------------------------------------------
    def _on_change_select_df(self, change):

        self.out.clear_output()

        if change['type'] == 'change' and change['name'] == 'value':
            self.df_name = change['new']

        with self.out:
            #-----
            self.kw_df = self.df_dict[self.df_name]
            self.kw_df.dropna(axis=0, how='all', inplace=True)
            self.kw_df.dropna(axis=1, how='all', inplace=True)

            self.w_sel_cols.options = ['None', 'All'] + list(self.kw_df.columns)
            self.w_sel_cols.value = 'None'

            self.df_out = self.kw_df.copy()
            display(self.df_out)

            self.search_paper = ''

    #---------------------------------------------------------------------------
    def _on_change_select_new_df(self, change):

        self.out.clear_output()

        if change['type'] == 'change' and change['name'] == 'value':
            self.df_header = change['new']

        with self.out:
            #-----
            self.df_dict = pd.read_excel(self.cur_sel_kw, sheet_name=None, index_col=None,
                                         header=[i for i in range(self.df_header)])

            self.kw_df = self.df_dict[self.df_name]
            self.kw_df.dropna(axis=0, how='all', inplace=True)
            self.kw_df.dropna(axis=1, how='all', inplace=True)

            self.w_sel_cols.options = ['None', 'All'] + list(self.kw_df.columns)
            self.w_sel_cols.value = 'None'

            self.df_out = self.kw_df.copy()
            display(self.df_out)

    #---------------------------------------------------------------------------
    def _on_select_change_string(self, change):

        self.out.clear_output()

        with self.out:
            #----------
            if self.w_sel_field.value and self.w_sel_rjoin_options.value:
                # join the various options together
                # with each option enclosed by "" for literal search
                joint_string = f' {self.w_sel_rjoin_options.value} '.join([f'"{j}"'
                                                                           for j in
                                                                           [f'{i[0].lower()}' for i in self.df_out[[self.w_sel_cols.value]].values
                                                                            if str(i[0]) != 'nan']])
                #-----
                # start search string
                if self.w_sel_cjoin_options.value == 'START':
                    self.search_paper += f'{self.w_sel_field.value} = ({joint_string})'
                #-----
                # join or exclude next field
                elif self.w_sel_cjoin_options.value == 'AND' or self.w_sel_cjoin_options.value == 'NOT':
                    self.search_paper += \
                        f' {self.w_sel_cjoin_options.value} {self.w_sel_field.value} = ({joint_string})'
                # join next subfield
                elif self.w_sel_cjoin_options.value == 'OR':
                    self.search_paper = \
                        f'{self.search_paper[:-1]} {self.w_sel_cjoin_options.value} {joint_string})'
                #-----
                if self.w_sel_field.value == 'ALL':
                    self.search_paper = self.search_paper.replace('/', '')

            #----------
            # reset search string in case of error
            if self.w_sel_cjoin_options.value == 'RESET':
                self.search_paper = ''

            #----------
            # print final search string for visual inspection
            print(f'{color.BOLD}{color.RED}search paper:{color.END}  ', self.search_paper, '\n')

            # display dataframe containing all keywords
            display(self.df_out)

            # set all selections equal to blank for next use
            self.w_sel_field.value = None
            self.w_sel_rjoin_options.value = None
            self.w_sel_cjoin_options.value = None

    #---------------------------------------------------------------------------
    def _on_select_replace_string(self, change):

        self.out.clear_output()

        with self.out:
            #-----
            if self.w_sel_db.value == 'Web of Science' and self.w_sel_dbtype.value == 'All Databases':
                self.all_db = 'All Databases'
                self.search_paper = self.search_paper.replace('ALL', 'TS')
                print(f'{color.BOLD}{color.RED}"ALL" has been replaced by "TS"!!!{color.END}\n')
            else:
                self.all_db = None

            print(f'{color.BOLD}{color.RED}search paper:{color.END}  {self.search_paper} \n')

            # display dataframe containing all keywords
            display(self.df_out)

    #---------------------------------------------------------------------------
    def _on_click_search_bib(self, b):

        self.out.clear_output()

        with self.out:
            #----------
            if self.w_sel_dbtype.value == 'All Databases':
                all_db_used = 'All Databases'
                self.search_paper = self.search_paper.replace('ALL', 'TS')
                print(f'{color.BOLD}{color.RED}"ALL" has been replaced by "TS"!!!{color.END}\n')
            else:
                self.all_db = None
            #-----
            search_wos(search_string_in=self.search_paper,
                       all_db_in=self.all_db,
                       start_date_in=self.w_ent_start_year.value,
                       end_date_in=self.w_ent_end_year.value,
                       filter_in=self.w_sel_filter_options.value,
                       doctype_in=self.w_sel_doctype_options.value,
                       save_recs_in=self.w_ent_save_recs.value,
                       fout_type_in=self.w_sel_fout_type.value
                       )

            #----------
            print(f'{color.BOLD}{color.RED}search paper:{color.END}  {self.search_paper} \n')

    #---------------------------------------------------------------------------
    #---------------------------------------------------------------------------
    #---------------------------------------------------------------------------

    def display_widgets(self):

        self.create_widgets()

        self.out = ipyw.Output()
        self.out.clear_output()

        #-----------------------------------------------------------------

        tabs = ipyw.Tab(layout=ipyw.Layout(width='100%', height='450px'))
        t_children = []
        tabs.children = t_children

        empty_space = ipyw.Label(value='')

        #-----
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
        #-----
        vb010 = ipyw.VBox([self.w_sel_df_tit, self.w_sel_df],
                          layout=ipyw.Layout(width='100%',
                                             align_items='center'))
        vb011 = ipyw.VBox([self.w_sel_header_tit, self.w_sel_header],
                          layout=ipyw.Layout(width='100%',
                                             align_items='center'))
        gb01 = ipyw.GridBox([vb010, vb011],
                            layout=ipyw.Layout(width='100%',
                                               grid_template_rows='auto',
                                               grid_template_columns='55% 40%',
                                               align_items='center',
                                               grid_gap='0px 15px'))

        b01 = ipyw.Box([self.w_sel_cols], layout=ipyw.Layout(width='100%'))

        vb01 = ipyw.VBox([gb01, b01],
                         layout=ipyw.Layout(width='100%',
                                            align_items='center'))
        #-----
        hb020 = ipyw.HBox([self.w_sel_field_tit, self.w_sel_field],
                          layout=ipyw.Layout(width='100%',
                                             align_items='center'))
        hb021 = ipyw.HBox([self.w_sel_rjoin_options_tit, self.w_sel_rjoin_options],
                          layout=ipyw.Layout(width='100%',
                                             align_items='center'))
        hb022 = ipyw.HBox([self.w_sel_cjoin_options_tit, self.w_sel_cjoin_options],
                          layout=ipyw.Layout(width='100%',
                                             align_items='center'))

        gb02 = ipyw.GridBox([hb020, hb021, hb022],
                            layout=ipyw.Layout(width='100%',
                                               grid_template_rows='auto auto auto auto',
                                               grid_template_columns='100%',
                                               align_items='initial',
                                               grid_gap='0px 0px'))

        #-----
        hb100 = ipyw.HBox([self.w_sel_dbtype_tit, self.w_sel_dbtype],
                          layout=ipyw.Layout(width='100%',
                                             align_items='center'))
        hb101 = ipyw.HBox([self.w_ent_start_year, self.w_ent_end_year],
                          layout=ipyw.Layout(width='100%',
                                             align_items='center'))
        hb102 = ipyw.HBox([self.w_sel_filter_options_tit, self.w_sel_filter_options],
                          layout=ipyw.Layout(width='100%',
                                             align_items='center'))
        hb103 = ipyw.HBox([self.w_sel_doctype_options_tit, self.w_sel_doctype_options],
                          layout=ipyw.Layout(width='100%',
                                             align_items='center'))

        hb104 = ipyw.HBox([self.w_sel_fout_type_tit, self.w_sel_fout_type],
                          layout=ipyw.Layout(width='100%',
                                             align_items='center'))

        gb10 = ipyw.GridBox([hb100, hb101, hb102, hb103, hb104, self.w_ent_save_recs, self.w_but_search_bib],
                            layout=ipyw.Layout(width='100%',
                                               grid_template_rows='auto auto auto auto auto auto',
                                               grid_template_columns='100%',
                                               align_items='center',
                                               grid_gap='0px 0px'))

        #-----
        gb11 = ipyw.GridBox([gb02, gb10],
                            layout=ipyw.Layout(width='100%',
                                               grid_template_rows='auto auto',
                                               grid_template_columns='100%',
                                               align_items='center',
                                               grid_gap='10px 0px'))

        #-----
        gb0 = ipyw.GridBox([gb00, vb01, gb11],
                           layout=ipyw.Layout(width='100%',
                                              grid_template_rows='auto',
                                              grid_template_columns='32% 35% 25%',
                                              align_items='center',
                                              grid_gap='0px 20px'))

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
