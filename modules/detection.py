# Python Modules
import numpy as np
import cv2, time

# RetinaFace Modules
from layers.functions.prior_box_onnx import PriorBox
from utils.nms.py_cpu_nms import py_cpu_nms
from utils.box_utils_onnx import decode_onnx, decode_landm_onnx

def detection(img_raw, onnx_session, cfg, args, resize = 800): # model, device, cfg, resize = 1):
    
    img = img_raw[:,:,:3].copy()
    
    # Resize before inserting into ONNX model
    img = cv2.resize(img_raw, (resize, resize))
    img = np.float32(img)
    im_height, im_width, _ = img.shape
    
    scale = np.array([img.shape[1], img.shape[0], img.shape[1], img.shape[0]])
    scale1 = np.array([img.shape[1], img.shape[0], img.shape[1], img.shape[0],
                        img.shape[1], img.shape[0], img.shape[1], img.shape[0],
                        img.shape[1], img.shape[0]])
    
    img -= (104, 117, 123)
    img = img.transpose(2, 0, 1)
    img = np.expand_dims(img, axis = 0)
        
    start = time.time()
    
    onnx_input = {onnx_session.get_inputs()[0].name: img}
    result = onnx_session.run(None, onnx_input)
    loc = result[0]
    conf = result[1]
    landms = result[2]
        
    priorbox = PriorBox(cfg, image_size=(im_height, im_width))
    priors = priorbox.forward()
    
    boxes = decode_onnx(loc[0], priors, cfg['variance'])
    boxes = boxes * scale
    
    scores = conf.squeeze(0)[:, 1]
    
    landms = decode_landm_onnx(landms[0], priors, cfg['variance'])
            
    landms = landms * scale1

    # ignore low scores
    inds = np.where(scores > args.confidence_threshold)[0]
    boxes = boxes[inds] 
    landms = landms[inds]
    scores = scores[inds]
    
    # keep top-K before NMS
    order = scores.argsort()[::-1][:args.top_k]
    boxes = boxes[order]
    landms = landms[order]
    scores = scores[order]

    # do NMS
    dets = np.hstack((boxes, scores[:, np.newaxis])).astype(np.float32, copy=False)
    keep = py_cpu_nms(dets, args.nms_threshold)
    
    dets = dets[keep, :]
    landms = landms[keep]

    # keep top-K faster NMS
    dets = dets[:args.keep_top_k, :]
    landms = landms[:args.keep_top_k, :]
    
    end = time.time()
    
    if(dets.shape[0] > 0):
        ret = True
    else:
        ret = False
        
    return dets, landms, int(end-start), ret

def prepare_image(img_data):
    # Resize Image
    aspect_ratio = img_data.shape[1] / img_data.shape[0]
    
    if(aspect_ratio >= 1):
        width = 800
        height = int(width / aspect_ratio)
    else:
        height = 800
        width = int(height * aspect_ratio)
    
    dim = (width, height)
    
    resize_image = cv2.resize(img_data, dim, interpolation = cv2.INTER_AREA)
    
    return resize_image, aspect_ratio