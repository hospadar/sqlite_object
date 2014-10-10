from sqlite_object import SqliteList

import unittest, os


class TestSqliteObjects(unittest.TestCase):
    def test_list(self):
        l = SqliteList()
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
        
        
if __name__ == '__main__':
    unittest.main()