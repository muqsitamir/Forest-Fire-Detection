def bb_intersection_over_union(boxA, boxB):
    # determine the (x, y)-coordinates of the intersection rectangle
    xA = max(boxA[0], boxB[0])
    yA = max(boxA[1], boxB[1])
    xB = min(boxA[2], boxB[2])
    yB = min(boxA[3], boxB[3])
    # compute the area of intersection rectangle
    interArea = max(0, xB - xA + 1) * max(0, yB - yA + 1)
    # compute the area of both the prediction and ground-truth
    # rectangles
    boxAArea = (boxA[2] - boxA[0] + 1) * (boxA[3] - boxA[1] + 1)
    boxBArea = (boxB[2] - boxB[0] + 1) * (boxB[3] - boxB[1] + 1)
    # compute the intersection over union by taking the intersection
    # area and dividing it by the sum of prediction + ground-truth
    # areas - the interesection area
    iou = interArea / float(boxAArea + boxBArea - interArea)
    # return the intersection over union value
    return iou


def is_dont_care(box, camera):
    dont_cares, iou_threshold = camera.dont_care.values(), camera.iou_threshold
    width, height = camera.image_width, camera.image_height
    x, y, w, h = int(box['x'] * width), int(box['y'] * height), int(box['width'] * width), int(box['height'] * height)
    box_a = (x, y, x + w, y + h)

    for patch in dont_cares:
        box_b = (patch['x'], patch['y'], patch['x'] + patch['width'], patch['y'] + patch['height'])
        iou = bb_intersection_over_union(box_a, box_b)

        if iou * 100 > iou_threshold:
            return True

    return False
