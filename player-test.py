import pygame
pygame.init()

#création écran
clock = pygame.time.Clock()
width = 800
height = 500
FPS = 60
animSpeed = 30

#création couleur
noir = 0,0,0
blanc = 255,255,255
rouge = 255,0,0
base_font = pygame.font.Font(None,20)

#screen
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Player - Test")

#Images
playerAnims = pygame.image.load("allanims.png").convert_alpha()
playerW,playerH = playerAnims.get_size()
tileW,tileH = playerW//14, playerH//22
playerTileset = [[playerAnims.subsurface(x,y,tileW,tileH)for x in range(0,playerW,tileW)]for y in range(0,playerH,tileH)]

#décors/ maps
platformes = [pygame.Rect(0,height-20,width,20),pygame.Rect(width//2,0,100,100),pygame.Rect(width//2,500,50,50)]

class Perso:
    def __init__(self,nom,img):
        self.nom = nom
        self.img = img
        self.dim = [(49,45,22,20),(46,66,29,27),(41,91,38,36)]

class Player:
    def __init__(self,x,y,ori,touches,nom,color,perso):
        self.x = x
        self.y = y
        self.ori = ori #1 -> droite / 0 -> gauche
        self.touches = touches
        self.nom = nom
        self.color = color
        self.playSet = perso.img
        self.offset = [(49,45,22,20),(46,66,29,27),(41,91,38,36)]
        self.corps = [pygame.Rect(self.x+49,self.y+45,22,20),pygame.Rect(self.x+46,self.y+66,29,27),pygame.Rect(self.x+41,self.y+91,38,36)]

        self.vit = 0
        self.dpct = [0,0]
        self.idAnim = [0,0,1] #nb anim , index anim , vitesse
        self.fallCount = 0
        self.puissanceSaut = 0

        #booléen
        #haut,bas,gauche,droite,attaque1,attaque2
        self.mvt = [False,False,False,False,False,False]
        self.sol = False
        self.air = True
        self.isHit = False
        self.isHurt = False
    
    def action(self):
        #réinitialisation
        self.dpct[1] = self.fall() #tombe en continue (gravité)
        self.isLeft,self.isRight,self.isCrouch,self.isJump = False,False,False,False

        #Saut
        if self.mvt[0] and not self.sol:
            platformes.append(pygame.Rect(self.x,self.y+128,128,10))
            self.puissanceSaut = 0
            self.isJump = False

        elif self.mvt[0] and self.sol and not self.isCrouch:
            if self.puissanceSaut > 200:
                self.puissanceSaut = 200
                self.mvt[0] = False
            self.puissanceSaut += 10
                
        elif self.puissanceSaut>5 and not self.mvt[0]:
            self.fallCount = 0
            self.isJump = True
            high = self.puissanceSaut // 5
            self.y -= high
            self.puissanceSaut -= high

            if self.idAnim[0] in [7,18]:
                self.checkFrame(6,5)
                self.idAnim[2] = 5
            else:
                if self.ori == 1:
                    self.idAnim[0] = 7
                else:
                    self.idAnim[0] = 18
                self.idAnim[1] = 0

        #Touche du bas
        if self.mvt[1]:
            #fast-fall
            if self.air:
                print("fast fall")
            #accroupi/traverser
            else:
                self.isCrouch = True
                if self.idAnim[0] in [1,12]:
                    self.checkFrame(2,30)
                    self.idAnim[2] = 30
                else:
                    if self.ori == 1:
                        self.idAnim[0] = 1
                    else:
                        self.idAnim[0] = 12
                    self.idAnim[1] = 0

                if self.dpct[0]>0.1:
                    self.dpct[0] -= 0.1
                elif self.dpct[0]<-0.1:
                    self.dpct[0] += 0.1
                else:
                    self.dpct[0] = 0
        
        #touche de gauche
        if self.mvt[2] and not self.mvt[3]:
            #accélération gauche
            self.isLeft = True
            self.ori = 0
            if self.idAnim[0] == 19:
                self.checkFrame(8,6)
                self.idAnim[2] = 6
            else: 
                self.idAnim[0] = 20
                self.idAnim[1] = 0

            if self.dpct[0] > -8:
                self.dpct[0] -= 0.3

        #touche de droite
        if self.mvt[3] and not self.mvt[2]:
            #accélération droite
            self.isRight = True
            self.ori = 1
            if self.idAnim[0] == 9:
                self.checkFrame(8,6)
                self.idAnim[2] = 6
            else:
                self.idAnim[0] = 9
                self.idAnim[1] = 0

            if self.dpct[0] < 8:
                self.dpct[0] += 0.3

        #attaque 1
        if self.mvt[4]:
            print("attaque1")
        #attaque 2
        if self.mvt[5]:
            print("attaque2")
        
        #Rien
        if self.sol and not self.isCrouch and not self.isLeft and not self.isRight:
            
            if self.idAnim[0] in [10,21]:
                self.checkFrame(4,30)
                self.idAnim[2] = 30
            else:
                if self.ori == 1:
                    self.idAnim[0] = 10
                else:
                    self.idAnim[0] = 21
                self.idAnim[1] = 0

            if self.dpct[0]>0.2:
                self.dpct[0] -= 0.2
            elif self.dpct[0]<-0.2:
                self.dpct[0] += 0.2
            else:
                self.dpct[0] = 0
    
    def collision_test(self,platformes):
        for tile in platformes:
            for index,boule in enumerate(self.corps):
                if boule.colliderect(tile):
                    return tile,index
        return None,None
    
    def move(self,platformes):
        for boule in self.corps:
            boule.x += self.dpct[0]

        col_Plat,index_col = self.collision_test(platformes)

        if col_Plat == None:
            self.x += self.dpct[0]
        else:
            if self.dpct[0]>0:
                self.x = col_Plat.left - self.offset[index_col][0] - self.offset[index_col][2]
            elif self.dpct[0]<0:
                self.x = col_Plat.right - self.offset[index_col][0] + 1
            self.dpct[0] = 0
            return
        
        for boule in self.corps:
            boule.x -= self.dpct[0]
            boule.y += self.dpct[1]
        
        col_Plat,index_col = self.collision_test(platformes)

        if col_Plat == None:
            self.y += self.dpct[1]
            self.air = True
            self.sol = False
        else:
            if self.dpct[1] > 0: 
                self.y = col_Plat.top-128
                self.air = False
                self.sol = True
            else:
                print('oui')
                self.y = col_Plat.bottom + self.offset[index_col][1]
                self.air = True
                self.isJump = False
                self.sol = False
            self.dpct[1] = 0
            
    def fall(self):
        self.fallCount += 0.5
        if self.fallCount > 11:
            self.fallCount = 11
        return int(self.fallCount)

    def checkFrame(self,nbAnim,animSpeed):
        if self.idAnim[1] < nbAnim * animSpeed-1:
            self.idAnim[1] += 1
        else:
            self.idAnim[1] = 0
    
    def devColi(self):
        for hurt in self.corps:
            pygame.draw.rect(screen,rouge,hurt,2)
    
    def devCoor(self):
        coor = base_font.render(f"Coor : {int(self.x)},{int(self.y)}",True,rouge)
        vitesse = base_font.render(f"Vitesse : {round(self.dpct[0],2)},{round(self.dpct[1],2)}",True,rouge)
        anim = base_font.render(f"Animation : {self.idAnim[0]},{self.idAnim[1]//self.idAnim[2]}",True,rouge)
        puissaut = base_font.render(f"Saut : {self.puissanceSaut}",True,rouge)
        screen.blit(coor,(10,10))
        screen.blit(vitesse,(10,30))
        screen.blit(anim,(10,50))
        screen.blit(puissaut,(10,70))
    
    def show(self):
        self.move(platformes)
        self.corps = [pygame.Rect(self.x+49,self.y+45,22,20),pygame.Rect(self.x+46,self.y+66,29,27),pygame.Rect(self.x+41,self.y+91,38,36)]
        screen.blit(self.playSet[self.idAnim[0]][self.idAnim[1]//self.idAnim[2]],(self.x,self.y))
        self.devColi()
        self.devCoor()
        
#Perso
snowgirl = Perso("Snowgirl",playerTileset)

#joueurs
j1 = Player(500,128,1,[32,115,97,100,260,261],"Mattchau",blanc,snowgirl)
joueurs = [j1]

mainLoop = True

while mainLoop:
    screen.fill(noir)

    for plat in platformes:
        pygame.draw.rect(screen,blanc,plat)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            mainLoop = False
        
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                mainLoop = False
            
            for j in joueurs:           
                if event.key == j.touches[0]: #haut
                    j.mvt[0] = True
                if event.key == j.touches[1]: #bas
                    j.mvt[1] = True
                if event.key == j.touches[2]: #gauche
                    j.mvt[2] = True
                if event.key == j.touches[3]: #droite
                    j.mvt[3] = True
                if event.key == j.touches[4]: #attaque1
                    j.mvt[4] = True
                if event.key == j.touches[5]: #attaque2
                    j.mvt[5] = True
        
        elif event.type == pygame.KEYUP:

            for j in joueurs:
                if event.key == j.touches[0]: #haut
                    j.mvt[0] = False
                if event.key == j.touches[1]: #bas
                    j.mvt[1] = False
                if event.key == j.touches[2]: #gauche
                    j.mvt[2] = False
                if event.key == j.touches[3]: #droite
                    j.mvt[3] = False
                if event.key == j.touches[4]: #attaque1
                    j.mvt[4] = False
                if event.key == j.touches[5]: #attaque2
                    j.mvt[5] = False
    
    for j in joueurs:
        j.action()
        j.show()
    pygame.display.update()
    clock.tick(FPS)

pygame.quit()