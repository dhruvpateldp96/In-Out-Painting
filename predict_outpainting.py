
from segmentation_models import Unet, Nestnet, Xnet

import numpy as np
from keras import backend as K
from keras.models import Model, load_model
from keras.layers import Flatten, Dense, Dropout
from keras.layers import Conv2D
from keras.applications.resnet50 import ResNet50, preprocess_input
from keras.optimizers import Adam
from keras.preprocessing.image import ImageDataGenerator
from keras.models import load_model
import os
import sys
from PIL import Image
from skimage.color import rgb2gray
import numpy as np
from matplotlib import pyplot as plt
import cv2
from keras.callbacks import EarlyStopping, ModelCheckpoint, TensorBoard

TRAIN_DATASET_PATH='/home/dhruv/Allprojects/NIH-XRAY/Train/'
VALID_DATASET_PATH='/home/dhruv/Allprojects/NIH-XRAY/Validation/'
TEST_DATASET_PATH='/home/dhruv/Allprojects/NIH-XRAY/Test/'
IMAGE_SIZE    = (256, 256)
CROP_LENGTH   = 836
NUM_CLASSES   = 2
BATCH_SIZE    = 1  # try reducing batch size or freeze more layers if your GPU runs out of memory
FREEZE_LAYERS = 2  # freeze the first this many layers for training
NUM_EPOCHS    = 3
WEIGHTS_FINAL = 'model-cropped-final.h5'
NUMBER=0

def searchForPatches(filename,lines,index):

	for i in range(len(lines)):
		line=lines[i][0:-1]
		fields=line.split('#')
		if(filename == fields[0]):
			line=lines[i+index][0:-1]
			# print('index=',index)
			fields=line.split('#')
			# print('Returning!!',filename)
			return fields

	fields=['',0,0,155,155]		
	return fields
			
def random_crop(img, random_crop_size, filename,index,lines):
    # Note: image_data_format is 'channel_last'

    # Now we need to search for the filename in the patchfile and extract
    # the patches
    fields=searchForPatches(filename,lines,index)
    # print('filename',filename)
    # print('index',index)
    
    # line=lines[index][0:-1]
    # fields=line.split('#')
    # print(fields)

    x=0
    y=0
    dx=0
    dy=0

    # if(filename == fields[0]):

    x=int(fields[1])
    y=int(fields[2])
    dx=int(fields[3])
    dy=int(fields[4])
    img=img[y:(y+dy), x:(x+dx), :]
    img = cv2.resize(img,(224,224))
    img=img/255.0


    # print(x,y,dx,dy)
    # plt.imshow(img)
    # plt.show()
    # plt.imshow(img)
    # plt.show()
    # print(img)
    # print('numbers=',NUMBER)
    # NUMBER=NUMBER+1
    return img


def crop(img, random_crop_size):
    # Note: image_data_format is 'channel_last'
    # assert img.shape[2] == 3
    
    
    height, width = img.shape[0], img.shape[1]
    dy0, dx0 = 836,836
    x0 = 94
    y0 = 45
    img=img[y0:(y0+dy0), x0:(x0+dx0), :]
    img=img/255
    img = cv2.resize(img,(224,224))
    
    return img

def crop_generator(batches, crop_length,lines):#224
    """Take as input a Keras ImageGen (Iterator) and generate random
    crops from the image batches generated by the original iterator.
    """

    filenames=((batches.filenames))
    # for i in batches:
    # 	# print(i)
    # 	idx = (batches.batch_index - 1) * batches.batch_size
    # 	print(batches.filenames[idx : idx + batches.batch_size])
    print("-------------------------------------------------THIS IS VAL-----------------------------------------------------------------")
   
    while True:
	    batch_x= next(batches)
	        
	    # print('batch_shape=',batch_x.shape)
	        # print('batch_names=',batch_x.filenames)
	    batch_crops_inp = np.zeros((4,batch_x.shape[0], 224, 224,3))#224
	        # batch_crops_tar = np.zeros((batch_x.shape[0], 224, 224,3))
	    
	    # index=0    
	    for i in range(batch_x.shape[0]):            
	        for j in range(4):
	            batch_crops_inp[j][i] = random_crop(batch_x[i], (crop_length, crop_length),filenames[i],j,lines)
	            # index=index+1
	    batch_crops_inp=np.reshape(batch_crops_inp,(batch_crops_inp.shape[0]*batch_crops_inp.shape[1],224,224,3))        
	    batch_crops_out=out_painting_mask(batch_crops_inp)
	    # batch_crops_out=batch_crops_inp

	    batch_crops_inp=rgb2gray(batch_crops_inp)
	    batch_crops_inp=np.reshape(batch_crops_inp,(batch_crops_inp.shape[0],224,224,1))
	    # print(batch_crops_inp.shape,'inp')
	    # plt.imshow(batch_crops_inp[1,:,:,0],cmap='gray',vmin=0,vmax=1)
	    # # plt.imshow(batch_crops_inp[1])
	    # plt.show()
	    # print(batch_crops_out.shape,'out')
	    # plt.imshow(batch_crops_out[1,:,:,0],cmap='gray',vmin=0,vmax=1)
	    # # plt.imshow(batch_crops_out[1])
	    # plt.show()
	    # print(batch_crops_inp.shape,'inp')
	    # plt.imshow(batch_crops_inp[2,:,:,0],cmap='gray',vmin=0,vmax=1)
	    # # plt.imshow(batch_crops_inp[2])
	    # plt.show()
	    # print(batch_crops_out.shape,'out')
	    # plt.imshow(batch_crops_out[2,:,:,0],cmap='gray',vmin=0,vmax=1)
	    # # plt.imshow(batch_crops_out[2])
	    # plt.show()
	    # print(batch_crops_inp.shape,'inp')
	    # plt.imshow(batch_crops_inp[3,:,:,0],cmap='gray',vmin=0,vmax=1)
	    # # plt.imshow(batch_crops_inp[3])
	    # plt.show()
	    # print(batch_crops_out.shape,'out')
	    # plt.imshow(batch_crops_out[3,:,:,0],cmap='gray',vmin=0,vmax=1)
	    # # plt.imshow(batch_crops_out[3])
	    # plt.show()
	    print(batch_crops_out.shape,'out')
	    # print(batch_crops_inp.shape,'inp')
	   
	    # print(batch_crops_inp.shape,np.min(batch_crops_inp),np.max(batch_crops_inp))
	    # print(batch_crops_out.shape,np.min(batch_crops_out),np.max(batch_crops_out))
	    # yield(batch_crops_out,batch_crops_inp)

	    yield(batch_crops_out)

	    # return batch_crops_inp    
	        # yield (batch_crops_inp,batch_crops_tar)



def main():
	
	with open('/home/dhruv/Allprojects/Feature-Learning-for-Disease-Classification/PatchFiles/test_sml.txt') as f:
		lines3 = f.readlines()

	test_datagen = ImageDataGenerator()
	test_batches = test_datagen.flow_from_directory(TEST_DATASET_PATH,
                                                  target_size=(1024,1024),
                                                  shuffle=True,
                                                  class_mode=None,
                                                  batch_size=BATCH_SIZE)
	
	# train_datagen = ImageDataGenerator()
	# train_batches = train_datagen.flow_from_directory(TRAIN_DATASET_PATH,
 #                                                  target_size=(1024,1024),
 #                                                  shuffle=True,
 #                                                  class_mode=None,
 #                                                  batch_size=BATCH_SIZE)

	# valid_datagen = ImageDataGenerator()
	# valid_batches = valid_datagen.flow_from_directory(VALID_DATASET_PATH ,
 #    	                                              target_size=(1024,1024),
 #    	                                              shuffle=False,
 #        	                                          class_mode=None,
 #        	                                          batch_size=BATCH_SIZE)
	
	# train_crops_orig = crop_generator(train_batches, CROP_LENGTH,lines3) #224
	# valid_crops_orig = crop_generator_val(valid_batches, CROP_LENGTH,lines2)
	test_crops_orig = crop_generator(test_batches, CROP_LENGTH,lines3) #224
	model = Unet(backbone_name='resnet18', encoder_weights=None) # build U-Net
	model.compile(optimizer='Adam', loss='mean_squared_error')
	model.summary()
	model.load_weights('best_model.h5')

	# print('inpaited',in_painted_x.shape)
	# print('1 channel y',train_crops_1_ch.shape)
	# print(in_painted_x.shape)
	# print(train_crops_1_ch.shape)

	# callbacks = [EarlyStopping(monitor='val_loss', patience=2),
	#              ModelCheckpoint(filepath='best_model.h5', monitor='val_loss', save_best_only=True),
	#              TensorBoard(log_dir='./logs', histogram_freq=0, write_graph=True, write_images=True)]
	# model.fit_generator(generator=train_crops_orig,
 #                    steps_per_epoch=15,
 #                    validation_data=valid_crops_orig,
 #                    callbacks=callbacks,
 #                    validation_steps=15,
 #                    epochs=15)
	# model.save('outpaint.h5')


	predict = model.predict_generator(generator=test_crops_orig,steps=15)
	# predict = model.predict()
	print(predict.shape,'predict_batch_size')
	for i in range(50):
		plt.imshow(predict[i,:,:,0],cmap='gray',vmin=0,vmax=1)
		# plt.imshow(batch_crops_inp[1])
		plt.show()
		# plt.imshow(predict[2,:,:,0],cmap='gray',vmin=0,vmax=1)
		# # plt.imshow(batch_crops_out[1])
		# plt.show()

		# plt.imshow(predict[3,:,:,0],cmap='gray',vmin=0,vmax=1)
		# # plt.imshow(batch_crops_inp[1])
		# plt.show()
		# plt.imshow(predict[4,:,:,0],cmap='gray',vmin=0,vmax=1)
		# # plt.imshow(batch_crops_out[1])
		# plt.show()	

def out_painting_mask(batch_x):

	
	#Creating random mask dimensions for inpainting
	out_paint_x=np.zeros((batch_x.shape[0],224,224,3))
	
	width=224
	height=224


	for i in range(0,batch_x.shape[0]):
		mask=np.ones((224,224,3))

		#choosing h and w such that it conserves 50% of the image
		h=np.random.randint(50,224)
		w=np.random.randint(50,224)
		while not ((224-2*h)*(224-2*w) >=25088 and 2*h<224 and 2*w<224):
			h=np.random.randint(0,224)
			w=np.random.randint(0,224)
			# print('h',h)
			# print('w',w)
			# print((224-2*h)*(224-2*w))
			# print('*********************')
		
		#locations of masks
		
		mask[0:h,0:224,:]=0
		mask[224-h:224,0:224,:]=0
		mask[0:224,0:w,:]=0
		mask[0:224,224-w:224,:]=0

		# plt.imshow(batch_x[i])
		# plt.show()
		
		out_paint_x[i]=np.multiply(batch_x[i],mask)

		# plt.imshow(out_paint_x[i])
		# plt.show()
		
		
 
	return out_paint_x
	




if __name__=="__main__":
	main()

