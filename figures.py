# -*- coding: utf-8 -*-
"""
Figuras y visualizaciones
Tomás Larrain A.
13 de Agosto de 2014
"""

import numpy as np
import utils.ASRUtils as asr
import utils.miscUtils as miscUtils
import cv2


def plotGrilla(I,ii,jj,a,b,m):
	# Dibuja la grilla en colores intercalados
	for i in range(m):
		
		if i%2 == 0:
			I = miscUtils.drawPatch(I,(ii[i],jj[i]),a,b, 255, 255, 0)
		
		else:
			I = miscUtils.drawPatch(I,(ii[i],jj[i]),a,b, 0, 255, 255)

	cv2.namedWindow("Grilla")
	cv2.imshow("Grilla",np.uint8(I))
	cv2.waitKey()
	return I

def displayResults(correctPhoto, cantPhotosDict, cantPhotosSparse, cantPhotosDict, idxPhoto, idxPerson, rootPath, dispWidth, dispHeight):	
	cantPersonas = len(correctPhoto)
	possibleMatchPhotos = idxPhoto[cantPhotosDict:cantPhotosSparse+1]
	displayImage = np.array([])
	
	for i in range(cantPersonas):
		
		matchPhoto = correctPhoto[i]
		matchPhoto = int(matchPhoto%cantPhotosSparse)
		matchPhoto = possibleMatchPhotos[matchPhoto]
		matchPerson = int(correctPhoto[i])/int(cantPhotosSparse)
		matchPerson = idxPerson[matchPerson]
		
		queryPerson = idxPerson[i]
		queryPhoto = idxPhoto[idxTestPhoto]
		
		queryRoute = os.path.join(rootPath, queryPerson)
		queryPhotos = os.listdir(queryRoute)
		queryRoutePhoto = os.path.join(queryRoute, queryPhotos[queryPhoto])

		matchRoute = os.path.join(rootPath, matchPerson)
		matchPhotos = os.listdir(matchRoute)
		matchRoutePhoto = os.path.join(matchRoute, matchPhotos[matchPhoto])

		Iq = miscUtils.readScaleImage(queryRoutePhoto, dispWidth, dispHeight)
		Im = miscUtils.readScaleImage(matchRoutePhoto, dispWidth, dispHeight)

		fila = np.hstack((Iq,Im))
		displayImage = miscUtils.concatenate(fila, displayImage, 'vertical')

	cv2.namedWindow('Resultado', cv2.WINDOW_AUTOSIZE)
	cv2.imshow('Resultado', np.uint8(displayImage))
	cv2.waitKey()


width = 400
height = 400
a = 25*4
b = 25*4
m = 400

dataBase = "AR"
rootPath = miscUtils.getDataBasePath(dataBase)
routePhoto = rootPath + '01/'+'face_001_01.png'

I = cv2.imread(routePhoto)
I = cv2.resize(I,(width,height))	

iiDict,jjDict = asr.grilla_v2(height, width, a, b, m) # Grilla de m cantidad de parches

plotGrilla(I,iiDict,jjDict,a,b,m)
