import wx, time, cv2, dlib, onnxruntime, os

# Custom Modules
from data import cfg_mnet, cfg_re50
from modules import imageframe, detection

class mainframe(wx.Frame):

    def __init__(self, parent, args):
        wx.Frame.__init__(self, parent, id=wx.ID_ANY, title=u"Face Censor Tool", pos=wx.DefaultPosition, size=wx.Size(
            500, 600), style=wx.CLOSE_BOX | wx.DEFAULT_FRAME_STYLE | wx.MINIMIZE | wx.TAB_TRAVERSAL)

        self.default_thickness = 15
        self.default_minimal_censor = 200
        self.dlib = args.dlib
        self.args = args

        self.SetSizeHints(wx.DefaultSize, wx.DefaultSize)
        self.SetBackgroundColour(
            wx.SystemSettings.GetColour(wx.SYS_COLOUR_HIGHLIGHTTEXT))

        mainsizer = wx.BoxSizer(wx.VERTICAL)

        self.top_label = wx.StaticText(
            self, wx.ID_ANY, u"Face Censor Tool", wx.DefaultPosition, wx.DefaultSize, 0)
        self.top_label.Wrap(-1)

        self.top_label.SetFont(wx.Font(12, wx.FONTFAMILY_SWISS,
                                       wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, "Arial"))

        mainsizer.Add(self.top_label, 0, wx.ALL, 5)

        self.m_staticline3 = wx.StaticLine(
            self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL)
        mainsizer.Add(self.m_staticline3, 0, wx.EXPAND | wx.ALL, 5)

        self.folder_panel = wx.Panel(
            self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL)
        self.folder_panel.SetBackgroundColour(
            wx.SystemSettings.GetColour(wx.SYS_COLOUR_WINDOW))
        self.folder_panel.SetMaxSize(wx.Size(-1, 80))

        upper_sizer = wx.FlexGridSizer(3, 2, 5, 5)
        upper_sizer.AddGrowableCol(1)
        upper_sizer.SetFlexibleDirection(wx.BOTH)
        upper_sizer.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        self.fromfolder_label = wx.StaticText(
            self.folder_panel, wx.ID_ANY, u"Select Folder : ", wx.DefaultPosition, wx.DefaultSize, 0)
        self.fromfolder_label.Wrap(-1)

        self.fromfolder_label.SetFont(wx.Font(
            10, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, "Arial"))

        upper_sizer.Add(self.fromfolder_label, 0, wx.EXPAND | wx.LEFT, 5)

        self.fromfolder_picker = wx.DirPickerCtrl(self.folder_panel, wx.ID_ANY, wx.EmptyString,
                                                  u"Select the image folder", wx.DefaultPosition, wx.DefaultSize,
                                                  wx.DIRP_DEFAULT_STYLE)
        upper_sizer.Add(self.fromfolder_picker, 1, wx.EXPAND | wx.RIGHT, 5)

        # Model
        self.model_label = wx.StaticText(
            self.folder_panel, wx.ID_ANY, u"Model : ", wx.DefaultPosition, wx.DefaultSize, 0)
        self.model_label.Wrap(-1)

        self.model_label.SetFont(wx.Font(
            10, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, "Arial"))

        upper_sizer.Add(self.model_label, 0, wx.EXPAND | wx.LEFT, 5)

        model = ['High Accuracy', 'High Performance']
        self.combo = wx.ComboBox(self.folder_panel, choices=model, value='')
        upper_sizer.Add(self.combo, 0, wx.EXPAND | wx.RIGHT, 5)

        # Thickness
        self.thickness_label = wx.StaticText(
            self.folder_panel, wx.ID_ANY, u"Thickness : ", wx.DefaultPosition, wx.DefaultSize, 0)
        self.thickness_label.Wrap(-1)

        self.thickness_label.SetFont(wx.Font(
            10, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, "Arial"))

        upper_sizer.Add(self.thickness_label, 0, wx.EXPAND | wx.LEFT, 5)

        self.thickness_text = wx.TextCtrl(self.folder_panel, wx.ID_ANY, value = "15")
        
        upper_sizer.Add(self.thickness_text, 0, wx.EXPAND | wx.RIGHT, 5)
               
        self.folder_panel.SetSizer(upper_sizer)
        self.folder_panel.Layout()
        upper_sizer.Fit(self.folder_panel)
        mainsizer.Add(self.folder_panel, 1, wx.ALIGN_TOP |
                      wx.ALL | wx.EXPAND, 5)

        self.m_staticline1 = wx.StaticLine(
            self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL)
        mainsizer.Add(self.m_staticline1, 0, wx.EXPAND | wx.ALL, 5)

        self.status_txt = wx.TextCtrl(
            self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_MULTILINE)
        self.status_txt.SetFont(wx.Font(10, wx.FONTFAMILY_SWISS,
                                        wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, "Arial"))
        self.status_txt.Enable(False)

        mainsizer.Add(self.status_txt, 1, wx.ALL | wx.EXPAND, 5)

        self.m_staticline4 = wx.StaticLine(
            self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL)
        mainsizer.Add(self.m_staticline4, 0, wx.EXPAND | wx.ALL, 5)

        self.button_panel = wx.Panel(
            self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL)
        self.button_panel.SetMaxSize(wx.Size(-1, 50))

        button_sizer = wx.BoxSizer(wx.HORIZONTAL)

        self.censor_btn = wx.Button(
            self.button_panel, wx.ID_ANY, u"Start Censor Face", wx.DefaultPosition, wx.DefaultSize, 0)
        button_sizer.Add(self.censor_btn, 0, wx.ALL, 5)

        self.censor_btn.Bind(wx.EVT_BUTTON, self.oncensorclick)

        self.button_panel.SetSizer(button_sizer)
        self.button_panel.Layout()
        button_sizer.Fit(self.button_panel)

        mainsizer.Add(self.button_panel, 1, wx.EXPAND | wx.LEFT | wx.TOP, 5)

        self.SetSizer(mainsizer)
        self.Layout()

        self.Centre(wx.BOTH)

    def showinputdialog(self, frame, inputtext, titletext, default=''):
        # Create text input
        dlg = wx.TextEntryDialog(frame, inputtext, titletext)
        dlg.SetValue("15")

        if dlg.ShowModal() == wx.ID_OK:
            return dlg.GetValue()

        return ""

    def oncensorclick(self, event):

        frompath = self.fromfolder_picker.GetPath()
        cnn_network = self.combo.GetCurrentSelection()
        cpuchecked = 1

        cfg = None
        iou_threshold = 0.5

        if cnn_network == 1:
            cfg = cfg_mnet
            weight_file = 'weights/Mobile0.25.onnx'
        elif cnn_network == 0:
            cfg = cfg_re50
            weight_file = "weights/FaceDetector.onnx"

        try:
            # net and model
            session = onnxruntime.InferenceSession(weight_file)

            print('Finished loading model')
            resize = 1

            if(frompath != ''):
                self.writestatus('Censoring image from {}'.format(frompath))

                success = 0
                fail = 0
                filepath = []
                shortname = []
                imageannotation = []
                thickness = []
                for root, dirs, files in os.walk(frompath, topdown=False):
                    for name in files:
                        name_split = name.split('.')

                        if(len(name_split) > 1):
                            if(name_split[1] == 'jpg' or name_split[1] == 'png' or name_split[1] == 'JPG' or name_split[1] == 'PNG'):
                                image_path = os.path.join(root, name)

                                self.writestatus(
                                    'Preparing Image: {}'.format(name))

                                img_data = cv2.imread(image_path)

                                resize_image, aspect_ratio = detection.prepare_image(
                                    img_data)

                                # Detection
                                resize_param = 800
                                dets, landmark, time_usage, ret = detection.detection(
                                    resize_image, session, cfg, self.args, resize_param)


                                # Result
                                if(ret):
                                    # For Resize preparation
                                    scale_x = img_data.shape[1] / 800
                                    scale_y = img_data.shape[0] / 800

                                    self.writestatus(
                                        'Success within {} second'.format(time_usage))

                                    # Define Default value
                                    shortname.append(name)
                                    filepath.append(image_path)
                                    
                                    imglandmark, thick = self.get_builtin_annotation(dets, landmark, img_data, scale_x, scale_y, int(self.thickness_text.GetValue()) )
                                    thickness.append(thick)
                                        
                                    imageannotation.append(imglandmark)
                                    success += 1
                                else:
                                    self.writestatus('Failed to censor face.')
                                    fail += 1

                if(len(filepath) > 0 and len(imageannotation) > 0):
                    dial = wx.MessageDialog(None, 'Censoring face successfully. Click OK to preview and modify the censoring area.', 'Censorface',
                        wx.OK | wx.ICON_INFORMATION)
                    dial.ShowModal()
                    
                    imagewindow = imageframe.imageframe(self, filepath, shortname, imageannotation, thickness)
                    imagewindow.Show()

                self.writestatus(
                    'Detection and Censor complete -> {} success images and {} failed images.'.format(success, fail))
            else:
                self.writestatus('You do not select any folder.')
            
        except Exception as e:
            print("Error: {}".format(e))
            dial = wx.MessageDialog(None, 'Censoring face fail.', 'Censorface',
                wx.OK | wx.ICON_HAND)
            dial.ShowModal()
            
    def writestatus(self, status):
        localtime = time.localtime(time.time())
        self.status_txt.AppendText('[{}/{}/{} {}:{}:{}] {}\n'.format(localtime.tm_mday, localtime.tm_mon, localtime.tm_year,
                                                                     localtime.tm_hour, localtime.tm_min, localtime.tm_sec, status))
        print(status)

    def thickness_calculation(self, scale_x):
        thickness = int(self.default_thickness * scale_x)
        return thickness

    def get_annotation(self, dets, landmark_detector, image, scale_x, scale_y):
        if(len(dets) == 0):
            return image

        point = []
        for i in range(dets.shape[0]):
            box = dets[i]
            # lms = landmark[i]
            x0 = int(box[0] * scale_x)
            y0 = int(box[1] * scale_y)
            x1 = int(box[2] * scale_x)
            y1 = int(box[3] * scale_y)
            
            face_area = image[y0:y1, x0:x1].copy()
            confidence = box[4]
            
            size_bb_x = int(x1-x0)
            size_bb_y = int(y1-y0)
            scale_bb_x = size_bb_x / 800
            scale_bb_y = size_bb_y / 800
            
            # Draw Point
            shape = landmark_detector(image, dlib.rectangle(int(x0), int(y0), int(x1), int(y1)))
            righteye = (shape.part(36).x, shape.part(36).y)
            lefteye = (shape.part(45).x, shape.part(45).y)
            
            point.append([righteye, lefteye])
        
        return point

    def get_builtin_annotation(self, dets, landmark, image, scale_x, scale_y, thick):
        if(len(dets) == 0):
            return image
        
        point = []
        thickness = []
        for i in range(dets.shape[0]):
            box = dets[i]
            # lms = landmark[i]
            x0 = int(box[0] * scale_x)
            y0 = int(box[1] * scale_y)
            x1 = int(box[2] * scale_x)
            y1 = int(box[3] * scale_y)
            lms = landmark[i]
            
            # Select landmark
            lms_x = lms[::2]
            lms_y = lms[1::2]
            
            righteye = (int(lms_x[0] * scale_x), int(lms_y[0] * scale_y))
            lefteye = (int(lms_x[1] * scale_x), int(lms_y[1] * scale_y))
            
            point.append([righteye, lefteye])
            
            thick = int(thick) #self.thickness_calculation((x1-x0)/ self.default_minimal_censor)
            
            thickness.append(thick)
            
        return point, thickness
            
    def __del__(self):
        pass