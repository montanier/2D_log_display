#!/usr/bin/python

import sys

import sdl2
import sdl2.ext
import sdl2.sdlgfx

from sdl2 import rect, render
from sdl2.ext.compat import isiterable

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

def main():
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

    sprite1 = factory.from_image(RESOURCES.get_path("robot.png"))
    sprite2 = factory.from_image(RESOURCES.get_path("robot.png"))
    positionX = 100
    positionY = 100
    angle = 0
    sprite1.position = 100, 100
    sprite1.angle = 0.5
    sprite2.position = 100, 100
    sprite2.angle = 0.5
    robots_sprites = []
    robots_sprites.append(sprite1)
    robots_sprites.append(sprite2)

    running = True
    while running:
        events = sdl2.ext.get_events()
        for event in events:
            if event.type == sdl2.SDL_QUIT:
                running = False
                break

        sdl2.SDL_Delay(10)
        positionX+=1
        positionY+=1
        angle = angle+1
        robots_sprites[0].position = positionX,positionY
        robots_sprites[0].angle = angle

        texture_renderer.color= WHITE
        texture_renderer.clear()
        spriterenderer.render(robots_sprites)
        world.process()

    sdl2.ext.quit()


if __name__ == "__main__":
    main()
