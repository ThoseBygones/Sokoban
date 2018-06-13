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
        self.level = [list('...#######'+\
                           '####.....#'+\
                           '#..***.$.#'+\
                           '#..*..#.##'+\
                           '#.#####.#.'+\
                           '#.#...#.#.'+\
                           '#...$.#.#.'+\
                           '###$#.#.#.'+\
                           '#...$...#.'+\
                           '#.@.##..#.'+\
                           '#########.'), 
                      list('.#######....'+\
                           '##.....##...'+\
                           '#..#.$..#...'+\
                           '#.$.$$#.#...'+\
                           '##.#.$..###.'+\
                           '.#...##.*.##'+\
                           '.#####..*..#'+\
                           '.....#.#*..#'+\
                           '.....#..*..#'+\
                           '.....#..*@.#'+\
                           '.....#######'),
                      list('....#####..........'+\
                           '....#...#..........'+\
                           '....#$..#..........'+\
                           '..###..$##.........'+\
                           '..#..$.$.#.........'+\
                           '###.#.##.#...######'+\
                           '#...#.##.#####..**#'+\
                           '#.$..$..........**#'+\
                           '#####.###.#@##..**#'+\
                           '....#.....#########'+\
                           '....#######........')]
        
        self.w = [10, 12, 19]
        self.h = [11, 11, 11]
        self.man = [92, 117, 163] #8行，11列（9=163 // 19 12=163 mod 19）
        self.boxInPositionCnt = [3, 4, 5]
        self.boxCnt = [4, 5, 6]
        
    def toBox(self, chapter, index):
        if self.level[chapter][index] == '.' or self.level[chapter][index] == '@':
            self.level[chapter][index] = '$'
        else:
            self.level[chapter][index] = '&'

    def toMan(self, chapter, index):
        if self.level[chapter][index] == '.' or self.level[chapter][index] == '$':
            self.level[chapter][index] = '@'
        else:
            self.level[chapter][index] = '+'
    
    def toFloor(self, chapter, index):
        if self.level[chapter][index] == '@' or self.level[chapter][index] == '$':
            self.level[chapter][index] = '.'
        else:
            self.level[chapter][index] = '*'
    
    def offset(self, d, width):
        d4 = [-1, -width, 1, width]
        m4 = ['l', 'u', 'r', 'd']
        return d4[m4.index(d.lower())]
    
    def draw(self, screen, chapter, skin):
        w = skin.get_width() / 4
        #print(self.level)
        #print(self.w[chapter], self.h[chapter])
        for i in range(0, self.w[chapter]):
            for j in range(0, self.h[chapter]):
                if self.level[chapter][j * self.w[chapter] + i] == '#':
                    screen.blit(skin, (i*w, j*w), (0,2*w,w,w))
                elif self.level[chapter][j * self.w[chapter] + i] == '.':
                    screen.blit(skin, (i*w, j*w), (0,0,w,w))
                elif self.level[chapter][j * self.w[chapter] + i] == '@':
                    screen.blit(skin, (i*w, j*w), (w,0,w,w))
                elif self.level[chapter][j * self.w[chapter] + i] == '$':
                    screen.blit(skin, (i*w, j*w), (2*w,0,w,w))
                elif self.level[chapter][j * self.w[chapter] + i] == '*':
                    screen.blit(skin, (i*w, j*w), (0,w,w,w))
                elif self.level[chapter][j * self.w[chapter] + i] == '+':
                    screen.blit(skin, (i*w, j*w), (w,w,w,w))
                elif self.level[chapter][j * self.w[chapter] + i] == '&':
                    screen.blit(skin, (i*w, j*w), (2*w,w,w,w))
    
    # 返回1表示推了箱子的移动，返回0表示没推箱子的移动，返回-1表示移动不成功
    def move(self, chapter, op):
        #print("方向：" + op)
        h = self.offset(op, self.w[chapter])
        if self.level[chapter][self.man[chapter] + h] == '.' or self.level[chapter][self.man[chapter] + h] == '*':
            # move
            self.toMan(chapter, self.man[chapter] + h)
            self.toFloor(chapter, self.man[chapter])
            self.man[chapter] += h
            return 0
        elif self.level[chapter][self.man[chapter] + h] == '&' or self.level[chapter][self.man[chapter] + h] == '$':
            if self.level[chapter][self.man[chapter] + 2 * h] == '.' or self.level[chapter][self.man[chapter] + 2 * h] == '*':
                # push
                if self.level[chapter][self.man[chapter] + h] == '&':
                    self.boxInPositionCnt[chapter] -= 1
                    #print(self.boxInPositionCnt)
                self.toBox(chapter, self.man[chapter] + 2 * h)
                self.toMan(chapter, self.man[chapter] + h)
                self.toFloor(chapter, self.man[chapter])
                self.man[chapter] += h
                if self.level[chapter][self.man[chapter] + h] == '&':
                    self.boxInPositionCnt[chapter] += 1
                    #print(self.boxInPositionCnt)
                return 1
            else:
                return -1
        else:
            return -1
    
    # 还原函数
    def revmove(self, chapter, op):
        d = op[0]
        flag = op[1]
        #print(flag)
        h = self.offset(d, self.w[chapter])
        if flag == 1:
            # push
            if self.level[chapter][self.man[chapter] + h] == '&':
                self.boxInPositionCnt[chapter] -= 1
                #print(self.boxInPositionCnt)
            self.toBox(chapter, self.man[chapter])
            self.toMan(chapter, self.man[chapter] - h)
            self.toFloor(chapter, self.man[chapter] + h)
            self.man[chapter] -= h
            if self.level[chapter][self.man[chapter] + h] == '&':
                self.boxInPositionCnt[chapter] += 1
                #print(self.boxInPositionCnt)
        elif flag == 0:
            # move
            self.toMan(chapter, self.man[chapter] - h)
            self.toFloor(chapter, self.man[chapter])
            self.man[chapter] -= h

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

# 显示关卡选择界面的函数
def showChapterInterface(screen, interface, chapter1, chapter2, chapter3, prevInterface):
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == MOUSEBUTTONDOWN:
            if chapter1.inButtonRange():
                return 1
            elif chapter2.inButtonRange():
                return 2
            elif chapter3.inButtonRange():
                return 3
            elif prevInterface.inButtonRange():
                return 4
    screen.blit(interface, (0,0))
    chapter1.show(screen)
    chapter2.show(screen)
    chapter3.show(screen)
    prevInterface.show(screen)
    return 0

def showWinInterface(screen, interface, nextChapter, returnToChoose, flag):
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == MOUSEBUTTONDOWN:
            if nextChapter.inButtonRange():
                return 1
            elif returnToChoose.inButtonRange():
                return 2
    screen.blit(interface, (0,0))
    if flag:
        nextChapter.show(screen)
    returnToChoose.show(screen)
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
    button1 = Button('GameStartUp.png', 'GameStartDown.png', (200,300))
    # “游戏说明”按钮
    button2 = Button('GameTipsUp.png', 'GameTipsDown.png', (200,350))
    # “第一关”按钮
    buttonc1 = Button('Chapter1Up.png', 'Chapter1Down.png', (200,175))
    # “第二关”按钮
    buttonc2 = Button('Chapter2Up.png', 'Chapter2Down.png', (200,225))
    # “第三关”按钮
    buttonc3 = Button('Chapter3Up.png', 'Chapter3Down.png', (200,275))
    # “返回主界面”按钮
    buttonmain = Button('ReturnInterfaceUp.png', 'ReturnInterfaceDown.png', (200,350))
    # “下一关”按钮
    buttonnext = Button('NextChapterUp.png', 'NextChapterDown.png', (100,350))
    # “返回选关”按钮（样式1）
    buttonret1 = Button('Return2ChooseUp.png', 'Return2ChooseDown.png', (300,350))
    # “返回选关”按钮（样式2）
    buttonret2 = Button('Return2ChooseUp.png', 'Return2ChooseDown.png', (200,350))
    # 主界面背景图片
    interface = pygame.image.load("Interface.png")
    # 游戏说明界面图片
    gametips = pygame.image.load("GameTips.png")
    # 选择关卡界面图片
    choosechapter = pygame.image.load("ChooseChapter.png")
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
            # 得到选择的关卡
            while True:
                clock.tick(60)
                chapter = showChapterInterface(screen, choosechapter, buttonc1, buttonc2, buttonc3, buttonmain) - 1
                if chapter == 3:
                    break
                if chapter == -1:
                    pygame.display.update()
                    continue
                #print(chapter)
                # 播放音乐
                pygame.mixer.music.play()
                # create Sokoban object
                skb = Sokoban()
                screen.fill(skin.get_at((0,0)))
                skb.draw(screen, chapter, skin)
                # 利用双端队列deque来维护历史操作队列
                dq = deque([])
                # main game loop
                while True:
                    clock.tick(60)
                    retGameInterface = False
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
                                flag = skb.move(chapter, 'l')
                                dq.append(['l', flag])
                                skb.draw(screen, chapter, skin)
                            elif event.key == K_UP:
                                flag = skb.move(chapter, 'u')
                                dq.append(['u', flag])
                                skb.draw(screen, chapter, skin)
                            elif event.key == K_RIGHT:
                                flag = skb.move(chapter, 'r')
                                dq.append(['r', flag])
                                skb.draw(screen, chapter, skin)
                            elif event.key == K_DOWN:
                                flag = skb.move(chapter, 'd')
                                dq.append(['d', flag])
                                skb.draw(screen, chapter, skin)
                            elif event.key == K_BACKSPACE:
                                if len(dq) > 0:
                                    op = dq.pop()
                                    #print(op)
                                    skb.revmove(chapter, op)
                                    skb.draw(screen, chapter, skin)
                            if len(dq) > 50:
                                dq.popleft()
                    if skb.boxInPositionCnt[chapter] == skb.boxCnt[chapter]:
                        clock.tick(60)
                        if chapter == 0 or chapter == 1:
                            win = showWinInterface(screen, chapterpass, buttonnext, buttonret1, 1)
                        elif chapter == 2:
                            win = showWinInterface(screen, chapterpass, buttonnext, buttonret2, 0)
                        #print('win' + str(win))
                        if win == 1:
                            dq.clear()
                            if chapter < 2:
                                chapter += 1
                                screen.fill(skin.get_at((0,0)))
                                skb.draw(screen, chapter, skin)
                            pygame.display.update()
                            continue
                        elif win == 2:
                            retGameInterface = True
                    if retGameInterface == True:
                        pygame.mixer.music.stop()
                        pygame.display.update()
                        break
                    pygame.display.update()
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