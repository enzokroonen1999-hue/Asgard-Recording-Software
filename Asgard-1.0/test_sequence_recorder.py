import json
import os
import tempfile
import unittest

from sequence_recorder import MotionSequence, is_recordable_command, parse_status_report


class MotionSequenceTests(unittest.TestCase):
    def test_only_motion_and_gripper_commands_are_recordable(self):
        self.assertTrue(is_recordable_command("G1 A-12.5 B3 F100"))
        self.assertTrue(is_recordable_command("M3 S127.5"))
        self.assertFalse(is_recordable_command("$H"))
        self.assertFalse(is_recordable_command("G4 P0"))
        self.assertFalse(is_recordable_command("G1 A1; $H"))

    def test_record_commands_and_status_with_elapsed_times(self):
        sequence = MotionSequence()
        sequence.start()
        start = sequence.started_at
        self.assertTrue(sequence.record_command("G1 A2 F50", timestamp=start + 0.25))
        self.assertTrue(sequence.record_status("<Idle|MPos:A:2.000|FS:0,0>", timestamp=start + 0.3))
        self.assertFalse(sequence.record_command("$H", timestamp=start + 0.4))
        self.assertEqual(sequence.command_count, 1)
        self.assertAlmostEqual(sequence.events[0]["t_s"], 0.25)
        self.assertAlmostEqual(sequence.events[1]["t_s"], 0.3)

    def test_sequence_round_trip_and_rejects_unsupported_commands(self):
        sequence = MotionSequence()
        sequence.start()
        sequence.record_command("G0 X1.25")
        sequence.stop()
        with tempfile.TemporaryDirectory() as directory:
            path = os.path.join(directory, "sequence.json")
            sequence.save(path)
            loaded = MotionSequence()
            loaded.load(path)
            self.assertEqual(loaded.events, sequence.events)

            with open(path, "w") as sequence_file:
                json.dump({"schema_version": 1, "events": [{
                    "type": "command", "t_s": 0, "command": "$H",
                }]}, sequence_file)
            with self.assertRaises(ValueError):
                loaded.load(path)

    def test_parse_status_report_keeps_raw_values_and_state(self):
        parsed = parse_status_report("<Run|MPos:A:1.250,B:-2.5|FS:35,0>")
        self.assertEqual(parsed["state"], "Run")
        self.assertEqual(parsed["mpos"], {"A": 1.25, "B": -2.5})
        self.assertEqual(parsed["feed"], 35.0)
        self.assertEqual(parsed["raw"], "<Run|MPos:A:1.250,B:-2.5|FS:35,0>")


if __name__ == "__main__":
    unittest.main()