from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GL import *
from PIL import Image
import numpy

import math
import sys
import random
import time
import logging
import struct
import cv2
import matplotlib.pyplot as plt

px = -1.2
py = 0.5
pz = 23
x = 0
y = 0
redx = 1
redy = 1

imgHeight = 0
imgWidth = 0
bitmap_tex = None
window = None
ORANGE = (255,120,50)
GREEN = (0,255,0)
RED = (255,0,0)
BLUE = (0,0,255)
boardLines = []

def buttons(key,x,y):
    global redx,redy, pz, window
    logging.log(50,"buttons %s" % format(key))
    #logging.log(50,"redx %s" % redx)
    #logging.log(50,"redy %s" % redy)
    #logging.log(50,"pz %s" % pz)
    if key == b'a':
        #logging.log(50,"pressed a {0}".format(key))
        redx = redx-1
    if key == b'd':
        #logging.log(50,"pressed d {0}".format(key))
        redx = redx+5
    if key == b'w':
        #logging.log(50,"pressed w {0}".format(key))
        redy = redy+5
    if key == b's':
        #logging.log(50,"pressed s {0}".format(key))
        redy = redy-1
    if key == b'f':
        #logging.log(50,"pressed s {0}".format(key))
        pz = pz-1
    if key == b'g':
        #logging.log(50,"pressed s {0}".format(key))
        pz = pz+3
    if key == b' ':
        #logging.log(50,"STOP {0}".format(key))
        px = 0
        py = 0
    if key == b'\x1b': #/* escape */
        glutDestroyWindow(window = window);
        exit(0);
    redraw()

def redraw(*arg, **kwarg):
    global original_texture_id, altered_texture_id
    #logging.log(50,"A redraw %s" % original_texture_id)
    #logging.log(50,"B redraw %s" % altered_texture_id)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    draw_rect(is_display_altered = False, texture_id=original_texture_id)
    draw_rect(is_display_altered = True, texture_id=altered_texture_id)
    glutSwapBuffers()

def run_scene():
    global original_texture_id, altered_texture_id, window
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(1000, 700)
    glutInitWindowPosition(0, 0)
    window = glutCreateWindow("Minimal sphere OpenGL")
    lightning()
    
    original_texture_id, altered_texture_id = read_texture('Euro_Women_R1.png')
    
    glutDisplayFunc(redraw)
    glMatrixMode(GL_PROJECTION)
    #gluPerspective(40, 1, 1, 40)
    gluPerspective(45, 1, 0.1, 550.0)
    #glOrtho(0, 1000, 0, 1000, -1, 1)
    glMatrixMode(GL_MODELVIEW)
    gluLookAt(0, 0, 20,
              0, 0, 0,
              0, 1, 0)
    glPushMatrix()
    
    glutKeyboardFunc(buttons)
    glutTimerFunc(0, redraw, 0)
    glutReshapeFunc(redraw);
    glutMainLoop()
    return


def lightning():
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_LIGHTING)
    glEnable(GL_BLEND)
    glLightfv(GL_LIGHT0, GL_POSITION, [10, 4, 10, 1])
    glLightfv(GL_LIGHT0, GL_DIFFUSE, [0.8, 1, 0.8, 1])
    glLightf(GL_LIGHT0, GL_CONSTANT_ATTENUATION, 0.1)
    glLightf(GL_LIGHT0, GL_LINEAR_ATTENUATION, 0.05)
    glEnable(GL_LIGHT0)
    return


def draw_rect(*arg, is_display_altered=False, texture_id=None,**kwarg):
    global px, py, pz, imgWidth, imgHeight, x,y, redx, redy
    #logging.log(50,"draw_rect %s" % is_display_altered)
    xOffset = 0
    if is_display_altered:
        xOffset = 1.35
    
    glPushMatrix()
    glTranslatef(px+xOffset,py, -6+pz)
    glRotatef(180.0, 1.0, 0.0, 0.0)
    glEnable(GL_TEXTURE_2D)
    glBindTexture(GL_TEXTURE_2D, texture_id)
    glEnable(GL_TEXTURE_GEN_S)
    glEnable(GL_TEXTURE_GEN_T)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT);
    glTexGeni(GL_S, GL_TEXTURE_GEN_MODE, GL_OBJECT_LINEAR )
    glTexGeni(GL_T, GL_TEXTURE_GEN_MODE, GL_OBJECT_LINEAR )
    #glutSolidSphere(1, 50, 50)
    #glutSolidCube(50)
    # draw textured quad
    
    glColor3f(1,1,1)

    glEnable(GL_TEXTURE_2D)
    
    #logging.log(50,"draw_rect %s QUADS" % x)
    #logging.log(50,"draw_rect %s QUADS" % (x+redx))
    #logging.log(50,"draw_rect %s QUADS" % y)
    #logging.log(50,"draw_rect %s QUADS" % (y+redy))
    #glLineWidth(10)
    #glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
    glBegin(GL_QUADS)
    glTexCoord2f(0, 1)
    glVertex2f(x, y)
    glTexCoord2f(1, 1)
    glVertex2f(x+redx, y)
    glTexCoord2f(1, 0)
    glVertex2f(x+redx, y+redy)
    glTexCoord2f(0, 0)
    glVertex2f(x, y+redy)
    glEnd()
    
    glDisable(GL_TEXTURE_2D)
    glPopMatrix()
    return

def crop_for_zoom(img):
    global zoom_area
    #Returns a rectangular region from this image. The box is a 4-tuple defining the left, upper, right, and lower pixel coordinate
    return img.crop(zoom_area)

def read_texture(filename):
    global imgWidth, imgHeight, zoom_area, boardLines
    img = Image.open(filename)
    #logging.log(50,"img mode %s " % img.mode)
    print(img.width )
    print(img.height )
    img_data2=transform_goban(img)
    
    img_data2=goban_grid(img)
    
    img = crop_for_zoom(img)
    img_data = numpy.array(list(img.getdata()), numpy.int8)
    imgWidth = img.width
    imgHeight = img.height
    texture_id1 = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texture_id1)
    glPixelStorei(GL_UNPACK_ALIGNMENT, 1)
    #glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP)
    #glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
    glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_DECAL)
    img_format = GL_RGB if img.mode == "RGB" else GL_RGBA
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, img.size[0], img.size[1], 0,
             img_format, GL_UNSIGNED_BYTE, img_data)
             
    
    texture_id2 = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texture_id2)
    glPixelStorei(GL_UNPACK_ALIGNMENT, 1)
    #glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP)
    #glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
    glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_DECAL)
    img_format = GL_RGB if img.mode == "RGB" else GL_RGBA
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, img.size[0], img.size[1], 0,
             img_format, GL_UNSIGNED_BYTE, img_data2)
    return texture_id1,texture_id2

def transform_goban(img):
    global zoom_area, boardLines
    imgCopy = img.copy()
    somePixelValue = imgCopy.getpixel((0, 0))
    logging.log(50,"type {0}".format(type(imgCopy)))
    logging.log(50,"somePixelValue {0}".format(somePixelValue))
    #imgCopy.getpixel((x,y))
    #imgCopy.putdata(data, scale=1.0, offset=0.0)
    #imgCopy.putpixel((x,y),value)
    #for x in range(100):
    #    for y in range(100):
    #        imgCopy.putpixel((x,y),somePixelValue)
    put_cross(imgCopy, 535,692)
    put_cross(imgCopy, 124,637)
    put_cross(imgCopy, 303,531)
    put_cross(imgCopy, 613,551)
    
    corners=find_crosses(imgCopy)
    logging.log(50,"find_crosses {0}".format(corners))
    
    verticalMargin = 30
    horizontalMargin = 30
    zoom_area=(\
        max(0,min(a for (a,b) in corners)-horizontalMargin), max(0,min(b for (a,b) in corners)-verticalMargin),\
        min(img.width-1,max(a for (a,b) in corners)+horizontalMargin), min(img.height -1,max(b for (a,b) in corners)+verticalMargin)\
    )
    
    logging.log(50,"zoom_area {0}".format(zoom_area))
    
    
    
    #put_visible_cross(imgCopy, 535,692)
    #put_visible_cross(imgCopy, 124,637, color=(0,255,0))
    #put_visible_cross(imgCopy, 303,531, color=(0,255,0))
    #put_visible_cross(imgCopy, 613,551)
    ellipse_half_horiz= math.floor((zoom_area[2]-zoom_area[0]-2*horizontalMargin)/2.65)
    ellipse_half_vert = math.floor((zoom_area[3]-zoom_area[1]-2*verticalMargin)/2.65)
    imgCopy = crop_for_zoom(imgCopy)
    put_ellipse(imgCopy, math.floor((zoom_area[2]-zoom_area[0])/2), math.floor((zoom_area[3]-zoom_area[1])/2), a=ellipse_half_horiz, b=ellipse_half_vert )
    
    cropped_corners = [(a-zoom_area[0],b-zoom_area[1]) for (a,b) in corners]
    logging.log(50,"cropped_corners {0}".format(cropped_corners))
    fill_outside(imgCopy, cropped_corners)
    
    global left, top, right, bot, left_with_margin, top_with_margin, right_with_margin, bot_with_margin
    
    classify(imgCopy)
    ##
    ## looking for the exact board frame, removing the rest
    ##
    # top triangles
    # 1 top left
    imgBorders = green_dot_board_under_non_board(imgCopy)
    top_left_wide_sector = [(0,0),(top_with_margin[0],left_with_margin[1]),(top_with_margin[0],0),(0,left_with_margin[1])]
    lineA, lineB = get_green_line(imgBorders, top_left_wide_sector)
    boardLines.append((lineA, lineB),)
    #draw_line(imgBorders, lineA,lineB)
    top_left_outside_triangle = [(0,0),(-1000,math.floor(-1000*lineA+lineB)),(1000,math.floor(1000*lineA+lineB))]
    fill_triangle(imgBorders, top_left_outside_triangle)
    #fill_quad(imgBorders, top_left_wide_sector, color = BLUE)
    # 1 top right
    top_right_wide_sector = [(imgBorders.width,0),(top_with_margin[0],right_with_margin[1]),(top_with_margin[0],0),(imgBorders.width,right_with_margin[1])]
    lineA, lineB = get_green_line(imgBorders, top_right_wide_sector)
    boardLines.append((lineA, lineB),)
    #fill_quad(imgBorders, top_right_wide_sector, color = BLUE)
    #draw_line(imgBorders, lineA,lineB)
    top_left_outside_triangle = [(imgBorders.width,0),(-1000,math.floor(-1000*lineA+lineB)),(1000,math.floor(1000*lineA+lineB))]
    logging.log(50,"top_left_outside_triangle {0}".format(top_left_outside_triangle))
    fill_triangle(imgBorders, top_left_outside_triangle)
    
    reset_colors(imgBorders, src=[GREEN, BLUE], color=ORANGE)
    
    # top triangles
    # 1 bottom left
    imgBorders = green_dot_board_above_non_board(imgBorders)
    
    bot_left_wide_sector = [(0,img.height),(bot_with_margin[0],left_with_margin[1]),(bot_with_margin[0],img.height),(0,left_with_margin[1])]
    lineA, lineB = get_green_line(imgBorders, bot_left_wide_sector)
    boardLines.append((lineA, lineB),)
    #draw_line(imgBorders, lineA,lineB)
    bot_left_outside_triangle = [(0,img.height),(-1000,math.floor(-1000*lineA+lineB)),(1000,math.floor(1000*lineA+lineB))]
    fill_triangle(imgBorders, bot_left_outside_triangle)
    #fill_quad(imgBorders, bot_left_wide_sector, color = BLUE)
    # 1 top right
    bot_right_wide_sector = [(imgBorders.width,img.height),(bot_with_margin[0],right_with_margin[1]),(bot_with_margin[0],img.height),(imgBorders.width,right_with_margin[1])]
    lineA, lineB = get_green_line(imgBorders, bot_right_wide_sector)
    boardLines.append((lineA, lineB),)
    #fill_quad(imgBorders, bot_right_wide_sector, color = BLUE)
    draw_line(imgBorders, lineA,lineB)
    bot_left_outside_triangle = [(imgBorders.width,img.height),(-1000,math.floor(-1000*lineA+lineB)),(1000,math.floor(1000*lineA+lineB))]
    logging.log(50,"bot_left_outside_triangle {0}".format(bot_left_outside_triangle))
    fill_triangle(imgBorders, bot_left_outside_triangle)
    
    #reset_colors(imgBorders, src=[GREEN, BLUE], color=ORANGE)
    
    #result = numpy.array(list(imgCopy.getdata()), numpy.int8)
    result = numpy.array(list(imgBorders.getdata()), numpy.int8)
    return result

def goban_grid(img):
    global zoom_area, boardLines
    imgCopy = img.copy()
    
    verticalMargin = 30
    horizontalMargin = 30
    
    imgCopy = crop_for_zoom(imgCopy)
    
    global left, top, right, bot, left_with_margin, top_with_margin, right_with_margin, bot_with_margin
    
    classify(imgCopy)
    
    avgA = (boardLines[0][0]+boardLines[1][0]+boardLines[2][0]+boardLines[3][0])/4
    
    # groups of parallel lines
    grp1 = [(a,b) for (a,b) in boardLines if a <=avgA]
    grp2 = [(a,b) for (a,b) in boardLines if a >avgA]
    
    for (lineA, lineB) in grp1:
        draw_line(imgCopy, lineA,lineB, color = GREEN)
    
    for (lineA, lineB) in grp2:
        draw_line(imgCopy, lineA,lineB, color = BLUE)
    
    for i in range(0,19):
        logging.log(50,"img mode %s " % (i+0.5))
        draw_line(imgCopy, grp1[1][0]+(0.5+i)*(grp1[0][0]-grp1[1][0])/19,grp1[1][1]+(0.5+i)*(grp1[0][1]-grp1[1][1])/19, color = GREEN)
    
    result = numpy.array(list(imgCopy.getdata()), numpy.int8)
    return result

def put_cross(img, x, y, size =2, color = RED, thickness = 1):
    logging.log(50,"put_cross {0}".format((x,y)))
    img.putpixel((x,y),color)
    for delta in range(size):
        for thickDelta in range(thickness):
            thick = thickDelta-math.floor(thickness/2)
            img.putpixel((x+delta,y+thick),color)
            img.putpixel((x-delta,y+thick),color)
            img.putpixel((x+thick,y+delta),color)
            img.putpixel((x+thick,y-delta),color)

def reset_colors(img, src=[GREEN, BLUE], color=ORANGE):
    for (x,y) in [(a, b) for a in range(0,img.width) for b in range(0,img.height)]:
        if img.getpixel((x, y)) in src:
            img.putpixel((x,y),color)

def find_crosses(img, color = RED):
    result = []
    for (x,y) in [(a, b) for a in range(1,img.width-1) for b in range(1,img.height-1)]:
        if img.getpixel((x, y)) == color and \
            img.getpixel((x+1, y)) == color and \
            img.getpixel((x-1, y)) == color and \
            img.getpixel((x, y+1)) == color and \
            img.getpixel((x, y-1)) == color and \
            img.getpixel((x+1, y+1)) != color and \
            img.getpixel((x-1, y-1)) != color and \
            img.getpixel((x-1, y+1)) != color and \
            img.getpixel((x+1, y-1)) != color :
            result.append( (x, y))
    return result

def put_visible_cross(img, x, y, size =4, color = GREEN, thickness = 2):
    put_cross(img,x,y, size =20, color = color, thickness = 10)

def put_circle(img, x, y, size =100, color = RED, thickness = 1):
    logging.log(50,"put_circle {0}".format((x,y)))
    a = math.floor(size/2)
    b = math.floor(size/4)
    for (dx,dy) in [(da, db) for da in range(0,a-1) for db in range(0,b-1)]:
        if ((dx**2)/(a**2)+(dy**2)/(b**2))<=1:
            img.putpixel((x+dx,y+dy),color)
            img.putpixel((x-dx,y+dy),color)
            img.putpixel((x+dx,y-dy),color)
            img.putpixel((x-dx,y-dy),color)

def put_ellipse(img, x, y, a = math.floor(100/2), b = math.floor(100/4), color = RED, thickness = 1):
    logging.log(50,"put_ellipse {0}".format((x,y)))
    for (dx,dy) in [(da, db) for da in range(0,a-1) for db in range(0,b-1)]:
        if ((dx**2)/(a**2)+(dy**2)/(b**2))<=1:
            img.putpixel((x+dx,y+dy),color)
            img.putpixel((x-dx,y+dy),color)
            img.putpixel((x+dx,y-dy),color)
            img.putpixel((x-dx,y-dy),color)

def fill_outside(img, corners, color = RED ):
    global left, top, right, bot, left_with_margin, top_with_margin, right_with_margin, bot_with_margin
    zoom_area=(\
        min(a for (a,b) in corners), min(b for (a,b) in corners),\
        max(a for (a,b) in corners) ,max(b for (a,b) in corners)\
    )
    left  = [(a,b) for (a,b) in corners if a==zoom_area[0]][0]
    top   = [(a,b) for (a,b) in corners if b==zoom_area[1] and (a,b) not in [left]][0]
    right = [(a,b) for (a,b) in corners if a==zoom_area[2] and (a,b) not in [left, top]][0]
    bot   = [(a,b) for (a,b) in corners if b==zoom_area[3] and (a,b) not in [left, top, right]][0]
    
    margin = (zoom_area[2] - zoom_area[0])/20
    
    left_with_margin = (max(left[0]-margin,0), left[1])
    top_with_margin = (top[0], max(top[1]-margin,0))
    
    right_with_margin = (min(right[0]+margin,img.width-1), right[1])
    bot_with_margin = (bot[0], min(bot[1]+margin,img.height-1))
    
    logging.log(50,"fill_outside LEFT {0}".format(left))
    logging.log(50,"fill_outside TOP {0}".format(top))
    logging.log(50,"fill_outside RIGHT {0}".format(right))
    for (x,y) in [(a, b) for a in range(0,img.width) for b in range(0,img.height)]:
        #if x <= top[0] and y <= left[1] and y < x*(top[1]-left[1])/((top[0]-left[0]))+left[1]:
        #    img.putpixel((x,y),color)
        #if x <= bot[0] and y >= left[1] and y > x*(bot[1]-left[1])/((bot[0]-left[0]))+left[1]:
        #    img.putpixel((x,y),color)
        #if x >= top[0] and y <= right[1] and y < x*(right[1]-10-top[1]/2)/((right[0]-top[0]))+right[1]-10-right[0]*(right[1]-10-top[1]/2)/((right[0]-top[0])):
        #    img.putpixel((x,y),color)
        #if x >= bot[0] and y >= right[1] and y > (x-10)*(right[1]-bot[1])/((right[0]-bot[0]))+right[1]-right[0]*(right[1]-bot[1])/((right[0]-bot[0])):
        #    img.putpixel((x,y),color)
        #if y < top[1]-10 or y >= bot[1] or x < left[0]-10 or x > right[0]+10:
        #    img.putpixel((x,y),color)
        if not(is_in_quad(x,y,[left_with_margin,top_with_margin, right_with_margin, bot_with_margin])):
            img.putpixel((x,y),color)

def fill_triangle(img, corners, color=RED):
    for (x,y) in [(a, b) for a in range(0,img.width) for b in range(0,img.height)]:
        if is_in_triangle(x,y,corners):
            img.putpixel((x,y),color)

def fill_quad(img, corners, color=RED):
    for (x,y) in [(a, b) for a in range(0,img.width) for b in range(0,img.height)]:
        if is_in_quad(x,y,corners):
            img.putpixel((x,y),color)

#3 classes based on color: black, white, board
def classify(img):
    global ORANGE
    for (x,y) in [(a, b) for a in range(0,img.width) for b in range(0,img.height)]:
        color = img.getpixel((x, y))
        if color == RED:
            continue
        #if color[2] < 150:
        if color[2] < 160:
            # can be board or black
            #if color[0] > 150:
            if color[0] > 165:
                # too red, probably board
                img.putpixel((x,y),ORANGE)
            else:
                img.putpixel((x,y),(0,0,0))
        else:
            # can be white
            img.putpixel((x,y),(255,255,255))

def green_dot_board_under_non_board(img):
    global ORANGE, GREEN, RED
    result = img.copy()
    for (x,y) in [(a, b) for a in range(1,img.width-1) for b in range(1,img.height)]:
        color = img.getpixel((x, y))
        if(color == ORANGE):
            colorAbove = img.getpixel((x, y-1))
            colorLeft = img.getpixel((x-1, y))
            colorRight = img.getpixel((x+1, y))
            #logging.log(50,"FOUND BOARD {0}".format((x,y)))
            if colorAbove != ORANGE and colorAbove != GREEN and colorAbove != RED and colorLeft != RED and colorRight != RED:
                #logging.log(50,"FOUND BORDER {0}".format((x,y)))
                result.putpixel((x,y),BLUE)
    for x in range(0,img.width-1):
        for y in range(0,img.height):
            color = result.getpixel((x, y))
            if color == BLUE:
                result.putpixel((x,y),GREEN)
                break
    return result

def green_dot_board_above_non_board(img):
    global ORANGE, GREEN, RED
    result = img.copy()
    for (x,y) in [(a, b) for a in range(1,img.width-1) for b in range(1,img.height-1)]:
        color = img.getpixel((x, img.height-y))
        if(color == ORANGE):
            colorAbove = img.getpixel((x, img.height-y+1))
            colorLeft = img.getpixel((x-1, img.height-y))
            colorRight = img.getpixel((x+1, img.height-y))
            #logging.log(50,"FOUND BOARD {0}".format((x,y)))
            if colorAbove != ORANGE and colorAbove != GREEN and colorAbove != RED and colorLeft != RED and colorRight != RED:
                #logging.log(50,"FOUND BORDER {0}".format((x,y)))
                result.putpixel((x,img.height-y),BLUE)
    for x in range(0,img.width):
        for y in range(1,img.height):
            color = result.getpixel((x, img.height-y))
            if color == BLUE:
                result.putpixel((x,img.height-y),GREEN)
                break
    return result

# get the green line parameters (y = ax+b) by Least squares
# constraints: 
# - area of search
# - 2 forced areas (big corners)
# - "a" positive
def get_green_line(img, corners):
    green_dots = []
    for (x,y) in [(a, b) for a in range(1,img.width-1) for b in range(1,img.height) if is_in_quad(a,b,corners)]:
         color = img.getpixel((x, y))
         if(color == GREEN):
            green_dots.append((x,y))
    return linear_least_quares(green_dots)

def linear_least_quares(list_of_points):
    xs = numpy.array([a for (a,b) in list_of_points])
    ys = numpy.array([b for (a,b) in list_of_points])
    A = numpy.vstack([xs, numpy.ones(len(xs))]).T
    m, c = numpy.linalg.lstsq(A, ys, rcond=None)[0]
    return m,c

def draw_line(img, a,b, color = BLUE, xmin=0, xmax=1000000):
    for x in range(xmin, min(img.width-1, xmax)):
        y=a*x+b
        if y>=0 and y<img.height:
            img.putpixel((math.floor(x),math.floor(y)),color)

def getLine(ptA, PtB):
    a = (PtB[1]-ptA[1])/((PtB[0]-ptA[0]))
    b = PtB[1]-a*PtB[0]
    return a,b


def is_in_quad(x,y,quad):
    return is_in_triangle(x,y,[quad[0],quad[1],quad[2]]) or is_in_triangle(x,y,[quad[0],quad[2],quad[3]]) or is_in_triangle(x,y,[quad[1],quad[2],quad[3]])

def sign (p1, p2, p3):
    return (p1[0] - p3[0]) * (p2[1] - p3[1]) - (p2[0] - p3[0]) * (p1[1] - p3[1])


def is_in_triangle(x,y,triangle):
    d1 = sign((x,y), triangle[0], triangle[1])
    d2 = sign((x,y), triangle[1], triangle[2])
    d3 = sign((x,y), triangle[2], triangle[0])

    has_neg = (d1 < 0) or (d2 < 0) or (d3 < 0)
    has_pos = (d1 > 0) or (d2 > 0) or (d3 > 0)

    return not(has_neg and has_pos)

if __name__ == '__main__':
    logging.log(50,"is in quad {0}".format(is_in_quad(1,1,[(0,0),(2,2),(0,3),(3,0)])))
    xs = numpy.array([0, 1, 2, 3])
    ys = numpy.array([-1, 0.2, 0.9, 2.1])
    A = numpy.vstack([xs, numpy.ones(len(xs))]).T
    m, c = numpy.linalg.lstsq(A, ys, rcond=None)[0]
    #logging.log(50,"linear least square {0}".format([m, c]))
    
    logging.log(50,"linear least square {0}".format(linear_least_quares([(0,-1),(1,0.2),(2,0.9),(3,2.1)])))
    
    
    
    run_scene()