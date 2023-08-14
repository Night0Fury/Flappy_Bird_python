import random
import sys
import pygame
from pygame.locals import *  # Basic pygame imports

# Global Variables for the game
FPS = 45
SCREENWIDTH = 720
SCREENHEIGHT = 1000
SCREEN = pygame.display.set_mode((SCREENWIDTH, SCREENHEIGHT))
GROUNDY = SCREENHEIGHT * 0.8
GAME_image = {}
GAME_SOUNDS = {}
PLAYER = 'files/image/bird.png'
BACKGROUND = 'files/image/background.jpg'
PIPE = 'files/image/pipe.png'

def welcomeScreen():
    """
    Shows welcome images on the screen
    """
    global messagex, messagey  # Define these variables as global

    playerx = int(SCREENWIDTH/5)
    playery = int((SCREENHEIGHT - GAME_image['player'].get_height())/2)
    messagex = int((SCREENWIDTH - GAME_image['message'].get_width())/2)
    messagey = int(SCREENHEIGHT*0.13)
    basex = 0

    while True:
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()

            elif event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP):
                return

        SCREEN.blit(GAME_image['background'], (0, 0))
        SCREEN.blit(GAME_image['player'], (playerx, playery))
        SCREEN.blit(GAME_image['message'], (messagex, messagey))
        SCREEN.blit(GAME_image['base'], (basex, GROUNDY))
        pygame.display.update()
        FPSCLOCK.tick(FPS)
def mainGame():
    score = 0
    playerx = int(SCREENWIDTH/5)
    playery = int(SCREENWIDTH/2)
    basex = 0

    # Create 2 pipes for blitting on the screen
    newPipe1 = getRandomPipe()
    newPipe2 = getRandomPipe()

    # my List of upper pipes
    upperPipes = [
        {'x': SCREENWIDTH+200, 'y':newPipe1[0]['y']},
        {'x': SCREENWIDTH+200+(SCREENWIDTH/2), 'y':newPipe2[0]['y']},
    ]
    # my List of lower pipes
    lowerPipes = [
        {'x': SCREENWIDTH+200, 'y':newPipe1[1]['y']},
        {'x': SCREENWIDTH+200+(SCREENWIDTH/2), 'y':newPipe2[1]['y']},
    ]

    pipeVelX = -4

    playerVelY = -9
    playerMaxVelY = 10
    playerMinVelY = -8
    playerAccY = 1

    playerFlapAccv = -12 # velocity while flapping
    playerFlapped = False # It is true only when the bird is flapping

    while True:
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP):
                if playery > 0:
                    playerVelY = playerFlapAccv
                    playerFlapped = True
                    GAME_SOUNDS['wing'].play()

        crashTest = isCollide(playerx, playery, upperPipes, lowerPipes)
        if crashTest:
            GAME_SOUNDS['hit'].play()
            GAME_SOUNDS['swoosh'].play()  # Play the swoosh sound
            restartGame()  # Restart the game

        #check for score
        playerMidPos = playerx + GAME_image['player'].get_width()/2
        for pipe in upperPipes:
            pipeMidPos = pipe['x'] + GAME_image['pipe'][0].get_width()/2
            if pipeMidPos<= playerMidPos < pipeMidPos +4:
                score +=1
                print(f"Your score is {score}") 
                GAME_SOUNDS['point'].play()


        if playerVelY <playerMaxVelY and not playerFlapped:
            playerVelY += playerAccY

        if playerFlapped:
            playerFlapped = False            
        playerHeight = GAME_image['player'].get_height()
        playery = playery + min(playerVelY, GROUNDY - playery - playerHeight)

        # move pipes to the left
        for upperPipe , lowerPipe in zip(upperPipes, lowerPipes):
            upperPipe['x'] += pipeVelX
            lowerPipe['x'] += pipeVelX

        # Add a new pipe when the first is about to cross the leftmost part of the screen
        if 0<upperPipes[0]['x']<5:
            newpipe = getRandomPipe()
            upperPipes.append(newpipe[0])
            lowerPipes.append(newpipe[1])

        # if the pipe is out of the screen, remove it
        if upperPipes[0]['x'] < -GAME_image['pipe'][0].get_width():
            upperPipes.pop(0)
            lowerPipes.pop(0)
        
        # Lets blit our image now
        SCREEN.blit(GAME_image['background'], (0, 0))
        for upperPipe, lowerPipe in zip(upperPipes, lowerPipes):
            SCREEN.blit(GAME_image['pipe'][0], (upperPipe['x'], upperPipe['y']))
            SCREEN.blit(GAME_image['pipe'][1], (lowerPipe['x'], lowerPipe['y']))

        SCREEN.blit(GAME_image['base'], (basex, GROUNDY))
        SCREEN.blit(GAME_image['player'], (playerx, playery))
        myDigits = [int(x) for x in list(str(score))]
        width = 0
        for digit in myDigits:
            width += GAME_image['numbers'][digit].get_width()
        Xoffset = (SCREENWIDTH - width)/2

        for digit in myDigits:
            SCREEN.blit(GAME_image['numbers'][digit], (Xoffset, SCREENHEIGHT*0.12))
            Xoffset += GAME_image['numbers'][digit].get_width()
        pygame.display.update()
        FPSCLOCK.tick(FPS)

def isCollide(playerx, playery, upperPipes, lowerPipes):
    if playery> GROUNDY - 50  or playery<0:
        GAME_SOUNDS['hit'].play()
        return True
    
    for pipe in upperPipes:
        pipeHeight = GAME_image['pipe'][0].get_height()
        if (
            playery < pipeHeight + pipe['y']
            and abs(playerx - pipe['x']) < GAME_image['pipe'][0].get_width()
        ):
            GAME_SOUNDS['hit'].play()
            return True

    for pipe in lowerPipes:
        if (
            playery + GAME_image['player'].get_height() > pipe['y']
            and abs(playerx - pipe['x']) < GAME_image['pipe'][0].get_width()
        ):
            GAME_SOUNDS['hit'].play()
            return True

    return False

def getRandomPipe():
    pipeHeight = GAME_image['pipe'][0].get_height()
    offset = SCREENHEIGHT/4
    y2 = offset + random.randrange(0, int(SCREENHEIGHT - GAME_image['base'].get_height()  - 1.2 *offset))
    pipeX = SCREENWIDTH + 10
    y1 = pipeHeight - y2 + offset
    pipe = [
        {'x': pipeX, 'y': -y1}, #upper Pipe
        {'x': pipeX, 'y': y2} #lower Pipe
    ]
    return pipe

def restartGame():
    global score
    score = 0
    welcomeScreen()
    mainGame()

if __name__ == "__main__":
    pygame.init()
    pygame.mixer.init()

    FPSCLOCK = pygame.time.Clock()
    pygame.display.set_caption('Flappy Bird ')

    GAME_image['numbers'] = (
        pygame.image.load('files/image/0.png').convert_alpha(),
        pygame.image.load('files/image/1.png').convert_alpha(),
        pygame.image.load('files/image/2.png').convert_alpha(),
        pygame.image.load('files/image/3.png').convert_alpha(),
        pygame.image.load('files/image/4.png').convert_alpha(),
        pygame.image.load('files/image/5.png').convert_alpha(),
        pygame.image.load('files/image/6.png').convert_alpha(),
        pygame.image.load('files/image/7.png').convert_alpha(),
        pygame.image.load('files/image/8.png').convert_alpha(),
        pygame.image.load('files/image/9.png').convert_alpha(),
    )

    GAME_image['message'] =pygame.image.load('files/image/message.png').convert_alpha()
    GAME_image['base'] =pygame.image.load('files/image/base.png').convert_alpha()
    GAME_image['pipe'] =(pygame.transform.rotate(pygame.image.load( PIPE).convert_alpha(), 180), 
    pygame.image.load(PIPE).convert_alpha()
    )

    # Game sounds
    GAME_SOUNDS['die'] = pygame.mixer.Sound('files/audio/die.wav')
    GAME_SOUNDS['hit'] = pygame.mixer.Sound('files/audio/hit.wav')
    GAME_SOUNDS['point'] = pygame.mixer.Sound('files/audio/point.wav')
    GAME_SOUNDS['swoosh'] = pygame.mixer.Sound('files/audio/swoosh.wav')
    GAME_SOUNDS['wing'] = pygame.mixer.Sound('files/audio/wing.wav')

    GAME_image['background'] = pygame.image.load(BACKGROUND).convert()
    GAME_image['player'] = pygame.image.load(PLAYER).convert_alpha()

    while True:
        welcomeScreen() # Shows welcome screen to the user until he presses a button
        mainGame() # This is the main game function 