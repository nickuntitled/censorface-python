# Python Modules
import argparse, wx

# Custom Modules
from modules import mainframe

def get_args():
    parser = argparse.ArgumentParser(description='Censorface GUI')

    parser.add_argument('--confidence_threshold', default=0.02,
                        type=float, help='confidence_threshold')
    parser.add_argument('--top_k', default=5000, type=int, help='top_k')
    parser.add_argument('--nms_threshold', default=0.4,
                        type=float, help='nms_threshold')
    parser.add_argument('--keep_top_k', default=750, type=int, help='keep_top_k')
    parser.add_argument('-s', '--save_image', action="store_true",
                        default=True, help='show detection results')
    parser.add_argument('--vis_thres', default=0.6, type=float,
                        help='visualization_threshold')
    parser.add_argument('--dlib', default=False, type=bool,
                        help='Enable Dlib.')

    args = parser.parse_args()
    return args

if __name__ == '__main__':
    args = get_args()

    # Define Application
    app = wx.App()

    # Create Main Frame
    frame = mainframe.mainframe(None, args)
    frame.Show()

    # Loop the application
    app.MainLoop()
