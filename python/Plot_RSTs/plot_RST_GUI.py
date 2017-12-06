from sys import version_info

import matplotlib
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
import matplotlib.pyplot as plt

from python.Plot_RSTs.Plot_RSTs import PlotRSTs
import python.Plot_RSTs.GUI_constants as const_GUI

matplotlib.use('TkAgg')

if version_info[0] < 3:
    import Tkinter as tk
    import tkFont
else:
    import tkinter as tk
    import tkinter.font as tkFont

class plot_RST_GUI:
    def __init__(self, master):
        # create a custom font
        self.customFont = tkFont.Font(family="Helvetica", size=const_GUI.default_font_size)

        self.master = master
        self.master.title(const_GUI.title)
        self.master.rowconfigure(1, weight=1)

        # Define the GUI frames
        self.frame_data_options = tk.Frame(self.master)
        self.frame_general_attributes = tk.Frame(self.master)
        self.frame_display_options = tk.Frame(self.master)
        self.frame_map = tk.Frame(self.master)
        self.frame_nav_toolbar = tk.Frame(self.master)

        # Define the GUI frame's layout
        self.frame_data_options.grid(row=0, column=0, sticky=tk.N, padx=5, pady=5)
        self.frame_general_attributes.grid(row=0, column=1, sticky=tk.N, padx=5, pady=5)
        self.frame_display_options.grid(row=0, column=2, sticky=tk.N, padx=5, pady=5)
        self.frame_map.grid(row=1, columnspan=4)
        self.frame_map.rowconfigure(0, weight=1)
        self.frame_nav_toolbar.grid(row=2, columnspan=2)

        # Define the data options widgets
        self.data_options_label = tk.Label(self.frame_data_options, text=const_GUI.data_options_label, font=self.customFont)
        # Choose NCEP or ERA Interim
        self.model_data_label = tk.Label(self.frame_data_options, text=const_GUI.model_data_label, font=self.customFont)
        self.model_data_list = const_GUI.models_list
        self.model_data_var = tk.StringVar()
        self.model_data_var.set(const_GUI.default_model_data)
        self.model_data_entry = tk.OptionMenu(self.frame_data_options, self.model_data_var, *self.model_data_list)
        self.model_data_entry.config(font=self.customFont)

        # Choose Geostrophic Vorticity or just Vorticity
        self.data_to_map_label = tk.Label(self.frame_data_options, text=const_GUI.data_to_map_label, font=self.customFont)
        self.data_to_map_list = const_GUI.data_to_map_list
        self.data_to_map_var = tk.StringVar()
        self.data_to_map_var.set(const_GUI.default_data_to_map)
        self.data_to_map_entry = tk.OptionMenu(self.frame_data_options, self.data_to_map_var, *self.data_to_map_list)
        self.data_to_map_entry.config(font=self.customFont)

        # 'Use interpolation'
        self.use_interpolation = tk.IntVar()
        self.use_interpolation.set(const_GUI.default_use_interpolation)
        self.checkbutton1_data_options = tk.Checkbutton(self.frame_data_options,
                                                        text=const_GUI.data_options_1,
                                                        variable=self.use_interpolation,
                                                        font=self.customFont)
        # 'Show troughs/ridges dots'
        self.show_dots = tk.IntVar()
        self.show_dots.set(const_GUI.default_show_dots)
        self.checkbutton2_data_options = tk.Checkbutton(self.frame_data_options,
                                                        text=const_GUI.data_options_2,
                                                        variable=self.show_dots,
                                                        font=self.customFont)
        # 'Show RST info'
        self.show_rst_info = tk.IntVar()
        self.show_rst_info.set(const_GUI.default_show_rst_info)
        self.checkbutton3_data_options = tk.Checkbutton(self.frame_data_options,
                                                        text=const_GUI.data_options_3,
                                                        variable=self.show_rst_info,
                                                        font=self.customFont)
        # 'Polyfit RST'
        self.polyfit_rst = tk.IntVar()
        self.polyfit_rst.set(const_GUI.default_polyfit_rst)
        self.checkbutton4_data_options = tk.Checkbutton(self.frame_data_options,
                                                        text=const_GUI.data_options_4,
                                                        variable=self.polyfit_rst,
                                                        font=self.customFont)

        # Define the data options widget's layout (1 = 'Use interpolation', 2 = 'Show vorticity', 3 = 'Show geostrophic vorticity',
        #                                          4 = 'Show troughs/ridges dots', 5 = 'Show RST info')
        self.data_options_label.grid(row=0, column=0, columnspan=2)
        self.model_data_label.grid(row=1, column=0, sticky=tk.W)
        self.model_data_entry.grid(row=2, column=0, sticky=tk.W)
        self.data_to_map_label.grid(row=3, column=0, sticky=tk.W)
        self.data_to_map_entry.grid(row=4, column=0, sticky=tk.W)
        self.checkbutton1_data_options.grid(row=1, column=1, sticky=tk.W)
        self.checkbutton2_data_options.grid(row=2, column=1, sticky=tk.W)
        self.checkbutton3_data_options.grid(row=3, column=1, sticky=tk.W)
        self.checkbutton4_data_options.grid(row=4, column=1, sticky=tk.W)

        # Define the general attributes widgets
        self.date_label = tk.Label(self.frame_general_attributes, text=const_GUI.date_label, font=self.customFont)
        self.year_label = tk.Label(self.frame_general_attributes, text=const_GUI.year_label, font=self.customFont)
        self.month_label = tk.Label(self.frame_general_attributes, text=const_GUI.month_label, font=self.customFont)
        self.day_label = tk.Label(self.frame_general_attributes, text=const_GUI.day_label, font=self.customFont)
        self.year_list = [str(x) for x in range(1979, 2017)]
        #self.year_list = ["1979", "1985", "1994"]
        self.year_var = tk.StringVar()
        self.year_var.set(const_GUI.default_year)
        self.year_entry = tk.OptionMenu(self.frame_general_attributes, self.year_var, *self.year_list)
        self.year_entry.config(font=self.customFont)
        # self.year_entry.configure(state="disabled")
        self.month_list = ["%02d" % x for x in range(1, 13)]
        self.month_var = tk.StringVar()
        self.month_var.set(const_GUI.default_month)
        self.month_entry = tk.OptionMenu(self.frame_general_attributes, self.month_var, *self.month_list)
        self.month_entry.config(font=self.customFont)
        self.day_list = ["%02d" % x for x in range(1, 32)]
        self.day_var = tk.StringVar()
        self.day_var.set(const_GUI.default_day)
        self.day_entry = tk.OptionMenu(self.frame_general_attributes, self.day_var, *self.day_list)
        self.day_entry.config(font=self.customFont)

        self.prev_day_button = tk.Button(self.frame_general_attributes,
                                         text=const_GUI.prev_day_button_text,
                                         command=self.show_prev_day,
                                         width=13,
                                         font=self.customFont)
        self.next_day_button = tk.Button(self.frame_general_attributes,
                                         text=const_GUI.next_day_button_text,
                                         command=self.show_next_day,
                                         width=13,
                                         font=self.customFont)


        self.files_path_label = tk.Label(self.frame_general_attributes, text=const_GUI.files_path_label, font=self.customFont)
        self.files_path_var = tk.StringVar()
        self.files_path_var.set(const_GUI.default_file_path)
        self.files_path_entry = tk.Entry(self.frame_general_attributes, textvariable=self.files_path_var, font=self.customFont)

        self.detached_map = tk.IntVar()
        self.detached_map.set(0)
        self.detached_map_checkbutton = tk.Checkbutton(self.frame_general_attributes,
                                                       variable=self.detached_map,
                                                       text=const_GUI.detached_map_checkbutton,
                                                       font=self.customFont)

        self.draw_button = tk.Button(self.frame_general_attributes,
                                     text=const_GUI.draw_button_text,
                                     command=self.draw_map,
                                     font=self.customFont)

        # Define the general attributes layout
        self.files_path_label.grid(row=0, column=3, padx=10)
        self.files_path_entry.grid(row=1, column=3, padx=10)

        self.date_label.grid(row=0, column=0, columnspan=3)
        self.year_label.grid(row=1, column=0)
        self.month_label.grid(row=1, column=1)
        self.day_label.grid(row=1, column=2)
        self.year_entry.grid(row=2, column=0)
        self.month_entry.grid(row=2, column=1)
        self.day_entry.grid(row=2, column=2)

        self.prev_day_button.grid(row=4,column=0)
        self.next_day_button.grid(row=4,column=2)

        self.detached_map_checkbutton.grid(row=3, column=3)

        self.draw_button.grid(row=5, column=3)

        # Define display options widgets
        # Buttons to adjust the font
        self.font_size_label = tk.Label(self.frame_display_options, text=const_GUI.font_size_label, font=self.customFont)
        self.smaller_font = tk.Button(self.frame_display_options,
                                      text="-",
                                      command=self.contract_font,
                                      width=3,
                                      font=self.customFont)
        self.default_font = tk.Button(self.frame_display_options,
                                     text="Default",
                                     command=self.make_default_font_size,
                                     font=self.customFont)
        self.bigger_font = tk.Button(self.frame_display_options,
                                     text="+",
                                     command=self.enlarge_font,
                                     width=3,
                                     font=self.customFont)

        self.choose_cb_label = tk.Label(self.frame_display_options, text=const_GUI.choose_cb_label, font=self.customFont)
        self.cb_list = const_GUI.cb_list
        self.cb_var = tk.StringVar()
        self.cb_var.set(const_GUI.default_cb)
        self.cb_menu = tk.OptionMenu(self.frame_display_options, self.cb_var, *self.cb_list)
        self.cb_menu.config(font=self.customFont)

        # Define the display options layout
        self.font_size_label.grid(row=0, column=0, columnspan=3)
        self.smaller_font.grid(row=1, column=0)
        self.default_font.grid(row=1, column=1)
        self.bigger_font.grid(row=1, column=2)

        self.choose_cb_label.grid(row=2, column=0, columnspan=3)
        self.cb_menu.grid(row=3, column=0, columnspan=3)

        # Initialize the plotRSTs objects according to the default year
        self.current_year = const_GUI.default_year
        self.plotRSTs_NCEP_instance = PlotRSTs('NCEP', self.current_year)
        self.plotRSTs_ERA_instance = PlotRSTs('ERA_Interim', self.current_year)
        self.plotRSTs_ERA_25_instance = PlotRSTs('ERA Int 2.5', self.current_year)

        root.mainloop()

    def show_prev_day(self):
        current_day = self.year_var.get() + "-" + self.month_var.get() + "-" + self.day_var.get() + " 12:00:00"
        # Get the previous datetime object date from the plotRSTS instance
        prev_date,_ = self.plotRSTs_NCEP_instance.get_next_and_prev_days(current_day)

        if prev_date:
            prev_day_year = str(prev_date)[0:4]
            prev_day_month = str(prev_date)[5:7]
            prev_day_day = str(prev_date)[8:10]
            self.year_var.set(prev_day_year)
            self.month_var.set(prev_day_month)
            self.day_var.set(prev_day_day)

            self.draw_map()

    def show_next_day(self):
        current_day = self.year_var.get() + "-" + self.month_var.get() + "-" + self.day_var.get() + " 12:00:00"
        # Get the next string date from the plotRSTS instance
        _, next_date = self.plotRSTs_NCEP_instance.get_next_and_prev_days(current_day)

        if next_date:
            next_day_year = str(next_date)[0:4]
            next_day_month = str(next_date)[5:7]
            next_day_day = str(next_date)[8:10]
            self.year_var.set(next_day_year)
            self.month_var.set(next_day_month)
            self.day_var.set(next_day_day)

            self.draw_map()

    def enlarge_font(self):
        '''Make the font 2 points bigger'''
        size = self.customFont['size']
        self.customFont.configure(size=size + 2)

    def contract_font(self):
        '''Make the font 2 points smaller'''
        size = self.customFont['size']
        self.customFont.configure(size=size - 2)

    def make_default_font_size(self):
        self.customFont.configure(size=const_GUI.default_font_size)

    def draw_map(self):
        if self.year_var.get() != self.current_year:
            # Replace the plotRSTs objects according to the current year
            self.current_year = self.year_var.get()
            self.plotRSTs_NCEP_instance = PlotRSTs('NCEP', self.current_year)
            self.plotRSTs_ERA_instance = PlotRSTs('ERA_Interim', self.current_year)
            self.plotRSTs_ERA_25_instance = PlotRSTs('ERA Int 2.5', self.current_year)

        # The first part is completely done by matplotlib, and then transferred to Tkinter
        current_day = self.year_var.get() + "-" + self.month_var.get() + "-" + self.day_var.get() + " 12:00:00"

        map_figure, map_axis = plt.subplots()
        map_figure.set_figheight(8)
        map_figure.set_figwidth(7)

        if self.model_data_var.get() == const_GUI.models_list[0]:
            # Plot the NCEP model data
            is_rst_condition_met = self.plotRSTs_NCEP_instance.calculate_maps_data(current_day,
                                                                                   use_interpolation=self.use_interpolation.get(),
                                                                                   data_to_map=self.data_to_map_var.get(),
                                                                                   show_dots=self.show_dots.get())
            rst_map = self.plotRSTs_NCEP_instance.create_map(map_axis,
                                                             show_rst_info=self.show_rst_info.get(),
                                                             req_colormap=self.cb_var.get(),
                                                             polyfit_rst=self.polyfit_rst.get())
        elif self.model_data_var.get() == const_GUI.models_list[1]:
            # Plot the ERA Interim model data
            is_rst_condition_met = self.plotRSTs_ERA_instance.calculate_maps_data(current_day,
                                                                                  use_interpolation=self.use_interpolation.get(),
                                                                                  data_to_map=self.data_to_map_var.get(),
                                                                                  show_dots=self.show_dots.get())
            rst_map = self.plotRSTs_ERA_instance.create_map(map_axis,
                                                            show_rst_info=self.show_rst_info.get(),
                                                            req_colormap=self.cb_var.get(),
                                                            polyfit_rst=self.polyfit_rst.get())
        elif self.model_data_var.get() == const_GUI.models_list[2]:
            # Plot the ERA Interim 2.5 degrees model data
            is_rst_condition_met = self.plotRSTs_ERA_25_instance.calculate_maps_data(current_day,
                                                                                  use_interpolation=self.use_interpolation.get(),
                                                                                  data_to_map=self.data_to_map_var.get(),
                                                                                  show_dots=self.show_dots.get())
            rst_map = self.plotRSTs_ERA_25_instance.create_map(map_axis,
                                                            show_rst_info=self.show_rst_info.get(),
                                                            req_colormap=self.cb_var.get(),
                                                            polyfit_rst=self.polyfit_rst.get())


        if self.detached_map.get() == 0:
            # The map is drawn inside the current GUI
            # Create the tk.DrawingArea
            canvas = FigureCanvasTkAgg(map_figure, master=self.frame_map)
            canvas.show()
            canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew")

            # Add the toolbar in a different frame and remove the x,y coords from appearing
            for child in self.frame_nav_toolbar.winfo_children():
                child.destroy()
            map_axis.format_coord = lambda x, y: ''
            toolbar = NavigationToolbar2TkAgg(canvas, self.frame_nav_toolbar)
            toolbar.update()
            # canvas._tkcanvas.grid(row=1, column=0)
        else:
            # The map is drawn in a seperate window
            main_seperate = tk.Tk()
            main_seperate.wm_title("Map")  # TODO change this

            # a tk.DrawingArea
            canvas = FigureCanvasTkAgg(map_figure, master=main_seperate)
            canvas.show()
            canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

            toolbar = NavigationToolbar2TkAgg(canvas, main_seperate)
            toolbar.update()
            canvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=1)


root = tk.Tk()
my_gui = plot_RST_GUI(root)
root.mainloop()
