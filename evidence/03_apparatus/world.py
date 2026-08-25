"""A minimal AI2-THOR world: one empty white room containing a single agent.

The room is built with AI2-THOR's procedural scene support ("Procedural" scene
plus a CreateHouse action), so it contains nothing but a floor, four walls,
a ceiling, and light. Experimental control over visual variety is the point.
"""

from __future__ import annotations

import math

from ai2thor.controller import Controller

ROOM_SIZE = 4.0    # side length in meters
WALL_HEIGHT = 3.0
MOVE_MAGNITUDE = 0.5
TURN_DEGREES = 45

# Verified against the build's material database at startup; if missing we fall
# back to the first material whose name contains "white".
WHITE_MATERIAL = "PureWhite"

# The agent-facing action vocabulary and its mapping onto THOR actions.
# "speak" and "wait" have no physical effect; they map onto Pass.
ACTIONS = {
    "move_forward": dict(action="MoveAhead", moveMagnitude=MOVE_MAGNITUDE),
    "move_back": dict(action="MoveBack", moveMagnitude=MOVE_MAGNITUDE),
    "turn_left": dict(action="RotateLeft", degrees=TURN_DEGREES),
    "turn_right": dict(action="RotateRight", degrees=TURN_DEGREES),
    "look_up": dict(action="LookUp"),
    "look_down": dict(action="LookDown"),
    "speak": dict(action="Pass"),
    "wait": dict(action="Pass"),
}

COMPASS = ["north", "northeast", "east", "southeast",
           "south", "southwest", "west", "northwest"]


def _wall(wall_id: str, p0: tuple, p1: tuple, material: str) -> dict:
    (x0, z0), (x1, z1) = p0, p1
    return {
        "id": wall_id,
        "roomId": "room_0",
        "material": {"name": material},
        "polygon": [
            {"x": x0, "y": 0, "z": z0},
            {"x": x1, "y": 0, "z": z1},
            {"x": x0, "y": WALL_HEIGHT, "z": z0},
            {"x": x1, "y": WALL_HEIGHT, "z": z1},
        ],
    }


def build_house(material: str) -> dict:
    s = ROOM_SIZE
    # Walls are one-sided; emit each edge in both windings so the room is
    # closed regardless of viewing direction.
    corners = [(0, 0), (0, s), (s, s), (s, 0)]
    walls = []
    for i in range(4):
        p0, p1 = corners[i], corners[(i + 1) % 4]
        walls.append(_wall(f"wall_{i}a", p0, p1, material))
        walls.append(_wall(f"wall_{i}b", p1, p0, material))
    return {
        "id": "white_room",
        "proceduralParameters": {
            "ceilingMaterial": {"name": material},
            "floorColliderThickness": 1.0,
            "receptacleHeight": 0.7,
            "skyboxId": "Sky1",
            "lights": [
                {
                    "id": "directional_light",
                    "type": "directional",
                    "position": {"x": s / 2, "y": WALL_HEIGHT - 0.4, "z": s / 2},
                    "rotation": {"x": 66, "y": 75, "z": 0},
                    "intensity": 0.7,
                    "rgb": {"r": 1.0, "g": 1.0, "b": 1.0},
                },
                {
                    "id": "point_light",
                    "type": "point",
                    "position": {"x": s / 2, "y": WALL_HEIGHT - 0.5, "z": s / 2},
                    "intensity": 0.9,
                    "range": 15,
                    "rgb": {"r": 1.0, "g": 1.0, "b": 1.0},
                },
            ],
        },
        "rooms": [
            {
                "id": "room_0",
                "roomType": "LivingRoom",
                "floorMaterial": {"name": material},
                "floorPolygon": [
                    {"x": 0, "y": 0, "z": 0},
                    {"x": 0, "y": 0, "z": s},
                    {"x": s, "y": 0, "z": s},
                    {"x": s, "y": 0, "z": 0},
                ],
                "children": [],
                "ceilings": [],
            }
        ],
        "walls": walls,
        "doors": [],
        "windows": [],
        "objects": [],
        "metadata": {
            "agent": {
                "horizon": 0,
                "position": {"x": s / 2, "y": 0.95, "z": 1.0},
                "rotation": {"x": 0, "y": 0, "z": 0},
                "standing": True,
            },
            "schema": "1.0.0",
        },
    }


class WhiteRoom:
    """The world. Holds ground truth; hands the agent only observations."""

    def __init__(self, width: int = 640, height: int = 480):
        self.controller = Controller(
            scene="Procedural",
            width=width,
            height=height,
            gridSize=0.25,
            snapToGrid=False,
            visibilityDistance=10.0,
        )
        material = self._resolve_material()
        event = self.controller.step(action="CreateHouse", house=build_house(material))
        if not event.metadata["lastActionSuccess"]:
            raise RuntimeError(
                f"CreateHouse failed: {event.metadata.get('errorMessage')}"
            )
        self.controller.step(
            action="TeleportFull",
            position={"x": ROOM_SIZE / 2, "y": 0.95, "z": 1.0},
            rotation={"x": 0, "y": 0, "z": 0},
            horizon=0,
            standing=True,
        )
        # Flush a few frames so the on-screen window shows the finished room
        # instead of the build's boot scene (which lingers until steps render).
        for _ in range(5):
            self.controller.step(action="Pass")
        self.last_action_result = {"action": None, "success": True, "error": None}

    def reset_pose(self) -> None:
        """Return the agent's body to the starting pose (for repeated trials)."""
        self.controller.step(
            action="TeleportFull",
            position={"x": ROOM_SIZE / 2, "y": 0.95, "z": 1.0},
            rotation={"x": 0, "y": 0, "z": 0},
            horizon=0,
            standing=True,
        )
        self.controller.step(action="Pass")
        self.last_action_result = {"action": None, "success": True, "error": None}

    def _resolve_material(self) -> str:
        event = self.controller.step(action="GetMaterials")
        names: list[str] = []
        ret = event.metadata.get("actionReturn")
        if isinstance(ret, dict):
            for group in ret.values():
                if isinstance(group, list):
                    names.extend(str(n) for n in group)
        elif isinstance(ret, list):
            names = [str(n) for n in ret]
        if WHITE_MATERIAL in names:
            return WHITE_MATERIAL
        for name in names:
            if "white" in name.lower():
                return name
        return names[0] if names else WHITE_MATERIAL

    # ------------------------------------------------------------------ #

    def step(self, action_name: str) -> dict:
        """Execute one agent-vocabulary action. Returns a result dict."""
        if action_name not in ACTIONS:
            self.last_action_result = {
                "action": action_name,
                "success": False,
                "error": f"unknown action '{action_name}'",
            }
            return self.last_action_result
        event = self.controller.step(**ACTIONS[action_name])
        self.last_action_result = {
            "action": action_name,
            "success": event.metadata["lastActionSuccess"],
            "error": event.metadata.get("errorMessage") or None,
        }
        return self.last_action_result

    def frame(self):
        return self.controller.last_event.frame

    # ------------------------------------------------------------------ #

    def observe(self) -> dict:
        """What the agent is allowed to know, as structured data plus text."""
        meta = self.controller.last_event.metadata
        agent = meta["agent"]
        x, z = agent["position"]["x"], agent["position"]["z"]
        yaw = agent["rotation"]["y"] % 360
        horizon = agent["cameraHorizon"]
        heading = COMPASS[int(((yaw + 22.5) % 360) // 45)]
        structural = {"Wall", "Floor", "Ceiling", "Doorway", "Window", "Doorframe"}
        visible = sorted(
            o["objectType"]
            for o in meta["objects"]
            if o.get("visible") and o["objectType"] not in structural
        )
        obs = {
            "heading": heading,
            "horizon": round(horizon, 1),
            "wall_distance": self._distance_to_wall(x, z, yaw),
            "visible_objects": visible,
            "last_action": dict(self.last_action_result),
        }
        obs["description"] = self._describe(obs)
        return obs

    def _distance_to_wall(self, x: float, z: float, yaw: float) -> float:
        dx = math.sin(math.radians(yaw))
        dz = math.cos(math.radians(yaw))
        hits = []
        for d, p, lo, hi in ((dx, x, 0.0, ROOM_SIZE), (dz, z, 0.0, ROOM_SIZE)):
            if abs(d) > 1e-6:
                for bound in (lo, hi):
                    t = (bound - p) / d
                    if t > 0:
                        hits.append(t)
        return round(min(hits), 1) if hits else 0.0

    def _describe(self, obs: dict) -> str:
        parts = [
            "You are standing in a small room with plain white walls, "
            "a white floor, and a white ceiling.",
            f"You are facing {obs['heading']}. "
            f"The wall ahead of you is about {obs['wall_distance']} meters away.",
        ]
        if obs["horizon"] < -5:
            parts.append("Your gaze is tilted upward.")
        elif obs["horizon"] > 5:
            parts.append("Your gaze is tilted downward.")
        if obs["visible_objects"]:
            parts.append("You can see: " + ", ".join(obs["visible_objects"]) + ".")
        else:
            parts.append("You see nothing else in the room.")
        last = obs["last_action"]
        if last["action"] is not None:
            if last["success"]:
                parts.append(f"Your last action ({last['action']}) succeeded.")
            else:
                reason = "you bumped into something" if "collided" in str(
                    last["error"] or "").lower() else (last["error"] or "it failed")
                parts.append(f"Your last action ({last['action']}) failed: {reason}.")
        return " ".join(parts)

    def stop(self):
        self.controller.stop()
