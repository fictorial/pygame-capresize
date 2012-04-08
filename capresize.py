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


def resize_with_caps(src, dst_size, cap_insets=None, grow='scale'):
    """Stretch nine-grid source surface to surface of desired size.

    src

        The source surface.

    dst_size

        The destination surface size (width, height).  If height is
        0 maintains aspect ratio of source surface.

    cap_insets

        The size of each of the 4 end caps (left, top, right,
        bottom).

        If None, the left and right end caps are taken as 1/2 the
        source surface width; and, the top and bottom end caps are
        taken as 1/2 the source surface height. In this case it's
        expected that the center stretchy part is 1x1 pixel.

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

    # s:source, d:destination,
    # c:cap, m:middle/stretchable portion
    # l:left, t:top, b:bottom, r:right
    # w:width, h:height

    sw, sh = src.get_size()

    if cap_insets is None:
        assert sw % 2 == 1 and sh % 2 == 1
        cl, cr = sw // 2
        ct, cb = sh // 2
    else:
        cl, ct, cr, cb = cap_insets

    dw, dh = dst_size
    if dh == 0:
        dh = int(sh * dw / float(sw))

    dst = pygame.surface.Surface((dw, dh), pygame.SRCALPHA, 32)

    smw = sw - cl - cr
    smh = sh - cb - ct
    dmw = dw - cl - cr
    dmh = dh - cb - ct

    r = pygame.Rect

    # render caps: A, C, G, I in that order

    dst.blit(src, r(0, 0, cl, ct), r(0, 0, cl, ct))
    dst.blit(src, r(dw - cr, 0, cr, ct), r(sw - cr, 0, cr, ct))
    dst.blit(src, r(0, dh - cb, cl, cb), r(0, sh - cb, cl, cb))
    dst.blit(src, r(dw - cr, dh - cb, cr, cb), r(sw - cr, sh - cb, cr, cb))

    # extract subsurfaces from src for growable portions

    B = src.subsurface(r(cl, 0, smw, ct))
    D = src.subsurface(r(0, ct, cl, smh))
    E = src.subsurface(r(cl, ct, smw, smh))
    F = src.subsurface(r(sw - cr, ct, cr, smh))
    H = src.subsurface(r(cl, sh - cb, smw, cb))

    if grow == 'scale' or grow == 'stretch':
        sc = pygame.transform.smoothscale
        dst.blit(sc(B, (dmw, ct)), (cl, 0))
        dst.blit(sc(D, (cl, dmh)), (0, ct))
        dst.blit(sc(E, (dmw, dmh)), (cl, ct))
        dst.blit(sc(F, (cr, dmh)), (dw - cr, ct))
        dst.blit(sc(H, (dmw, cb)), (cl, dh - cb))
    elif grow == 'tile':
        n_across = dmw // smw
        rem_px_across = dmw - n_across * smw

        n_down = dmh // smh
        rem_px_down = dmh - n_down * smh

        def render_across(tile, y, h):
            x = cl
            for i in range(int(n_across)):
                dst.blit(tile, (x, y))
                x += smw
            if rem_px_across > 0:
                dst.blit(tile, (x, y), r(0, 0, rem_px_across, h))

        render_across(B, 0, ct)
        render_across(H, dh - smh, cb)

        def render_down(tile, x, w):
            y = ct
            for i in range(int(n_down)):
                dst.blit(tile, (x, y))
                y += smh
            if rem_px_down > 0:
                dst.blit(tile, (x, y), r(0, 0, w, rem_px_down))

        render_down(D, 0, cl)
        render_down(F, dw - smw, cr)

        y = ct
        for i in range(int(n_down)):
            render_across(E, y, smh)
            y += smh

        if rem_px_down > 0:
            x = cl
            for i in range(int(n_across)):
                dst.blit(E, (x, y), r(0, 0, smw, rem_px_down))
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

    template_cap_insets = (24, 24, 24, 24)

    template_tiled = resize_with_caps(template, (24 * 15, 24 * 9),
                                      template_cap_insets, 'tile')

    template_tiled1 = resize_with_caps(template, (24 * 7 + 4, 24 * 6 + 6),
                                       template_cap_insets, 'tile')

    template_stretched = resize_with_caps(template, (24 * 15, 24 * 9),
                                          template_cap_insets, 'stretch')

    #button = pygame.image.load('button.png').convert_alpha()
    #button_stretched = resize_with_caps(button, (450, 120), (10, 9), 'scale')

    button = pygame.image.load('textfield.png').convert_alpha()
    button_cap_insets = (1, 6, 1, 4)
    button_stretched = resize_with_caps(button, (450, 120),
                                        button_cap_insets, 'scale')

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
