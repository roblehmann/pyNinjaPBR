"""
"""
import os
import pprint
import random
import sys
import wx
import matplotlib
matplotlib.use('WXAgg')
from matplotlib.figure import Figure
from matplotlib.backends.backend_wxagg import \
    FigureCanvasWxAgg as FigCanvas, \
    NavigationToolbar2WxAgg as NavigationToolbar
import numpy as np
import pylab
import matplotlib.pyplot as plt
    
class BoundControlBox(wx.Panel):
    """ A static box with a couple of radio buttons and a text
        box. Allows to switch between an automatic mode and a 
        manual mode with an associated value.
    """
    def __init__(self, parent, ID, label, initval):
        wx.Panel.__init__(self, parent, ID)
        
        self.value = initval
        
        box = wx.StaticBox(self, -1, label)
        sizer = wx.StaticBoxSizer(box, wx.VERTICAL)
        
        self.radio_auto = wx.RadioButton(self, -1, 
            label="Auto", style=wx.RB_GROUP)
        self.radio_manual = wx.RadioButton(self, -1,
            label="Manual")
        self.manual_text = wx.TextCtrl(self, -1, 
            size=(35,-1),
            value=str(initval),
            style=wx.TE_PROCESS_ENTER)
        
        self.Bind(wx.EVT_UPDATE_UI, self.on_update_manual_text, self.manual_text)
        self.Bind(wx.EVT_TEXT_ENTER, self.on_text_enter, self.manual_text)
        
        manual_box = wx.BoxSizer(wx.HORIZONTAL)
        manual_box.Add(self.radio_manual, flag=wx.ALIGN_CENTER_VERTICAL)
        manual_box.Add(self.manual_text, flag=wx.ALIGN_CENTER_VERTICAL)
        
        sizer.Add(self.radio_auto, 0, wx.ALL, 10)
        sizer.Add(manual_box, 0, wx.ALL, 10)
        
        self.SetSizer(sizer)
        sizer.Fit(self)
    
    def on_update_manual_text(self, event):
        self.manual_text.Enable(self.radio_manual.GetValue())
    
    def on_text_enter(self, event):
        self.value = self.manual_text.GetValue()
    
    def is_auto(self):
        return self.radio_auto.GetValue()
        
    def manual_value(self):
        return self.value


class GraphFrame(wx.Frame):
    """ The Curve Plotter Frame of the Captor Interface
    """
    title = 'Captor OD Monitor'
    
    def __init__(self,parent, dataStore, variableToPlot=None):
        wx.Frame.__init__(self, parent, -1, self.title)
        self.parent     = parent
        self.dataStore    = dataStore
        if variableToPlot == None:
            if self.dataStore != None:
                variableToPlot = self.dataStore.data.keys()[0]
            else:
                variableToPlot = ''
        self.variableToPlot = variableToPlot # name of variable to plot, for access in DataStore
        self.create_menu()
        self.create_status_bar()
        self.create_main_panel()

    def create_menu(self):
        self.menubar = wx.MenuBar()
        
        menu_file = wx.Menu()
        m_expt = menu_file.Append(-1, "&Save plot\tCtrl-S", "Save plot to file")
        self.Bind(wx.EVT_MENU, self.on_save_plot, m_expt)
        menu_file.AppendSeparator()
        m_exit = menu_file.Append(-1, "E&xit\tCtrl-X", "Exit")
        self.Bind(wx.EVT_MENU, self.OnClose, m_exit)
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        self.menubar.Append(menu_file, "&File")
        self.SetMenuBar(self.menubar)

    def create_main_panel(self):
        self.panel = wx.Panel(self)

        self.init_plot()
        self.canvas = FigCanvas(self.panel, -1, self.fig)

        self.xmin_control = BoundControlBox(self.panel, -1, "X min", 0)
        self.xmax_control = BoundControlBox(self.panel, -1, "X max", 100)
        self.ymin_control = BoundControlBox(self.panel, -1, "Y min", 0)
        self.ymax_control = BoundControlBox(self.panel, -1, "Y max", 10)
        
        self.select_variable_button = wx.Button(self.panel, -1, "Select Variable")
        self.Bind(wx.EVT_BUTTON, self.on_select_var_button, self.select_variable_button)

        self.clear_button = wx.Button(self.panel, -1, "Clear")
        self.Bind(wx.EVT_BUTTON, self.on_clear_button, self.clear_button)
        
        self.redraw_button = wx.Button(self.panel, -1, "Redraw")
        self.Bind(wx.EVT_BUTTON, self.on_redraw_button, self.redraw_button)
        
        self.cb_grid = wx.CheckBox(self.panel, -1, 
            "Show Grid",
            style=wx.ALIGN_RIGHT)
        self.Bind(wx.EVT_CHECKBOX, self.on_cb_grid, self.cb_grid)
        self.cb_grid.SetValue(True)
        
        self.cb_xlab = wx.CheckBox(self.panel, -1, 
            "Show X labels",
            style=wx.ALIGN_RIGHT)
        self.Bind(wx.EVT_CHECKBOX, self.on_cb_xlab, self.cb_xlab)        
        self.cb_xlab.SetValue(True)
        
        self.hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        self.hbox1.Add(self.select_variable_button, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        self.hbox1.AddSpacer(20)
        self.hbox1.Add(self.redraw_button, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        self.hbox1.AddSpacer(10)
        self.hbox1.Add(self.clear_button, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        self.hbox1.AddSpacer(10)
        self.hbox1.Add(self.cb_grid, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        self.hbox1.AddSpacer(10)
        self.hbox1.Add(self.cb_xlab, border=5, flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        
        self.hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        self.hbox2.Add(self.xmin_control, border=5, flag=wx.ALL)
        self.hbox2.Add(self.xmax_control, border=5, flag=wx.ALL)
        self.hbox2.AddSpacer(24)
        self.hbox2.Add(self.ymin_control, border=5, flag=wx.ALL)
        self.hbox2.Add(self.ymax_control, border=5, flag=wx.ALL)
        
        self.vbox = wx.BoxSizer(wx.VERTICAL)
        self.vbox.Add(self.canvas, 1, flag=wx.LEFT | wx.TOP | wx.GROW)        
        self.vbox.Add(self.hbox1, 0, flag=wx.ALIGN_LEFT | wx.TOP)
        self.vbox.Add(self.hbox2, 0, flag=wx.ALIGN_LEFT | wx.TOP)
        
        self.panel.SetSizer(self.vbox)
        self.vbox.Fit(self)
    
    def create_status_bar(self):
        self.statusbar = self.CreateStatusBar()

    def init_plot(self):
        self.dpi = 100
        self.fig = Figure((3.0, 3.0), dpi=self.dpi)

        self.axes = self.fig.add_subplot(111)
        plt.subplots_adjust(right=3)
        self.axes.set_axis_bgcolor('black')
        self.axes.set_title('OD Curve ' + self.variableToPlot, size=12)
        
        # self.axes.set_xlabel("Time (s)")
        self.axes.set_ylabel("OD")
        pylab.setp(self.axes.get_xticklabels(), fontsize=8)
        pylab.setp(self.axes.get_yticklabels(), fontsize=8)
        
        # add brightness plot axes
        self.axes2 = self.axes.twinx()
        self.axes2.set_ylabel("Brightness (0-255)")        
        pylab.setp(self.axes2.get_xticklabels(), fontsize=8)
        pylab.setp(self.axes2.get_yticklabels(), fontsize=8)

        self.axes2.set_ybound(lower=-1, upper=256)

        # add brightness plot axes
        self.axes3 = self.axes.twinx()
        self.axes3.set_ylabel("Temperature (Deg. C)")        
        self.axes3.set_ybound(lower=0, upper=50)
        self.axes3.spines['right'].set_position(('axes', 1.08))
        self.axes3.set_frame_on(True)
        self.axes3.patch.set_visible(False)
        pylab.setp(self.axes3.get_xticklabels(), fontsize=8)
        pylab.setp(self.axes3.get_yticklabels(), fontsize=8)
        
        # plot the data as a line series, and save the reference 
        # to the plotted line series
        #
        if self.dataStore != None:
            self.plot_data = self.axes.plot(
                self.dataStore.getData(self.variableToPlot), 
                linewidth=2,
                color=(1, 0, 0),
                )[0]

            self.bght_plot_data = self.axes2.plot(
                self.dataStore.getData("Brightness"), 
                linewidth=1,
                color=(1, 1, 0),
                )[0]

            self.temp_plot_data = self.axes3.plot(
                self.dataStore.getData("temp_ch0"), 
                linewidth=1,
                color=(0, 1, 0),
                )[0]

        
    def draw_plot(self):
        """ Redraws the plot
        """
        # when xmin is on auto, it "follows" xmax to produce a 
        # sliding window effect. therefore, xmin is assigned after
        # xmax.
        #
        if not self.dataStore:
            msgbox = wx.MessageBox('No data available to redraw!', 
                                   'Warning', wx.ICON_EXCLAMATION | wx.STAY_ON_TOP)
            return
        x = self.dataStore.getData(self.variableToPlot)
        x_brightness = self.dataStore.getData("Brightness")
        x_temp = self.dataStore.getData("temp_ch0")
        if self.xmax_control.is_auto():
            xmax = len(x) if len(x) > 50 else 50
        else:
            xmax = int(self.xmax_control.manual_value())
            
        if self.xmin_control.is_auto():            
            xmin = xmax - 50
        else:
            xmin = int(self.xmin_control.manual_value())

        # for ymin and ymax, find the minimal and maximal values
        # in the data set and add a mininal margin.
        # 
        # note that it's easy to change this scheme to the 
        # minimal/maximal value in the current display, and not
        # the whole data set.
        # 
        if self.ymin_control.is_auto():
            ymin = round(min(x), 0) - 1
        else:
            ymin = int(self.ymin_control.manual_value())
        
        if self.ymax_control.is_auto():
            ymax = round(max(x), 0) + 1
        else:
            ymax = int(self.ymax_control.manual_value())

        self.axes.set_xbound(lower=xmin, upper=xmax)
        self.axes.set_ybound(lower=ymin, upper=ymax)
        
        self.axes2.set_ybound(lower=1, upper=256)
        self.axes3.set_ybound(lower=0, upper=50)
        # update title 
        self.axes.set_title('OD Curve ' + self.variableToPlot, size=12)
        # anecdote: axes.grid assumes b=True if any other flag is
        # given even if b is set to False.
        # so just passing the flag into the first statement won't
        # work.
        #
        if self.cb_grid.IsChecked():
            self.axes.grid(True, color='gray')
        else:
            self.axes.grid(False)

        # Using setp here is convenient, because get_xticklabels
        # returns a list over which one needs to explicitly 
        # iterate, and setp already handles this.
        #  
        pylab.setp(self.axes.get_xticklabels(), 
            visible=self.cb_xlab.IsChecked())
        
        self.plot_data.set_xdata(np.arange(len(x)))
        self.plot_data.set_ydata(np.array(x))

        self.bght_plot_data.set_xdata(np.arange(len(x)))
        self.bght_plot_data.set_ydata(np.array(x_brightness))
        self.temp_plot_data.set_xdata(np.arange(len(x)))
        self.temp_plot_data.set_ydata(np.array(x_temp))
        self.canvas.draw()
    
    def on_select_var_button(self, event):
        """select variable to plot"""
        if not self.dataStore:
            print "No data to plot"
            msgbox = wx.MessageBox('No data available to plot!', 
                                   'Warning', wx.ICON_EXCLAMATION | wx.STAY_ON_TOP)
            return
        varNames = sorted(self.dataStore.data.keys())
        varNames.remove("Time")
        dlg = wx.SingleChoiceDialog(self, "Select OD to plot", "...",varNames, wx.CHOICEDLG_STYLE)

        if dlg.ShowModal() == wx.ID_OK:
            vn = dlg.GetStringSelection()
            self.variableToPlot = vn
        dlg.Destroy()
        self.draw_plot()
        
    def on_redraw_button(self, event):
        """refresh plot"""
        self.draw_plot()
        
    def on_clear_button(self, event):
        """clear plot by removing all data from datastore"""
        if not self.dataStore:
            return
        self.dataStore.clear()
        self.draw_plot()
        
    def on_cb_grid(self, event):
        self.draw_plot()
    
    def on_cb_xlab(self, event):
        self.draw_plot()
    
    def on_save_plot(self, event):
        file_choices = "PNG (*.png)|*.png"
        
        dlg = wx.FileDialog(
            self, 
            message="Save plot as...",
            defaultDir=os.getcwd(),
            defaultFile="plot.png",
            wildcard=file_choices,
            style=wx.SAVE)
        
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            self.canvas.print_figure(path, dpi=self.dpi)
            self.flash_status_message("Saved to %s" % path)
    
    def OnClose(self, event):
        self.parent.odCurveFrame = None
        self.parent.notebook_1_pane_1.button_odPlot.Enable()
        self.Destroy()
    
    def flash_status_message(self, msg, flash_len_ms=1500):
        self.statusbar.SetStatusText(msg)
        self.timeroff = wx.Timer(self)
        self.Bind(
            wx.EVT_TIMER, 
            self.on_flash_status_off, 
            self.timeroff)
        self.timeroff.Start(flash_len_ms, oneShot=True)
    
    def on_flash_status_off(self, event):
        self.statusbar.SetStatusText('')
