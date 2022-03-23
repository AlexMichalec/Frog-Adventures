import time

import pygame
import random

WIN_W = 600
WIN_H = 600

def write (screen,text,size,x,y,font="Comic Sans",color=(250,250,250)):
    font = pygame.font.SysFont(font,size)
    render = font.render(text, True, color)
    screen.blit(render,(x,y))

class Doors:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.color = (0,0,0)
        self.visible = False
        self.shape = pygame.Rect(self.x, self.y, 40, 60)

    def draw(self, screen):
        if self.visible:
            pygame.draw.rect(screen, self.color, self.shape)
            sek = int((time.time()*4))%4
            sek = sek*2 -6
            pygame.draw.polygon(screen,(245,0,0),[(self.x+10,self.y-30+sek),(self.x+30,self.y-30+sek),(self.x+20,self.y-10+sek)])

    def move(self,vy):
        self.y += vy
        self.shape = pygame.Rect(self.x, self.y, 40, 60)


    def collision(self,hero):
        if self.visible and self.shape.colliderect(hero.shape):
            return True
        else:
            return False


class Coin:
    def __init__(self,x,y):
        self.x = x
        self.y = y
        self.r = 7
        self.color = (240,185,0)

    def draw(self,screen):
        pygame.draw.circle(screen,self.color,(self.x,self.y),self.r)

    def move(self,vy):
        self.y += vy

    def collision(self,hero):
        if hero.x<self.x<hero.x+30 and hero.y<self.y<hero.y+30:
            return True
        else:
            return False


class Hero:
    def __init__(self, x=300, y=300):
        self.x = x
        self.y = y
        self.color = [40,190,85]
        self.shape = pygame.Rect(self.x,self.y,30,30)
        self.jumpable = False

    def draw(self,screen):
        pygame.draw.rect(screen,self.color,self.shape)

    def move(self,vx,vy):
        self.x += vx
        self.x = min(max(self.x,0),WIN_W-30)
        self.y += vy
        self.y = min(max(self.y,0),WIN_H-30)
        self.shape = pygame.Rect(self.x, self.y, 30, 30)


class Platform:
    def __init__(self,x,y,width=100,height=20,color=(40,155,70) ):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.kill = False
        self.shape = pygame.Rect(self.x,self.y,self.width,self.height)
        self.color = color
    def draw(self,screen):
        pygame.draw.rect(screen,self.color,self.shape)

    def move(self,vy):
        self.y += vy
        self.shape = pygame.Rect(self.x, self.y, self.width, self.height)

    def collision(self,something):
        if(self.shape.colliderect(something)):
            return True
        else:
            return False


class World:
    def __init__(self,width,height,hero,level,base=WIN_H*3/4):
        self.window_width = width
        self.window_height = height
        self.background_color = (0,140-min(140,level*10),max(0,200-level*10))
        self.pcolor = (max(0,40-level*5), max(0,155-level*5), 70)
        self.platforms = [Platform(0,height*3/4,width,height*1/4,color=self.pcolor)]
        self.coins = [Coin(random.randint(20,WIN_W-20),WIN_H*3/4-10)]
        self.hero = hero
        self.door = Doors(random.randint(20, WIN_W - 40), WIN_H * 3 / 4 - 50)
        self.setPlatforms(level+2,base)

    def setPlatforms(self, n, base):
        temp = WIN_W/2
        for i in range (2*n):
            p = Platform(max(min(WIN_W-100,temp+random.randint(-250,250)),0),
                         (3/4)*self.window_width*(4-i)/5,
                         color=self.pcolor,
                         width=random.randint(50,150))
            temp = p.x
            self.platforms.append(p)
            self.coins.append(Coin(min(WIN_W-10,random.randint(p.x+10,p.x+p.width-10)),p.y-10))
        if base!=self.platforms[0].y:
            r = base-self.platforms[0].y
            for p in self.platforms:
                p.move(r)
            for c in self.coins:
                c.move(r)
            self.door.move(r)

    def draw(self,screen,if_intro=False):
        screen.fill(self.background_color)
        for p in self.platforms:
            p.draw(screen)
        for c in self.coins:
            c.draw(screen)
        if not if_intro:
            self.hero.draw(screen)
        self.door.draw(screen)

    def collision(self,hero):
        for p in self.platforms:
            if p.collision(hero.shape):
                if p.y > hero.y:
                    hero.y=p.y-30
                    hero.jumpable = True
                else:
                    hero.y=p.y+p.height
                return True
        return False

    def collect_coins(self):
        for c in self.coins:
            if c.collision(self.hero):
                self.coins.remove(c)
                if len(self.coins) == 0:
                    self.door.visible = True
                return True


class Game:
    def __init__(self):
        pygame.init()
        self.window_width = 600
        self.window_height = 600
        self.level = 1
        self.screen = pygame.display.set_mode((self.window_width,self.window_height))
        pygame.display.set_caption("Frog Adventures 🐸")
        self.hero = Hero()
        self.world = World(self.window_width,self.window_height,self.hero,self.level)
        self.v = [0,0]
        self.points = 0


    def intro(self):
        self.world.draw(self.screen,True)
        write(self.screen, "Frog Adventures", 60, 43, 183, font="courier new",color=(0,0,0))
        write(self.screen,"Frog Adventures",60,40,180,font="courier new")
        write(self.screen, "press R to restart",25,200,350)
        write(self.screen, "press ESC to exit", 20, 220, 400)
        write(self.screen, "Game: Alex Michalec", 20, 380, 550)
        write(self.screen, "Music: Kevin MacLeod", 20, 20, 550)

        pygame.display.update()
        time.sleep(1)

    def play(self):
        while(True):
            if self.world.door.collision(self.hero):
                self.reload()
            self.handleEvents()
            self.v[1] += 0.05
            if self.world.collision(self.hero):
                self.v[1] = min(self.v[1], 0)
         #       print("EJ",self.hero.y)
            if self.world.collect_coins():
                self.points +=1
            if self.hero.y <100:
                for p in self.world.platforms:
                    p.move(max(0,-1*self.v[1]))
                for c in self.world.coins:
                    c.move(max(0,-1*self.v[1]))
                self.world.door.move(max(0, -1 * self.v[1]))
                self.hero.move(self.v[0], 1)
            elif self.hero.y >500:
                for p in self.world.platforms:
                    p.move(min(0,-1*self.v[1]))
                for c in self.world.coins:
                    c.move(min(0,-1*self.v[1]))
                self.world.door.move(min(0,-1*self.v[1]))
                self.hero.move(self.v[0], -1)
            else:
                self.hero.move(*self.v)
            self.world.draw(self.screen)
            write(self.screen,str(self.points),30,10,10)
            write(self.screen, str(self.level), 30, 550, 10)
            pygame.display.update()

    def reload(self):
        self.world = World(self.window_width, self.window_height,self.hero,self.level+1,self.world.platforms[0].y)
        self.level+=1
        self.hero.color[1] -=4
        self.hero.color[1] = max (self.hero.color[1],70)

    def handleEvents(self):
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                quit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    quit()
                elif e.key == pygame.K_DOWN:
                    self.v[1] = 1
                elif e.key == pygame.K_UP:
                    if self.hero.jumpable:
                        self.hero.jumpable = False
                        self.v[1] = -4
                elif e.key == pygame.K_r:
                    game = Game()
                    game.play()
                elif e.key == pygame.K_LEFT:
                    self.v[0] = -1
                elif e.key == pygame.K_RIGHT:
                    self.v[0] = 1
            elif e.type == pygame.KEYUP:
                if e.key in (pygame.K_UP,pygame.K_DOWN):
                    self.v[1] = 0
                if e.key in (pygame.K_LEFT,pygame.K_RIGHT):
                    self.v[0] = 0




if __name__ == '__main__':

    game=Game()
    pygame.mixer.init()
    pygame.mixer.music.load("Pleasant Porridge.mp3")
    pygame.mixer.music.play(loops=-1)
    game.intro()
    game.play()

"""
"Pleasant Porridge" Kevin MacLeod (incompetech.com)
Licensed under Creative Commons: By Attribution 4.0 License
http://creativecommons.org/licenses/by/4.0/
"""