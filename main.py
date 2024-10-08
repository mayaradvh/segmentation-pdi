#===============================================================================
# Exemplo: segmentação de uma imagem em escala de cinza.
#-------------------------------------------------------------------------------
# Autor: Bogdan T. Nassu
# Universidade Tecnológica Federal do Paraná
#===============================================================================

import sys
import timeit
import numpy as np
import cv2

#===============================================================================

INPUT_IMAGE =  'arroz.bmp'

# TODO: ajuste estes parâmetros!
NEGATIVO = False
THRESHOLD = 0.8
ALTURA_MIN = 1
LARGURA_MIN = 1
N_PIXELS_MIN = 100
ARROZ = 1.0
NO_ARROZ = 0.0

#===============================================================================

def binariza (img, threshold):
    ''' Binarização simples por limiarização.

Parâmetros: img: imagem de entrada. Se tiver mais que 1 canal, binariza cada
              canal independentemente.
            threshold: limiar.
            
Valor de retorno: versão binarizada da img_in.'''

    # TODO: escreva o código desta função.
    # Dica/desafio: usando a função np.where, dá para fazer a binarização muito
    # rapidamente, e com apenas uma linha de código!

    return np.where(img > threshold, ARROZ, NO_ARROZ).astype(np.float32)

#-------------------------------------------------------------------------------

def rotula (img, largura_min, altura_min, n_pixels_min):
    '''Rotulagem usando flood fill. Marca os objetos da imagem com os valores
[0.1,0.2,etc].

Parâmetros: img: imagem de entrada E saída.
            largura_min: descarta componentes com largura menor que esta.
            altura_min: descarta componentes com altura menor que esta.
            n_pixels_min: descarta componentes com menos pixels que isso.

Valor de retorno: uma lista, onde cada item é um vetor associativo (dictionary)
com os seguintes campos:

'label': rótulo do componente.
'n_pixels': número de pixels do componente.
'T', 'L', 'B', 'R': coordenadas do retângulo envolvente de um componente conexo,
respectivamente: topo, esquerda, baixo e direita.'''

    # TODO: escreva esta função.
    # Use a abordagem com flood fill recursivo.

    list_componentes = []

    def inunda(label, img, x, y, n_pixels, coordenadas):
        if x < coordenadas['R']:
            coordenadas['R'] = x

        if x > coordenadas['L']:
            coordenadas['L'] = x

        if y < coordenadas['T']:
            coordenadas['T'] = y

        if y > coordenadas['B']:
            coordenadas['B'] = y

        img[x][y] = label
        n_pixels = n_pixels + 1
        if x-1 >=0 and img[x-1][y] == ARROZ: 
            n_pixels, coordenadas = inunda(label, img, x-1, y, n_pixels, coordenadas)
        if y-1 >=0 and img[x][y-1] == ARROZ: 
            n_pixels, coordenadas = inunda(label, img, x, y-1, n_pixels, coordenadas)
        if x < len(img) and img[x+1][y] == ARROZ: 
            n_pixels, coordenadas = inunda(label, img, x+1, y, n_pixels, coordenadas)
        if y < len(img[x]) and img[x][y+1] == ARROZ: 
            n_pixels, coordenadas = inunda(label, img, x, y+1, n_pixels, coordenadas)
        return n_pixels, coordenadas

    label = 2
    for x, value in enumerate(img):
        for y, pix in enumerate (value):
            if pix == ARROZ:
                n_pixels, coordenadas = inunda(label, img, x, y, n_pixels=0, coordenadas={'T': y, 'L': x, 'B': y, 'R':x})
                # verificar ruídos
                if n_pixels < N_PIXELS_MIN: #ruído
                    np.where(img == label, NO_ARROZ, img) #coloca como fundo onde tem ruído
                else: # não ruído
                    componente = {'label': label, 'n_pixels': n_pixels, 'coordenadas': coordenadas} # salva o arroz
                    list_componentes.append(componente)
                    label = label + 1

    return (list_componentes)

#===============================================================================

def main ():

    # Abre a imagem em escala de cinza.
    img = cv2.imread (INPUT_IMAGE, cv2.IMREAD_GRAYSCALE)
    if img is None:
        print ('Erro abrindo a imagem.\n')
        sys.exit ()

    # É uma boa prática manter o shape com 3 valores, independente da imagem ser
    # colorida ou não. Também já convertemos para float32.
    img = img.reshape ((img.shape [0], img.shape [1], 1))
    img = img.astype (np.float32) / 255

    # Mantém uma cópia colorida para desenhar a saída.
    img_out = cv2.cvtColor (img, cv2.COLOR_GRAY2BGR)

    # Segmenta a imagem.
    if NEGATIVO:
        img = 1 - img
    img = binariza (img, THRESHOLD)
    cv2.imshow ('01 - binarizada', img)
    cv2.imwrite ('01 - binarizada.png', img*255)

    start_time = timeit.default_timer ()
    componentes = rotula (img, LARGURA_MIN, ALTURA_MIN, N_PIXELS_MIN)
    n_componentes = len (componentes)
    print ('Tempo: %f' % (timeit.default_timer () - start_time))
    print ('%d componentes detectados.' % n_componentes)

    # Mostra os objetos encontrados.
    for c in componentes:
        cv2.rectangle (img_out, (c['coordenadas']['L'], c['coordenadas'] ['T']), (c['coordenadas'] ['R'], c['coordenadas'] ['B']), (0,0,1))

    cv2.imshow ('02 - out', img_out)
    cv2.imwrite ('02 - out.png', img_out*255)
    cv2.waitKey ()
    cv2.destroyAllWindows ()


if __name__ == '__main__':
    main ()

#===============================================================================
