#!/usr/bin/python

import sys

import sdl2
import sdl2.ext
import sdl2.sdlgfx

from sdl2 import rect, render
from sdl2.ext.compat import isiterable

import csv

BLACK = sdl2.ext.Color(0, 0, 0)
WHITE = sdl2.ext.Color(255, 255, 255)

class Entity(sdl2.ext.Entity):
    def __init__(self, world, sprite, posx=0, posy=0):
        self.sprite = sprite
        self.sprite.position = posx, posy


class TextureRenderer(sdl2.ext.TextureSpriteRenderSystem):
    def __init__(self, target):
        super(TextureRenderer, self).__init__(target)

    def render(self, sprites, x=None, y=None):
        """Overrides the render method of sdl2.ext.TextureSpriteRenderSystem to
        use "SDL_RenderCopyEx" instead of "SDL_RenderCopy" to allow sprite
        rotation:
        http://wiki.libsdl.org/SDL_RenderCopyEx
        """

        r = rect.SDL_Rect(0, 0, 0, 0)
        if isiterable(sprites):
            rcopy = render.SDL_RenderCopyEx
            renderer = self.sdlrenderer
            x = x or 0
            y = y or 0
            for sp in sprites:
                r.x = x + sp.x
                r.y = y + sp.y
                r.w, r.h = sp.size
                if rcopy(renderer, sp.texture, None, r, sp.angle, None, render.SDL_FLIP_NONE) == -1:
                    raise SDLError()
        else:
            r.x = sprites.x
            r.y = sprites.y
            r.w, r.h = sprites.size
            if x is not None and y is not None:
                r.x = x
                r.y = y
            render.SDL_RenderCopyEx(self.sdlrenderer,
                                    sprites.texture,
                                    None,
                                    r,
                                    sprites.angle,
                                    None,
                                    render.SDL_FLIP_NONE)
        render.SDL_RenderPresent(self.sdlrenderer)

class PointData(object):
    def __init__(self):
        super(PointData, self).__init__()
        self.maxx = 0
        self.maxy = 0
        self.realX = 0.0
        self.realy = 0.0
        self.sprite = None
        self.angle = 0.0

class Point(sdl2.ext.Entity):
    def __init__(self,world,idPoint,sprite,maxx,maxy,posx=0,posy=0):
        super(Point, self).__init__()
        self.sprite = sprite
        self.sprite.position = posx, posy
        self.sprite.angle = 0
        self.pointdata = PointData()
        self.pointdata.maxx = maxx
        self.pointdata.maxy = maxy
        self.pointdata.realX = posx
        self.pointdata.realY = posy
        self.pointdata.angle = 0
        self.pointdata.idPoint = idPoint

    def process(self,pointRecord):
        self.pointdata.realX = pointRecord["x"]
        self.pointdata.realY = pointRecord["y"]
        self.pointdata.angle = pointRecord["angle"]
        self.sprite.position = int(self.pointdata.realX),int(self.pointdata.realY)
        self.sprite.angle = self.pointdata.angle

def main(log):
    sdl2.ext.init()

    RESOURCES = sdl2.ext.Resources(__file__, "resources")
    window = sdl2.ext.Window("Hello World!", size=(640, 480))
    window.color = WHITE
    window.show()

    world = sdl2.ext.World()

    texture_renderer = sdl2.ext.Renderer(window)
    spriterenderer = TextureRenderer(texture_renderer)
    world.add_system(spriterenderer)

    factory = sdl2.ext.SpriteFactory(sdl2.ext.TEXTURE, renderer=texture_renderer)

    points = []
    points_sprites = []

    running = True
    timeStep = 0
    while running:
        events = sdl2.ext.get_events()
        for event in events:
            if event.type == sdl2.SDL_QUIT:
                running = False
                break

        for record in log:
            if record["timeStep"] == timeStep:
                print record["timeStep"]
                for pointRecord in record["points"]:
                    pointFound = False
                    for pointLoged in points:
                        if pointRecord["pointId"] == pointLoged.pointdata.idPoint:
                            pointFound = True
                            pointLoged.process(pointRecord)
                            break
                    if pointFound == False:
                        sprite = factory.from_image(RESOURCES.get_path("robot.png"))
                        points.append(Point(world,pointRecord["pointId"],sprite,800,600,0,0))
                        points_sprites.append(sprite)
                        points[len(points)-1].process(pointRecord)

        texture_renderer.color= WHITE
        texture_renderer.clear()
        spriterenderer.render(points_sprites)
        world.process()

        timeStep += 1
        sdl2.SDL_Delay(100)

    sdl2.ext.quit()


if __name__ == "__main__":
    #fileReader = csv.reader(open("log.csv"))
    fileReader = csv.reader(open("trajectory_0"),delimiter=' ')
    headerInfo = fileReader.next()
    header = []
    log = []
    for h in headerInfo:
        header.append(h)
    #TODO check assumptions on info present in the 
    for row in fileReader:
        timeStep = int(row[0])
        pointId = int(row[1])
        foundTimeStep = False
        for record in log:
            if record["timeStep"] == timeStep:
                pointInfo = {}
                pointInfo["pointId"] = pointId
                pointInfo["x"] = float(row[2])
                pointInfo["y"] = float(row[3])
                if row[4] != '':
                    print("." + row[4] + ".")
                    pointInfo["angle"] = float(row[4])
                else:
                    pointInfo["angle"] = 0
                record["points"].append(pointInfo)
                foundTimeStep = True
                break
        if foundTimeStep == False: 
            newTimeStep = {}
            newTimeStep["timeStep"] = timeStep
            newTimeStep["points"] = []
            pointInfo = {}
            pointInfo["pointId"] = pointId
            pointInfo["x"] = float(row[2])
            pointInfo["y"] = float(row[3])
            if row[4] != '':
                print("." + row[4] + ".")
                pointInfo["angle"] = float(row[4])
            else:
                pointInfo["angle"] = 0
            newTimeStep["points"].append(pointInfo)
            log.append(newTimeStep)
    main(log)
