# -*- coding: utf-8 -*-
"""
Created on Thu Mar  1 11:32:44 2018

@author: ThoseBygones
"""

'''
"." 空白处，可通过
"#" 墙,不可通过
"@" 人,可移动
"$" 箱子,可推动
"*" 终点
"&" 到终点的箱子
'''

from collections import deque
import pygame, sys, os
from pygame.locals import *

class Button(object):
    def __init__(self, buttonUpImage, buttonDownImage, pos):
        self.buttonUp = pygame.image.load(buttonUpImage).convert_alpha()
        self.buttonDown = pygame.image.load(buttonDownImage).convert_alpha()
        self.pos = pos
        self.game_start = False
    
    def inButtonRange(self):
        mouseX, mouseY = pygame.mouse.get_pos()
        x, y = self.pos
        w, h = self.buttonUp.get_size()
        inX = x - w/2 < mouseX < x + w/2
        inY = y - h/2 < mouseY < y + h/2
        return inX and inY

    def show(self, screen):
        w, h = self.buttonUp.get_size()
        x, y = self.pos
        if self.inButtonRange():
            screen.blit(self.buttonDown, (x-w/2,y-h/2))
        else:
            screen.blit(self.buttonUp, (x-w/2, y-h/2))

class Sokoban:
    
    def __init__(self):
        self.level = list('....#####..........'+\
                          '....#...#..........'+\
                          '....#$..#..........'+\
                          '..###..$##.........'+\
                          '..#..$.$.#.........'+\
                          '###.#.##.#...######'+\
                          '#...#.##.#####..**#'+\
                          '#.$..$..........**#'+\
                          '#####.###.#@##..**#'+\
                          '....#.....#########'+\
                          '....#######........')
        self.w = 19
        self.h = 11
        self.man = 163 #8行，11列（9=163 // 19 12=163 mod 19）
        self.boxInPositionCnt = 0
        
    def toBox(self, level, index):
        if level[index] == '.' or level[index] == '@':
            level[index] = '$'
        else:
            level[index] = '&'

    def toMan(self, level, i):
        if level[i] == '.' or level[i] == '$':
            level[i]='@'
        else:
            level[i]='+'
    
    def toFloor(self, level, i):
        if level[i] == '@' or level[i] == '$':
            level[i]='.'
        else:
            level[i]='*'
    
    def offset(self, d, width):
        d4 = [-1, -width, 1, width]
        m4 = ['l','u','r','d']
        return d4[m4.index(d.lower())]
    
    def draw(self, screen, skin):
        w = skin.get_width() / 4
        for i in range(0,self.w):
            for j in range(0,self.h):
                if self.level[j*self.w + i] == '#':
                    screen.blit(skin, (i*w, j*w), (0,2*w,w,w))
                elif self.level[j*self.w + i] == '.':
                    screen.blit(skin, (i*w, j*w), (0,0,w,w))
                elif self.level[j*self.w + i] == '@':
                    screen.blit(skin, (i*w, j*w), (w,0,w,w))
                elif self.level[j*self.w + i] == '$':
                    screen.blit(skin, (i*w, j*w), (2*w,0,w,w))
                elif self.level[j*self.w + i] == '*':
                    screen.blit(skin, (i*w, j*w), (0,w,w,w))
                elif self.level[j*self.w + i] == '+':
                    screen.blit(skin, (i*w, j*w), (w,w,w,w))
                elif self.level[j*self.w + i] == '&':
                    screen.blit(skin, (i*w, j*w), (2*w,w,w,w))
    
    #def move(self, d):
    #    self._move(d)
    
    # 返回1表示推了箱子的移动，返回0表示没推箱子的移动，返回-1表示移动不成功
    def move(self, op):
        #print("方向：" + op)
        h = self.offset(op, self.w)
        if self.level[self.man + h] == '.' or self.level[self.man + h] == '*':
            # move
            self.toMan(self.level, self.man + h)
            self.toFloor(self.level, self.man)
            self.man += h
            return 0
        elif self.level[self.man + h] == '&' or self.level[self.man + h] == '$':
            if self.level[self.man + 2 * h] == '.' or self.level[self.man + 2 * h] == '*':
                # push
                if self.level[self.man + h] == '&':
                    self.boxInPositionCnt -= 1
                    #print(self.boxInPositionCnt)
                self.toBox(self.level, self.man + 2 * h)
                self.toMan(self.level, self.man + h)
                self.toFloor(self.level, self.man)
                self.man += h
                if self.level[self.man + h] == '&':
                    self.boxInPositionCnt += 1
                    #print(self.boxInPositionCnt)
                return 1
            else:
                return -1
        else:
            return -1
    
    # 还原函数
    def revmove(self, op):
        d = op[0]
        flag = op[1]
        #print(flag)
        h = self.offset(d, self.w)
        if flag == 1:
            # push
            if self.level[self.man + h] == '&':
                self.boxInPositionCnt -= 1
                #print(self.boxInPositionCnt)
            self.toBox(self.level, self.man)
            self.toMan(self.level, self.man - h)
            self.toFloor(self.level, self.man + h)
            self.man -= h
            if self.level[self.man + h] == '&':
                self.boxInPositionCnt += 1
                #print(self.boxInPositionCnt)
        elif flag == 0:
            # move
            self.toMan(self.level, self.man - h)
            self.toFloor(self.level, self.man)
            self.man -= h

# 显示游戏主界面的函数
def showGameInterface(screen, interface, startGame, gameTips):
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == MOUSEBUTTONDOWN:
            if startGame.inButtonRange():
                return 1
            elif gameTips.inButtonRange():
                return 2
    screen.blit(interface, (0,0))
    startGame.show(screen)
    gameTips.show(screen)
    return 0

def showWinInterface(screen, interface, returnInterface):
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == MOUSEBUTTONDOWN:
            if returnInterface.inButtonRange():
                return 1
    screen.blit(interface, (0,0))
    returnInterface.show(screen)
    return 0

def main():
    # 初始化pygame
    pygame.init()
    # 设置游戏图标
    gameicon = pygame.image.load("BoxIcon.png")  
    # 展示游戏图标
    pygame.display.set_icon(gameicon)
    # 设置背景音乐
    bgm = pygame.mixer.music.load("Hebe - A Little Happiness.mp3")
    # 设置主界面大小
    screen = pygame.display.set_mode((400,400))
    # “开始游戏”按钮
    button1 = Button('GameStartButtonUp.png', 'GameStartButtonDown.png', (200,300))
    # “游戏说明”按钮
    button2 = Button('GameTipsButtonUp.png', 'GameTipsButtonDown.png', (200,350))
    # “返回主界面”按钮
    button3 = Button('ReturnInterfaceUp.png', 'ReturnInterfaceDown.png', (200,350))
    # 主界面背景图片
    interface = pygame.image.load("Interface.png")
    # 游戏说明界面图片
    gametips = pygame.image.load("GameTips.png")
    # 通关提示界面图片
    chapterpass = pygame.image.load("ChapterPass.png")
    # 加载游戏界面图片资源
    skinfilename = os.path.join('borgar.png')
    try:
        skin = pygame.image.load(skinfilename)
    except pygame.error as msg:
        print('cannot load skin')
        raise(SystemExit(msg))
    skin = skin.convert()

    # 设置游戏界面标题
    pygame.display.set_caption('I Love Sokoban ~')
    
    clock = pygame.time.Clock()
    
    # 按住某个键每隔interval(50)毫秒产生一个KEYDOWN事件，delay(200)就是多少毫秒后才开始触发这个事件。
    pygame.key.set_repeat(200,50)
    # 游戏主循环
    while True:
        # 给tick方法加上的参数就成为了游戏绘制的最大帧率
        clock.tick(60)
        flag = showGameInterface(screen, interface, button1, button2)
        # 点击开始游戏
        if flag == 1:
            # 播放音乐
            pygame.mixer.music.play()
            screen.fill(skin.get_at((0,0)))
            # create Sokoban object
            skb = Sokoban()
            skb.draw(screen,skin)
            # 利用双端队列deque来维护历史操作队列
            dq = deque([])
            # main game loop
            while True:
                # 给tick方法加上的参数就成为了游戏绘制的最大帧率
                retGameInterface = False
                clock.tick(60)
                for event in pygame.event.get():
                    if event.type == QUIT:
                        #print skb.solution
                        pygame.quit()
                        sys.exit()
                    elif event.type == KEYDOWN:
                        if event.key == K_ESCAPE:
                            retGameInterface = True
                            break
                        elif event.key == K_LEFT:
                            flag = skb.move('l')
                            dq.append(['l', flag])
                            skb.draw(screen,skin)
                        elif event.key == K_UP:
                            flag = skb.move('u')
                            dq.append(['u', flag])
                            skb.draw(screen,skin)
                        elif event.key == K_RIGHT:
                            flag = skb.move('r')
                            dq.append(['r', flag])
                            skb.draw(screen,skin)
                        elif event.key == K_DOWN:
                            flag = skb.move('d')
                            dq.append(['d', flag])
                            skb.draw(screen,skin)
                        elif event.key == K_BACKSPACE:
                            if len(dq) > 0:
                                op = dq.pop()
                                #print(op)
                                skb.revmove(op)
                                skb.draw(screen,skin)
                        if len(dq) > 50:
                            dq.popleft()
                #screen.blit(interface,(0,0))
                #button1.show(screen)
                #button2.show(screen)
                if skb.boxInPositionCnt == 6:
                    clock.tick(60)
                    win = showWinInterface(screen, chapterpass, button3)
                    if win == 1:
                        retGameInterface = True
                pygame.display.update()
                if retGameInterface == True:
                    pygame.mixer.music.stop()
                    break
        elif flag == 2:
            clock.tick(60)
            retGameInterface = False
            while True:
                for event in pygame.event.get():
                    if event.type == QUIT:
                        pygame.quit()
                        sys.exit()
                    elif event.type == KEYDOWN:
                        if event.key == K_ESCAPE:
                            retGameInterface = True
                            break
                screen.blit(gametips, (0,0))
                pygame.display.update()
                if retGameInterface == True:
                    break
        pygame.display.update()

if __name__ == '__main__':
    main()