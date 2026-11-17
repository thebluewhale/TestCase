"""Step 2: product mask from a hand-given bounding box (GrabCut).  THERE IS NO AUTOMATIC DETECTION IN THIS PoC:
someone (a person, or the AI after looking at grid_preview.jpg) must supply the box in ORIGINAL-image pixels.

usage: python segment.py IMAGE NAME X0 Y0 X1 Y1 [--fg X0 Y0 X1 Y1] [--no-deskin]
  box  : loosely encloses the whole visible product, 1-3 % margin, must not cut the product
  --fg : optional rectangle that is certainly product (e.g. the middle of the back); use when the plain box leaks or loses part
out : NAME_rgba.png (BGR + alpha mask)  and  NAME_seg_preview.jpg (look at this before going on)"""
import sys, numpy as np, cv2
a = sys.argv[1:]; img, name = a[0], a[1]; x0,y0,x1,y1 = map(int,a[2:6])
fg = list(map(int,a[a.index('--fg')+1:a.index('--fg')+5])) if '--fg' in a else None
im = cv2.imread(img); H,W = im.shape[:2]
k = min(1.0,1100/max(H,W)); sm = cv2.resize(im,None,fx=k,fy=k,interpolation=cv2.INTER_AREA) if k<1 else im      # GrabCut on <=1100 px
bx0,by0,bx1,by1 = [int(v*k) for v in (x0,y0,x1,y1)]; bg=np.zeros((1,65)); fgm_=np.zeros((1,65))
if fg is None:
    m = np.zeros(sm.shape[:2],np.uint8); cv2.grabCut(sm,m,(bx0,by0,bx1-bx0,by1-by0),bg,fgm_,8,cv2.GC_INIT_WITH_RECT)
else:
    m = np.full(sm.shape[:2],cv2.GC_BGD,np.uint8); m[by0:by1,bx0:bx1] = cv2.GC_PR_FGD
    f = [int(v*k) for v in fg]; m[f[1]:f[3],f[0]:f[2]] = cv2.GC_FGD; cv2.grabCut(sm,m,None,bg,fgm_,8,cv2.GC_INIT_WITH_MASK)
fgm = ((m==cv2.GC_FGD)|(m==cv2.GC_PR_FGD)).astype(np.uint8)
n,lab,st,_ = cv2.connectedComponentsWithStats(fgm); fgm = (lab==1+np.argmax(st[1:,cv2.CC_STAT_AREA])).astype(np.uint8)   # largest blob only
fgm = cv2.morphologyEx(fgm,cv2.MORPH_CLOSE,np.ones((5,5),np.uint8))
skin_frac = 0.0
if '--no-deskin' not in a:                                         # hand-held shots: remove skin-coloured pixels from the mask
    ycc = cv2.cvtColor(sm,cv2.COLOR_BGR2YCrCb); skin = (ycc[...,1]>142)&(ycc[...,2]<124)&(fgm>0); skin_frac = skin.sum()/max(1,fgm.sum())
    if 0.02 < skin_frac < 0.4:
        kk = max(3,int(np.sqrt(fgm.sum())*0.01))|1
        m2 = cv2.morphologyEx(((fgm>0)&~(cv2.dilate(skin.astype(np.uint8),np.ones((kk,kk),np.uint8))>0)).astype(np.uint8),cv2.MORPH_OPEN,np.ones((kk,kk),np.uint8))
        n,lab,st,_ = cv2.connectedComponentsWithStats(m2); fgm = (lab==1+np.argmax(st[1:,cv2.CC_STAT_AREA])).astype(np.uint8)
full = cv2.GaussianBlur(cv2.resize(fgm*255,(W,H),interpolation=cv2.INTER_LINEAR),(0,0),max(0.8,0.6/k))
cv2.imwrite(f'{name}_rgba.png',np.dstack([im,full]))
# diagnostics + preview
ys,xs = np.nonzero(fgm); cnt,_ = cv2.findContours(fgm,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE); hull = cv2.convexHull(max(cnt,key=len))
touch = [s for s,c in (('left',xs.min()<=bx0+1),('top',ys.min()<=by0+1),('right',xs.max()>=bx1-2),('bottom',ys.max()>=by1-2)) if c]
print(f"{name}: mask/box area {fgm.sum()/((bx1-bx0)*(by1-by0)):.2f} | mask/convex-hull {fgm.sum()/cv2.contourArea(hull):.3f} | touches box border: {touch or 'none'} | skin fraction {skin_frac:.3f}")
v = sm.copy(); v[fgm==0] = (v[fgm==0]*0.3).astype(np.uint8); cv2.drawContours(v,cnt,-1,(0,255,0),1); cv2.rectangle(v,(bx0,by0),(bx1,by1),(0,255,255),1)
cv2.imwrite(f'{name}_seg_preview.jpg',v,[cv2.IMWRITE_JPEG_QUALITY,90])
