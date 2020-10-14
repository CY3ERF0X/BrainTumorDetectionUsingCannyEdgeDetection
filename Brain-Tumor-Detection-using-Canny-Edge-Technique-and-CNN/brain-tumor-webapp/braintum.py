def image_detect(filename):
  from PIL import Image
  import numpy as np
  import cv2
  from matplotlib import pyplot as plt
  from PIL import Image
  from skimage.morphology import extrema
  from skimage.morphology import watershed as skwater
  print(filename)
  #canny starts
  def auto_canny(image, sigma=0.33):
    # compute the median of the single channel pixel intensities
    v = np.median(image)
  
    # apply automatic Canny edge detection using the computed median
    lower = int(max(0, (1.0 - sigma) * v))
    upper = int(min(255, (1.0 + sigma) * v))
    edged = cv2.Canny(image, lower, upper)
  
    # return the edged image
    return edged

  def ShowImage(title,img,ctype):
    plt.figure(figsize=(10, 10))
    if ctype=='bgr':
      b,g,r = cv2.split(img)       # get b,g,r
      rgb_img = cv2.merge([r,g,b])     # switch it to rgb
      plt.imshow(rgb_img)
    elif ctype=='hsv':
      rgb = cv2.cvtColor(img,cv2.COLOR_HSV2RGB)
      plt.imshow(rgb)
    elif ctype=='gray':
      plt.imshow(img,cmap='gray')
    elif ctype=='rgb':
      plt.imshow(img)
    else:
      raise Exception("Unknown colour type")
    plt.axis('off')
    plt.title(title)
    plt.show()
  img= cv2.imread(filename)
  gray= cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
  ShowImage('Brain MRI',gray,'gray')

  ret, thresh = cv2.threshold(gray,0,255,cv2.THRESH_OTSU)
  ShowImage('Thresholding image',thresh,'gray')

  ret, markers = cv2.connectedComponents(thresh)

  #Get the area taken by each component. Ignore label 0 since this is the background.
  marker_area = [np.sum(markers==m) for m in range(np.max(markers)) if m!=0] 
  #Get label of largest component by area
  largest_component = np.argmax(marker_area)+1 #Add 1 since we dropped zero above                        
  #Get pixels which correspond to the brain
  brain_mask = markers==largest_component

  brain_out = img.copy()
  #In a copy of the original image, clear those pixels that don't correspond to the brain
  brain_out[brain_mask==False] = (0,0,0)

  img = cv2.imread(filename)
  gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
  ret, thresh = cv2.threshold(gray,0,255,cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)
  #canny-edge-detection
  auto=auto_canny(thresh)
  cv2.imshow("canny",auto)
  cv2.waitKey(0)
  resu=auto+thresh
  cv2.imshow("res=canny+thresh",resu)
  cv2.waitKey(0)
  cv2.imshow("invert res",cv2.bitwise_not(resu))
  cv2.waitKey(0)
  # noise removal
  kernel = np.ones((3,3),np.uint8)
  opening = cv2.morphologyEx(thresh,cv2.MORPH_OPEN,kernel, iterations = 2)
      
  # sure background area
  sure_bg = cv2.dilate(opening,kernel,iterations=3)
      
  # Finding sure foreground area
  dist_transform = cv2.distanceTransform(opening,cv2.DIST_L2,5)
  ret, sure_fg = cv2.threshold(dist_transform,0.7*dist_transform.max(),255,0)
      
  # Finding unknown region
  sure_fg = np.uint8(sure_fg)
  unknown = cv2.subtract(sure_bg,sure_fg)
    
  # Marker labelling
  ret, markers = cv2.connectedComponents(sure_fg)
      
  # Add one to all labels so that sure background is not 0, but 1
  markers = markers+1

      
  # Now, mark the region of unknown with zero
  markers[unknown==255] = 0
  markers = cv2.watershed(img,markers)
  img[markers == -1] = [255,0,0]

  im1 = cv2.cvtColor(img,cv2.COLOR_HSV2RGB)
  ShowImage('Watershed segmented image',im1,'gray')

  brain_mask = np.uint8(brain_mask)
  kernel = np.ones((8,8),np.uint8)
  closing = cv2.morphologyEx(brain_mask, cv2.MORPH_CLOSE, kernel)
  ShowImage('Closing', closing, 'gray')

  brain_out = img.copy()
  #In a copy of the original image, clear those pixels that don't correspond to the brain
  brain_out[closing==False] = (0,0,0)

#img_path="./static/WhatsApp_Image_2020-10-14_at_19.35.58.jpeg"
#image_detect(img_path)