import unittest

from routing import parse_tg_chat_map, telegram_target_for


class RoutingTest(unittest.TestCase):
    def test_empty_map(self):
        route_map, warnings = parse_tg_chat_map("")

        self.assertEqual({}, route_map)
        self.assertEqual([], warnings)

    def test_single_mapping(self):
        route_map, warnings = parse_tg_chat_map("-71032535556121:-1001111111111")

        self.assertEqual({-71032535556121: "-1001111111111"}, route_map)
        self.assertEqual([], warnings)

    def test_multiple_mappings(self):
        route_map, warnings = parse_tg_chat_map(
            "-71032535556121:-1001111111111,-72646267836456:-1002222222222"
        )

        self.assertEqual(
            {
                -71032535556121: "-1001111111111",
                -72646267836456: "-1002222222222",
            },
            route_map,
        )
        self.assertEqual([], warnings)

    def test_whitespace_is_trimmed(self):
        route_map, warnings = parse_tg_chat_map(" -71032535556121 : -1001111111111 ")

        self.assertEqual({-71032535556121: "-1001111111111"}, route_map)
        self.assertEqual([], warnings)

    def test_comments_are_ignored(self):
        route_map, warnings = parse_tg_chat_map(
            """
            # parents
            -71032535556121:-1001111111111, # class
            -72646267836456:-1002222222222
            """
        )

        self.assertEqual(
            {
                -71032535556121: "-1001111111111",
                -72646267836456: "-1002222222222",
            },
            route_map,
        )
        self.assertEqual([], warnings)

    def test_comment_only_map_is_empty(self):
        route_map, warnings = parse_tg_chat_map("# parents\n# class")

        self.assertEqual({}, route_map)
        self.assertEqual([], warnings)

    def test_invalid_entries_return_warnings_without_values(self):
        route_map, warnings = parse_tg_chat_map(
            "bad:-1001111111111, -71032535556121:, missing-separator, "
        )

        self.assertEqual({}, route_map)
        self.assertEqual(
            [
                {"position": 1, "reason": "invalid_max_chat_id"},
                {"position": 2, "reason": "missing_tg_chat_id"},
                {"position": 3, "reason": "missing_separator"},
                {"position": 4, "reason": "empty_entry"},
            ],
            warnings,
        )

    def test_mapped_target_wins(self):
        target, source = telegram_target_for(
            -71032535556121,
            {-71032535556121: "-1001111111111"},
            "-1009999999999",
        )

        self.assertEqual("-1001111111111", target)
        self.assertEqual("mapped", source)

    def test_fallback_behavior(self):
        target, source = telegram_target_for(-71032535556121, {}, "-1009999999999")

        self.assertEqual("-1009999999999", target)
        self.assertEqual("fallback_TG_CHAT_ID", source)

    def test_blank_fallback_is_missing(self):
        target, source = telegram_target_for(-71032535556121, {}, "   ")

        self.assertIsNone(target)
        self.assertEqual("missing_target", source)

    def test_missing_target_behavior(self):
        target, source = telegram_target_for(-71032535556121, {}, None)

        self.assertIsNone(target)
        self.assertEqual("missing_target", source)


if __name__ == "__main__":
    unittest.main()
