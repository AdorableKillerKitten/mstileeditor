# tkinter as the interface 
# TODO: Jot down structure of ms Tiles 
# Get the MS Colorpalette
# SetUp Basic Window DONE
# Add a Canvas DONE
# add a Grid DONE 
# Add A Palette (at first with a default Palette) DONE
# Add Color select 
# add coloring in pixel DONE
# add coloring in area and choosing background color 
# Add function to chose colors for the palette 
# Add additional palette quickselect
# add Palette animation feature 
# Export Tiledata and palette data 
# fancy for later -> auto replace tile and palette info in source code
# little less fancy autoappend tile data to source code 
# __________Redesign___________
# find a way through usage of classes to get rid of all the global variables 
# check whether canvas creates objects for every drawing command in that case I have to change the drawing routine 
# rewrite tool and pixelcanvas so that 
# tool only holds information about which commands to apply
# all the color information is saved in the pixelcanvas itself 
# rewrite previewframe in such a way that each tile is its own pixelcanvas
# 
# Current Priotrity: 
# 1. TileSelection
# 2. Palette Colorpicker 
# 3. Generate asm data for colorpalette and tiles 
# 4. Save and load function 
#  

# fill sometimes get stuck in a recursive loop
# when using pickle and changing the canvas object this causes issues when trying to load data,
# use a different approach instead 


from tkinter import * 
from tkinter import ttk 
from functools import partial 
import random 
import pickle

def createRandomPalette(): # returns a list  random Indexes for generating a random palette out of the default Palette
    
    return random.sample(range(0,63),16)


# VARIABLE DECLERATION BOCK
# ------------------------------------------------------------------------------------------------------------------------------------------

paletteIndexes = createRandomPalette()
PixelWidth = 60
canvasWidth = 8*PixelWidth
canvasHeight = canvasWidth
defaultPalette = ['#000000', '#400000', '#C00000', '#FF0000', '#004000', '#404000', '#C04000', '#FF4000', '#00C000', '#40C000', '#C0C000', '#FFC000', '#00FF00', '#40FF00', '#C0FF00', '#FFFF00', '#000040', '#400040', '#C00040', '#FF0040', '#004040', '#404040', '#C04040', '#FF4040', '#00C040', '#40C040', '#C0C040', '#FFC040', '#00FF40', '#40FF40', '#C0FF40', '#FFFF40', '#0000C0', '#4000C0', '#C000C0', '#FF00C0', '#0040C0', '#4040C0', '#C040C0', '#FF40C0', '#00C0C0', '#40C0C0', '#C0C0C0', '#FFC0C0', '#00FFC0', '#40FFC0', '#C0FFC0', '#FFFFC0', '#0000FF', '#4000FF', '#C000FF', '#FF00FF', '#0040FF', '#4040FF', '#C040FF', '#FF40FF', '#00C0FF', '#40C0FF', '#C0C0FF', '#FFC0FF', '#00FFFF', '#40FFFF', '#C0FFFF', '#FFFFFF']

previewPixelWidth = 3
previewCanvasWidth = 8*previewPixelWidth
previewCanvasHeight = previewCanvasWidth


mousePixel = [-1,-1]
lastX = 0
lastY = 0

selectedColor = 0

def colorConverter(r,g,b):
    # structure of MasterSystem Colorbyte xxBBGGRR
    colorLookuptable = ['00','40','C0','FF']
    # clean up color variables for safety
    r = r & 3
    g = g & 3
    b = b &3 
    return "#" + colorLookuptable[r] + colorLookuptable[g] + colorLookuptable[b]


def createByteValues_fromColor(col):

    clt = {'00':0,'40':1,'C0':2,'FF':3}


    col = col.replace('#','')
    
    r = clt[col[0:2]]
    g = clt[col[2:4]]
    b = clt[col[4:6]]

    r = r << 4
    g = g << 2 
    
    return r | g | b


#create basic greyscale
greyScale = []
greyScale.append(colorConverter(3,3,3))
greyScale.append(colorConverter(2,2,2))
greyScale.append(colorConverter(1,1,1))
greyScale.append(colorConverter(0,0,0))
for i in range(12):
    greyScale.append(defaultPalette[i+5])    

msPalette = []
for e in greyScale:
    msPalette.append(createByteValues_fromColor(e))

print(msPalette)


def formatToVASM(byteArr):
    outputString = ""
    for b in byteArr:
        pos = len(b)
        outputString += "db "
        
        for val in b:
            
            outputString += "&{:02x}".format(val)
            
            if( pos != 1):
                
                outputString += ", "
            else:
                outputString += "\n"
                
            pos -= 1
    
    return outputString      
           




def convertToPattern(colorGrid,palette=None):
    rows = []
    for y in colorGrid:
        currentLine = []
        if not palette:
            rows.append(colorGrid.index(y))
            continue

        for x in y:
            currentLine.append(palette.index(x))
        
        rows.append(currentLine)
    byteArr = []
    for i in range(len(rows)):

        maskValue = 128
        byte1 = 0
        byte2 = 0
        byte3 = 0
        byte4 = 0
        if not palette:
            x = rows[i]
            byte1 += maskValue * ( x&1)
            byte2 += maskValue * ((x&2) >> 1)
            byte3 += maskValue * ((x&4) >> 2)
            byte4 += maskValue * ((x &8) >> 4)
            maskValue = maskValue >> 1
        else:     
            for j in range(len(rows[i])):
                x = rows[j][i]
                byte1 += maskValue * ( x&1)
                byte2 += maskValue * ((x&2) >> 1)
                byte3 += maskValue * ((x&4) >> 2)
                byte4 += maskValue * ((x &8) >> 4)
                maskValue = maskValue >> 1
        byteArr.append([byte1,byte2,byte3,byte4])

    return formatToVASM(byteArr)
        

    





class PixelCanvas:
    def __init__(self, _pWidth, _pHeight, _width,_height, frame,tileNo = 0) -> None:
        self.pixelWidth = _pWidth
        self.pixelHeight = _pHeight
        self.width = _width
        self.height = _height
        self.masterFrame = frame
        self.canvas = Canvas(self.masterFrame,width=self.width,height=self.height,background="white",borderwidth=0,highlightthickness=0)
        self.pixelGrid = True
        self.gridColorValues = []
        self.tileNo = tileNo
        pass

    def setGridPos(self,x,y,padding=None):
        print(x,y)
        if not padding:
            self.canvas.grid(column=x,row=y,sticky="news")
        else:
            self.canvas.grid(column=x,row=y,padx=padding[0:1],pady=padding[2:3],sticky="news")

    def fillArea(self,x,y,color):
        origColor = self.gridColorValues[x][y]
        if color == origColor:
            return
        print(x,y)
        #self.setPixelColor([x,y],color)
        self.gridColorValues[x][y] = color
        if x >= 1 and self.gridColorValues[x-1][y] == origColor:
            self.fillArea(x-1,y,color)
        if x < len(self.gridColorValues)-1 and self.gridColorValues[x+1][y] == origColor:
            self.fillArea(x+1,y,color)
        if y >= 1 and self.gridColorValues[x][y-1] == origColor:
            self.fillArea(x,y-1,color)
        if y < len(self.gridColorValues[x])-1 and self.gridColorValues[x][y+1] == origColor:
            self.fillArea(x,y+1,color)
        return 

    def returnTileNo(self,event=None):
        return self.tileNo

    def colorInPixel(self,color,x,y): # Colors in a pixel x,y are relative to the PixelGrid Cooardinates
        if(self.pixelGrid):
            self.canvas.create_rectangle(x*self.pixelWidth,y*self.pixelWidth,(x+1)*self.pixelWidth,(y+1)*self.pixelWidth, outline="black", fill=color)
        else:
            self.canvas.create_rectangle(x*self.pixelWidth,y*self.pixelWidth,(x+1)*self.pixelWidth,(y+1)*self.pixelWidth, outline=color, fill=color)

    def cleanUpCanvas(self,event):
        
        self.canvas.delete("all")
        for y in range(len(self.gridColorValues)):
            for x in range(len(self.gridColorValues[y])):
                self.colorInPixel(self.gridColorValues[y][x],y,x)
        
        self.canvas.create_rectangle(0,0,self.canvas.winfo_width()-1,self.canvas.winfo_height()-1,outline='black')


    def setPixelColor(self, event,color):
        
        x,y = event
        
        self.gridColorValues[x][y] = color
       

    def drawGridLines(self): # sets up grid lines for the pixelGrid 
        for x in range(8):
            self.canvas.create_line(x*self.pixelWidth,0,x*self.pixelWidth,self.height)
            self.canvas.create_line(0,x*self.pixelWidth,self.width,x*self.pixelWidth)

    def resetCanvas(self,color="#FFFFFF"):
        for x in range(len(self.gridColorValues)):
            for y in range(len(self.gridColorValues[x])):
                self.gridColorValues[x][y] = "#FFFFFF"
        self.cleanUpCanvas(self)

    
class FileHandler:
    def __init__(self,pCanvas,tiles,tool)-> None:
        self.pCanvas = pCanvas
        self.tiles = tiles 
        self.tool = tool 
        self.file = None 

    def initFile(self,path="F:\\tmp.pk"):
        self.file= open(path,"wb")

    def cleanUp(self):
        if self.file:
            self.file.close() 
        else:
            pass 

    def save_f_data_file(self,filename="test.txt"):
            
        print(convertToPattern(self.pCanvas.gridColorValues,self.tool.palette1))
        print(convertToPattern(self.tool.palette1))
        #self.file.write(convertToPattern(colorValues,self.palette1))
        #self.file.close()

    def newFile(self):
        print("New File was registered")
        self.pCanvas.resetCanvas()
        for tile in self.tiles:
            tile.resetCanvas()
        

    def openFile(self):
        self.file = open("F:\\tmp.pk",'rb')
        self.pCanvas.gridColorValues = pickle.load(self.file)
        self.file.close()

        print("Opened File")


    def saveFile(self):
        self.initFile()
        print(self.pCanvas.gridColorValues)
        pickle.dump(self.pCanvas.gridColorValues,self.file,pickle.HIGHEST_PROTOCOL)
        self.file.close()
        print("File saved")
        

    def saveFileas(self):
        print("saved file as")



class Tool:
    def __init__(self) -> None:
        pass

    selectedTile = 0
    clicked = False    
    palette1 = greyScale
    palette2 = []
    colorSelectionIndex = 0
    lastGridPosition = [0,0]
    gridColorValues = []
    selTool = "Brush"
    toolCanvas = None
    tiles = None

    def selectTile(self,no):
        
        
        self.toolCanvas.gridColorValues = self.tiles[no].gridColorValues
        self.toolCanvas.cleanUpCanvas(event=None)
        #positionX = int(event.x / (previewPixelWidth* 8))
        #positionY = int(event.y / (previewPixelWidth* 8))
        #self.selectedTile = positionX + positionY*20
        #print(self.selectedTile)
        self.selectedTile= no


    def updateTile(self,event,tiles,canvas):
        tiles[self.selectedTile].gridColorValues = canvas.gridColorValues
        tiles[self.selectedTile].cleanUpCanvas(event)

    def initializePalette(self):
        indexes1 = createRandomPalette()
        indexes2 = createRandomPalette()
        for i in range(16):
            #self.palette1.append(defaultPalette[indexes1[i]])
            self.palette2.append(defaultPalette[indexes2[i]])

    def setIndex(self, newIndex):
        self.colorSelectionIndex = newIndex

    def currentGridPosition(self,x,y):
        
        return int(x/60),int(y/60)
    
    def updateLastPosition(self, x,y):
        self.lastGridPosition = self.currentGridPosition(self,x,y)

    def selectColor(self,no):
        self.colorSelectionIndex = no         

    def clickOnPixel(self,event,canvas):
        self.clicked = True
        x = int(event.x / 60)
        y = int(event.y/60)
        if self.selTool == "Brush":
            canvas.setPixelColor([x,y],self.palette1[ self.colorSelectionIndex]) 
        else:
            
            canvas.fillArea(x,y,self.palette1[ self.colorSelectionIndex])
        canvas.cleanUpCanvas(event)

    def updatePixel(self,event,tiles,canvas):

        if self.clicked: 
            self.clickOnPixel(event,canvas)
        self.updateTile(event,tiles,canvas)
        canvas.cleanUpCanvas(event)

    def releaseMouse(self,event):
        self.clicked = False

    def setTool(self,event):
        print(event.keysym)
        if event.keysym == 'b':
            self.selTool = "Brush"
        elif event.keysym == 'f':
            self.selTool = "Fill"
        elif event.keysym.isnumeric():
            self.selectTile(int(event.keysym))
        print(self.selTool)




def init():
    global selectedPalette
    global selectedColor
    global gridColorValues

    
    
    mainTool = Tool()
    mainTool.initializePalette()


    root = Tk()
    root.title("Sega Master System Tileeditor")

    

    mainframe = Frame(root)
    mainframe.grid(column=0,row=0)
    paletteFrame = Frame(mainframe)
    paletteFrame.grid(row=0,column=1,sticky=N)
    previewFrame = Frame(mainframe,background="red")
    previewFrame.grid(row=1,column=1)
    canvasFrame = Frame(mainframe)
    canvasFrame.grid(row=0,column=0)
    

    btnRow = 0
    btnCol = 0
    for i in range(16):
        
        
        
        btn = Button(paletteFrame,text=str(i),bg=mainTool.palette1[i],command=partial(mainTool.selectColor,i)  ) 
        btn.grid(column=btnCol,row=btnRow,sticky="news")
        btnCol += 1
        
        if btnCol == 2:
            btnRow += 1
            btnCol = 0


    
    previewTiles = []
    
    for y in range(8):
        for x in range(8):
            tileFrame = Frame(previewFrame,background="blue")
            tileFrame.grid(column=x,row=y)
            
            currentTile = PixelCanvas(previewPixelWidth,previewPixelWidth,previewCanvasWidth,previewCanvasHeight,tileFrame,(x+y*8))
            currentTile.setGridPos(0,0)
            currentTile.pixelGrid = False
            for x1 in range(8):
                currentTile.gridColorValues.append([])
                for y1 in range(8):
                    y1 = mainTool.palette1[0]
                    currentTile.gridColorValues[x1].append(y1)
            currentTile.canvas.bind("<Button-1>", lambda e, i=(x+y*8): mainTool.selectTile(i)  )
            currentTile.cleanUpCanvas(None)
           

            previewTiles.append(currentTile)

    


    pixelCanvas = PixelCanvas(PixelWidth,PixelWidth,canvasWidth,canvasHeight,canvasFrame)
    pixelCanvas.setGridPos(0,0)
    for x in range(8):
        pixelCanvas.gridColorValues.append([])
        for y in range(8):
            y = mainTool.palette1[0]
            pixelCanvas.gridColorValues[x].append(y)

    fileHandler = FileHandler(pixelCanvas,previewTiles,mainTool)
    fileHandler.initFile()

    mainTool.tiles = previewTiles
    mainTool.toolCanvas = pixelCanvas

    mainTool.selectTile(0)

    menubar = Menu(root)
    fileMenu = Menu(menubar,tearoff=0)
    fileMenu.add_command(label="New",command=fileHandler.newFile)
    fileMenu.add_command(label="Open",command=fileHandler.openFile)
    fileMenu.add_command(label="Save",command=fileHandler.saveFile)
    fileMenu.add_command(label="Save as",command=fileHandler.saveFileas)
    fileMenu.add_command(label="Binary Conversion",command=fileHandler.save_f_data_file)
    fileMenu.add_command(label="Close")


    menubar.add_cascade(label="File", menu=fileMenu)


    root.config(menu=menubar)
    
   

    return root,mainframe,paletteFrame,previewFrame,pixelCanvas,mainTool,previewTiles



root, mainframe, paletteFrame,previewFrame, canvas, mainTool,tiles = init()

canvas.cleanUpCanvas(event=None)


canvas.canvas.bind('<Motion>', lambda event : mainTool.updatePixel(event,tiles,canvas) ) 
canvas.canvas.bind('<Button-1>', lambda event : mainTool.clickOnPixel(event,canvas))
canvas.canvas.bind('<ButtonRelease-1>', mainTool.releaseMouse)





canvas.canvas.bind('<Key>',  mainTool.setTool)
canvas.canvas.focus_set()
root.mainloop()