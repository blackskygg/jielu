from sdl2.ext.common import SDLError
from sdl2.ext.compat import UnsupportedError, byteify
from sdl2 import endian, surface, pixels
from pyscreenshot import grab

def ScreenShot():
    imagesuface = None
    image = grab()
    mode = image.mode
    width, height = image.size
    rmask = gmask = bmask = amask = 0
    if mode in ("1", "L", "P"):
        # 1 = B/W, 1 bit per byte
        # "L" = greyscale, 8-bit
        # "P" = palette-based, 8-bit
        pitch = width
        depth = 8
    elif mode == "RGB":
        # 3x8-bit, 24bpp
        if endian.SDL_BYTEORDER == endian.SDL_LIL_ENDIAN:
            rmask = 0x0000FF
            gmask = 0x00FF00
            bmask = 0xFF0000
        else:
            rmask = 0xFF0000
            gmask = 0x00FF00
            bmask = 0x0000FF
        depth = 24
        pitch = width * 3
    elif mode in ("RGBA", "RGBX"):
        # RGBX: 4x8-bit, no alpha
        # RGBA: 4x8-bit, alpha
        if endian.SDL_BYTEORDER == endian.SDL_LIL_ENDIAN:
            rmask = 0x000000FF
            gmask = 0x0000FF00
            bmask = 0x00FF0000
            if mode == "RGBA":
                amask = 0xFF000000
        else:
            rmask = 0xFF000000
            gmask = 0x00FF0000
            bmask = 0x0000FF00
            if mode == "RGBA":
                amask = 0x000000FF
        depth = 32
        pitch = width * 4
    else:
        # We do not support CMYK or YCbCr for now
        raise TypeError("unsupported image format")

    pxbuf = image.tostring()
    imgsurface = surface.SDL_CreateRGBSurfaceFrom(pxbuf, width, height,
                                                  depth, pitch, rmask,
                                                  gmask, bmask, amask)
    if not imgsurface:
        raise SDLError()
    imgsurface = imgsurface.contents
    # the pixel buffer must not be freed for the lifetime of the surface
    imgsurface._pxbuf = pxbuf

    if mode == "P":
        # Create a SDL_Palette for the SDL_Surface
        def _chunk(seq, size):
            for x in range(0, len(seq), size):
                yield seq[x:x + size]

        rgbcolors = image.getpalette()
        sdlpalette = pixels.SDL_AllocPalette(len(rgbcolors) // 3)
        if not sdlpalette:
            raise SDLError()
        sdlpalette = sdlpalette.contents
        SDL_Color = pixels.SDL_Color
        for idx, (r, g, b) in enumerate(_chunk(rgbcolors, 3)):
            sdlpalette.colors[idx] = SDL_Color(r, g, b)
        ret = surface.SDL_SetSurfacePalette(imgsurface, sdlpalette)
        # This will decrease the refcount on the palette, so it gets
        # freed properly on releasing the SDL_Surface.
        pixels.SDL_FreePalette(sdlpalette)
        if ret != 0:
            raise SDLError()

    return imgsurface

ScreenShot()