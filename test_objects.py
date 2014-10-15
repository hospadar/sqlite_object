from __future__ import print_function
from sqlite_object import SqliteList, SqliteDict

import unittest, os



class TestSqliteObjects(unittest.TestCase):
    
    def run_list_tests(self, l):
        for i in range(10):
                l.append(i)
                
        #Test appending, prepending, and popping of either end of the list
        self.assertEqual(10, len(l))
        self.assertEqual(0, l[0])
        
        l.prepend("something")
        self.assertEqual(11, len(l))
        self.assertEqual("something", l[0])
        
        l.append("else")
        self.assertEqual(12, len(l))
        self.assertEqual("else", l[-1])
        self.assertEqual("else", l[11])
        self.assertEqual(l[10], l[-2])
        self.assertEqual(9, l[10])
        
        self.assertEqual("something", l.pop_first())
        self.assertEqual(11, len(l))
        self.assertEqual(0, l.pop_first())
        self.assertEqual(10, len(l))
        
        self.assertEqual("else", l.pop_last())
        self.assertEqual(9, len(l))
        self.assertEqual(9, l.pop_last())
        self.assertEqual(8, len(l))
        
        l.append("thing")
        self.assertEqual(l[-1], "thing")
        self.assertEqual(9, len(l))
        
        l.prepend("other")
        self.assertEqual(l[0], "other")
        self.assertEqual(10, len(l))
        
        #Test some getting and setting behavior
        l[0] = 52
        self.assertEqual(52, l[0])
        l[0] += 1
        self.assertEqual(53, l[0])
        l[-1] = 12
        self.assertEqual(12, l[-1])
        l[-1] -= 1
        self.assertEqual(11, l[-1])
        
        #make sure you can't get or set bad values
        self.assertRaises(IndexError, l.__getitem__, 50)
        self.assertRaises(IndexError, l.__setitem__, 50, 1)
        self.assertRaises(IndexError, l.__getitem__, -50)
        self.assertRaises(IndexError, l.__setitem__, -50, 1)
    
    def test_list(self):
        print("Testing list")
        #run a bunch o tests
        l = SqliteList()
        self.run_list_tests(l)
        
        #make sure it still works when you turn off indexing
        l = SqliteList(index=False)
        self.run_list_tests(l)
    
        #test initializer
        l = SqliteList(["a", "b", "c"])
        self.assertEqual(3, len(l))
        #test iterator
        self.assertEqual(["a", "b", "c"], [x for x in l])
        #test reverse
        self.assertEqual(["c", "b", "a"], [x for x in reversed(l)])
        
        #test extension
        l.extend([1, 2, 3])
        self.assertEqual(["a", "b", "c", 1, 2, 3], [x for x in l])
        
        #test filename-specified lists
        l = SqliteList(["a", "b", "c"], filename = "mylist.sqlite3")
        l2 = SqliteList(filename = "mylist.sqlite3")
        self.assertEqual([x for x in l], [x for x in l2])
        l2.append("hi")
        self.assertEqual([x for x in l], [x for x in l2])
        self.assertEqual("hi", l[-1])
        
        thing = SqliteList(["a", "b", "c"], filename = "doodad.sqlite3", persist=True)
        del thing
        self.assertRaises(NameError, eval, "thing")
        self.assertTrue(os.path.exists("doodad.sqlite3"))
        os.remove("doodad.sqlite3")
        
    def run_dict_tests(self, d):
        d["1"] = "a"
        d["2"] = "b"
        d["3"] = "c"
        self.assertIn("1", d)
        self.assertIn("2", d)
        self.assertIn("3", d)
        self.assertEqual("a", d["1"])
        self.assertEqual("b", d["2"])
        self.assertEqual("c", d["3"])
        self.assertEqual(3, len(d))
        del d["2"]
        self.assertNotIn("2", d)
        self.assertEqual("a", d["1"])
        self.assertEqual("c", d["3"])
        self.assertEqual(2, len(d))
        d.update({"1":20, "thing":"other"})
        self.assertEqual(3, len(d))
        self.assertEqual(20, d["1"])
        self.assertEqual("other", d["thing"])
        d["1"] += 1
        d["1"] += 1
        self.assertEqual(22, d["1"])
        self.assertEqual({"1", "3", "thing"}, set([x for x in d.keys()]))
        self.assertEqual({22, "c", "other"}, set([x for x in d.values()]))
        self.assertEqual({("1", 22), ("3", "c"), ("thing", "other")}, set([x for x in d.items()]))
        
    def test_dict(self):
        print("Running dict tests")
        d = SqliteDict()
        self.run_dict_tests( d)
        
        d = SqliteDict(index=False)
        self.run_dict_tests(d)
        d["extra"] = "item"
        
        d2 = SqliteDict({1:"a", 2:"b", 3:"c", "1":5})
        d.update(d2)
        self.assertEqual(7, len(d))
        self.assertIn(1, d)
        self.assertIn(2, d)
        self.assertEqual(5, d["1"])
        
        d = SqliteDict({1:"a", 2:"b", 3:"c", "1":5}, filename="mydict.sqlite")
        d2 = SqliteDict(filename="mydict.sqlite")
        
        self.assertEqual(set([x for x in d.items()]), set([x for x in d2.items()]))
        
        
if __name__ == '__main__':
    unittest.main()