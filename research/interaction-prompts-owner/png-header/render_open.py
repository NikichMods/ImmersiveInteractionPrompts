# SPDX-License-Identifier: MPL-2.0
"""Render one local technical OPEN from the user's Aphes.ttf; never redistribute output.

Requires Pillow/FreeType. No extraction, installation, engine launch or network.
"""
import argparse
import hashlib
import json
from pathlib import Path

import PIL
from PIL import Image, ImageDraw, ImageFont, features

FONT_SHA256 = '443fcae9fd3d3588a259d6c7746145b6c2a343cfb0c2f572fb330234c0f90ed0'
SIZE = (560, 112)  # 4x the 140x28 layout region; preserves aspect ratio.


def render(font_path, output):
    font_path, output = Path(font_path), Path(output)
    assert hashlib.sha256(font_path.read_bytes()).hexdigest() == FONT_SHA256, 'Unexpected font identity'
    assert not output.exists(), 'Preserve existing artifact; select a new output path'
    for pixels in range(112, 7, -1):
        font = ImageFont.truetype(str(font_path), pixels, layout_engine=ImageFont.Layout.BASIC)
        left, top, right, bottom = font.getbbox('OPEN')
        if right-left <= 528 and bottom-top <= 96:
            break
    else:
        raise ValueError('Glyphs do not fit')
    # Straight alpha with white RGB even at alpha zero avoids a black sampling fringe.
    image = Image.new('RGBA', SIZE, (255, 255, 255, 0))
    ImageDraw.Draw(image).text((16-left, (SIZE[1]-(bottom-top))//2-top), 'OPEN',
                              font=font, fill=(255,255,255,255))
    alpha = image.getchannel('A')
    assert alpha.getextrema() == (0,255) and alpha.getbbox(), 'Missing transparency or ink'
    assert any(0 < n < 255 for n in alpha.getdata()), 'Missing antialiasing'
    output.parent.mkdir(parents=True, exist_ok=True)
    image.save(output, format='PNG', compress_level=9)
    with Image.open(output) as saved:
        saved.load()
        assert saved.mode == 'RGBA' and saved.size == SIZE
        assert saved.tobytes() == image.tobytes()
    return {'text':'OPEN','meaning':'technical glyph test, not an Aphes translation',
            'fontSHA256':FONT_SHA256,'pngSHA256':hashlib.sha256(output.read_bytes()).hexdigest(),
            'size':list(SIZE),'mode':'RGBA','fontPixels':pixels,'inkBounds':list(alpha.getbbox()),
            'alphaExtrema':list(alpha.getextrema()),'pillow':PIL.__version__,
            'freetype':features.version('freetype2'),'bytes':output.stat().st_size}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--font', required=True)
    parser.add_argument('--out', required=True)
    args = parser.parse_args()
    print(json.dumps(render(args.font, args.out), indent=2))
