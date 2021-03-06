import sys, pygame

currInput = "-"
windowSize = 400, 400
width = windowSize[0]
height = windowSize[1]

if not pygame.font: print ('font disabled')
pygame.init()
clock = pygame.time.Clock()

screen = pygame.Surface(windowSize) # the game drawing surface
actualscreen = pygame.display.set_mode((windowSize))
pygame.display.set_caption("Delorean - Joystick Buttons")

titleFont = pygame.font.Font("assets/fonts/gameboy.ttf", 32)

joystick_count = pygame.joystick.get_count()

for i in range(joystick_count):
    stick = pygame.joystick.Joystick(i)
    stick.init()

def renderBackground():
        screen.fill((0,0,0))
        global currInput
        text = titleFont.render(currInput , 1, (230,230,230))
        textpos = text.get_rect(centerx = width*0.5, centery = height*0.5)
        screen.blit(text, textpos)

def handleEvents():
    global currInput
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit(); sys.exit()
        
        if event.type == pygame.JOYAXISMOTION:
            if event.value > 0.7 or event.value < -0.7:
                input = str(event.axis)
                if event.value > 0:
                    dir = "pos"
                else:
                    dir = "neg"
                currInput = "Axis "+input+": "+dir
        if event.type == pygame.JOYHATMOTION:
            print(event)
            
            #input = event.axis
            #currInput = str(input)
        if event.type == pygame.JOYBUTTONDOWN:
            input = str(event.button)
            currInput = "BTN: "+input
            
        if event.type == pygame.KEYDOWN:
            #keys = pygame.key.get_pressed()  #checking pressed keys
            if event.key == pygame.K_ESCAPE:
                pygame.quit(); sys.exit()
                
while 1:
    clock.tick(60)
    renderBackground()
    handleEvents()
    actualscreen.blit(screen, (0, 0))
    pygame.display.flip() # flip the buffer