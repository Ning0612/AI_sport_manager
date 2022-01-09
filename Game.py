import pygame
import cv2
import mediapipe as mp
import time
import random
import HandTrackingModule as htm
import os
import math
import numpy as np

#load camera,screen,distance limit setting from txt file
f = open("basic_setting.txt",'r')
Setting_list = f.readlines()
wCam, hCam = int(Setting_list[3]),int(Setting_list[5])
WIDTH,HEIGHT = int(Setting_list[7]),int(Setting_list[9])
distance_limit = [int(Setting_list[11]),int(Setting_list[13])]#[250,380]
cap = cv2.VideoCapture(int(Setting_list[1])) 
f.close()

#init
pygame.init()
screen = pygame.display.set_mode((WIDTH,HEIGHT))#視窗長寬
pygame.display.set_caption("AI運動管家")
clock =pygame.time.Clock()
pygame.mixer.init()
detector = htm.handDetector(maxHands=1)
mpDraw = mp.solutions.drawing_utils
mpPose = mp.solutions.pose
pose = mpPose.Pose()
cap.set(3, wCam)
cap.set(4, hCam)
handx,handy=[0,0],[-100,-100]
mouse_xy=[0,-100]
Pose_LM=[]
Score = 0
runing = True
Menu_state ,Game_Mode = 0, 0
click = False
Play_time = 30
Order_XY_list = [[3,6],[6,4],[16,3],[12,5],[7,2],[8,1]]
order_list = []
hand_distance_limit = []
distance_goal =  True 
boom_rate = 6
laxt_X_Time = 960
laxt_X_Speed = 960
Speed = 5
fruit_N = 0
Max_fruit = 5
FPS=60
gap=350

#load img files

RH_img = pygame.image.load(os.path.join("img","RH.png")).convert()
RH_click_img = pygame.image.load(os.path.join("img","RH_click.png")).convert()
LH_img = pygame.image.load(os.path.join("img","LH.png")).convert()
RF_img = pygame.image.load(os.path.join("img","RF.png")).convert()
LF_img = pygame.image.load(os.path.join("img","LF.png")).convert()
bug_img = pygame.image.load(os.path.join("img","bug.png")).convert()
Back_button_ico_img = pygame.image.load(os.path.join("img","Back_button_ico.png")).convert()
Exit_button_ico_img = pygame.image.load(os.path.join("img","Exit_button_ico.png")).convert()
Game_button_ico_img = pygame.image.load(os.path.join("img","Game_button_ico.png")).convert()
Game1_button_ico_img = pygame.image.load(os.path.join("img","Game1_button_ico.png")).convert()
Game2_button_ico_img = pygame.image.load(os.path.join("img","Game2_button_ico.png")).convert()
Game3_button_ico_img = pygame.image.load(os.path.join("img","Game3_button_ico.png")).convert()
Rank_button_ico_img = pygame.image.load(os.path.join("img","Rank_button_ico.png")).convert()
Setting_button_ico_img = pygame.image.load(os.path.join("img","Setting_button_ico.png")).convert()
Gophers_img = pygame.image.load(os.path.join("img","Gophers_img.png")).convert()
hammer_L_img = pygame.image.load(os.path.join("img","hammer_L.png")).convert()
hammer_R_img = pygame.image.load(os.path.join("img","hammer_R.png")).convert()
order_1_img = pygame.image.load(os.path.join("img","order_1.png")).convert()
order_2_img = pygame.image.load(os.path.join("img","order_2.png")).convert()
order_3_img = pygame.image.load(os.path.join("img","order_3.png")).convert()
order_4_img = pygame.image.load(os.path.join("img","order_4.png")).convert()
order_5_img = pygame.image.load(os.path.join("img","order_5.png")).convert()
order_6_img = pygame.image.load(os.path.join("img","order_6.png")).convert()
boom_img = pygame.image.load(os.path.join("img","boom.png")).convert()
Game_2_BG_img = pygame.image.load(os.path.join("img","Game_2_BG.png")).convert()
Bar_img = pygame.image.load(os.path.join("img","Bar.png")).convert()
magic_img = pygame.image.load(os.path.join("img","magic.png")).convert()
record_Background_img = pygame.image.load(os.path.join("img","record_Background.png")).convert()
ScoreBoard_img = pygame.image.load(os.path.join("img","ScoreBoard.png")).convert()
ScoreBoard_img.set_colorkey((0,0,0))
record_Background_img.set_colorkey((0,0,0))
LF_img.set_colorkey((0,0,0))
pygame.display.set_icon(LF_img)

#load txt files
Score_Record = 'ScoreRecord.txt'
Setting_Record = 'Game_setting.txt'
font_name = os.path.join("font.ttf")#load font file

#load music files
bug_die_sound = pygame.mixer.Sound(os.path.join("sound", "bug_die.wav"))
bomb_sound = pygame.mixer.Sound(os.path.join("sound", "bomb.wav"))
click_sound = pygame.mixer.Sound(os.path.join("sound", "click.wav"))
magic_sound = pygame.mixer.Sound(os.path.join("sound", "magic.wav"))
hit_sound = pygame.mixer.Sound(os.path.join("sound", "hit.wav"))
pygame.mixer.music.load(os.path.join("sound", "background.ogg"))
pygame.mixer.music.set_volume(0.4)

#build button sprite
class Game_button(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(Game_button_ico_img, (300,150))
        self.image.set_colorkey((0,0,0))
        self.rect = self.image.get_rect()
        self.rect.center = (WIDTH/2 - gap*1.5 ,HEIGHT/2)
        
class Setting_button(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(Setting_button_ico_img, (300,150))
        self.image.set_colorkey((0,0,0))
        self.rect = self.image.get_rect()
        self.rect.center = (WIDTH/2 - gap*0.5 ,HEIGHT/2)
        
class Rank_button(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(Rank_button_ico_img, (300,150))
        self.image.set_colorkey((0,0,0))
        self.rect = self.image.get_rect()
        self.rect.center = (WIDTH/2 + gap*0.5,HEIGHT/2)
        
class Exit_button(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(Exit_button_ico_img, (300,150))
        self.image.set_colorkey((0,0,0))
        self.rect = self.image.get_rect()
        self.rect.center = (WIDTH/2 + gap*1.5 ,HEIGHT/2)

class Save_button(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(Back_button_ico_img, (300,150))
        self.image.set_colorkey((0,0,0))
        self.rect = self.image.get_rect()
        self.rect.center = (WIDTH/2 + gap*2 ,HEIGHT/2 - 200)

class Back_button(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(Back_button_ico_img, (300,150))
        self.image.set_colorkey((0,0,0))
        self.rect = self.image.get_rect()
        self.rect.center = (WIDTH/2 + 400 *1.5 ,HEIGHT/2 - 200)
     
class Game1_button(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(Game1_button_ico_img, (300,150))
        self.image.set_colorkey((0,0,0))
        self.rect = self.image.get_rect()
        self.rect.center = (WIDTH/2 - 400 *1.5 ,HEIGHT/2-200)
        
class Game2_button(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(Game2_button_ico_img, (300,150))
        self.image.set_colorkey((0,0,0))
        self.rect = self.image.get_rect()
        self.rect.center = (WIDTH/2 - 400 *0.5,HEIGHT/2-200)
        
class Game3_button(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(Game3_button_ico_img, (300,150))
        self.image.set_colorkey((0,0,0))
        self.rect = self.image.get_rect()
        self.rect.center = (WIDTH/2 + 400 *0.5 ,HEIGHT/2-200)
        
# build order sprite(in game3)
class order_1(pygame.sprite.Sprite):
    
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(order_1_img, (100,100))
        self.image.set_colorkey((0,0,0))
        self.rect = self.image.get_rect()
        self.rect.center = (Order_XY_list[0][0]*100 ,Order_XY_list[0][1]*100)
       
    def update(self):
        self.rect.center = (Order_XY_list[0][0]*100 ,Order_XY_list[0][1]*100)
     
class order_2(pygame.sprite.Sprite):
    
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(order_2_img, (100,100))
        self.image.set_colorkey((0,0,0))
        self.rect = self.image.get_rect()
        self.rect.center = (Order_XY_list[1][0]*100 ,Order_XY_list[1][1]*100)
        
    def update(self):
            self.rect.center = (Order_XY_list[1][0]*100 ,Order_XY_list[1][1]*100)
        
class order_3(pygame.sprite.Sprite):
    
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(order_3_img, (100,100))
        self.image.set_colorkey((0,0,0))
        self.rect = self.image.get_rect()
        self.rect.center = (Order_XY_list[2][0]*100 ,Order_XY_list[2][1]*100)
        
    def update(self):
             self.rect.center = (Order_XY_list[2][0]*100 ,Order_XY_list[2][1]*100)
        
class order_4(pygame.sprite.Sprite):
    
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(order_4_img, (100,100))
        self.image.set_colorkey((0,0,0))
        self.rect = self.image.get_rect()
        self.rect.center = (Order_XY_list[3][0]*100 ,Order_XY_list[3][1]*100)

    def update(self):
            self.rect.center = (Order_XY_list[3][0]*100 ,Order_XY_list[3][1]*100)

class order_5(pygame.sprite.Sprite):
    
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(order_5_img, (100,100))
        self.image.set_colorkey((0,0,0))
        self.rect = self.image.get_rect()
        self.rect.center = (Order_XY_list[4][0]*100 ,Order_XY_list[4][1]*100)

    def update(self):
            self.rect.center = (Order_XY_list[4][0]*100 ,Order_XY_list[4][1]*100)

class order_6(pygame.sprite.Sprite):
    
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(order_6_img, (100,100))
        self.image.set_colorkey((0,0,0))
        self.rect = self.image.get_rect()
        self.rect.center = (Order_XY_list[5][0]*100 ,Order_XY_list[5][1]*100)

    def update(self):
            self.rect.center = (Order_XY_list[5][0]*100 ,Order_XY_list[5][1]*100)

# build mouse sprite(hand)
class Mouse(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(LH_img, (90,150)) 
        self.image.set_colorkey((0,0,0))
        self.rect = self.image.get_rect()
        self.rect.center = (0,-100)
        
    def update(self):
        self.rect = self.image.get_rect()
        self.rect.center = (mouse_xy[0],mouse_xy[1])
        if click:
            self.image = pygame.transform.scale(RH_click_img, (60,100)) 
            self.image.set_colorkey((0,0,0))
        else :
            self.image = pygame.transform.scale(LH_img, (60,100)) 
            self.image.set_colorkey((0,0,0))
            
# build hand sprite(left right)
class hand_L(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(LH_img, (90,150)) 
        self.image.set_colorkey((0,0,0))
        self.rect = self.image.get_rect()
        self.rect.center = (WIDTH/2,HEIGHT/2)
        
    def update(self):
        self.rect = self.image.get_rect()
        self.rect.center = (handx[0], handy[0])
        if Game_Mode == 1 :
            self.image = pygame.transform.scale(LF_img,(90,150)) #(90*(hand_area/2500),150*(hand_area/2500)
        elif Game_Mode == 2 :
            self.image = pygame.transform.scale(hammer_L_img, (90,150)) 
        elif Game_Mode == 3:
            self.image = pygame.transform.scale(magic_img, (100,100))
        self.image.set_colorkey((0,0,0))

class hand_R(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(RH_img, (90,150))
        self.image.set_colorkey((0,0,0))
        self.rect = self.image.get_rect()
        self.rect.center = (WIDTH/2,HEIGHT/2)
        
    def update(self):
        self.rect = self.image.get_rect()
        self.rect.center = (handx[1], handy[1])  
        if Game_Mode == 1 :
            self.image = pygame.transform.scale(RF_img, (90,150)) 
        elif Game_Mode == 2 :
            self.image = pygame.transform.scale(hammer_R_img, (90,150)) 
        elif Game_Mode == 3:
            self.image = pygame.transform.scale(magic_img, (100,100))
        self.image.set_colorkey((0,0,0))
        
# build Bug sprite(in game1)
class Bug(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(bug_img, (60,100)) 
        self.image.set_colorkey((0,0,0))
        self.rect = self.image.get_rect()
        #self.radius = int(self.rect.width * 0.85 / 2)
        self.bug_X = random.randrange(0,WIDTH - self.rect.width)
        self.bug_Y = random.randrange(0,HEIGHT- self.rect.height)
        self.refresh_x = random.randrange(-20,20) * (Speed/5)
        self.refresh_y = random.randrange(-20,20) * (Speed/5)
        self.rect.x = self.bug_X
        self.rect.y = self.bug_Y
        
    def update(self):
        if self.bug_X > 0 and self.bug_X < WIDTH - self.rect.width :
            self.bug_X += self.refresh_x
        if self.bug_Y > 0 and self.bug_Y < HEIGHT- self.rect.height :
            self.bug_Y += self.refresh_y
        self.rect.x = self.bug_X
        self.rect.y = self.bug_Y  
    
# build Gophers sprite(in game2)
class Gophers(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(Gophers_img, (90,150)) 
        self.image.set_colorkey((0,0,0))
        self.rect = self.image.get_rect()
        self.rect.center = (0,-100)
        self.Gophers_Y = 0
        self.hole_n = random.randrange(0,7)
        self.boom = random.randrange(0,boom_rate) == 1
    def update(self):
        if self.boom :
            self.image = pygame.transform.scale(boom_img, (120,120)) 
        else :
            self.image = pygame.transform.scale(Gophers_img, (90,150)) 
        self.image.set_colorkey((0,0,0))
        
        if self.Gophers_Y >=220:
            self.Gophers_Y = 70
            self.hole_n = random.randrange(0,7)
            self.boom = random.randrange(0,boom_rate) == 1
        else:
            self.Gophers_Y += (10 * (Speed/5))
            self.rect.center = (WIDTH/2 + (self.hole_n -3)*200,HEIGHT - self.Gophers_Y) 
            
        if self.boom :
            return -4
        else :
            return 1
        
    def kill(self): 
        self.Gophers_Y = 0
        self.hole_n = random.randrange(0,6)
        self.boom = random.randrange(0,boom_rate) == 1

Body_Group =  pygame.sprite.Group()
Hand_Group =  pygame.sprite.Group()
Bug_Group =  pygame.sprite.Group()
Menu_Group = pygame.sprite.Group()
Mouse_Group = pygame.sprite.Group()
Game_button_Group = pygame.sprite.Group()
Gophers_Group = pygame.sprite.Group()
Order_Group = pygame.sprite.Group()
Back_Group = pygame.sprite.Group()
record_Background_Group = pygame.sprite.Group()
Save_button_Group = pygame.sprite.Group()
fruit_group = pygame.sprite.Group()

Game_button = Game_button()
Setting_button = Setting_button()
Rank_button = Rank_button()
Exit_button = Exit_button()
Back_button = Back_button()
Save_button = Save_button()
Game1_button = Game1_button()
Game2_button = Game2_button()
Game3_button = Game3_button()

order_1 = order_1()
order_2 = order_2()
order_3 = order_3()
order_4 = order_4()
order_5 = order_5()
order_6 = order_6()

Mouse = Mouse()
Gophers = Gophers()
hand_L = hand_L()
hand_R = hand_R()
Bugs = Bug()

Hand_Group.add(hand_L)
Hand_Group.add(hand_R)

Menu_Group.add(Game_button)
Menu_Group.add(Setting_button)
Menu_Group.add(Rank_button)
Menu_Group.add(Exit_button)

Game_button_Group.add(Game1_button)
Game_button_Group.add(Game2_button)
Game_button_Group.add(Game3_button)
Game_button_Group.add(Back_button)

Order_Group.add(order_1)
Order_Group.add(order_2)
Order_Group.add(order_3)
Order_Group.add(order_4)
Order_Group.add(order_5)
Order_Group.add(order_6)
Back_Group.add(Back_button)
Save_button_Group.add(Save_button)
Bug_Group.add(Bugs)
Mouse_Group.add(Mouse)
Gophers_Group.add(Gophers)

def random_order():
    rand_XY_list=[]
    rand_XY=[]
    for i in range(6):
        rand_XY = [random.randrange(1,WIDTH//100),random.randrange(1,HEIGHT//100)]
        while rand_XY in rand_XY_list :
            rand_XY = [random.randrange(1,WIDTH//100),random.randrange(1,HEIGHT//100)]
        rand_XY_list.append(rand_XY)
    return rand_XY_list
        
def find_pose_landmark():
    Pose_lm=[]
    if  results.pose_landmarks:
        for id , lm in enumerate(results.pose_landmarks.landmark):
            h, w, c = img.shape
            Pose_lm.append([int(lm.x*w),int(lm.y*h)])
    return Pose_lm

def area(p1,p2,p3):
    area = abs((p2[0]-p1[0])*(p3[1]-p1[1])-(p2[1]-p1[1])*(p3[0]-p1[0]))/2
    return area

def Game1():
    Hand_Group.update()
    Bug_Group.update()
    Hand_Group.draw(screen)
    Bug_Group.draw(screen)
    hit = pygame.sprite.groupcollide(Hand_Group , Bug_Group, False , True)
    if hit :
        new_Bug()
        bug_die_sound.play()
        return 10
    else :
        return 0
    
def Game2():
    Hand_Group.update()
    s = Gophers.update()
    Hand_Group.draw(screen)
    Gophers_Group.draw(screen)
    hit = pygame.sprite.groupcollide(Hand_Group , Gophers_Group, False , True)
    screen.blit(Game_2_BG_img, (0, HEIGHT - 160))
    if hit :
        Gophers.kill()
        if s>0 :
            hit_sound.play()
        else :
            bomb_sound.play()
        return 10 * s
    else :
        return 0
    

def order_hit():
    if pygame.sprite.collide_rect(order_1,hand_L) or pygame.sprite.collide_rect(order_1,hand_R):
        Order_XY_list[0]=[-3,0]
        magic_sound.play()
        return 1
    elif pygame.sprite.collide_rect(order_2,hand_L) or pygame.sprite.collide_rect(order_2,hand_R):
        Order_XY_list[1]=[-3,0]
        magic_sound.play()
        return 2
    elif pygame.sprite.collide_rect(order_3,hand_L) or pygame.sprite.collide_rect(order_3,hand_R):
        Order_XY_list[2]=[-3,0]
        magic_sound.play()
        return 3
    elif pygame.sprite.collide_rect(order_4,hand_L) or pygame.sprite.collide_rect(order_4,hand_R):
        Order_XY_list[3]=[-3,0]
        magic_sound.play()
        return 4
    elif pygame.sprite.collide_rect(order_5,hand_L) or pygame.sprite.collide_rect(order_5,hand_R):
        Order_XY_list[4]=[-3,0]
        magic_sound.play()
        return 5
    elif pygame.sprite.collide_rect(order_6,hand_L) or pygame.sprite.collide_rect(order_6,hand_R):
        Order_XY_list[5]=[-3,0]
        magic_sound.play()
        return 6
    else :
        return 0
    
def distance(P1,P2):
    #d = area(Pose_LM[11],Pose_LM[12],Pose_LM[24])
    d = int(math.hypot(Pose_LM[P1][0] - Pose_LM[P2][0], Pose_LM[P1][1] - Pose_LM[P2][1]))
    if d < distance_limit[0]:
        #print(str(d)+" Too Far")
        draw_text(screen,"Too Far " + str(d),40,WIDTH/2 -350,10,[255,50,0])
        return False
    elif d > distance_limit[1]:
        #print(str(d)+" Too Colse")
        draw_text(screen,"Too Close "+ str(d),40,WIDTH/2 -350,10,[255,50,0])
        return False
    else :
        #print(str(d)+" Okay")
        draw_text(screen,"Okay "+ str(d),40,WIDTH/2 -350,10,[100,255,0])
        return True
    
def new_Bug():
    R = Bug()
    Bug_Group.empty()
    Bug_Group.add(R)
    
def draw_text(surf, text, size, x, y, color):
    font = pygame.font.Font(font_name, size)
    text_surface = font.render(text, True,(color[0],color[1],color[2]))
    text_rect = text_surface.get_rect()
    text_rect.centerx = x
    text_rect.top = y
    surf.blit(text_surface, text_rect)
    
def select_Menu():
    if len(Hand_LM) != 0:
        #print(Hand_LM)
        
        if fingers_pose == 7 or fingers_pose == 1:
            if pygame.sprite.collide_rect(Game_button,Mouse):
                click_sound.play()
                return 1
            elif pygame.sprite.collide_rect(Setting_button,Mouse):
                click_sound.play()
                return 2
            elif pygame.sprite.collide_rect(Rank_button,Mouse): 
                click_sound.play()
                return 3
            elif pygame.sprite.collide_rect(Exit_button,Mouse):
                click_sound.play()
                return 4
        Mouse_Group.update()
    Menu_Group.draw(screen)
    Mouse_Group.draw(screen)
    return 0

def select_Game():
    if len(Hand_LM) != 0:
        if fingers_pose == 7 or fingers_pose == 1:
            if pygame.sprite.collide_rect(Game1_button,Mouse):
                click_sound.play()
                return 1
            elif pygame.sprite.collide_rect(Game2_button,Mouse):
                click_sound.play()
                return 2
            elif pygame.sprite.collide_rect(Game3_button,Mouse): 
                click_sound.play()
                return 3
            elif pygame.sprite.collide_rect(Back_button,Mouse):
                click_sound.play()
                return 6
                #print("Exit")
        Mouse_Group.update()
    Game_button_Group.draw(screen)
    Mouse_Group.draw(screen)
    return 0

def save_record(Game,score,T,S):
    f = open(Score_Record, 'a')
    f.write(time.ctime(time.time())[4:] +'  ' +Game + '  Score:' + str(score) +' T:'+str(T) +' S:'+str(S) +'\n')
    f.close()

def print_record():
    
    f = open(Score_Record,'r')
    record = f.readlines()
    record.reverse()
    for i in range (len(record)):
        if i < 21 :
            record[i] = record[i].strip()
            draw_text(screen, record[i], 30 , WIDTH/2,  i * 40 + 150 , [255,255,255] )
        else :
            break
    f.close()
    
f = open(Setting_Record,'r')
setting_list = f.readlines()
f.close()
Play_time = int(setting_list[0])
Speed = int(setting_list[1])

laxt_X_Time = int(np.interp(Play_time,[30,300],[460,1460]))
laxt_X_Speed = int(np.interp(Speed,[30,300],[460,1460]))

pygame.mixer.music.play(-1)

while runing:
    clock.tick(FPS)#最多60fps
    success, img = cap.read()
    img = cv2.flip(img, 1)#圖片反轉
    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = pose.process(imgRGB)
    camshot = pygame.image.frombuffer(imgRGB.tostring(), (wCam,hCam), "RGB")
    Pose_LM = find_pose_landmark()
    img_hand_detector = detector.findHands(img,draw = False)
    Hand_LM, bbox = detector.findPosition(img_hand_detector)
    screen.blit(camshot, (0,0))
    screen.blit(ScoreBoard_img, (WIDTH/2-600, 10))
    
    if len(Pose_LM) != 0 :
        handx,handy=[Pose_LM[19][0],Pose_LM[20][0]],[Pose_LM[19][1],Pose_LM[20][1]]
        distance_goal = distance(24,12)
        
    if len(Hand_LM) != 0:
        fingers_pose = detector.fingersUp()
        mouse_xy[0],mouse_xy[1]= Hand_LM[9][0],Hand_LM[9][1]
        hand_area = area(Hand_LM[0],Hand_LM[5],Hand_LM[17])
        #print(hand_area)
        if fingers_pose == 7 or fingers_pose == 1:
            click = True
        else :
            click = False
        
    if Game_Mode == 0 or Game_Mode == 6:
        if Menu_state == 0 or Game_Mode == 6:
            Menu_state = select_Menu()
            Game_Mode = 0
            
        elif Menu_state == 1:
            Game_Mode = select_Game()
            
        elif Menu_state == 2 :
            screen.blit(Bar_img, (460,110))
            screen.blit(Bar_img, (460,310))
            Save_button_Group.update()
            Save_button_Group.draw(screen)
            Mouse_Group.update()
            Mouse_Group.draw(screen)
            
            if len(Hand_LM)!=0:
                P = Hand_LM[8]
                if click:
                    if P[1]> 85 and P[1] < 180:
                        if P[0] > 460 and P[0] < 1460:
                            laxt_X_Time = P[0]
                    if P[1]> 285 and P[1] < 380:
                        if P[0] > 460 and P[0] < 1460:
                            laxt_X_Speed = P[0]
                        
            T = int(np.interp(laxt_X_Time,[460,1460],[30,301]))
            draw_text(screen,str(T) , 40, laxt_X_Time, 110, [0,0,0])
            draw_text(screen,"Time" , 40, 380, 110, [0,0,0])
            S = int(np.interp(laxt_X_Speed,[460,1460],[1,11]))
            draw_text(screen,"Speed" , 40, 380, 310, [0,0,0])
            draw_text(screen,str(S) , 40, laxt_X_Speed, 310, [0,0,0])
            if click and pygame.sprite.collide_rect(Save_button,Mouse):
                f = open(Setting_Record,'w')
                f.write(str(T)+'\n'+str(S)+'\n')
                f.close()
                Play_time = T
                Speed = S
                Menu_state = 0
                click_sound.play()
                
        elif Menu_state == 3:
            screen.blit(record_Background_img, (WIDTH / 2 - 400 ,100))
            print_record()
            Back_Group.update()
            Mouse_Group.update()
            Back_Group.draw(screen)
            Mouse_Group.draw(screen)
            
            if click and pygame.sprite.collide_rect(Back_button,Mouse):
                Menu_state = 0
                click_sound.play()
        elif Menu_state == 4:
            runing = False
            
    if Game_Mode == 0 :
        Game_time = time.time()
        
    if Game_Mode == 1:
        if distance_goal :
            Score += Game1()
        draw_text(screen,'Left Time : ' + str(Play_time - int(time.time() - Game_time)), 40, WIDTH/2 + 300, 10,[255,0,0])
        if time.time() - Game_time > Play_time:
            Game_Mode = 0 
            Menu_state = 0
            save_record("打蟑螂 ",Score,Play_time,Speed)
            Score = 0
            
    elif Game_Mode == 2 :
        if distance_goal :
            Score += Game2()
        draw_text(screen,'Left Time : ' + str(Play_time - int(time.time() - Game_time)), 40, WIDTH/2 + 300, 10,[255,0,0])
        if time.time() - Game_time > Play_time:
            Game_Mode = 0 
            Menu_state = 0
            save_record("打地鼠 ",Score,Play_time,Speed)
            Score = 0
            
    elif Game_Mode == 3 :
        for i in range(len(order_list)):
            if order_list[i] != i+1:
                Order_XY_list = random_order()
                Score += (i * 10)
                order_list=[]
            elif i == 5:
                Order_XY_list = random_order()
                Score += 90
                order_list=[]
        N_order = 0
        if distance_goal :
            N_order = order_hit()
        if N_order != 0 and N_order not in order_list:
            order_list.append(N_order)
        draw_text(screen,'Left Time : ' + str(Play_time - int(time.time() - Game_time)), 40, WIDTH/2 + 300, 10,[255,0,0])
        Hand_Group.update()
        Order_Group.update()
        Order_Group.draw(screen)
        Hand_Group.draw(screen)
        if time.time() - Game_time > Play_time:
            Game_Mode = 0 
            Menu_state = 0
            save_record("數字連擊",Score,Play_time,Speed)
            Score = 0
      
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            runing = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                runing = False#離開 (ESC)      
                
    if Game_Mode != 0:     
        draw_text(screen, str(Score), 40, WIDTH/2, 10,[255,255,255])
    pygame.display.update()#顯示更新
    
cap.release() 
pygame.quit()