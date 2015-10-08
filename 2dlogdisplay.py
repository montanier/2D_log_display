#!/usr/bin/python

import sys
import os

import sdl2
import sdl2.ext
import sdl2.sdlgfx

from sdl2 import *
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
    fontpath = os.path.join(os.path.dirname(__file__), 'font', 'Glametrix.otf')

    window = sdl2.ext.Window("2D Log Display", size=(640, 480))
    window.color = WHITE
    window.show()

    world = sdl2.ext.World()

    texture_renderer = sdl2.ext.Renderer(window)
    spriterenderer = TextureRenderer(texture_renderer)
    world.add_system(spriterenderer)

    factory = sdl2.ext.SpriteFactory(sdl2.ext.TEXTURE, renderer=texture_renderer)
    fontManager = sdl2.ext.FontManager(fontpath,color=BLACK)

    points = []
    points_sprites = []
    text_sprites = []


    running = True
    timeStep = 0
    prevTimeStep = 0
    while running:
        events = sdl2.ext.get_events()
        for event in events:
            if event.type == sdl2.SDL_QUIT:
                running = False
                break

        for record in log:
            if record["timeStep"] == timeStep:
                if prevTimeStep < timeStep:
                    texture_renderer.color= WHITE
                    texture_renderer.clear()
                    del points_sprites[:]
                    del text_sprites[:]

                for pointRecord in record["points"]:
                    sprite = factory.from_image(RESOURCES.get_path("robot.png"))
                    sprite.position = int(pointRecord["x"]),int(pointRecord["y"])
                    sprite.angle = pointRecord["angle"]
                    points_sprites.append(sprite)

                    if "information" in pointRecord:
                        image = factory.from_text(pointRecord["information"],fontmanager=fontManager)
                        image.position = int(pointRecord["x"])+15,int(pointRecord["y"])-15
                        image.angle = 0
                        text_sprites.append(image)

                    prevTimeStep = timeStep

        texture_renderer.color= WHITE
        texture_renderer.clear()
        spriterenderer.render(points_sprites)
        spriterenderer.render(text_sprites)
        world.process()

        timeStep += 1
        sdl2.SDL_Delay(50)

    sdl2.ext.quit()


if __name__ == "__main__":
    #TODO use the options
    fileReader = csv.reader(open("log.csv"),delimiter=',')
    headerInfo = fileReader.next()
    header = []
    log = []
    for h in headerInfo:
        header.append(h)

    #TODO check assumptions on info present in the log
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
                    pointInfo["angle"] = float(row[4])
                else:
                    pointInfo["angle"] = 0
                if (len(row) > 5) and (row[5] != ''):
                    pointInfo["information"] = row[5]
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
                pointInfo["angle"] = float(row[4])
            else:
                pointInfo["angle"] = 0
            if (len(row) > 5) and (row[5] != ''):
                pointInfo["information"] = row[5]
            newTimeStep["points"].append(pointInfo)
            log.append(newTimeStep)

    main(log)
