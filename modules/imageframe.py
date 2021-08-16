import wx, cv2, os

class imageframe (wx.Frame):
    def __init__(self, parent, directory, fname, imageannotation, thickness):
        wx.Frame.__init__(self, parent, id=wx.ID_ANY, title=u"Image Preview", pos=wx.DefaultPosition,
		                  size=wx.Size(800, 600), style=wx.DEFAULT_FRAME_STYLE | wx.TAB_TRAVERSAL)
                          
        self.SetSizeHints(wx.DefaultSize, wx.DefaultSize)
        
        mainsizer = wx.BoxSizer(wx.HORIZONTAL)
        viewsizer = wx.BoxSizer(wx.HORIZONTAL)
        
        # Default
        self.movecensorspeed = 10
        
        # Array
        self.fname = fname
        self.directory = directory
        self.imageannotation = imageannotation
        self.annotatetext = []
        self.thickness = []
        
        for i in range(len(self.directory)):
            thicknessperlist = list()
            annotatesubtext = list()
            for j in range(len(self.imageannotation[i])):
                thicknessperlist.append(thickness[i][j])
                annotatesubtext.append("Censor Area {}".format(j+1))
                
            self.annotatetext.append(annotatesubtext)
            self.thickness.append(thicknessperlist)
            
        # Menubar
        self.menubar = wx.MenuBar( 0 )
        self.menubar.Append( self.createfilemenu() , u"File" )
        self.menubar.Append( self.createmodifymenu(), u"Modify" )
        self.SetMenuBar( self.menubar )
  
        # Set Statusbar
        self.mainstatusbar = self.CreateStatusBar( 1, wx.STB_SIZEGRIP, wx.ID_ANY )
        
        # Toolbar
        self.createtoolbar()

        # Panel
        self.mainpanel = wx.Panel( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
        
        # Sizer1
        vertsizer1 = wx.BoxSizer(wx.VERTICAL)
        
        # Label
        self.filelabel = wx.StaticText( self.mainpanel, wx.ID_ANY, u"File", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.filelabel.Wrap( -1 )
        vertsizer1.Add(self.filelabel, 0, wx.ALL, 5)
  
        # FileList
        filelistboxChoices = self.fname
        self.filelistbox = wx.ListBox(self.mainpanel, wx.ID_ANY, wx.DefaultPosition,
		                              wx.DefaultSize, filelistboxChoices, 0); self.filelistbox.SetSelection(0)
        self.filelistbox.SetMinSize((300, -1))
        self.filelistbox.SetMaxSize((1000, -1))
        vertsizer1.Add(self.filelistbox, 1, wx.ALL | wx.EXPAND, 5)
        
        mainsizer.Add(vertsizer1, 1, wx.ALL | wx.EXPAND, 5)
        
        # Sizer2
        vertsizer2 = wx.BoxSizer(wx.VERTICAL)
        
        # Label
        self.annotatelabel = wx.StaticText( self.mainpanel, wx.ID_ANY, u"Annotation", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.annotatelabel.Wrap( -1 )
        vertsizer2.Add(self.annotatelabel, 0, wx.ALL, 5)
  
        # AnnotateList
        annotatelistboxChoices = self.annotatetext[0]
        self.annotatelistbox = wx.ListBox(self.mainpanel, wx.ID_ANY, wx.DefaultPosition,
		                              wx.DefaultSize, annotatelistboxChoices, 0)
        self.annotatelistbox.SetMinSize((300, -1))
        self.annotatelistbox.SetMaxSize((1000, -1))
        self.annotatelistbox.SetSelection(0)
        vertsizer2.Add(self.annotatelistbox, 1, wx.ALL | wx.EXPAND, 5)
        
        mainsizer.Add(vertsizer2, 1, wx.ALL | wx.EXPAND, 5)
        
        # Sizer3
        vertsizer3 = wx.BoxSizer(wx.VERTICAL)
        
        # Label
        self.previewlabel = wx.StaticText( self.mainpanel, wx.ID_ANY, u"Preview", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.previewlabel.Wrap( -1 )
        vertsizer3.Add(self.previewlabel, 0, wx.ALL, 5)
        
        # Bitmap
        bitmap = self.converttobitmapfromnumpy(r"{}".format(directory[0]), self.imageannotation[0][0], self.thickness[0][0])
        self.m_bitmap2 = wx.StaticBitmap(
		    self.mainpanel, wx.ID_ANY, bitmap, wx.DefaultPosition, wx.DefaultSize, 0)
        vertsizer3.Add(self.m_bitmap2, 1, wx.ALL | wx.EXPAND, 5)

        mainsizer.Add(vertsizer3, 1, wx.EXPAND | wx.ALL, 5)
        
        self.mainpanel.SetSizer(mainsizer)
        self.mainpanel.Layout()
        
        viewsizer.Add(self.mainpanel, 0, wx.EXPAND | wx.ALL, 5)
        self.SetSizer(viewsizer)
        self.Layout()
        
        self.Centre(wx.BOTH)

        self.filelistbox.Bind(wx.EVT_LISTBOX, self.onfilechange)
        self.annotatelistbox.Bind(wx.EVT_LISTBOX, self.onannotatechange)

    def createfilemenu(self):
        filemenu = wx.Menu()
        exportmenu = wx.MenuItem( filemenu, wx.ID_ANY, u"Export"+ u"\t" + u"CTRL+S", wx.EmptyString, wx.ITEM_NORMAL )
        exitmenu = wx.MenuItem( filemenu, wx.ID_ANY, u"Exit"+ u"\t" + u"CTRL+X", wx.EmptyString, wx.ITEM_NORMAL )
        
        filemenu.Append( exportmenu )
        filemenu.AppendSeparator()
        filemenu.Append( exitmenu )

        # Bind Event
        self.Bind(wx.EVT_MENU, self.onexport, exportmenu)
        self.Bind(wx.EVT_MENU, self.onclose, exitmenu)

        return filemenu

    def createmodifymenu(self):
        modifymenu = wx.Menu()
        deleteannotationmenu = wx.MenuItem( modifymenu, wx.ID_ANY, u"Delete Censor Area"+ u"\t" + u"CTRL+D", wx.EmptyString, wx.ITEM_NORMAL )
        modifythicknessmenu = wx.MenuItem( modifymenu, wx.ID_ANY, u"Modify Thickness"+ u"\t" + u"CTRL+T", wx.EmptyString, wx.ITEM_NORMAL )
        incthicknessmenu = wx.MenuItem( modifymenu, wx.ID_ANY, u"Increase Thickness"+ u"\t" + u"CTRL++", wx.EmptyString, wx.ITEM_NORMAL )
        decthicknessmenu = wx.MenuItem( modifymenu, wx.ID_ANY, u"Decrease Thickness"+ u"\t" + u"CTRL+-", wx.EmptyString, wx.ITEM_NORMAL )
        
        moveleftmenu = wx.MenuItem( modifymenu, wx.ID_ANY, u"Move Censor Area Left"+ u"\t" + u"CTRL+Left", wx.EmptyString, wx.ITEM_NORMAL )
        moverightmenu = wx.MenuItem( modifymenu, wx.ID_ANY, u"Move Censor Area Right"+ u"\t" + u"CTRL+Right", wx.EmptyString, wx.ITEM_NORMAL )
        movetopmenu = wx.MenuItem( modifymenu, wx.ID_ANY, u"Move Censor Area Top"+ u"\t" + u"CTRL+Up", wx.EmptyString, wx.ITEM_NORMAL )
        movebottommenu = wx.MenuItem( modifymenu, wx.ID_ANY, u"Move Censor Area Bottom"+ u"\t" + u"CTRL+Down", wx.EmptyString, wx.ITEM_NORMAL )
        
        modifycensorspeed = wx.MenuItem( modifymenu, wx.ID_ANY, u"Modify Censor Pixel Usage"+ u"\t" + u"CTRL+M", wx.EmptyString, wx.ITEM_NORMAL )
        
        modifymenu.Append(incthicknessmenu)
        modifymenu.Append(decthicknessmenu)
        modifymenu.AppendSeparator()
        modifymenu.Append(moveleftmenu)
        modifymenu.Append(moverightmenu)
        modifymenu.Append(movetopmenu)
        modifymenu.Append(movebottommenu)
        modifymenu.AppendSeparator()
        modifymenu.Append(modifythicknessmenu)
        modifymenu.Append(modifycensorspeed)
        modifymenu.AppendSeparator()
        modifymenu.Append(deleteannotationmenu)

        # Bind Event
        self.Bind(wx.EVT_MENU, self.onmodifythickness, modifythicknessmenu)
        self.Bind(wx.EVT_MENU, self.onincreasethickness, incthicknessmenu)
        self.Bind(wx.EVT_MENU, self.ondecreasethickness, decthicknessmenu)
        
        self.Bind(wx.EVT_MENU, self.onmoveleft, moveleftmenu)
        self.Bind(wx.EVT_MENU, self.onmoveright, moverightmenu)
        self.Bind(wx.EVT_MENU, self.onmovetop, movetopmenu)
        self.Bind(wx.EVT_MENU, self.onmovebottom, movebottommenu)
        self.Bind(wx.EVT_MENU, self.onmodifycensorspeed, modifycensorspeed)
        self.Bind(wx.EVT_MENU, self.ondeleteannotate, deleteannotationmenu)

        return modifymenu

    def createtoolbar(self):
        toolbar = self.CreateToolBar(wx.TB_HORIZONTAL) #|wx.TB_HORZ_TEXT)
        export = toolbar.AddTool(3, 'Export', wx.Bitmap('icons/doc_export_icon.png'))
        toolbar.AddSeparator()
        deleteselected = toolbar.AddTool(1, 'Delete Selected Annotation', wx.Bitmap('icons/delete_icon.png'))
        modifythickness = toolbar.AddTool(2, 'Modify Thickness', wx.Bitmap('icons/doc_edit_icon.png'))
        modifycensorusage = toolbar.AddTool(9, 'Modify Censor Pixel Usage', wx.Bitmap('icons/cog_icon.png'))
        toolbar.AddSeparator()
        moveleft = toolbar.AddTool(3, 'Move Left', wx.Bitmap('icons/left_icon.png'))
        moveright = toolbar.AddTool(4, 'Move Right', wx.Bitmap('icons/right_icon.png'))
        movetop = toolbar.AddTool(5, 'Move Top', wx.Bitmap('icons/top_icon.png'))
        movebottom = toolbar.AddTool(6, 'Move Bottom', wx.Bitmap('icons/bottom_icon.png'))
        toolbar.AddSeparator()
        incthickness = toolbar.AddTool(7, 'Increase Thickness', wx.Bitmap('icons/plus_icon.png'))
        decthickness = toolbar.AddTool(8, 'Decrease Thickness', wx.Bitmap('icons/minus_icon.png'))
        toolbar.Realize()

        # Bind Event
        self.Bind(wx.EVT_TOOL, self.ondeleteannotate, deleteselected)
        self.Bind(wx.EVT_TOOL, self.onmodifythickness, modifythickness)
        self.Bind(wx.EVT_TOOL, self.onexport, export)
        
        self.Bind(wx.EVT_TOOL, self.onincreasethickness, incthickness)
        self.Bind(wx.EVT_TOOL, self.ondecreasethickness, decthickness)
        
        self.Bind(wx.EVT_TOOL, self.onmoveleft, moveleft)
        self.Bind(wx.EVT_TOOL, self.onmoveright, moveright)
        self.Bind(wx.EVT_TOOL, self.onmovetop, movetop)
        self.Bind(wx.EVT_TOOL, self.onmovebottom, movebottom)
        
        self.Bind(wx.EVT_TOOL, self.onmodifycensorspeed, modifycensorusage)

    def changestatus(self, text):
        self.mainstatusbar.SetStatusText(text)
        
    def generateannotatelist(self, annotate):
        size = len(annotate) + 1
        combolist = []
        for i in range(1, size):
            combolist.append('Censor Area {}'.format(str(i)))
        return combolist
    
    def clearcomboarea(self):
        size = self.annotatelistbox.GetCount()
        for i in range(0, size):
            self.annotatelistbox.Delete(0)
    
    def clearallcombo(self):
        filesize = self.filelistbox.GetCount()
        size = self.annotatelistbox.GetCount()
        for i in range(0, size):
            self.annotatelistbox.Delete(0)
            
        for i in range(0, filesize):
            self.filelistbox.Delete(0)
        
    def onmodifycensorspeed(self, event):
        self.movecensorspeed = int(self.showdialog("Modify Censor Pixel Usage", "Change the number of pixel usage in every move censor area you want.", "{}".format(self.movecensorspeed)))
        self.changestatus("Modify Censor Speed to {}".format(self.movecensorspeed))
        
    def onincreasethickness(self, event):
        try:
            curr_index = self.filelistbox.GetSelection()
            curr_annotate = self.annotatelistbox.GetSelection()
            self.thickness[curr_index][curr_annotate] += 1
            self.drawimage(curr_index, curr_annotate)
            self.changestatus("Increase Thickness to {}".format(self.thickness[curr_index][curr_annotate]))
            
        except Exception as e:
            self.changestatus("Modify thickness fail.")
            print("Error: {}".format(e))
            dial = wx.MessageDialog(None, 'Modify thickness fail.', 'Censorface',
                wx.OK | wx.ICON_HAND)
            dial.ShowModal()
        
        
    def ondecreasethickness(self, event):
        try:
            curr_index = self.filelistbox.GetSelection()
            curr_annotate = self.annotatelistbox.GetSelection()
            self.thickness[curr_index][curr_annotate] -= 1
            self.drawimage(curr_index, curr_annotate)
            self.changestatus("Decrease Thickness to {}".format(self.thickness[curr_index][curr_annotate]))
            
        except Exception as e:
            self.changestatus("Modify thickness fail.")
            print("Error: {}".format(e))
            dial = wx.MessageDialog(None, 'Modify thickness fail.', 'Censorface',
                wx.OK | wx.ICON_HAND)
            dial.ShowModal()
        
    def moveannotate(self, movex = 0, movey = 0):
        try:
            curr_index = self.filelistbox.GetSelection()
            curr_annotate = self.annotatelistbox.GetSelection()
            
            # Move
            data = self.imageannotation[curr_index][curr_annotate]
            data[0] = list(data[0])
            data[1] = list(data[1])
            
            data[0][0] += movex
            data[1][0] += movex
            data[0][1] += movey
            data[1][1] += movey
            
            data[0] = tuple(data[0])
            data[1] = tuple(data[1])
            
            self.imageannotation[curr_index][curr_annotate] = data
            
            # Redraw
            self.drawimage(curr_index, curr_annotate)
            
        except Exception as e:
            self.changestatus("Move censor area fail.")
            print("Error: {}".format(e))
            dial = wx.MessageDialog(None, 'Move censor area fail.', 'Censorface',
                wx.OK | wx.ICON_HAND)
            dial.ShowModal()
            
    def onmoveleft(self, event):
        self.moveannotate(self.movecensorspeed*(-1),0)
        self.changestatus("Move Censor Area to the left")
        
    def onmoveright(self, event):
        self.moveannotate(self.movecensorspeed,0)
        self.changestatus("Move Censor Area to the right")
        
    def onmovetop(self, event):
        self.moveannotate(0,self.movecensorspeed*(-1))
        self.changestatus("Move Censor Area to the top")
        
    def onmovebottom(self, event):
        self.moveannotate(0,self.movecensorspeed)
        self.changestatus("Move Censor Area to the bottom")
    
    def ondeleteannotate(self, event):
        dial = wx.MessageDialog(None, 'Are you sure to delete this censor?', 'Censorface',
            wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION)
        result = dial.ShowModal()
        
        if(result != wx.ID_YES):
            return

        curr_index = self.filelistbox.GetSelection()
        curr_annotate = self.annotatelistbox.GetSelection()
        self.annotatelistbox.Delete(curr_annotate)
            
        del self.imageannotation[curr_index][curr_annotate]
        del self.thickness[curr_index][curr_annotate]
        del self.annotatetext[curr_index][curr_annotate]
                
        if(len(self.imageannotation[curr_index]) == 0):
            self.filelistbox.Delete(curr_index)
            del self.directory[curr_index]
            del self.imageannotation[curr_index]
            del self.annotatetext[curr_index]
            del self.thickness[curr_index]
            del self.fname[curr_index]
                
        self.clearallcombo()
            
        if(len(self.directory) > 0):
            directorysize = len(self.directory)
            self.filelistbox.Append(self.fname)
                    
            self.annotatelistbox.Append(self.annotatetext[curr_index])
            
            self.filelistbox.SetSelection(curr_index)
            self.annotatelistbox.SetSelection(0)
            self.drawimage(curr_index, 0)
                
        self.changestatus("Delete Annotate Successfully.")
                
    def onmodifythickness(self, event):
        try:
            curr_index = self.filelistbox.GetSelection()
            curr_annotate = self.annotatelistbox.GetSelection()
            thickness = int(self.showdialog("Modify Thickness", "Change the censor thickness you want.", "{}".format(self.thickness[curr_index][curr_annotate])))
            self.thickness[curr_index][curr_annotate] = thickness
            self.drawimage(curr_index, curr_annotate)
                
            self.changestatus("Modify Censor Thickness to {}.".format(thickness))
            
        except Exception as e:
            self.changestatus("Modify thickness fail.")
            print("Error: {}".format(e))
            dial = wx.MessageDialog(None, 'Modify thickness fail.', 'Censorface',
                wx.OK | wx.ICON_HAND)
            dial.ShowModal()
            
    def onexport(self, event):
        try:
            #if True:
            dialog = wx.DirDialog(self, "Open the destination directory.", "", wx.DD_DEFAULT_STYLE | wx.DD_DIR_MUST_EXIST) 
            
            if dialog.ShowModal() == wx.ID_CANCEL:
                return
            
            pathname = dialog.GetPath()
            
            print("Export censored face files.")
            size_directory = len(self.directory)
            for index in range(size_directory):
                directory = self.directory[index]
                print("Face number {}: {}".format(str(index+1), directory))
                img_original = cv2.imread(directory)
                
                size_annotation = len(self.imageannotation[index])
                
                for sub_index in range(size_annotation):
                    img_original = self.visualize_result(img_original, self.imageannotation[index][sub_index], self.thickness[index][sub_index])
            
                cv2.imwrite("{}".format(os.path.join(pathname, self.fname[index])), img_original)
                
            dial = wx.MessageDialog(None, 'Export Censorface Successfully.', 'Censorface',
                wx.OK | wx.ICON_INFORMATION)
            dial.ShowModal()
            
            self.changestatus("Export successfully.")
            
        except Exception as e:
            print("Error: {}".format(e))
            self.changestatus("Export fail.")
            dial = wx.MessageDialog(None, 'Export Censorface Fail.', 'Censorface',
                wx.OK | wx.ICON_HAND)
            dial.ShowModal()
        
    def onclose(self, event):
        dial = wx.MessageDialog(None, 'Are you sure to close this window?', 'Censorface',
            wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION)
        result = dial.ShowModal()
        
        if(result == wx.ID_YES):
            self.Close()
        
    def showdialog(self, title, message, default = ""):
        dlg = wx.TextEntryDialog(self,message, title)
        dlg.SetValue(default)
        if dlg.ShowModal() == wx.ID_OK:
            value = dlg.GetValue()
        else:
            value = default
        dlg.Destroy()
        
        return value
    
    def drawimage(self, fileindex, annotateindex):
        try:
            path = self.directory[fileindex]
            annotate = self.imageannotation[fileindex][annotateindex]
            bitmap = self.converttobitmapfromnumpy(path, annotate, self.thickness[fileindex][annotateindex])
            self.m_bitmap2.SetBitmap(bitmap)
            
        except Exception as e:
            print("Error: {}".format(e))
            dial = wx.MessageDialog(None, 'Draw image fail.', 'Censorface',
                wx.OK | wx.ICON_HAND)
            dial.ShowModal()
        
    def onfilechange(self, event):
        try:
            # Clear Annotate Listbox
            self.clearcomboarea()
        
            # Change Image
            curr_index = self.filelistbox.GetSelection()
            listannotate = self.annotatetext[curr_index] #self.generateannotatelist(self.imageannotation[curr_index])
            self.annotatelistbox.Append(listannotate)
            self.annotatelistbox.SetSelection(0)
            self.drawimage(curr_index, 0)
            
        except Exception as e:
            print("Error: {}".format(e))
            dial = wx.MessageDialog(None, 'Change image fail.', 'Censorface',
                wx.OK | wx.ICON_HAND)
            dial.ShowModal()
        
    def onannotatechange(self, event):
        try:
            curr_index = self.filelistbox.GetSelection()
            curr_annotate = self.annotatelistbox.GetSelection()
            self.drawimage(curr_index, curr_annotate)
            
        except Exception as e:
            print("Error: {}".format(e))
            dial = wx.MessageDialog(None, 'Change annotate fail.', 'Censorface',
                wx.OK | wx.ICON_HAND)
            dial.ShowModal()
        
    def converttobitmapfromnumpy(self, path, imageannotation, thickness=15):
        img_data = cv2.imread(r"{}".format(path))
        img_data = self.visualize_result(img_data, imageannotation, thickness)
        img_data = cv2.cvtColor(img_data, cv2.COLOR_BGR2RGB)
        height, width, _ = img_data.shape[:3]
        
        ratio = width/height
        newheight = int(500/ratio)
        img_data = cv2.resize(img_data, (500, newheight), cv2.INTER_AREA)
        
        image = wx.EmptyImage(500,newheight)
        image.SetData( img_data.tobytes())
        wxBitmap = image.ConvertToBitmap()       # OR:  wx.BitmapFromImage(image)
        return wxBitmap

    def visualize_result(self, image, point, thickness = 15):
        if(len(point) == 0):
            return

        x1 = point[0][0]
        x2 = point[1][0]
        
        y1 = point[0][1]
        y2 = point[1][1]
        
        side_pixel = int(thickness / 2)
        other_pixel = int(thickness)
        x1 -= other_pixel
        y1 -= side_pixel
        x2 += other_pixel
        y2 += side_pixel
        
        image = cv2.rectangle(image, (x1,y1), (x2,y2), (0,0,0), -1)
        
        return image