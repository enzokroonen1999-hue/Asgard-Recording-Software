import json
import math
import re
import time


_NUMBER = r"[+-]?(?:\d+(?:\.\d*)?|\.\d+)"
_MOTION_COMMAND = re.compile(
    r"^(?:G0|G1)(?:\s+[ABCDXYZ]" + _NUMBER + r")+(?:\s+F" + _NUMBER + r")?$",
    re.IGNORECASE,
)
_GRIPPER_COMMAND = re.compile(r"^M3\s+S" + _NUMBER + r"$", re.IGNORECASE)


def is_recordable_command(command):
    command = command.strip()
    return bool(_MOTION_COMMAND.match(command) or _GRIPPER_COMMAND.match(command))


def parse_status_report(report):
    report = report.strip()
    if not (report.startswith("<") and report.endswith(">")):
        return {}

    fields = report[1:-1].split("|")
    parsed = {"state": fields[0], "raw": report, "mpos": {}, "feed": None}
    for field in fields[1:]:
        if field.startswith("MPos:"):
            for index, value in enumerate(field[5:].split(",")):
                if ":" in value:
                    axis, value = value.rsplit(":", 1)
                else:
                    axis = "axis_{}".format(index)
                try:
                    parsed["mpos"][axis] = float(value)
                except ValueError:
                    continue
        elif field.startswith("FS:"):
            try:
                parsed["feed"] = float(field[3:].split(",", 1)[0])
            except ValueError:
                pass
    return parsed


class MotionSequence:
    SCHEMA_VERSION = 1

    def __init__(self):
        self.events = []
        self.started_at = None

    @property
    def is_recording(self):
        return self.started_at is not None

    @property
    def command_count(self):
        return sum(event["type"] == "command" for event in self.events)

    def start(self):
        self.events = []
        self.started_at = time.monotonic()

    def stop(self):
        self.started_at = None

    def clear(self):
        self.events = []
        self.started_at = None

    def _elapsed(self, timestamp):
        if self.started_at is None:
            return None
        return max(0.0, timestamp - self.started_at)

    def record_command(self, command, status="", timestamp=None):
        command = command.strip()
        if not self.is_recording or not is_recordable_command(command):
            return False
        if timestamp is None:
            timestamp = time.monotonic()
        self.events.append({
            "type": "command",
            "t_s": self._elapsed(timestamp),
            "command": command,
            "status": status,
        })
        return True

    def record_status(self, status, timestamp=None):
        if not self.is_recording:
            return False
        if timestamp is None:
            timestamp = time.monotonic()
        self.events.append({
            "type": "status",
            "t_s": self._elapsed(timestamp),
            "report": status,
        })
        return True

    def save(self, path):
        document = {
            "schema_version": self.SCHEMA_VERSION,
            "events": self.events,
        }
        with open(path, "w") as sequence_file:
            json.dump(document, sequence_file, indent=2, sort_keys=True)

    def load(self, path):
        with open(path, "r") as sequence_file:
            document = json.load(sequence_file)
        if document.get("schema_version") != self.SCHEMA_VERSION:
            raise ValueError("Unsupported sequence file version")
        events = document.get("events")
        if not isinstance(events, list):
            raise ValueError("Sequence events must be a list")

        validated_events = []
        for event in events:
            if not isinstance(event, dict):
                raise ValueError("Invalid sequence event")
            event_type = event.get("type")
            timestamp = event.get("t_s")
            if (event_type not in ("command", "status")
                    or not isinstance(timestamp, (int, float))
                    or not math.isfinite(timestamp) or timestamp < 0):
                raise ValueError("Invalid sequence event metadata")
            if event_type == "command":
                command = event.get("command")
                status = event.get("status", "")
                if not isinstance(command, str) or not is_recordable_command(command):
                    raise ValueError("Sequence contains an unsupported command")
                if not isinstance(status, str):
                    raise ValueError("Invalid recorded controller status")
                validated_events.append({
                    "type": "command",
                    "t_s": timestamp,
                    "command": command,
                    "status": status,
                })
            else:
                report = event.get("report")
                if not isinstance(report, str):
                    raise ValueError("Invalid status report")
                validated_events.append({
                    "type": "status",
                    "t_s": timestamp,
                    "report": report,
                })
        self.events = validated_events
        self.started_at = None