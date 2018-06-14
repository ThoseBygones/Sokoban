# -*- coding: utf-8 -*-
"""
Created on Thu Mar  1 11:32:44 2018

@author: ThoseBygones
"""

'''
符号说明：
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

# 按钮类
class Button(object):
    # 构造函数
    def __init__(self, buttonUpImage, buttonDownImage, pos):
        # 按钮未按下的图片样式
        self.buttonUp = pygame.image.load(buttonUpImage).convert_alpha()
        # 按钮按下的图片样式
        self.buttonDown = pygame.image.load(buttonDownImage).convert_alpha()
        # 按钮在窗口中的位置
        self.pos = pos
    
    # 检查鼠标是否在按钮图片范围内
    def inButtonRange(self):
        # 获取鼠标的位置
        mouseX, mouseY = pygame.mouse.get_pos()
        x, y = self.pos
        w, h = self.buttonUp.get_size()
        inX = x - w/2 < mouseX < x + w/2
        inY = y - h/2 < mouseY < y + h/2
        return inX and inY

    # 在窗口中显示按钮
    def show(self, screen):
        w, h = self.buttonUp.get_size()
        x, y = self.pos
        # 根据鼠标位置变换样式
        if self.inButtonRange():
            screen.blit(self.buttonDown, (x-w/2,y-h/2))
        else:
            screen.blit(self.buttonUp, (x-w/2, y-h/2))

# 推箱子游戏类
class Sokoban:
    # 构造函数
    def __init__(self):
        # 设置关卡地图（三个）
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
        # 设置每个关卡地图大小（宽度、高度）
        self.w = [10, 12, 19]
        self.h = [11, 11, 11]
        # 设置每个关卡开始时，人在地图中的坐标位置
        self.man = [92, 117, 163]
        # 设置每个关卡中的箱子总数
        self.boxCnt = [4, 5, 6]
        # 设置每个关卡中到达目标点的箱子总数
        self.boxInPositionCnt = [0, 0, 0]
        
    # 以下是元素变换函数
    # 转换为箱子
    def toBox(self, chapter, index):
        if self.level[chapter][index] == '.' or self.level[chapter][index] == '@':
            self.level[chapter][index] = '$'
        else:
            self.level[chapter][index] = '&'

    # 转换为人
    def toMan(self, chapter, index):
        if self.level[chapter][index] == '.' or self.level[chapter][index] == '$':
            self.level[chapter][index] = '@'
        else:
            self.level[chapter][index] = '+'
    
    # 转换为地面
    def toFloor(self, chapter, index):
        if self.level[chapter][index] == '@' or self.level[chapter][index] == '$':
            self.level[chapter][index] = '.'
        else:
            self.level[chapter][index] = '*'
    
    # 偏移量计算函数
    def offset(self, d, width):
        d4 = [-1, -width, 1, width]
        m4 = ['l', 'u', 'r', 'd']
        return d4[m4.index(d.lower())]
    
    # 绘图函数，在窗口中绘制图当前地图及布局
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
    
    # 移动函数（返回1表示推了箱子的移动，返回0表示没推箱子的移动，返回-1表示移动不成功）
    def move(self, chapter, op):
        # 计算偏移
        h = self.offset(op, self.w[chapter])
        # 人前方没有障碍物
        if self.level[chapter][self.man[chapter] + h] == '.' or self.level[chapter][self.man[chapter] + h] == '*':
            # 只有人移动（没有推箱子）
            self.toMan(chapter, self.man[chapter] + h)
            self.toFloor(chapter, self.man[chapter])
            self.man[chapter] += h
            return 0
        # 人前方有障碍物
        elif self.level[chapter][self.man[chapter] + h] == '&' or self.level[chapter][self.man[chapter] + h] == '$':
            # 障碍物为箱子
            if self.level[chapter][self.man[chapter] + 2 * h] == '.' or self.level[chapter][self.man[chapter] + 2 * h] == '*':
                # 人推着箱子移动
                if self.level[chapter][self.man[chapter] + h] == '&':
                    # 原来到达目标点的箱子被移出，数量-1
                    self.boxInPositionCnt[chapter] -= 1
                    #print(self.boxInPositionCnt)
                self.toBox(chapter, self.man[chapter] + 2 * h)
                self.toMan(chapter, self.man[chapter] + h)
                self.toFloor(chapter, self.man[chapter])
                self.man[chapter] += h
                if self.level[chapter][self.man[chapter] + h] == '&':
                    # 有新的箱子到达目标点，数量+1
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
        # flag记录之前一步的移动的布局变化情况，即move()函数返回的值
        flag = op[1]
        h = self.offset(d, self.w[chapter])
        # 人推着箱子移动了
        if flag == 1:
            # 还原上一步箱子的状态和人的状态
            if self.level[chapter][self.man[chapter] + h] == '&':
                # 原来到达目标点的箱子被移出，数量-1
                self.boxInPositionCnt[chapter] -= 1
                #print(self.boxInPositionCnt)
            self.toBox(chapter, self.man[chapter])
            self.toMan(chapter, self.man[chapter] - h)
            self.toFloor(chapter, self.man[chapter] + h)
            self.man[chapter] -= h
            if self.level[chapter][self.man[chapter] + h] == '&':
                # 有新的箱子到达目标点，数量+1
                self.boxInPositionCnt[chapter] += 1
                #print(self.boxInPositionCnt)
        # 只有人移动了
        elif flag == 0:
            # 还原人的状态
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
            # 如果点击的是“开始游戏”
            if startGame.inButtonRange():
                return 1
            # 如果点击的是“游戏说明”
            elif gameTips.inButtonRange():
                return 2
    # 绘制背景图片
    screen.blit(interface, (0,0))
    # 显示“开始游戏”按钮
    startGame.show(screen)
    # 显示“游戏说明”按钮
    gameTips.show(screen)
    return 0

# 显示关卡选择界面的函数
def showChapterInterface(screen, interface, chapter1, chapter2, chapter3, prevInterface):
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == MOUSEBUTTONDOWN:
            # 如果点击的是“第一关”
            if chapter1.inButtonRange():
                return 1
            # 如果点击的是“第二关”
            elif chapter2.inButtonRange():
                return 2
            # 如果点击的是“第三关”
            elif chapter3.inButtonRange():
                return 3
            # 如果点击的是“返回主界面”
            elif prevInterface.inButtonRange():
                return 4
    # 绘制背景图片
    screen.blit(interface, (0,0))
    # 显示“第一关”按钮
    chapter1.show(screen)
    # 显示“第二关”按钮
    chapter2.show(screen)
    # 显示“第三关”按钮
    chapter3.show(screen)
    # 显示“返回主界面”按钮
    prevInterface.show(screen)
    return 0

# 显示过关界面的函数
def showWinInterface(screen, interface, nextChapter, returnToChoose, flag):
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == MOUSEBUTTONDOWN:
            # 如果点击的是“下一关”
            if nextChapter.inButtonRange():
                return 1
            # 如果点击的是“返回选关”
            elif returnToChoose.inButtonRange():
                return 2
    # 绘制背景图片
    screen.blit(interface, (0,0))
    # flag表示是否不是最后一关，如果不是则显示“下一关”按钮，否则不显示
    if flag:
        nextChapter.show(screen)
    # 显示“返回选关”按钮
    returnToChoose.show(screen)
    return 0

def main():
    # 初始化pygame
    pygame.init()
    # 加载各项游戏资源（异常处理）
    try:
        # 设置游戏图标
        gameicon = pygame.image.load("BoxIcon.png")  
        # 展示游戏图标
        pygame.display.set_icon(gameicon)
        # 设置背景音乐
        bgm = ["Hebe - A Little Happiness.mp3", "Mayday - Starry Starry Night.mp3", "Hu Xia - Those Bygones.mp3"]
        # 设置背景音乐音量为50%
        pygame.mixer.music.set_volume(0.5)
        # 设置过关时的音效
        chapterpasssound = pygame.mixer.Sound('Chapter Pass Sound.wav')
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
        skin = pygame.image.load(skinfilename)
        skin = skin.convert()
    except pygame.error as msg:
        raise(SystemExit(msg))

    # 设置游戏界面标题
    pygame.display.set_caption('I Love Sokoban ~')
    # 设置游戏进行过程中的定时器
    clock = pygame.time.Clock()
    # 按住某个键每隔interval(50)毫秒产生一个KEYDOWN事件，delay(200)就是多少毫秒后才开始触发这个事件
    pygame.key.set_repeat(200,50)
    # 游戏主循环
    while True:
        # 设置游戏绘制的最大帧率
        clock.tick(60)
        # flag记录了用户在主界面上点击的是哪个按钮
        flag = showGameInterface(screen, interface, button1, button2)
        # 如果点击点击开始游戏
        if flag == 1:
            # 进入选择的关卡界面循环
            while True:
                clock.tick(60)
                # chapter记录了用户在选择关卡界面上点击的是哪个按钮
                chapter = showChapterInterface(screen, choosechapter, buttonc1, buttonc2, buttonc3, buttonmain) - 1
                # 如果选择的是返回主界面，则退出本界面的循环
                if chapter == 3:
                    break
                # 没有选择则刷新等待
                if chapter == -1:
                    pygame.display.update()
                    continue
                # 如果选择了某一个关卡
                # 创建推箱子游戏主类的实例
                skb = Sokoban()
                # 绘制游戏窗口
                screen.fill(skin.get_at((0,0)))
                skb.draw(screen, chapter, skin)
                # 加载并播放每一关对应的音乐
                pygame.mixer.music.load(bgm[chapter])
                pygame.mixer.music.play(-1)
                # 利用双端队列deque来维护历史操作队列
                dq = deque([])
                # 游戏进程主循环
                while True:
                    clock.tick(60)
                    # retGameInterface记录是否返回选关界面
                    retGameInterface = False
                    for event in pygame.event.get():
                        if event.type == QUIT:
                            pygame.quit()
                            sys.exit()
                        elif event.type == KEYDOWN:
                            # 用户按下了Escape按键，则退出游戏进程循环
                            if event.key == K_ESCAPE:
                                retGameInterface = True
                                break
                            # 如果按下“上”、“下”、“左”、“右”的操作
                            # 画面更新，调用move函数进行移动改变布局
                            # 然后把这一步对象（包括由移动方向和move()函数返回值构成的操作记录元组）放进deque内保存
                            # 绘制改变布局后的新的界面
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
                            # 如果按下Backspace按键，则进行回退操作
                            elif event.key == K_BACKSPACE:
                                # 如果队列不为空
                                if len(dq) > 0:
                                    # 取出当前队尾的对象（操作记录元组）
                                    op = dq.pop()
                                    # 调用还原函数
                                    skb.revmove(chapter, op)
                                    # 绘制改变布局后的新的界面
                                    skb.draw(screen, chapter, skin)
                            # 如果当前队列长度大于50（即存放的操作记录元组数超过50条），则取出队首的对象（即丢弃最早的一条记录），以保持当前队列长度在50以内
                            if len(dq) > 50:
                                dq.popleft()
                    # 如果到达目标点的箱子数量与本关卡箱子总数相等，则过关
                    if skb.boxInPositionCnt[chapter] == skb.boxCnt[chapter]:
                        clock.tick(60)
                        # 背景音乐停止播放
                        pygame.mixer.music.stop()
                        # 根据这是哪一关来显示不同的通关界面（第三关通关界面没有“下一关”的按钮）
                        if chapter == 0 or chapter == 1:
                            win = showWinInterface(screen, chapterpass, buttonnext, buttonret1, 1)
                        elif chapter == 2:
                            win = showWinInterface(screen, chapterpass, buttonnext, buttonret2, 0)
                        # 播放通关音效
                        chapterpasssound.play()
                        # win记录了点击了哪个按钮
                        # 如果点击了“下一关”按钮
                        if win == 1:
                            # 清空队列
                            dq.clear()
                            # 如果不是最后一关
                            if chapter < 2:
                                # 自动跳到下一关
                                chapter += 1
                                # 停止通关音乐的播放
                                chapterpasssound.stop()
                                # 绘制下一关的关卡地图布局
                                screen.fill(skin.get_at((0,0)))
                                skb.draw(screen, chapter, skin)
                                # 加载并播放下一关对应的背景音乐
                                pygame.mixer.music.load(bgm[chapter])
                                pygame.mixer.music.play(-1)
                            pygame.display.update()
                            continue
                        # 如果点击了“返回选关”按钮，则退出该界面的循环
                        elif win == 2:
                            retGameInterface = True
                    # 如果退出推箱子游戏进程，则关闭所有的音乐
                    if retGameInterface == True:
                        chapterpasssound.stop()
                        pygame.mixer.music.stop()
                        pygame.display.update()
                        break
                    pygame.display.update()
        # 如果点击了“游戏说明”按钮
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