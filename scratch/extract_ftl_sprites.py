import os
import pygame

pygame.init()
pygame.display.set_mode((1, 1), pygame.NOFRAME)

IMG_OSPREY = r"C:\Users\droesch\.gemini\antigravity-ide\brain\03e0bdf0-e90e-4de9-b3a8-84b668795614\media__1786105004825.png"
IMG_KESTREL = r"C:\Users\droesch\.gemini\antigravity-ide\brain\03e0bdf0-e90e-4de9-b3a8-84b668795614\media__1786105004867.png"

OUT_DIR = r"c:\Users\droesch\Documents\Programmiertes\py-ftl\assets\ships"
os.makedirs(OUT_DIR, exist_ok=True)

img_osprey = pygame.image.load(IMG_OSPREY).convert_alpha()
img_kestrel = pygame.image.load(IMG_KESTREL).convert_alpha()

print(f"Osprey sheet size: {img_osprey.get_size()}")
print(f"Kestrel sheet size: {img_kestrel.get_size()}")

def crop_and_clean(surf, rect):
    sub = surf.subsurface(rect).copy()
    w, h = sub.get_size()
    # Replace white / grid background pixels (r > 240, g > 240, b > 240) with transparent alpha
    for x in range(w):
        for y in range(h):
            r, g, b, a = sub.get_at((x, y))
            if r > 240 and g > 240 and b > 240:
                sub.set_at((x, y), (0, 0, 0, 0))
    
    # Calculate bounding box of non-transparent pixels
    min_x, min_y, max_x, max_y = w, h, 0, 0
    found = False
    for x in range(w):
        for y in range(h):
            _, _, _, a = sub.get_at((x, y))
            if a > 10:
                found = True
                if x < min_x: min_x = x
                if x > max_x: max_x = x
                if y < min_y: min_y = y
                if y > max_y: max_y = y
    
    if found and max_x >= min_x and max_y >= min_y:
        crop_rect = pygame.Rect(min_x, min_y, max_x - min_x + 1, max_y - min_y + 1)
        res = pygame.Surface((crop_rect.width, crop_rect.height), pygame.SRCALPHA)
        res.blit(sub, (0, 0), crop_rect)
        return res
    return sub

# Kestrel sheet processing
w_k, h_k = img_kestrel.get_size()
col_w_k = w_k // 3

# Top row (Hull graphics): y 0 to int(h_k * 0.16)
y_hull_k = int(h_k * 0.16)
kestrel_a_hull = crop_and_clean(img_kestrel, pygame.Rect(0, 0, col_w_k, y_hull_k))
red_tail_hull = crop_and_clean(img_kestrel, pygame.Rect(col_w_k, 0, col_w_k, y_hull_k))
swallow_hull = crop_and_clean(img_kestrel, pygame.Rect(col_w_k * 2, 0, col_w_k, y_hull_k))

pygame.image.save(kestrel_a_hull, os.path.join(OUT_DIR, "kestrel_a_hull.png"))
pygame.image.save(red_tail_hull, os.path.join(OUT_DIR, "red_tail_hull.png"))
pygame.image.save(swallow_hull, os.path.join(OUT_DIR, "swallow_hull.png"))

# Row 3 (Floorplans): y int(h_k * 0.35) to int(h_k * 0.52)
y_fp_s = int(h_k * 0.35)
y_fp_h = int(h_k * 0.17)
kestrel_a_fp = crop_and_clean(img_kestrel, pygame.Rect(0, y_fp_s, col_w_k, y_fp_h))
red_tail_fp = crop_and_clean(img_kestrel, pygame.Rect(col_w_k, y_fp_s, col_w_k, y_fp_h))
swallow_fp = crop_and_clean(img_kestrel, pygame.Rect(col_w_k * 2, y_fp_s, col_w_k, y_fp_h))

pygame.image.save(kestrel_a_fp, os.path.join(OUT_DIR, "kestrel_a_floorplan.png"))
pygame.image.save(red_tail_fp, os.path.join(OUT_DIR, "red_tail_floorplan.png"))
pygame.image.save(swallow_fp, os.path.join(OUT_DIR, "swallow_floorplan.png"))


# Osprey sheet processing
w_o, h_o = img_osprey.get_size()
col_w_o = w_o // 3

y_hull_o = int(h_o * 0.16)
osprey_hull = crop_and_clean(img_osprey, pygame.Rect(0, 0, col_w_o, y_hull_o))
nisos_hull = crop_and_clean(img_osprey, pygame.Rect(col_w_o, 0, col_w_o, y_hull_o))
fregatidae_hull = crop_and_clean(img_osprey, pygame.Rect(col_w_o * 2, 0, col_w_o, y_hull_o))

pygame.image.save(osprey_hull, os.path.join(OUT_DIR, "osprey_hull.png"))
pygame.image.save(nisos_hull, os.path.join(OUT_DIR, "nisos_hull.png"))
pygame.image.save(fregatidae_hull, os.path.join(OUT_DIR, "fregatidae_hull.png"))

y_fp_s_o = int(h_o * 0.35)
y_fp_h_o = int(h_o * 0.17)
osprey_fp = crop_and_clean(img_osprey, pygame.Rect(0, y_fp_s_o, col_w_o, y_fp_h_o))
nisos_fp = crop_and_clean(img_osprey, pygame.Rect(col_w_o, y_fp_s_o, col_w_o, y_fp_h_o))
fregatidae_fp = crop_and_clean(img_osprey, pygame.Rect(col_w_o * 2, y_fp_s_o, col_w_o, y_fp_h_o))

pygame.image.save(osprey_fp, os.path.join(OUT_DIR, "osprey_floorplan.png"))
pygame.image.save(nisos_fp, os.path.join(OUT_DIR, "nisos_floorplan.png"))
pygame.image.save(fregatidae_fp, os.path.join(OUT_DIR, "fregatidae_floorplan.png"))

print("Extracted all 6 FTL ship hulls and floorplans successfully with Pygame!")
