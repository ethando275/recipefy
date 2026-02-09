import time, threading, textwrap
import cv2
import numpy as np
import httpx

from ultralytics import YOLO

# ----------------------------
# Config
# ----------------------------
SERVER_URL = "http://127.0.0.1:4444/analyze_frame"

# Use your downloaded weights
YOLO_MODEL_ID = "food_yolo.pt"

# Try to use Apple GPU
YOLO_DEVICE = "mps"   # change to "cpu" if needed

# Detection thresholds
YOLO_CONF = 0.35
YOLO_IOU = 0.45
MAX_BOXES = 8

# Gemini call cadence
SCAN_INTERVAL_SECONDS = 3.0
LOCKED_REFRESH_SECONDS = 10.0

net_client = httpx.Client(http2=True, timeout=15.0)


# ----------------------------
# State
# ----------------------------
class ARState:
    def __init__(self):
        self.payload = {}            # Gemini response
        self.in_flight = False

        self.is_locked = False
        self.stable_hits = 0
        self.last_labels = []
        self.prev_gray = None

        self.last_boxes_sig = None
        self.last_call_time = 0.0


state = ARState()


# ----------------------------
# Helpers
# ----------------------------
def detect_significant_motion(frame):
    small = cv2.resize(frame, (320, 180))
    gray = cv2.cvtColor(small, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (35, 35), 0)

    if state.prev_gray is None:
        state.prev_gray = gray
        return False

    diff = cv2.absdiff(state.prev_gray, gray)
    _, thresh = cv2.threshold(diff, 40, 255, cv2.THRESH_BINARY)
    motion_val = np.sum(thresh)

    state.prev_gray = gray
    return motion_val > 50000


def yolo_boxes_to_norm(boxes_xyxy, frame_w, frame_h):
    norm = []
    for (x1, y1, x2, y2) in boxes_xyxy:
        ymin = int(max(0, min(999, (y1 / frame_h) * 1000)))
        xmin = int(max(0, min(999, (x1 / frame_w) * 1000)))
        ymax = int(max(0, min(999, (y2 / frame_h) * 1000)))
        xmax = int(max(0, min(999, (x2 / frame_w) * 1000)))
        norm.append([ymin, xmin, ymax, xmax])
    return norm


def boxes_signature(norm_boxes):
    if not norm_boxes:
        return None
    q = []
    for b in norm_boxes:
        q.append(tuple((v // 25) for v in b))  # quantize
    return tuple(sorted(q))


def fetch_analysis(frame):
    state.in_flight = True
    try:
        ok, img_encoded = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
        if not ok:
            return

        files = {"file": ("f.jpg", img_encoded.tobytes(), "image/jpeg")}
        resp = net_client.post(SERVER_URL, files=files)

        if resp.status_code == 200:
            new_data = resp.json()

            # stability/lock based on returned labels list
            new_labels = sorted(
                [i.get("label", "") for i in new_data.get("ingredients", []) if i.get("label")]
            )

            if new_labels == state.last_labels and len(new_labels) > 0:
                state.stable_hits += 1
            else:
                state.stable_hits = 0
                state.is_locked = False

            state.last_labels = new_labels
            state.payload = new_data

            if state.stable_hits >= 3:
                state.is_locked = True

    except Exception as e:
        print(f"Connection error: {e}")
    finally:
        state.in_flight = False


def draw_ar_overlay(frame, yolo_norm_boxes, payload):
    h, w = frame.shape[:2]
    panel_w = 350

    # Gemini labels (optional)
    gem_ings = payload.get("ingredients", [])
    gem_labels = [g.get("label", "") for g in gem_ings if g.get("label")]

    # If Gemini returns same count as boxes, map by left->right
    box_labels = []
    if len(gem_labels) == len(yolo_norm_boxes) and len(yolo_norm_boxes) > 0:
        boxes_with_idx = sorted(list(enumerate(yolo_norm_boxes)), key=lambda x: x[1][1])  # xmin
        labels_sorted = sorted(gem_labels)
        mapped = [""] * len(yolo_norm_boxes)
        for k, (idx, _b) in enumerate(boxes_with_idx):
            mapped[idx] = labels_sorted[k]
        box_labels = mapped
    else:
        box_labels = [f"FOOD {i+1}" for i in range(len(yolo_norm_boxes))]

    # Draw YOLO boxes continuously
    for i, b in enumerate(yolo_norm_boxes):
        ymin, xmin, ymax, xmax = b[:4]
        l, t = int(xmin * w / 1000), int(ymin * h / 1000)
        r, bb = int(xmax * w / 1000), int(ymax * h / 1000)

        cv2.rectangle(frame, (l, t), (r, bb), (0, 255, 0), 2)
        label = box_labels[i].upper() if i < len(box_labels) else f"FOOD {i+1}"
        cv2.putText(frame, label, (l, max(15, t - 10)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 255, 0), 2)

    # Side panel
    overlay = frame.copy()
    cv2.rectangle(overlay, (w - panel_w, 0), (w, h), (0, 0, 0), -1)
    cv2.addWeighted(overlay, 0.60, frame, 0.40, 0, frame)

    status_text = "LOCKED" if state.is_locked else "SCANNING..."
    if state.in_flight:
        status_text += " (analyzing)"

    cv2.putText(frame, status_text, (w - panel_w + 15, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.50, (0, 255, 255), 2)

    # Ingredients list
    y_cursor = 60
    cv2.putText(frame, "INGREDIENTS:", (w - panel_w + 15, y_cursor),
                cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 255), 1)
    y_cursor += 22

    if gem_labels:
        for lbl in gem_labels[:10]:
            for line in textwrap.wrap(lbl, width=28):
                cv2.putText(frame, f"- {line}", (w - panel_w + 15, y_cursor),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.42, (200, 200, 200), 1)
                y_cursor += 18
    else:
        cv2.putText(frame, "(waiting for labels...)", (w - panel_w + 15, y_cursor),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.42, (200, 200, 200), 1)
        y_cursor += 18

    y_cursor += 18

    # Recipes
    recipes = payload.get("recipes", [])
    if recipes:
        cv2.putText(frame, "RECIPES:", (w - panel_w + 15, y_cursor),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 255), 1)
        y_cursor += 22

        for res in recipes[:3]:
            title = res.get("title", "")
            desc = res.get("description", "")

            for tl in textwrap.wrap(title, width=25):
                cv2.putText(frame, tl, (w - panel_w + 15, y_cursor),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 2)
                y_cursor += 22

            for dl in textwrap.wrap(desc, width=35):
                cv2.putText(frame, dl, (w - panel_w + 15, y_cursor),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.40, (180, 180, 180), 1)
                y_cursor += 18

            y_cursor += 20


def main():
    print(f"Loading YOLO model: {YOLO_MODEL_ID}")
    yolo = YOLO(YOLO_MODEL_ID)

    # Helpful debug (optional)
    # try:
    #     print("Model classes:", getattr(yolo, "names", None))
    # except Exception:
    #     pass

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Could not open webcam")
        return

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        h, w = frame.shape[:2]

        # YOLO inference every frame (continuous boxes)
        try:
            results = yolo.predict(
                frame,
                conf=YOLO_CONF,
                iou=YOLO_IOU,
                verbose=False,
                device=YOLO_DEVICE
            )
        except Exception as e:
            # If MPS fails for any reason, fall back to CPU automatically
            if YOLO_DEVICE == "mps":
                print(f"MPS failed ({e}); falling back to CPU.")
                globals()["YOLO_DEVICE"] = "cpu"
                results = yolo.predict(frame, conf=YOLO_CONF, iou=YOLO_IOU, verbose=False, device="cpu")
            else:
                raise

        r0 = results[0]

        boxes_xyxy = []
        if r0.boxes is not None and len(r0.boxes) > 0:
            confs = r0.boxes.conf.cpu().numpy().tolist()
            xyxy = r0.boxes.xyxy.cpu().numpy().tolist()

            idxs = sorted(range(len(confs)), key=lambda i: confs[i], reverse=True)[:MAX_BOXES]
            for i in idxs:
                x1, y1, x2, y2 = xyxy[i]
                boxes_xyxy.append((x1, y1, x2, y2))

        yolo_norm = yolo_boxes_to_norm(boxes_xyxy, w, h)
        sig = boxes_signature(yolo_norm)

        # Motion invalidates lock
        if detect_significant_motion(frame):
            state.is_locked = False
            state.stable_hits = 0

        # Gemini call decision (async)
        now = time.time()
        interval = LOCKED_REFRESH_SECONDS if state.is_locked else SCAN_INTERVAL_SECONDS
        boxes_changed = (sig != state.last_boxes_sig) and (sig is not None)
        time_ok = (now - state.last_call_time) > interval

        if not state.in_flight and (time_ok or boxes_changed):
            state.last_call_time = now
            state.last_boxes_sig = sig
            threading.Thread(target=fetch_analysis, args=(frame.copy(),), daemon=True).start()

        draw_ar_overlay(frame, yolo_norm, state.payload)

        # small "in-flight" dot
        if state.in_flight:
            cv2.circle(frame, (30, 30), 8, (0, 255, 255), -1)

        cv2.imshow("Recipefy AR (Food YOLO + Gemini)", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
