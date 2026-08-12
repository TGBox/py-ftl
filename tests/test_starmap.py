import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from classes.StarMap import StarMap


class TestStarMap(unittest.TestCase):

    def setUp(self):
        self.star_map = StarMap()

    def test_starmap_generation(self):
        self.assertGreater(len(self.star_map.nodes), 0)
        self.assertIsNotNone(self.star_map.current_node)
        assert self.star_map.current_node is not None
        self.assertEqual(self.star_map.current_node.event_type, "EMPTY")

        exit_nodes = [n for n in self.star_map.nodes if n.event_type == "EXIT"]
        self.assertEqual(len(exit_nodes), 1)

    def test_node_connectivity(self):
        # Verify every node (except exit) has at least 1 outgoing connection
        for node in self.star_map.nodes:
            if node.event_type != "EXIT":
                self.assertGreater(len(node.connections), 0, f"Node {node.id} should have connections.")

    def test_rebel_fleet_advancement(self):
        init_x = self.star_map.rebel_fleet_x
        self.star_map.advance_fleet()
        self.assertGreater(self.star_map.rebel_fleet_x, init_x)


if __name__ == "__main__":
    unittest.main()
