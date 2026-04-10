import cv2
from deep_sort_realtime.deepsort_tracker import DeepSort
from ultralytics import YOLO
from db import save_detection, update_live_count

# ---------- GLOBAL ----------
OFFSET = 15
trackableObjects = {}

class TrackableObject:
    def __init__(self, objectID, centroid):
        self.objectID = objectID
        self.centroids = [centroid]
        self.counted = False

# ---------- LOAD MODEL ----------
model = YOLO("yolov8n.pt")
tracker = DeepSort(max_age=30)

def reset_tracker():
    global trackableObjects
    trackableObjects = {}

# 🔥 ADDED save_flag PARAMETER
def process_frame(frame, frame_h, frame_w, line_y,
                  total_in, total_out, save_flag=False):

    global trackableObjects

    results = model(frame, verbose=False)[0]
    detections = []

    for box in results.boxes:
        if int(box.cls[0]) == 0 and float(box.conf[0]) > 0.5:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            w, h = x2 - x1, y2 - y1
            detections.append(([x1, y1, w, h], float(box.conf[0]), "person"))

    tracks = tracker.update_tracks(detections, frame=frame)
    ids_inside = set()

    for track in tracks:
        if not track.is_confirmed():
            continue

        tid = track.track_id
        l, t, r, b = map(int, track.to_ltrb())
        cx, cy = (l + r) // 2, (t + b) // 2
        ids_inside.add(tid)

        to = trackableObjects.get(tid)

        if to is None:
            to = TrackableObject(tid, (cx, cy))
        else:
            y_vals = [c[1] for c in to.centroids]
            direction = cy - sum(y_vals) / len(y_vals)
            to.centroids.append((cx, cy))

            if not to.counted:
                if direction < 0 and cy < line_y - OFFSET:
                    total_out += 1
                    to.counted = True
                elif direction > 0 and cy > line_y + OFFSET:
                    total_in += 1
                    to.counted = True

        trackableObjects[tid] = to

        # 🔥 ONLY SAVE SOMETIMES
        if save_flag:
            save_detection(tid, cx / frame_w, cy / frame_h)

        # Draw box
        cv2.rectangle(frame, (l, t), (r, b), (0, 255, 0), 2)
        cv2.putText(frame, f"ID {tid}", (l, t - 5),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6,
                    (0, 255, 0), 2)

    inside = len(ids_inside)

    update_live_count(total_in, total_out, inside)

    return frame, total_in, total_out, inside