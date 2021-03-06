#!/usr/bin/python
import os, sys, pygame, json, subprocess, math
from random import randrange, random
from config.config import paths, emulators, controls, quotes

if not pygame.font: print ('font disabled')
pygame.init()
clock = pygame.time.Clock()

#Emulator stuff
global paths, emulators, controls, quotes

realscreenInfo = pygame.display.Info() # find out the monitor resolution
realw = realscreenInfo.current_w 
realh = realscreenInfo.current_h

windowSize = 1000, 700 # Simple game size for drawing to 
centerH = windowSize[0]*0.5
#GLOBALS

gameTotal = sunpos = suntick = smsunpos = int()
gamePlaying = False
displayfps = False
launchCounter = 1
width = windowSize[0]
height = windowSize[1]
position = 1
speed = 1300
segmentLength = 200
rumbleLength = 20
drawDistance = 600
cameraHeight = 1000 # zheight
cameraDepth = 0.439 # null
roadWidth = 1000 # half roadwidth to use for midscreen - and +
trackLength = int() #null
playerX = 0.21033
playerZ = cameraHeight + cameraDepth
segments = []
stick = None
landscapeOff = 0
oldX = 0
oldY = 0
road = {
  "length": { "none": 0, "short":  100, "medium":  200, "long":  400 }, 
  "curve":  { "none": 0, "easy":    0.06, "medium":   0.08, "hard":    0.1 }
}


#initialise some screens
screen = pygame.Surface(windowSize) # the game drawing surface
actualscreen = pygame.display.set_mode((realw, realh), pygame.FULLSCREEN) # the actual screen for blit and flip
#actualscreen = pygame.display.set_mode((windowSize))
#realw = windowSize[0]
#realh = windowSize[1]

screen_rect = screen.get_rect()


# the horror of twin suns
origSunX = -86
origsmSunx = -86
sunpos = [140, 140] #it's a list, not a tuple - must be mutable
smsunpos = [110, 120]

suntick = 0

# useful colours
red = 255, 0, 0
green = 0, 255, 0
blue = 0, 0, 255
yellow = 0, 255, 255
black = 0, 0, 0
white = 245, 245, 245
grey = 128, 128, 128  
drkgrey = 40, 40, 40
greyHorizon = 195, 195, 195
lgrey = 200,200,200 
backsun = 170, 119, 55
cyan = 148, 208, 229

# ui states
currGame = 0 # current choice of game gameslist[currGame]
currGameState = 0 # state for drawing the game
staticCounter = 1000 #  static but it aint

#setup surface for some shit I forgot all about
sq = pygame.Surface((100, 100))
sqrect = sq.get_rect()


pygame.display.set_caption("Delorean - FluxRacer GUI") # catchy

#set up blank gamelist
gameData = None

class GameState():
    def __init__(self):
        self.state = "load"
    
    def get_state(self):
        return self.state
    
    def set_state(self, requiredState):
        self.state = requiredState
        
        if requiredState == "menu":
            pygame.mixer.music.play(-1)
        else:
            pygame.mixer.music.stop()
            
        print ("Setting state to %s" %(self.state))
        return self.state

def loadUIAssets():
    #background elements
    global backg, tvsurface, staticGroup, tvsurfacelg, sun, smsun, m1, m2
    
    #ui elements
    global shadm, smshadm, road, logo, horizon
    
    # car and other stuff
    global car, carshadow
    staticGroup = []

    backg = pygame.image.load('assets/images/background.png').convert()
    sun = pygame.image.load('assets/images/sun.png').convert_alpha()
    smsun = pygame.transform.smoothscale (sun, (43, 43))
    #small sun recolor
    # zero out RGB values
    smsun.fill((0, 0, 0, 255), None, pygame.BLEND_RGBA_MULT)
    # add in new RGB values
    smsun.fill(backsun[0:3] + (0,), None, pygame.BLEND_RGBA_ADD)

    m1 = pygame.image.load('assets/images/m1.png').convert_alpha()
    m2 = pygame.image.load('assets/images/m2.png').convert_alpha()
    car = pygame.image.load('assets/images/deloreanrear.png').convert_alpha()
    carshadow = pygame.image.load('assets/images/deloreanshadow.png').convert_alpha()    
    logo = pygame.image.load('assets/images/delorea.png').convert_alpha()
    s1 = pygame.image.load('assets/images/static.png').convert()
    s2 = pygame.transform.flip(s1, True, False)
    s3 = pygame.transform.flip(s1, False, True)
    s4 = pygame.image.load('assets/images/logo.png').convert()
    staticGroup.append(s1)
    staticGroup.append(s2)
    staticGroup.append(s3)
    staticGroup.append(s4)
    
    tvsurface = pygame.image.load('assets/images/screen-over.png').convert_alpha()
    tvsurfacelg = pygame.image.load('assets/images/screen-over-lg.png').convert_alpha()
    shadm =  pygame.image.load('assets/images/shad.png').convert_alpha()
    smshadm = pygame.transform.smoothscale (shadm, (130, 54))
    
    horizon = pygame.Surface((1000, 15))
    horizon.fill(greyHorizon)
    
def loadSounds():
    global blip
    blip = pygame.mixer.Sound("assets/sound/blerp.wav")
    pygame.mixer.music.load('assets/sound/vap-back.mp3') 
    
def loadGameData():
    global gameData, gameTotal, currGame
    generic = pygame.image.load('screens/default.jpg').convert()
    with open("./config/games.json", "r") as read_file:
        gameData = json.load(read_file)

    for g in gameData:
        try:
            t = pygame.image.load('screens/'+g["screenshot"]+'.png').convert()
            g["surf"] = pygame.transform.scale(t, (335, 255))
        
        except:
            try:
                t = pygame.image.load('screens/'+g["screenshot"]+'.jpg').convert()
                g["surf"] = pygame.transform.scale(t, (335, 255))
            
            except:
                print("failed to load screen for %s"%g["screenshot"])
                g["surf"] = generic            
    
    gameTotal = len(gameData)
    #currGame = randrange(gameTotal)
    
def setFonts():
    global sysFont, titleFont, gamefont, debugFont
    if pygame.font:
        gamefont = pygame.font.Font("assets/fonts/gameboy.ttf", 12)
        sysFont = pygame.font.Font("assets/fonts/gameboy.ttf", 20)
        titleFont = pygame.font.Font("assets/fonts/gameboy.ttf", 32)
        debugFont = pygame.font.Font(None, 15)
    else:
        print("Fonts appear to be broken")
        
loadSounds()
loadUIAssets()
loadGameData()
setFonts()


def updateQuote():
    ############################
    # Crudity
    ############################
    global currquote, quotes
    
    # "don't repeat yourself"
    newquote = currquote
    while newquote == currquote:
        # "don't repeat yourself"
        currquote = randrange(len(quotes)-1)

####################################
#######ROAD ROAD ROAD###############
####################################
#road segment object
class Seg:
    def __init__(self, index, p1, p2, color, paint, curve):
        self.index = index
        self.p1 = p1
        self.p2 = p2
        self.color = color
        self.paint = paint
        self.curve = curve
    
    def getp1(self):
        return (self.p1)
    
    def getp2(self):
        return (self.p2)
    
    def __str__(self):
        return ("%d in %s" % (self.index, self.color))         

# get a segment within the road map
def findSegment(z):
    ind = math.floor(z/segmentLength) % len(segments)
    return segments[ind]

#exponential foggery pokery
def exponentialFog(distance, density):
    val = 1 / (math.pow(math.e, (distance * distance * density)))
    return val

def addSegment(curve):
    global segments
    n = len(segments)
    p1 =  {
        "world": { "z": n*segmentLength },
        "camera": {},
        "screen": {}
    }
    p2 =  {
        "world": { "z": (n+1)*segmentLength },
        "camera": {},
        "screen": {}
    }
    if (math.floor(n/rumbleLength) % 2):
        paint = True
        color = 93, 93, 93
    else:
        paint = False
        color = 95, 95, 95
    curve: curve
    s = Seg(n, p1, p2, color, paint, curve)
    segments.append(s)

def addRoad(enter, hold, leave, curve):
    for n in range(enter):
        addSegment(easeIn(0, curve, n/enter))
    for n in range(hold):
        addSegment(curve)
    for n in range(leave):
        addSegment(easeInOut(curve, 0, n/leave))

def createStraight():
    addRoad(road['length']['medium'], road['length']['medium'], road['length']['medium'], -road['curve']['none'])
    
    
# generate the road
def resetRoad():
    global segments, segmentLength, rumbleLength, trackLength
    segments = [];
    
    createStraight()
    addRoad(road['length']['medium'], road['length']['medium'], road['length']['medium'], road['curve']['easy'])
    addRoad(road['length']['long'], road['length']['medium'], road['length']['medium'], -road['curve']['medium'])
    addRoad(road['length']['medium'], road['length']['medium'], road['length']['medium'], road['curve']['easy'])
    createStraight()   
    addRoad(road['length']['medium'], road['length']['long'], road['length']['medium'], -road['curve']['easy'])
    addRoad(road['length']['medium'], road['length']['medium'], road['length']['medium'], -road['curve']['medium'])
    addRoad(road['length']['short'], road['length']['medium'], road['length']['medium'], -road['curve']['none'])
    addRoad(road['length']['short'], road['length']['medium'], road['length']['long'], -road['curve']['medium'])
    createStraight()
        
    trackLength = len(segments) * segmentLength;
    
    print("length of road is %d" % (trackLength) )

    
    
####################################
# HELPERS   
####################################
#easing helpers
def easeIn(a,b,percent):
    return a + (b-a)*math.pow(percent,2)

def easeOut(a,b,percent):
    return a + (b-a)*(1-math.pow(1-percent,2))

def easeInOut(a,b,percent):
    return a + (b-a)*((-math.cos(percent*math.pi)/2) + 0.5)

def percentRemaining(n, total):
    return (n%total)/total   
    
# projection helper for 3d to 2d
def project(p, cameraX, cameraY, cameraZ, cameraDepth, width, height, roadWidth):
    p["camera"]["x"] = (p["world"].get("x") or 0) - cameraX
    p["camera"]["y"] = (p["world"].get("y") or 0) - cameraY
    p["camera"]["z"] = (p["world"].get("z") or 0) - cameraZ
    p["screen"]["scale"] = cameraDepth * (10 / p["camera"].get("z"))
    p["screen"]["x"] = round((width/2)  + (p["screen"].get("scale") * p["camera"].get("x") * width/2))
    p["screen"]["y"] = round((height/2) - (p["screen"].get("scale") * p["camera"].get("y") * height/2))
    p["screen"]["w"] = round((p["screen"].get("scale")*roadWidth*(width*0.5)))

# render a road section
def renderSegment(c, w2, x2, y2, w1, x1, y1, p, f = 0):    
    
    #green grass
    if p:
        green = 112, 130, 56
    else:
        green = 114, 132, 58
    pygame.draw.rect(screen, green , (0,y2, 1000, y1-y2))
    
    #clockwise from top left - the road 
    pygame.draw.polygon(screen, c, [
                                (x2-w2, y2),
                                (x2+w2, y2),
                                (x1+w1,y1),
                                (x1-w1,y1)
                            ]
                        )
    #stripe widths
    w2p = w2 * 0.05
    w1p = w1 * 0.05
    w2p2 = w2p * 2
    w1p2 = w1p * 2
    #yellows
    yell = 204, 204, 0
    pygame.draw.polygon(screen, yell, [
                                (x2-(w2-w2p), y2),
                                (x2-(w2-w2p2), y2),
                                (x1-(w1-w1p2),y1),
                                (x1-(w1-w1p),y1)
                            ]
                        )
    pygame.draw.polygon(screen, yell, [
                                (x2+(w2-w2p2), y2),
                                (x2+(w2-w2p), y2),
                                (x1+(w1-w2p),y1),
                                (x1+(w1-w2p2),y1)
                            ]
                        )
    if p:
        rumble = 220, 220, 220
    else:
        rumble = 200, 0, 0
        
    w2poff = w2 * 0.2
    w1poff = w1 * 0.2

    pygame.draw.polygon(screen, rumble, [
                                (x2-(w2+w2poff), y2),
                                (x2-w2, y2),
                                (x1-w1,y1),
                                (x1-(w1+w1poff),y1)
                            ]
                        )
    pygame.draw.polygon(screen, rumble, [
                                (x2+w2, y2),
                                (x2+(w2+w2poff), y2),
                                (x1+(w1+w1poff),y1),
                                (x1+w1,y1)
                            ]
                        )
                        
    #center line
    w2p = w2 * 0.02
    w1p = w1 * 0.02
    
    whiteline = 200, 200, 200
    if p:
        pygame.draw.polygon(screen, (whiteline), [
                                (x2-w2p, y2),
                                (x2+w2p, y2),
                                (x1+w2p,y1),
                                (x1-w2p,y1)
                            ]
                        )
    if f < 1:
        fh = y1-y2
        f = f*255

        s = pygame.Surface((width,fh))  # the size of your rect
        s.set_alpha(255-f)                # alpha level
        s.fill((0,0, 0))           # this fills the entire surface
        screen.blit(s, (0, y2))    # (0,0) are the top-left coordinates

# draw all sections in view    
def drawRoad():
    global drawDistance, position, cameraHeight, cameraDepth, roadWidth, playerX, width, height, trackLength, car
    baseSegment = findSegment(position);
    basePercent = percentRemaining(position, segmentLength)
    dx = -(baseSegment.curve * basePercent)
    x = 0
    
    maxy = height;
    for n in range(drawDistance):
        segInd = (baseSegment.index + n) % len(segments)
        segment = segments[segInd];
        # loop the track
        looped = segment.index < baseSegment.index
        if looped == True:
            position = 1
            
        project(segment.p1, (playerX * roadWidth) -x, cameraHeight, position, cameraDepth, width, height, roadWidth); # update screen values closest edge to camera
        project(segment.p2, (playerX * roadWidth) -x -dx, cameraHeight, position, cameraDepth, width, height, roadWidth); # update screen values furthest edge from camera
        
        x  = x + dx;
        dx = dx + segment.curve;
        
        if ((segment.p1["camera"].get("z") <= cameraDepth) or (segment.p2["screen"].get("y") >= maxy)): # discard invisible sections
           continue
           
        # generate the section co-ords  to pass to the render function
        c = segment.color
        p = segment.paint
        w2 = segment.p2["screen"].get("w") # furthest from camera
        x2 = segment.p2["screen"].get("x")
        y2 = segment.p2["screen"].get("y")
        w1 = segment.p1["screen"].get("w") # closest
        x1 = segment.p1["screen"].get("x")
        y1 = segment.p1["screen"].get("y")
        f = exponentialFog(n/drawDistance, 0.9);
        
        renderSegment(c, w2, x2, y2, w1, x1, y1, p, f)
        
        maxy = segment.p2["screen"].get("y")

def updateWorld():
    global position, speed, playerX, stick
    
    if stick:    
        playerX = stick.get_axis(controls["steering"])
    else:
        ms = pygame.mouse.get_pos()
        playerX = ((realw*0.5) - ms[0])*0.001 
    position = position + speed

    #print((realw*0.5)*0.001)
    

def renderBackground():
    ############################
    # This is just the backdrop - bad name
    ############################
    screen.blit(backg, (0,0))
    updateWorld()
    drawRoad()
    
    renderLandscape()
    renderLogo()

def renderLandscape():
    global position, playerZ, landscapeOff, m1, m2
    
    speed = 0.01
    
    #find current segment to get curve data
    playerSegment = findSegment(position+playerZ);
    currCurve = playerSegment.curve
    # user input for offset
    ms = pygame.mouse.get_pos()    
    if stick:    
        ctrlOffset = stick.get_axis(controls["steering"])*-50
    else:
        ctrlOffset = ((realw*0.5) - ms[0])*0.05
        
    # calculate road curvature offset 
    landscapeOff = landscapeOff + (0.5  * currCurve) * -80
    # set total offset
    totalOffset = ctrlOffset+landscapeOff
    
    #draw the car - quick
    plrect = carshadow.get_rect()
    #shadow first - lets hardcode some stuff
    srect = shadm.get_rect()
    srect.top = 490
    srect.left = (width*0.5-82)+(((currCurve) * 2000))
    screen.blit(carshadow, srect)
    # then the car
    plrect.top = 480 + (random()*2) # add vertical noise for bumps
    plrect.left = (width*0.5-70)+(((currCurve) * 2000))
    screen.blit(car, plrect)
    
    smoff = (500 - smsunpos[0])
    soff = (300 - sunpos[0])
    if smoff < 0:
        smoff *= -1
    if soff < 0:
        soff *= -1
        
    smsunmult = (1 + (smoff*0.002))
    sunmult = (1 + (soff*0.002))
    smelev = (500 - smsunpos[0])*0.001;
    selev = (500 - sunpos[0])*0.0015;
    
    if smsunpos[0] >= 1021:
        sunpos[0] = origSunX
        smsunpos[0] = origsmSunx
        sunpos[1] = 250
        smsunpos[1] = 200

        return

    smsunpos[0] = smsunpos[0] + (smsunmult*speed)
    smsunpos[1] = smsunpos[1] - (smelev*speed)
    
    sunpos[0] = sunpos[0] + (sunmult*speed)
    sunpos[1] = sunpos[1] - (selev*speed)

    
    s = sun
    sm = smsun
    
    smrect = smsun.get_rect()
    smrect.left = (smsunpos[0]-21)+(totalOffset*0.2)
    smrect.top = smsunpos[1]

    screen.blit(sm, smrect)
    
    srect = s.get_rect()
    srect.left = (sunpos[0]-43)+(totalOffset*0.2)
    srect.top = sunpos[1]
    screen.blit(s, srect)

    # draw the mountains
    mrect = m2.get_rect() #m2 being the big background one
    mw = m2.get_width() # harcode - cheaper than mw = sm.get_width()
    loff = (totalOffset*0.5) % mw # modulo the offset and width
    mrect.left = -538+loff # offset half width for niceness - use half the offset for paralax
    mrect.top = 238 # hardcode - cheaper than sm.get_height()
    screen.blit(m2, mrect) # blit at the remainder
    mrect.left = mrect.left - mw # move left by one image width
    screen.blit(m2, mrect) # draw another one to fill the gap as we move offscreen
    
    #draw front mountain
    mrect2 = m1.get_rect()
    smw = m1.get_width() # hardcode
    loff = totalOffset % smw
    mrect2.left = loff
    mrect2.top = 309
    screen.blit(m1, mrect2)
    mrect2.left = mrect2.left - smw
    screen.blit(m1, mrect2)
    
    
def renderLogo():
    ############################
    # Render the non functional ui content
    ############################    

    logoV = 600 # used to be 600
    #deloria logo
    logo_rect = logo.get_rect(centerx=screen_rect.centerx)
    screen.blit(logo, (logo_rect.left, logoV)) 

    quoteV = 678 #was 138
    if pygame.font:   
        q = quotes[currquote]
        text = gamefont.render(q , 1, lgrey)
        textpos = text.get_rect(centerx = centerH, centery = quoteV)
        screen.blit(text, textpos)
    if displayfps:
        fps = str(int(clock.get_fps()))
        fp = debugFont.render("Craig's fps = "+fps, 1, black)
        screen.blit(fp, (910,20))

def renderLoading():
    ############################
    # Render the Loading screen
    ############################
    global gamePlaying, launchCounter   
    if pygame.font:   
        text = titleFont.render("Loading..." , 1, drkgrey)
        textpos = text.get_rect(centerx = centerH, centery = windowSize[1]/2)
        screen.blit(text, textpos)
    
    if gamePlaying == False:
        if launchCounter > 100:
            gamePlaying = True
            launchGame()
        else:
            launchCounter = launchCounter + 1
        

def launchGame()-> subprocess.CompletedProcess:
    #############################
    # Launch the current selected game
    #############################
    global gamePlaying, launchCounter, stick
     
    currGameObj = gameData[currGame] # get current game
    gsys = currGameObj["system"] # what emulator is needed
    if gsys == "IBM PC":
        launchstring = os.path.abspath(currGameObj["exePath"])
        print(launchstring)
        pr = subprocess.run([launchstring], capture_output=True)
    else:        
        workDir = paths[gsys]  # get the emulator working directory
        emulator = emulators[gsys] # get the emulator excecutable name
        launchstring = os.path.abspath(str(workDir+emulator)) # setup exe call
        print(launchstring)
        emArgs = ""
        if gsys == "AM2":
            emArgs = currGameObj["screenshot"]
        elif gsys == "AM3":
            emArgs = ".\\roms\\{}.zip ".format(currGameObj["screenshot"])
        elif gsys == "MAME":
            emArgs = currGameObj["screenshot"]
            
        stick.quit()
        pr = subprocess.run([launchstring, emArgs], cwd=workDir, capture_output=True)
    
    if pr:
        delorean.set_state("menu")
        launchCounter = 0
        gamePlaying = False
        stick = pygame.joystick.Joystick(i)
        stick.init()
    
    
def renderGames():
    #############################
    # Render the game tiles
    #############################
    
    global gameData, gameTotal, posy
    g = gameData[currGame]
    
    ogInd = currGame-1
    ngInd = currGame+1
    og = None
    ng = None
    
    if currGame > 0:
        og = gameData[ogInd]
        
    if currGame < len(gameData)-1:
        ng = gameData[ngInd]
    
    currGameSurf = g["surf"]
    tilew = currGameSurf.get_width()
    tileh = currGameSurf.get_height()
    posx = centerH - (tilew*0.5)
    posy = (29)# was 29
    sqrect.top = posy
    sqrect.left = posx 
    
    screen.blit(currGameSurf, sqrect)
    renderStatic()
    screen.blit(tvsurface, sqrect)
    
       
    if pygame.font:       
        gametitle = titleFont.render(g["name"] , 1, white)
        tepos = gametitle.get_rect(centerx=sqrect.left+(tilew*0.5), centery= posy+tileh + 20)
        screen.blit(gametitle, tepos)
        
        systitle = sysFont.render(g["system"] , 1, lgrey)
        tepos = systitle.get_rect(centerx=sqrect.left+(tilew*0.5), centery= posy+tileh + 50)
        screen.blit(systitle, tepos)
        
        gameCount = str(currGame+1) + " of " + str(gameTotal)
        systotal = sysFont.render(gameCount, 1, lgrey)
        syspos = systotal.get_rect(top = 10, left = 20)
        screen.blit(systotal, syspos)

    screen.blit(shadm, (293, posy+350))
    
    weeW = int(tilew*0.3)
    weeH = int(tileh*0.3)
    
    if og:
        oldX = posx - (weeW+20)
        oldY = posy + int((tileh-weeH)*.1)
        sqrect.left = oldX
        sqrect.top = oldY
        weeOld = og["surf"]
        weeOld = pygame.transform.smoothscale (weeOld, (weeW, weeH))
        weeOld.set_alpha(150)
        screen.blit(weeOld, sqrect)
    #render next game
    
        sqrect.top = 412
        sqrect.left = 184
        screen.blit(smshadm, sqrect)
    
    if ng:
        newX = posx + (tilew+20)
        newY = posy + int((tileh-weeH)*.1)
        sqrect.left = newX
        sqrect.top = newY
        weeNew = ng["surf"]
        weeNew = pygame.transform.smoothscale (weeNew, (weeW, weeH))
        weeNew.set_alpha(150)
        screen.blit(weeNew, sqrect)
        
        sqrect.top = 412
        sqrect.left = 681
        screen.blit(smshadm, sqrect)
        
    screen.blit(tvsurfacelg, (0,0,1000,700))

def renderStatic():
    global staticCounter, staticGroup, posy
    staticCounter += 1
    displ = 0;
    if (staticCounter <= 1099):
        return
    else:
        if (staticCounter <= 1100):
            displ = randrange(14)
            if (displ >= 3):
                return
        elif (staticCounter <= 1130):  
            displ = randrange(4);
            if (displ>=4):
                return
        elif (staticCounter <= 1150):  
            displ = randrange(3)+2;
            if (displ>=4):
                return
        elif (staticCounter <= 1158):  
            displ = 3
        elif (staticCounter <= 1170):  
            displ = randrange(4);
            if (displ>=4):
                return
        elif (staticCounter >= 1171):
            staticCounter = 0
            updateQuote()
            return
            
        if (displ != 0):   
            currStatic = staticGroup[displ]
            screen.blit(currStatic, (333, posy, 335, 255))

def handleEvents():
    #########################
    # handle inputs
    #########################
    
    global currGame, DDZ, maxText, stick, displayfps
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit(); sys.exit()

        if event.type == pygame.JOYBUTTONDOWN:
            input = event.button
            if delorean.get_state() == "menu": # only affect menu
                if input == controls["gameup"]:          
                    if currGame < (len(gameData)-1):
                        currGame+=1
                        pygame.mixer.Sound.play(blip)
                elif input == controls["gamedown"]:
                    if currGame > 0:
                        currGame-=1
                        pygame.mixer.Sound.play(blip)            
                elif input == controls["gameselect"]:  
                    delorean.set_state("playing")
                    
        if event.type == pygame.KEYDOWN:
            #keys = pygame.key.get_pressed()  #checking pressed keys
            if event.key == pygame.K_ESCAPE:
                pygame.quit(); sys.exit()
            if delorean.get_state() == "menu": # only affect menu
                if event.key == pygame.K_LEFT:
                    if currGame > 0:
                        currGame-=1
                        pygame.mixer.Sound.play(blip)
                if event.key == pygame.K_RIGHT:
                    if currGame < (len(gameData)-1):
                        currGame+=1
                        pygame.mixer.Sound.play(blip)
                if event.key == pygame.K_RETURN:
                    delorean.set_state("playing")
                
            if event.key == pygame.K_UP:
                if displayfps:
                    displayfps = False
                else:
                    displayfps = True
            if event.key == pygame.K_SPACE:        
                updateQuote()
            



#######################
#  initial menu setup - start here
#######################

# create intial gamestate class
delorean = GameState() # new instance of the gamestate class assigned to delorean
# pick a random quote
currquote = randrange(len(quotes)-1)
# set to menu
delorean.set_state("menu");

resetRoad()
joystick_count = pygame.joystick.get_count()
for i in range(joystick_count):
    stick = pygame.joystick.Joystick(i)
    stick.init()

        
#######################
#  main loop
#######################
def renderGameState():
    state = delorean.get_state() # get current game state
    renderBackground() # always render the background
    if state == "menu":
        #print("test")
        renderGames()
    if state == "playing":
        renderLoading()   
    handleEvents() # finally handle input event
    
    #ox = (realw - 1000)*0.5
    #oy = (realh - 700)*0.5
    #actualscreen.blit(screen, (ox, oy)) # blit to the actual screen
    
    scaledscreen = pygame.transform.smoothscale (screen,(realw, realh)) # scale up the screen to window size
    actualscreen.blit(scaledscreen, (0 ,0))
    pygame.display.flip() # flip the buffer

while 1:
    clock.tick(60)
    renderGameState()
