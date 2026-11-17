#!/usr/bin/env python3
"""Runbook preview: original-coordinate grid, box GrabCut and review artifacts."""
import argparse,json
from pathlib import Path
import cv2
import numpy as np
from PIL import Image
from review_product_consistency_v4.assets import decode_image
from review_product_consistency_v4.pipeline import load_config
from review_product_consistency_v4.metrology.segmentation import segment
from review_product_consistency_v4.metrology.preview import grid_preview,segmentation_preview


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--image',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--product-box',nargs=4,type=int)
    parser.add_argument('--foreground-box',nargs=4,type=int)
    parser.add_argument('--no-deskin',action='store_true')
    parser.add_argument('--grid-only',action='store_true')
    args=parser.parse_args();image=decode_image(args.image,load_config())
    args.output.mkdir(parents=True,exist_ok=False)
    grid_preview(image.pixels).save(args.output/'grid.png')
    if args.grid_only:return
    cv2.setNumThreads(1)
    alpha,unknown,info=segment(np.array(image.pixels),args.product_box,foreground_box=args.foreground_box,deskin=not args.no_deskin)
    Image.fromarray(alpha).save(args.output/'product_mask.png')
    Image.fromarray(unknown.astype(np.uint8)*255).save(args.output/'unknown_mask.png')
    segmentation_preview(image.pixels,alpha,unknown.astype(np.uint8)*255,args.product_box,args.foreground_box).save(args.output/'segmentation_preview.png')
    (args.output/'segmentation.json').write_text(json.dumps({'input':image.metadata(),'segmentation':info},ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(info,ensure_ascii=False))

if __name__=='__main__':main()
