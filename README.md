# censorface-python

This repository contains the Censorface python GUI application. It apples RetinaFace as the face detection technique using ONNX runtime as the framework. It censors by getting the both eyes coordinates. 

## Explanation

- main [dot] py is the main application.
- weights is the ONNX runtime trained models.
- modules is the GUI made by wxPython and the face detection codes.
- layers, utils are the Retinaface built-in codes.
- data is the RetinaFace configuration.

## How to install

You can install by using:

```
pip install -r requirements
```

to install the require pacakges.

## Weights folder

You can download from the link in [Google Drive][gdrive_path]. Then, copy in the same executable file or in the root folder.

## How to run

You can run by applying:

```
python main.py
```

for testing.

## How to build an executable

You can build by install pyinstaller. Then, apply this command:

```
python setup.py
```

to build the single exe file. For running the application or distribution, you have to copy icons and weights folders to the same application path.

## Citation

Citation from the RetinaFace technique.

```
@inproceedings{Deng2020CVPR,
    title = {RetinaFace: Single-Shot Multi-Level Face Localisation in the Wild},
    author = {Deng, Jiankang and Guo, Jia and Ververas, Evangelos and Kotsia, Irene and Zafeiriou, Stefanos},
    booktitle = {CVPR},
    year = {2020}
}
```

[gdrive_path]: https://drive.google.com/drive/folders/1Io5EcnLRm18Df6DFJa_2Rrb69x63McK6?usp=sharing