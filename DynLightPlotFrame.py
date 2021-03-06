# -*- coding: UTF-8 -*-
#
# generated by wxGlade 0.6.8 on Sun Oct 13 18:29:42 2013
#

import wx
import matplotlib
matplotlib.use('WXAgg')
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.backends.backend_wx import NavigationToolbar2Wx
from matplotlib.figure import Figure
from numpy import cumsum
# begin wxGlade: dependencies
# end wxGlade

# begin wxGlade: extracode
# end wxGlade


class DynLightPlotFrame(wx.Frame):
    def __init__(self, *args, **kwds):
        # begin wxGlade: DynLightPlotFrame.__init__
        kwds["style"] = wx.DEFAULT_FRAME_STYLE
        wx.Frame.__init__(self, *args, **kwds)

        self.__set_properties()
        self.__do_layout()
        # end wxGlade
        self.__attach_events()
        
        # dynamic light profile data
        self.dynLight = [(0,0),(0,0)]
        # setup plot
        self.dpi = 100
        self.figure = Figure((5.0, 4.0), dpi=self.dpi)
        self.canvas = FigureCanvas(self, -1, self.figure)
        self.axes = self.figure.add_subplot(111)
        
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.canvas, 1, wx.LEFT | wx.TOP | wx.GROW)
        self.SetSizer(self.sizer)
        self.Fit()        
        # self.draw()

    def draw(self):
        chamber = int(self.GetParent().dyn_light_ch_select_combo_box.GetValue())
        print self.dynLight[chamber]
        bght    = [x for (x,y) in self.dynLight[chamber]]
        dur     = cumsum([y  for (x,y) in self.dynLight[chamber]])
        self.axes.clear()
        self.axes.plot(dur, bght)
        self.axes.set_xlabel("Time (s)")
        self.axes.set_ylabel("Brightness (0-255)")
        self.canvas.draw()
        self.axes.grid(True)
        
    def OnPaint(self, event):
            self.canvas.draw()
            
    def __set_properties(self):
        # begin wxGlade: DynLightPlotFrame.__set_properties
        self.SetTitle(_("Dynamic Light Profile"))
        self.SetSize((433, 500))
        # end wxGlade

    def __do_layout(self):
        # begin wxGlade: DynLightPlotFrame.__do_layout
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(sizer_1)
        self.Layout()
        # end wxGlade

    def __attach_events(self):
        #register events at the controls
        self.Bind(wx.EVT_CLOSE, self.OnClose)

    def OnClose(self, event):
        """Called on frame close."""
        self.GetParent().dynLightPlotFrame = None
        self.Destroy()

# end of class DynLightPlotFrame
