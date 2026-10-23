from PIL import Image, ImageDraw, ImageFont
M = Image.open('/mnt/user-data/uploads/orc-irl-sails-master-1024.png').convert('RGBA')
FONT = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
ORANGE=(255,102,0,255); GREEN=(0x2E,0x8E,0x47,255); WHITE=(255,255,255,255)

def design(S, letter, col, rounded=True):
    """Same layout as the 17 Oct 192 px icons, measured from them, drawn at 4x then reduced."""
    B = S*4
    im = Image.new('RGBA',(B,B),(0,0,0,0))
    d = ImageDraw.Draw(im)
    if rounded: d.rounded_rectangle([0,0,B-1,B-1], radius=int(0.21*B), fill=WHITE)
    else:       d.rectangle([0,0,B-1,B-1], fill=WHITE)
    sz = int(0.798*B); sails = M.resize((sz,sz), Image.LANCZOS)
    im.alpha_composite(sails, (int(0.112*B), int(0.094*B)))
    cx = cy = 0.737*B
    r_ring, r = 0.240*B, 0.2083*B
    d.ellipse([cx-r_ring,cy-r_ring,cx+r_ring,cy+r_ring], fill=WHITE)
    d.ellipse([cx-r,cy-r,cx+r,cy+r], fill=col)
    cap = 0.214*B
    f = ImageFont.truetype(FONT, int(cap/0.729))   # DejaVu Sans Bold cap height ~0.729 em
    d.text((cx+0.008*B, cy), letter, font=f, fill=WHITE, anchor='mm')
    if rounded:  # keep transparent corners clean
        mask = Image.new('L',(B,B),0); ImageDraw.Draw(mask).rounded_rectangle([0,0,B-1,B-1], radius=int(0.21*B), fill=255)
        im.putalpha(Image.composite(im.getchannel('A'), Image.new('L',(B,B),0), mask))
    return im.resize((S,S), Image.LANCZOS)

def maskable(S, letter, col, k=0.68):
    """Full-bleed white square; the whole design scaled to fit inside the central 80% safe circle."""
    full = design(2048, letter, col, rounded=False)
    inner = int(S*k); art = full.resize((inner,inner), Image.LANCZOS)
    im = Image.new('RGBA',(S,S),WHITE); off=(S-inner)//2
    im.alpha_composite(art,(off,off)); return im.convert('RGB')

for name,L,col in (('course','C',GREEN),('rib','R',ORANGE)):
    design(192,L,col).save(f'icon-{name}-192.png', optimize=True)
    design(512,L,col).save(f'icon-{name}-512.png', optimize=True)
    maskable(512,L,col).save(f'icon-{name}-maskable-512.png', optimize=True)

# --- Test copy (/course-test/) icons: a red "TEST" label in the empty top-left, kept inside the maskable safe circle
RED=(200,30,30,255)
def add_test(im):
    S=im.size[0]; B=S*4; big=im.resize((B,B),Image.LANCZOS); d=ImageDraw.Draw(big)
    x0,y0,x1,y1=0.10*B,0.10*B,0.42*B,0.25*B
    d.rounded_rectangle([x0,y0,x1,y1],radius=int(0.04*B),fill=RED)
    f=ImageFont.truetype(FONT,int((y1-y0)*0.62/0.729*0.75))
    d.text(((x0+x1)/2,(y0+y1)/2),'TEST',font=f,fill=WHITE,anchor='mm')
    return big.resize((S,S),Image.LANCZOS)
def design_test(S,rounded=True): return add_test(design(S,'C',GREEN,rounded))
def maskable_test(S,k=0.68):
    full=design_test(2048,rounded=False); inner=int(S*k); art=full.resize((inner,inner),Image.LANCZOS)
    im=Image.new('RGBA',(S,S),WHITE); off=(S-inner)//2; im.alpha_composite(art,(off,off)); return im.convert('RGB')
design_test(192).save('icon-course-test-192.png',optimize=True)
design_test(512).save('icon-course-test-512.png',optimize=True)
maskable_test(512).save('icon-course-test-maskable-512.png',optimize=True)
