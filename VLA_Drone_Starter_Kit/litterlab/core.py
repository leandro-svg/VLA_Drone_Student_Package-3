"""Read this file first: geometry, pixels, expert, and simulated motion.

World vectors are [north, east] metres. The camera is level and nadir,
image right is east, and image up is north. This is a deliberately simple
kinematic teaching model, not PX4, a photorealistic simulator or flight code.
"""
from dataclasses import dataclass
import numpy as np
from PIL import Image, ImageDraw

CATEGORIES = ("bottle", "can", "paper")
COLOURS = ((220, 50, 50), (45, 80, 225), (225, 195, 40))
SIZE = 96
FOCAL_PX = 48.0
HEIGHT = 5.0
DT = 0.5
MAX_DELTA = 0.5


def bounded(vector, limit=MAX_DELTA):
    vector = np.asarray(vector, dtype=float)
    if vector.shape != (2,) or not np.isfinite(vector).all():
        raise ValueError("Expected two finite horizontal values")
    return vector * min(1.0, limit / max(np.linalg.norm(vector), 1e-12))


def pixel_to_offset(u, v, height=HEIGHT, focal=FOCAL_PX):
    """Level nadir only; output north/east metres relative to the camera."""
    return np.array([(SIZE / 2 - v) * height / focal,
                     (u - SIZE / 2) * height / focal])


def offset_to_pixel(offset, height=HEIGHT, focal=FOCAL_PX):
    n, e = offset
    return np.array([SIZE / 2 + e * focal / height,
                     SIZE / 2 - n * focal / height])


def parse_instruction(text):
    """Restricted vocabulary for the exercise; not general language grounding."""
    hits = [i for i, name in enumerate(CATEGORIES) if name in text.lower().split()]
    if len(hits) != 1:
        raise ValueError("Use exactly one of bottle, can, paper in the instruction")
    return hits[0]


@dataclass
class Observation:
    image: Image.Image
    position: np.ndarray
    velocity: np.ndarray
    capture_time: float


class Field:
    def __init__(self, seed=0, missing=None, response=1.0):
        self.seed = int(seed)
        rng = np.random.default_rng(seed)
        self.objects = []
        # Separate item centres to prevent overlap from hiding a teaching target.
        for category in range(3):
            while True:
                point = rng.uniform(-2.3, 2.3, 2)
                if all(np.linalg.norm(point - q) > .75 for _, q in self.objects):
                    break
            if category != missing:
                self.objects.append((category, point))
        self.position = rng.uniform(-.5, .5, 2)
        self.velocity = np.zeros(2)
        self.time = 0.0
        self.response = float(response)

    def observe(self):
        im = Image.new("RGB", (SIZE, SIZE), (54, 95, 49))
        draw = ImageDraw.Draw(im)
        for category, point in self.objects:
            u, v = offset_to_pixel(point - self.position)
            draw.ellipse((u-2.5, v-2.5, u+2.5, v+2.5), fill=COLOURS[category])
        # An unlabelled grey distractor. No crosshair/text contaminates model input.
        u, v = offset_to_pixel(np.array([3., -3.]) - self.position)
        draw.rectangle((u-2, v-2, u+2, v+2), fill=(140, 140, 140))
        return Observation(im, self.position.copy(), self.velocity.copy(), self.time)

    def expert(self, target):
        """Privileged target location, allowed only for demonstrations/evaluation."""
        point = next((q for c, q in self.objects if c == target), None)
        return np.zeros(2) if point is None else bounded(point - self.position)

    def apply(self, delta):
        # Anchor once, then follow the same absolute target for the whole interval.
        target = self.position + bounded(delta)
        target = np.clip(target, -4.0, 4.0)
        for _ in range(25):
            wanted = bounded((target - self.position) * 2.5, .8)
            self.velocity += (wanted - self.velocity) * min(.02 / (.25 * self.response), 1)
            self.position += self.velocity * .02
        self.time += DT
        return target

    def success(self, target):
        point = next((q for c, q in self.objects if c == target), None)
        return point is not None and np.linalg.norm(point-self.position) < .20 and np.linalg.norm(self.velocity) < .18


def visual_features(image):
    """All three colour centroids + presence, without selecting the target.

    Colours encode class in this teaching world; these features do NOT recognise
    real litter. The learner receives all objects, not a crop of the answer.
    """
    a = np.asarray(image, dtype=np.int16)
    out = []
    for colour in COLOURS:
        mask = np.linalg.norm(a - np.array(colour), axis=2) < 45
        y, x = np.where(mask)
        if len(x):
            out.extend([(SIZE/2-y.mean())/(SIZE/2), (x.mean()-SIZE/2)/(SIZE/2), 1.])
        else:
            out.extend([0., 0., 0.])
    return np.array(out, dtype=np.float32)


def policy_features(obs, target):
    language = np.zeros(3, dtype=np.float32)
    if target is not None:
        language[target] = 1
    return np.concatenate([visual_features(obs.image), language, obs.velocity]).astype(np.float32)


def classical(obs, target):
    feats = visual_features(obs.image).reshape(3, 3)
    if not feats[target, 2]:
        return np.zeros(2)
    return bounded(feats[target, :2] * HEIGHT)


def detect_and_map(obs):
    feats = visual_features(obs.image).reshape(3, 3)
    return [{"category": CATEGORIES[i], "local_ned_m": [*map(float, obs.position + f[:2]*HEIGHT), 0.0],
             "evidence_time_s": obs.capture_time} for i, f in enumerate(feats) if f[2]]
