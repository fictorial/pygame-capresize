"""This module creates a Pygame surface from a source surface that
has "end caps" on its corners. The caps remain unscaled in the 
destination surface and the rest is scaled/tiled.

This was inspired by Android's NinePatch and iOS'
resizableImageWithCapInsets

"""

import pygame


AUTHOR = 'Brian Hammond <brian@fictorial.com>'
LICENSE = 'MIT'
COPYRIGHT = 'Copyright (C) 2012 Fictorial LLC'


__version__ = '1.0.0'


def resize_with_caps(src, dst_size, cap_size=None, grow='scale'):
    """Stretch nine-grid source surface to surface of desired size.

    src

        The source surface.

    dst_size

        The destination surface size (width, height).
        If height is 0 maintains aspect ratio of source surface.

    cap_size

        The size of the end caps (width, height).

        If None, the cap width is taken as 1/2 the source surface
        width and 1/2 the source surface height.  In this case, it
        is expected that the source surface has an odd width and
        height (e.g. 13) and the middle "stretchy part" is 1x1.

    grow

        The method used to grow portions of the source image that
        are not end caps.  The default is 'scale' which means the
        relevant source surface portions are scaled before being
        copied to the destination surface.  The other option is
        'tile' which instead tiles the relevant source surface
        portions into the destination surface.

    Source and destination surfaces are laid out as follows.

        A B C
        D E F
        G H I

    A, C, G, and I are the end caps; B and H stretch horizontally;
    D and F stretch vertically; and E stretches in both directions.

    Returns the destination surface.
    """

    # s:source, c:cap, d:destination,
    # m:middle/stretchable portion, w:width, h:height

    sw, sh = src.get_size()

    if cap_size is None:
        assert sw % 2 == 1 and sh % 2 == 1
        cw, ch = sw // 2, sh // 2
    else:
        cw, ch = cap_size

    dw, dh = dst_size
    if dh == 0:
        dh = int(sh * dw / float(sw))

    dst = pygame.surface.Surface((dw, dh), pygame.SRCALPHA, 32)

    smw, smh = sw - cw * 2, sh - ch * 2
    dmw, dmh = dw - cw * 2, dh - ch * 2

    r = pygame.Rect

    # render caps: A, C, G, I in that order

    dst.blit(src, r(0, 0, cw, ch), r(0, 0, cw, ch))
    dst.blit(src, r(dw - cw, 0, cw, ch), r(sw - cw, 0, cw, ch))
    dst.blit(src, r(0, dh - ch, cw, ch), r(0, sh - ch, cw, ch))
    dst.blit(src, r(dw - cw, dh - ch, cw, ch), r(sw - cw, sh - ch, cw, ch))

    # extract subsurfaces from src for growable portions

    B = src.subsurface(r(cw, 0, smw, ch))
    D = src.subsurface(r(0, ch, cw, smh))
    E = src.subsurface(r(cw, ch, smw, smh))
    F = src.subsurface(r(sw - cw, ch, cw, smh))
    H = src.subsurface(r(cw, sh - ch, smw, ch))

    if grow == 'scale' or grow == 'stretch':
        sc = pygame.transform.smoothscale
        dst.blit(sc(B, (dmw, ch)), (cw, 0))
        dst.blit(sc(D, (cw, dmh)), (0, ch))
        dst.blit(sc(E, (dmw, dmh)), (cw, ch))
        dst.blit(sc(F, (cw, dmh)), (dw - cw, ch))
        dst.blit(sc(H, (dmw, ch)), (cw, dh - ch))
    elif grow == 'tile':
        n_across = dmw // smw
        rem_px_across = dmw - n_across * smw

        n_down = dmh // smh
        rem_px_down = dmh - n_down * smh

        def render_across(tile, y):
            x = cw
            for i in range(int(n_across)):
                dst.blit(tile, (x, y))
                x += smw
            if rem_px_across > 0:
                dst.blit(tile, (x, y), r(0, 0, rem_px_across, ch))

        render_across(B, 0)
        render_across(H, dh - smh)

        def render_down(tile, x):
            y = ch
            for i in range(int(n_down)):
                dst.blit(tile, (x, y))
                y += smh
            if rem_px_down > 0:
                dst.blit(tile, (x, y), r(0, 0, cw, rem_px_down))

        render_down(D, 0)
        render_down(F, dw - smw)

        y = ch
        for i in range(int(n_down)):
            render_across(E, y)
            y += smh

        if rem_px_down > 0:
            x = cw
            for i in range(int(n_across)):
                dst.blit(E, (x, y), r(0, 0, cw, rem_px_down))
                x += smw
            if rem_px_across > 0:
                dst.blit(E, (x, y), r(0, 0, rem_px_across, rem_px_down))

    return dst


if __name__ == '__main__':
    pygame.init()
    screen = pygame.display.set_mode((640, 800))
    title = 'L: sources; R: stretch, tile, tile w/ leftovers, stretched button'
    pygame.display.set_caption(title)

    template = pygame.image.load('template.png').convert_alpha()

    cap_size = (24, 24)

    template_tiled = resize_with_caps(template, (24 * 15, 24 * 9),
                                      cap_size, 'tile')

    template_tiled1 = resize_with_caps(template, (24 * 7 + 4, 24 * 6 + 6),
                                       cap_size, 'tile')

    template_stretched = resize_with_caps(template, (24 * 15, 24 * 9),
                                          cap_size, 'stretch')

    button = pygame.image.load('button.png').convert_alpha()
    button_stretched = resize_with_caps(button, (450, 120), (10, 9), 'scale')

    clock = pygame.time.Clock()
    running = True
    while running:
        dt = clock.tick(4) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False

        if not running:
            break

        screen.fill((255, 255, 255))
        screen.blit(template, (10, 10))
        screen.blit(template_stretched, (150, 10))
        screen.blit(template_tiled, (150, 24 * 9 + 20))
        screen.blit(template_tiled1, (150, 2 * 24 * 9 + 30))
        screen.blit(button, (10, 640))
        screen.blit(button_stretched, (150, 640))
        pygame.display.flip()
