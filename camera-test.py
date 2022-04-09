#Import
import pygame
from tkinter import Tk
import os
pygame.init()

#création écran
os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (0,0)
clock = pygame.time.Clock()
width = Tk().winfo_screenwidth()
height = Tk().winfo_screenheight()
midW = width //2
midH = height //2
FPS = 60

#création couleurs/polices
noir = 0,0,0
blanc = 255,255,255
bleu = 0,0,255
jaune = 255,255,0
rouge = 255,0,0
base_font = pygame.font.Font(None,20)
cote = 50 #longueur du coté du carré éjection

#screen
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("caméra-test")

#Image de fond
playerAnims = pygame.image.load("allanims.png").convert_alpha()
playerW,playerH = playerAnims.get_size()
tileW,tileH = playerW//14, playerH//22
playerTileset = [[playerAnims.subsurface(x,y,tileW,tileH)for x in range(0,playerW,tileW)]for y in range(0,playerH,tileH)]
tileSetImg = pygame.image.load("images\map.png").convert_alpha()
img = tileSetImg.subsurface(0,0,2666,1500)
wImg, hImg = img.get_size()
imgMap = tileSetImg.subsurface(0,1500,2666,1500)

imgOiseau = pygame.image.load("images\oiseau.png").convert_alpha()
birdImgX, birdImgY = imgOiseau.get_size()
tileBird = [imgOiseau.subsurface(x*500,0,500,500)for x in range(4)]

#élément de décors
class PlatForme:
    def __init__(self,x,y,xplat,yplat,long,larg,color,img):
        """
        x,y : coordonnées du coin de l'image
        xPlat,yPlat : coordonées du coin de colision
        long,larg : dimension taille colision
        couleur : si aucune image
        """
        self.x, self.y = x, y
        self.xPlat, self.yPlat = xplat, yplat
        self.long, self.larg  = long, larg
        self.color = color
        self.img = img
    
    def afficher(self,baryX,baryY):
        X, Y = self.x - baryX + midW, self.y - baryY + midH
        Xcoll, Ycoll = self.xPlat - baryX + midW, self.yPlat - baryY + midH

        if baryX < midW:
            X = self.x
            Xcoll = self.xPlat
        if baryY < midH:
            Y = self.y
            Ycoll = self.yPlat
        if baryX > wImg - midW:
            X = self.x - wImg + width
            Xcoll = self.xPlat - wImg + width
        if baryY > hImg - midH:
            Y = self.y - hImg + height
            Ycoll = self.yPlat - hImg + height
        if self.img != None:
            screen.blit(self.img,(X,Y))
            #show Colisions
            pygame.draw.rect(screen,self.color,pygame.Rect(Xcoll,Ycoll,self.long,self.larg),4)
            return 
        return pygame.draw.rect(screen,self.color,pygame.Rect(X,Y,self.long,self.larg))

#joueur
class Player:
    def __init__(self,x,y,color,touche):
        self.x = x
        self.y = y
        self.X = x
        self.Y = y
        self.color = color
        self.mvt = [False,False,False,False]
        self.touches = touche
        self.outside = False

    def action(self):
        if self.mvt[0] and self.y >= 4:
            self.y -= 4
        if self.mvt[1] and self.y <= hImg-14:
            self.y += 4
        if self.mvt[2] and self.x >= 4:
            self.x -= 4
        if self.mvt[3] and self.x <= wImg-14:
            self.x += 4
    
    def showStat(self,baryX,baryY,showX):
        coor = base_font.render(f"{self.x},{self.y}",True,rouge)
        screen.blit(coor,(showX,10))
        self.X = self.x - baryX + midW
        self.Y = self.y - baryY + midH
        coor2 = base_font.render(f"{self.X},{self.Y}",True,rouge)
        screen.blit(coor2,(showX,30))

    def findCenter(self,baryX,baryY):
        #baryX, baryY = coordonnées du centre des deux joueurs
        #cote : La longueur du coté du carré lorqu'on sort de l'écran
        self.outside = False
        self.X = self.x - baryX + midW
        self.Y = self.y - baryY + midH

        #Le joueur est trop proche des bords de l'image
        if baryX < midW:
            self.X = self.x
        if baryY < midH:
            self.Y = self.y
        if baryX > wImg - midW:
            self.X = self.x - wImg + width
        if baryY > hImg - midH:
            self.Y = self.y - hImg + height
        
        #Le joueur est en dehors de la fenêtre d'affichage
        if ((self.X < cote//2 and baryX > midW) or (self.X > width-cote//2 and baryX < wImg-midW)
            or (self.Y < cote//2 and baryY > midH) or (self.Y > height-cote//2 and baryY < hImg-midH)):

            self.outside = True
            self.xSquare, self.ySquare = self.X-cote//2,self.Y-cote//2
            if self.x <= cote//2:
                self.X = self.x
                self.xSquare = 0
            elif self.X <= cote//2:
                self.X = cote//2
                self.xSquare = self.X-cote//2
            elif self.x >= wImg - cote//2:
                self.X = width - wImg + self.x
                self.xSquare = width - cote
            elif self.X >= width - cote//2:
                self.X = width - cote//2
                self.xSquare = self.X-cote//2
            
            if self.y <= cote//2:
                self.Y = self.y
                self.ySquare = 0
            elif self.Y <= cote:
                self.Y = cote//2
                self.ySquare = self.Y-cote//2
            elif self.y >= hImg - cote//2:
                self.Y = height - hImg + self.y
                self.ySquare = height - cote
            elif self.Y >= height - cote//2:
                self.Y = height - cote//2
                self.ySquare = self.Y-cote//2

            pygame.draw.rect(screen,rouge,(self.xSquare,self.ySquare,cote,cote),2)
    
    def afficher(self):
        return pygame.draw.rect(screen,self.color,pygame.Rect(self.X,self.Y,10,10))

#caméra
class Camera:
    def __init__(self,x,y,long,haut,img):
        self.x = x 
        self.y = y
        self.long = long
        self.haut = haut
        self.img = img
    
    def set_cam(self,px,py,wp,hp):
        """
        px, py = baryX, baryY
        wp, hp = longueur hauteur du perso
        """
        self.offsetX = self.x+px+wp//2-midW
        self.offsetY = self.y+py+hp//2-midH
        if px < midW:
            self.offsetX = self.x
        if px > self.long - midW:
            self.offsetX = self.x + self.long - width
        if py < midH:
            self.offsetY = self.y
        if py > self.haut - midH:
            self.offsetY = self.y + self.haut - height
        return screen.blit(self.img,(-self.offsetX//2,-self.offsetY//2))
        
    
    def splitScreen(self):
        return screen.blit(self.img,(self.x,self.y))


class decorsElmt:
    def __init__(self,x,y,long,larg,couleur,vit,img):
        self.x = x
        self.y = y
        self.long = long
        self.larg = larg
        self.color = couleur
        self.vit = vit
        self.img = img
        self.count = 0
    
    def dpct(self):
        if self.x <0:
            self.x = wImg
        elif self.x > wImg:
            self.x = 0
        if self.y < 0:
            self.y = hImg
        elif self.y > hImg:
            self.y = 0

        self.x += self.vit[0]
        self.y += self.vit[1]
    
    def afficher(self,baryX,baryY,Frame):
        if Frame %5 == 0:
            if self.count>2:
                self.count = 0
            else:
                self.count += 1
        X = self.x - baryX + midW
        Y = self.y - baryY + midH
        if baryX < midW:
            X = self.x
        if baryY < midH:
            Y = self.y
        if baryX > wImg - midW:
            X = self.x - wImg + width
        if baryY > hImg - midH:
            Y = self.y - hImg + height
        if self.img == None:
            return pygame.draw.rect(screen,self.color,pygame.Rect(X,Y,self.long,self.larg))
        return screen.blit(self.img[self.count],(X,Y))

def findBary(joueurs,cx,cy):
    sumX = cx
    sumY = cy
    for j in joueurs:
        sumX += j.x
        sumY += j.y
    baryX = sumX // (len(joueurs)+1)
    baryY = sumY // (len(joueurs)+1)
    return baryX, baryY

def needSplit(joueurs,img,camX,camY):
    for j in joueurs:
        if j.outside:
            newImg = img.subsurface((camX+ j.x)//2,(camY+ j.y)//2,50,50)
            newCam = Camera(j.xSquare, j.ySquare,cote,cote,newImg)
            newCam.splitScreen()

def checkInput(joueurs):
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE: #quitter
                return True
            for j in joueurs:
                if event.key == j.touches[0]: #haut
                    j.mvt[0] = True

                elif event.key == j.touches[1]: #bas
                    j.mvt[1] = True

                elif event.key == j.touches[2]: #gauche
                    j.mvt[2] = True

                elif event.key == j.touches[3]: #droite
                    j.mvt[3] = True
            
        if event.type == pygame.KEYUP:
            for j in joueurs:
                if event.key == j.touches[0]: #haut
                    j.mvt[0] = False

                elif event.key == j.touches[1]: #bas
                    j.mvt[1] = False

                elif event.key == j.touches[2]: #gauche 
                    j.mvt[2] = False

                elif event.key == j.touches[3]: #droite
                    j.mvt[3] = False
    

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
#~~~~~~~~~~~~~~~~~~~~~~ MAIN ~~~~~~~~~~~~~~~~~~~~~~#
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

#tout les joueurs
j1 = Player(wImg//2-30,hImg//2,noir,[119,115,97,100])
j2 = Player(wImg//2+30,hImg//2,blanc,[273,274,276,275])
j3 = Player(560,275,rouge,[261,258,257,259])
joueurs = [j1,j2]

#toutes les plates formes
carte = PlatForme(wImg//2-1333,hImg//2-790,wImg//2-550,hImg//2+75,1100,100,rouge,imgMap)
pf1 = PlatForme(wImg//2-300,hImg//2-100,wImg//2-300,hImg//2-100,200,20,rouge,None)
pf2 = PlatForme(wImg//2-100,hImg//2-200,wImg//2-100,hImg//2-200,200,20,rouge,None)
pf3 = PlatForme(wImg//2+100,hImg//2-100,wImg//2+100,hImg//2-100,200,20,rouge,None)
collision = [carte,pf1,pf2,pf3]

#tout les éléments de décors en mouvement
oiseau1 = decorsElmt(midW,height//4,20,10,jaune,[-10,0],tileBird)
oiseau2 = decorsElmt(midW,midH+20,50,20,bleu,[-5,3],tileBird)
elmts = [oiseau1]

#initialisation de l'image de fond pour qu'elle soit centrée
cam = Camera(wImg//2-midW,hImg//2-midH,wImg, hImg,img)

mainLoop = True
Frame = 0
while mainLoop:
    if checkInput(joueurs):
        break
    #on actualise les joueurs
    for j in joueurs:
        j.action()

    #on actualise les éléments de décors
    for e in elmts:
        e.dpct()
    
    #calcul du barycentre entre les joueurs et le centre de la map
    baryX,baryY = findBary(joueurs,cam.x+midW,cam.y+midH)

    #on gère l'affichage du fond
    cam.set_cam(baryX,baryY,10,10)
    needSplit(joueurs,img,cam.offsetX,cam.offsetY)

    #affichange : map, joueur, éléments
    for e in elmts:
        e.afficher(baryX,baryY,Frame)
    for map in collision:
        map.afficher(baryX,baryY)
    for j in joueurs:
        j.findCenter(baryX,baryY)
        j.afficher()

    pygame.display.update()
    if Frame>58:
        Frame = 0
    else:
        Frame += 1
    clock.tick(FPS)
    
pygame.quit()