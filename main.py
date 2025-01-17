#===============================================================================
# Exemplo: segmentação de uma imagem em escala de cinza.
#-------------------------------------------------------------------------------
# Autor: Bogdan T. Nassu
# Estudantes: Mayara Dal Vesco Hoger e Guilherme Corrêa Koller
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
THRESHOLD = 0.8  # 0.8 arroz e 0.3 texto
ALTURA_MIN = 1000
LARGURA_MIN = 1000
N_PIXELS_MIN = 100  # 100 arroz e 20 texto
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

    return np.where(img > threshold, ARROZ, NO_ARROZ)

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

    def inunda(label, img, linha, coluna, n_pixels, coordenadas):
        if coluna < coordenadas['L']:
            coordenadas['L'] = coluna

        if coluna > coordenadas['R']:
            coordenadas['R'] = coluna

        if linha < coordenadas['B']:
            coordenadas['B'] = linha

        if linha > coordenadas['T']:
            coordenadas['T'] = linha

        img[linha][coluna] = label
        n_pixels = n_pixels + 1
        if linha-1 >=0 and img[linha-1][coluna] == ARROZ: 
            n_pixels, coordenadas = inunda(label, img, linha-1, coluna, n_pixels, coordenadas)
        if coluna-1 >=0 and img[linha][coluna-1] == ARROZ: 
            n_pixels, coordenadas = inunda(label, img, linha, coluna-1, n_pixels, coordenadas)
        if linha < len(img) and img[linha+1][coluna] == ARROZ: 
            n_pixels, coordenadas = inunda(label, img, linha+1, coluna, n_pixels, coordenadas)
        if coluna < len(img[linha]) and img[linha][coluna+1] == ARROZ: 
            n_pixels, coordenadas = inunda(label, img, linha, coluna+1, n_pixels, coordenadas)
        return n_pixels, coordenadas

    label = 2
    for linha, value in enumerate(img):
        for coluna, pix in enumerate (value):
            if pix == ARROZ:
                n_pixels, coordenadas = inunda(label, img, linha, coluna, n_pixels=0, coordenadas={'T': linha, 'L': coluna, 'B': linha, 'R':coluna})
                # verificar ruídos
                print(coordenadas['R'] - coordenadas['L'])
                if n_pixels < n_pixels_min and (coordenadas['T'] - coordenadas['B']) < altura_min and (coordenadas['R'] - coordenadas['L']) < largura_min: #ruído
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
