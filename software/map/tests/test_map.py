import os
import tempfile
import threading
import unittest
import urllib.parse
import urllib.request

import suitmap                                     # noqa: F401, puts the protocol on the path
from suitmap import JOINTS, Map, Seen
from suitmap.lists import IMU_PLACES, joint_values
from suitmap.web import serve
from ci import stp
from suitsim import Suit


def seen_of(suit: Suit) -> list[Seen]:
    return [Seen(u.uid.hex(), u.line, u.kind, u.ads, 0x0100) for u in suit.units]


class TestMap(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.TemporaryDirectory()
        self.path = os.path.join(self.d.name, "map.json")
        self.suit = Suit.standard(16)
        self.m = Map(self.path)
        self.m.bring_up(seen_of(self.suit))

    def tearDown(self):
        self.d.cleanup()

    def test_known_without_asking(self):
        by_uid = {u.uid.hex(): u for u in self.suit.units}
        known = {e.place: by_uid[e.uid].name for e in self.m.units.values() if e.place}
        self.assertEqual(known[4], "glove L")
        self.assertEqual(known[16], "sock R")
        self.assertEqual(known[17], "head")
        self.assertEqual(known[18], "chest and abdomen")
        self.assertEqual({p: known[p] for p in (21, 22)}, {21: "Nataša", 22: "Míša"})
        self.assertEqual(self.m.units[next(u for u, s in by_uid.items()
                                            if s.kind == stp.KIND_MISA)].number, stp.MISA)
        asked = self.m.questions()
        self.assertEqual(len(asked), 3 * 4 + 2)           # three modules a limb, line 7's two

    def test_answers_give_places_and_numbers(self):
        for q in self.m.questions():
            self.m.answer(q.uid, self.m.free_places(q.line)[0])
        self.assertEqual(self.m.questions(), [])
        numbers = [e.number for e in self.m.units.values()]
        self.assertEqual(len(numbers), len(set(numbers)))
        twos = sorted(n for n in numbers if n >> 5 == stp.T_TWO)
        self.assertEqual(twos, [stp.address(stp.T_TWO, k) for k in range(1, 16)])
        self.assertEqual([n for n in numbers if n >> 5 == stp.T_ONE], [stp.address(stp.T_ONE, 1)])
        again = Map(self.path)                              # kept in the JSON
        self.assertEqual({u: e.place for u, e in again.units.items()},
                         {u: e.place for u, e in self.m.units.items()})

    def test_a_module_replaced(self):
        for q in self.m.questions():
            self.m.answer(q.uid, self.m.free_places(q.line)[0])
        old = next(e for e in self.m.units.values() if e.place == 2)
        seen = [s for s in seen_of(self.suit) if s.uid != old.uid]
        seen.append(Seen("aa" * 12, old.line, old.kind, old.ads, 0x0100))
        self.m.bring_up(seen)
        new = self.m.units["aa" * 12]
        self.assertEqual((new.place, new.number, new.confirmed), (2, old.number, False))
        again = Map(self.m.path)                         # kept over a restart
        again.bring_up(seen)
        again.confirm(new.uid)
        self.assertNotIn(old.uid, again.units)
        self.assertTrue(again.units[new.uid].confirmed)

    def test_a_module_moved_to_another_line(self):
        for q in self.m.questions():
            self.m.answer(q.uid, self.m.free_places(q.line)[0])
        moved = next(e for e in self.m.units.values() if e.place == 2)
        seen = [s if s.uid != moved.uid else Seen(s.uid, 2, s.kind, s.ads, s.firmware)
                for s in seen_of(self.suit)]
        self.m.bring_up(seen)
        self.assertEqual(self.m.units[moved.uid].place, 0)
        self.assertIn(moved.uid, [q.uid for q in self.m.questions()])

    def test_missing_kept_until_forgotten(self):
        gone = self.suit.units[0].uid.hex()
        self.m.bring_up([s for s in seen_of(self.suit) if s.uid != gone])
        self.assertIn(gone, self.m.units)
        self.m.forget(gone)
        self.assertNotIn(gone, self.m.units)
        with self.assertRaises(ValueError):
            self.m.forget(self.suit.units[1].uid.hex())

    def test_one_bias_and_the_service_mode(self):
        a, b = [s.uid.hex() for s in self.suit.units[:2]]
        self.m.set(a, bias=True)
        self.m.set(b, bias=True)
        self.assertEqual([e.uid for e in self.m.units.values() if e.bias], [b])
        self.m.service = False
        with self.assertRaises(PermissionError):
            self.m.set(a, shield=1)


class TestPage(unittest.TestCase):
    def test_the_page_and_an_answer(self):
        with tempfile.TemporaryDirectory() as d:
            m = Map(os.path.join(d, "map.json"))
            m.bring_up(seen_of(Suit.standard(4, gloves=False, socks=False)))
            blinked = []
            server = serve(m, "127.0.0.1", 0, storoz=lambda: "running", blink=blinked.append)
            t = threading.Thread(target=server.serve_forever, daemon=True)
            t.start()
            url = f"http://127.0.0.1:{server.server_address[1]}"
            body = urllib.request.urlopen(url + "/").read().decode()
            self.assertIn("http-equiv=refresh content=2", body)
            self.assertIn("Storož: running", body)
            self.assertNotIn("<script", body)
            q = m.questions()[0]
            for path, form in (("/ask", {"uid": q.uid}),
                               ("/answer", {"uid": q.uid, "place": m.free_places(q.line)[0]})):
                data = urllib.parse.urlencode(form).encode()
                urllib.request.urlopen(url + path, data)
            self.assertEqual(blinked, [q.uid, None])
            self.assertTrue(m.units[q.uid].place)
            server.shutdown()
            server.server_close()


class TestLists(unittest.TestCase):
    def test_every_joint_has_its_bones(self):
        bones = {b for places in IMU_PLACES.values() for b in places}
        for j in JOINTS:
            self.assertIn(j.parent, bones, j.name)
            self.assertIn(j.child, bones, j.name)
        self.assertLessEqual(len(joint_values()), 127)
        for _, _, lo, hi in joint_values():
            self.assertTrue(-128 <= lo < hi <= 127)

    def test_imu_places_match_the_units(self):
        from suitmap.lists import PLACES
        by_name = {v: k for k, v in PLACES.items()}
        for u in Suit.standard(16).units:
            if u.line == 8:
                continue
            name = u.name
            for short, side in ((" L", "left "), (" R", "right ")):
                if name.endswith(short):
                    name = side + name[:-2].replace("glove", "hand").replace("sock", "foot")
            self.assertEqual(len(IMU_PLACES[by_name[name]]), u.imus, u.name)


if __name__ == "__main__":
    unittest.main()
