import unittest

from agent311 import data, stats

# A tiny fake dataset in the same shape as data.clean_row() produces.
ROWS = [
    {"fsa": "M6H", "ward": "Davenport (09)", "type": "Road Pothole / Road Damage", "status": "Completed", "month": "2025-03", "division": "Transportation Services", "date": "2025-03-01", "intersection": ""},
    {"fsa": "M6H", "ward": "Davenport (09)", "type": "Road Pothole / Road Damage", "status": "Cancelled", "month": "2025-03", "division": "Transportation Services", "date": "2025-03-02", "intersection": ""},
    {"fsa": "M6H", "ward": "Davenport (09)", "type": "Construction Noise", "status": "Completed", "month": "2025-04", "division": "Municipal Licensing & Standards", "date": "2025-04-01", "intersection": ""},
    {"fsa": "M5V", "ward": "Spadina-Fort York (10)", "type": "Construction Noise", "status": "Completed", "month": "2025-05", "division": "Municipal Licensing & Standards", "date": "2025-05-01", "intersection": ""},
]


class StatsTest(unittest.TestCase):
    def test_postal_area_summary(self):
        summary = stats.area_summary(ROWS, "m6h", "Road Pothole / Road Damage")
        self.assertEqual(summary["total_requests"], 3)
        self.assertEqual(summary["count_of_this_type"], 2)
        self.assertEqual(summary["rank_in_area"], 1)
        self.assertEqual(summary["status_breakdown"], {"Completed": 1, "Cancelled": 1})

    def test_ward_by_number_and_name(self):
        self.assertEqual(stats.find_ward(ROWS, "ward 9"), "Davenport (09)")
        self.assertEqual(stats.find_ward(ROWS, "10"), "Spadina-Fort York (10)")
        self.assertEqual(stats.find_ward(ROWS, "davenport"), "Davenport (09)")

    def test_unknown_area(self):
        self.assertIn("error", stats.area_summary(ROWS, "narnia"))

    def test_clean_row_handles_intersection(self):
        raw = {
            "Creation Date": "2025-01-01 00:01:05.0000000", "Status": "Completed",
            "First 3 Chars of Postal Code": "Intersection", "Intersection Street 1": "King St W",
            "Intersection Street 2": "John St", "Ward": "Spadina-Fort York (10)",
            "Service Request Type": "Traffic Signal Repair", "Division": "Transportation Services",
        }
        row = data.clean_row(raw)
        self.assertEqual(row["fsa"], "")
        self.assertEqual(row["intersection"], "King St W & John St")
        self.assertEqual(row["month"], "2025-01")

    def test_division_for_type(self):
        self.assertEqual(data.division_for_type(ROWS, "Construction Noise"), "Municipal Licensing & Standards")


if __name__ == "__main__":
    unittest.main()
