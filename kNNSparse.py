# -*- coding: utf-8 -*-
""""
Pruebas para el algoritmo propuesto kNN-Sparse
Tomás Larrain A.
6 de junio de 2014
"""

import numpy as np
import utils.ASRUtils as asr
import utils.miscUtils as miscUtils
import os
import time
import cv2

# Parametros
m = 600			# Cantidad de patches seleccionados por foto para A
m2 = 150 		# Cantidad de patches para Matriz S
height = 100	# Alto del resize de la imagen
width = 100		# Ancho del resize de la imagen
a = 18			# Alto del patch
b = 18			# Ancho del patch
alpha = 0.5 	# Peso del centro
Q = 5			# Cluster Padres
R = 5 			# Cluser Hijos
sub = 1			# Subsample
sparseThreshold = 0 # Umbral para binarizar la representación sparse
cantPersonas = 20 # Cantidad de personas para el experimento

# Inicializacion Variables
cantIteraciones = 100
porcAcumulado = 0
testTimeAcumulado = 0
trainTimeAcumulado = 0


# Datos de entrada del dataset
dataBase = "ORL"
rootPath = miscUtils.getDataBasePath(dataBase)
cantPhotos = miscUtils.photosPerPerson(rootPath)
cantPhotosDict = 2
cantPhotosSparse = cantPhotos-cantPhotosDict-1

U = asr.LUT(height,width,a,b) # Look Up Table
ii,jj = asr.grilla(height,width,a,b,m) # Generacion de esquinas superiores izquierdas aleatorias (i,j)

for it in range(cantIteraciones):
	
	print "Iteracion ", it+1, " de ", cantIteraciones
	print "Entrenando..."
	
	beginTime = time.time()

	# Entrenamiento: Diccionario A y Parches Sparse
	YC = np.array([])
	YP = np.array([])

	# Seleccion aleatoria de individuos
	idxPhoto, idxPerson = miscUtils.randomSelection(rootPath, cantPhotos, cantPersonas)
	

	for i in range(cantPersonas):
		
		route = os.path.join(rootPath,idxPerson[i])
		photos = os.listdir(route)
		Y = np.array([])
		
		for j in range(cantPhotosDict):
			
			
			routePhoto = os.path.join(route,photos[idxPhoto[j]])
			I = asr.readScaleImage(routePhoto,width,height)

			Yaux = asr.patches(I,ii,jj,U,a,b,alpha,sub)
		
			if len(Y) == 0:
				Y = Yaux.copy()
			else:
				Y = np.vstack((Y,Yaux))
				
		
		YCaux,YPaux = asr.modelling(Y,Q,R) # Clusteriza la matriz Y en padres e hijos

		if len(YC) == 0:
			YC = YCaux.copy()
			YP = YPaux.copy()
		else:
			YC = np.vstack((YC,YCaux))
			YP = np.vstack((YP,YPaux))
		

	Y = np.array([])
	Ysparse = np.array([])

	ii,jj = asr.grilla(height,width,a,b,m2)

	for i in range(cantPersonas):
		route = os.path.join(rootPath,idxPerson[i])
		photos = os.listdir(route)
		
		for j in range(cantPhotosSparse):
			idx = j+cantPhotosDict
			routePhoto = os.path.join(route,photos[idxPhoto[idx]])

			I = asr.readScaleImage(routePhoto,width,height)
			# Generacion de esquinas superiores izquierdas aleatorias (i,j)
			Y = asr.patches(I,ii,jj,U,a,b,alpha,sub)
			alpha1 = asr.normL1_omp(Y,YC,R)
			
			if len(Ysparse) == 0:
				Ysparse = alpha1.copy()
			else:
				Ysparse = np.hstack((Ysparse,alpha1))
				

	Ysparse = Ysparse.transpose()
	YsparseBinary = (Ysparse < -sparseThreshold) | (Ysparse > sparseThreshold)
	# YsparseBinary = Ysparse != 0
	

	trainTime = time.time() - beginTime
	trainTimeAcumulado += trainTime
	aciertos = 0
	responses = np.zeros(0)

	for i in range(cantPersonas):
		responses = np.append(responses,float(idxPerson[i])*np.ones(cantPhotosSparse))

	

	print "Testing..."
	beginTime = time.time()
	for i in range(cantPersonas):
		
		route = os.path.join(rootPath,idxPerson[i])
		photos = os.listdir(route)
		routePhoto = os.path.join(route,photos[idxPhoto[cantPhotos-1]])
		
		I = asr.readScaleImage(routePhoto,width,height)
		Y = asr.patches(I,ii,jj,U,a,b,alpha,sub)

		alpha1 = asr.normL1_omp(Y,YC,R)
		# alpha1 = asr.normL1_lasso(Y,YC,R)
		
		resto = float('inf')
		restoAux = float('inf')
		correcto = cantPersonas+1
		alpha1 = alpha1.transpose()
		# alphaBinary = (alpha1 < -sparseThreshold) | (alpha1 > sparseThreshold)
		alphaBinary = alpha1 != 0
		
		for j in range(cantPersonas*cantPhotosSparse):
			
			Yclass = YsparseBinary[j*m2:(j+1)*m2,:]
			resta = np.abs(Yclass-alphaBinary)
			restoAux = np.sum(resta)

			if restoAux < resto:
				correcto = responses[j]
				resto = restoAux

		if int(correcto) == int(idxPerson[i]):
			aciertos += 1
	
	testTime = time.time() - beginTime
	testTimeAcumulado += testTime/cantPersonas	
	print "Porcentaje Aciertos: " , float(aciertos)/cantPersonas*100,	"%\n"	
	porcAcumulado += float(aciertos)/cantPersonas*100


print "Experimento finalizado"
print "Tiempo de entrenamiento promedio: ", trainTimeAcumulado/cantIteraciones, " segundos"
print "Tiempo de testing promedio: ", testTimeAcumulado/cantIteraciones, " segundos/persona"
print "Porcentaje acumulado: ", porcAcumulado/cantIteraciones, "%"



