__author__ = 'nsaintarnaud'

"""
sudokupy - sovle simple sudoku puzzles

objects
- Grid = 9x9
- Digit = 1x1
- DigitGroup = any of 9x1 (row), 1x9 (col), 3x3 (box)

grid has
- references to 9 boxes, 9 rows, 9 cols, 81 digits

digit has
- list of possible values; if the list has size=1 then that's the solution
- reference to parent grid, row, col and box
- set method to set the value, which tells its parent row, col and box that
the value is no longer possible for the other digits

"""

import sys
import argparse


# use this character to display an unknown value in a grid
UNKNOWN_DIGIT_INPUT = "-._ 0"  # any of those will be accepted as unknown
UNKNOWN_DIGIT_DISPLAY = "-"    # unknown digits will be displayed as this
ROW_TERMINATOR = "\n\r"

class Digit:
    """One of the 81 positions in the grid.
    Keeps track of possible values; if there is only one possible value 
    then that Digit is solved."""

    def __init__(self, grid, position, row, col, box, 
            values = [1,2,3,4,5,6,7,8,9]):
        self.grid = grid
        self.position = position
        self.row = row
        self.col = col
        self.box = box
        self.v = set(values)  # possible values

    def solved(self, debug=False):
        """Digit is solved if only one possible value left"""

        if debug:
            import pdb; pdb.set_trace()
        return (1 == len(self.v))

    def getSolvedValue(self):
        """solved if only one possible value left"""
        if self.solved():
            return int(list(self.v)[0])
        else: 
            return None

    def setSolvedValue(self, myvalue, propagate=False):
        self.v = set([myvalue])
        if propagate:
            self.propagate()

    def propagate(self):
        """if the digit is solved, tell the containing row, col and box 
        that the Digit's value is no longer possible"""

        #import pdb; pdb.set_trace()
        if self.solved():
            """this caused the digit to be solved"""
            self.row.not_possible(self.getSolvedValue())
            self.col.not_possible(self.getSolvedValue())
            self.box.not_possible(self.getSolvedValue())

    def not_possible(self, value, recurse=False):
        """remove the value from the possible values"""
        if self.solved(): 
            raise Exception("at least one value has to be possible")
        else:
            self.v.discard(value)
        if recurse:
            self.propagate()

    def tostring(self, printAllPossibleValues=False):
        if self.solved():
            return str(self.getSolvedValue())
        elif printAllPossibleValues:
            dig = [str(x) for x in self.v]
            # import pdb; pdb.set_trace()
            return "[" + ",".join(dig) + "]"
        else:
            return UNKNOWN_DIGIT_DISPLAY


class DigitGroup:
    """Stuff common to groups of Digits, e.g. row, col, box"""

    def __init__(self):
        self.digits = []

    def append(self, d):
        if not isinstance(d, Digit):
            raise Exception("expecting a list of Digits")
        self.digits.append(d)
        
    def not_possible(self, value):
        for dig in self.digits:
            if not dig.solved(): 
                dig.not_possible(value)

    def tostring(self, printAllPossibleValues=False):
        st = ""
        for dig in self.digits:
            st += dig.tostring(printAllPossibleValues)
            if printAllPossibleValues:
                st += "\n"
        if printAllPossibleValues:
            st += "\n"
        return st


def row_col_box(position):
    """return the row, column and box number.
    Our convention is that the digits are strung together row0 .. row8
    and boxes are counted left to right, then top to bottom
    so that the 36th digit (self.digits[35]) is 
    in the 4th row (self.rows[3]), 
    in the 9th column (self.cols[8]) and 
    in the 6th box (self.box[5]).
    """
    r = int(position/9)
    c = position % 9
    b = int(r/3) * 3 + int(c/3)
    return (r,c,b)


class Grid:
    """9x9 grid, top-level container"""

    def __init__(self):
        """initialize an empty grid"""

        self.digits = []
        self.rows = [DigitGroup() for i in range(9)]
        self.cols = [DigitGroup() for i in range(9)]
        self.boxes = [DigitGroup() for i in range(9)]
        self.loaded = False

        for position in range(81):
            (r,c,b) = row_col_box(position)
            d = Digit(self, position, self.rows[r], self.cols[c], self.boxes[b])
            self.digits.append(d)
            self.rows[r].append(d)
            self.cols[c].append(d)
            self.boxes[b].append(d)
        

    def number_unsolved(self):
        """return the number of unsolved digits"""
        unsolved = 0
        for dig in self.digits:
            if not dig.solved():
                unsolved += 1
        return unsolved

    def solved(self):
        return (0 == self.number_unsolved())

    def propagate_all(self):
        for dig in self.digits:
            dig.propagate()

    def load(self, puzzle):
        """Load a string representing the puzzle into the Grid, row by row.
        Digits 1-9 are understood.
        Any other character is construed as unknown.
        A carriage return skips to the next row."""


        counter = 0;  # which Digit are we on
        for c in puzzle:
            if counter > 80:
                # we have all 81 digits, ignore rest
                break
            elif c in "123456789":
                if args.verbose:
                    print "found digit   '{}', digit #{}, {} left unsolved".format(
                        c, counter, self.number_unsolved())
                self.digits[counter].setSolvedValue(c)
                counter += 1
            elif c in UNKNOWN_DIGIT_INPUT:
                if args.verbose:
                    print "found unknown '{}', digit #{}, {} left unsolved".format(
                        c, counter, self.number_unsolved())
                counter += 1
            elif c in ROW_TERMINATOR:
                # skip to next row, but only if not already at end or row
                if counter % 9 != 0:
                    if args.verbose:
                        print "found row terminator; skipping to next row"
                    counter = 9 * ( int(counter/9) +1 ) 
            else:
                # ignore anything else
                pass

        self.loaded = True


    def tostring(self, pretty = True):
        counter = 0
        s = ""
        for d in self.digits:
            s += d.tostring()
            if pretty:
                counter += 1
                if (counter % 9) == 0:
                    s += "\n"
        return s


if __name__ == "__main__":

    MAX_ITERATIONS = 20
    
    EXAMPLE_GRID = """
..67...8.
..426....
.3.8.94.7
8...92..1
..3..8...
.7.5..2..
.........
...4....5
9.2...31.
"""

    parser = argparse.ArgumentParser(description="solve a Sudoku puzzle")

    parser.add_argument("filename", nargs="?",
                        help="file with a text description of the initial state of the puzzle")
    parser.add_argument("-x", "--example", action="store_true", 
                        help="solve an example puzzle")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-v", "--verbose", action="store_true")
    group.add_argument("-q", "--quiet", action="store_true")

    args = parser.parse_args()

    g = Grid()

    if args.example:
        g.load(EXAMPLE_GRID)
    elif args.filename:
        f = open(args.filename)
        gridtext = f.read()
        g.load(gridtext)
        
    if not g.loaded:
        parser.print_help()
        sys.exit(2)

    if not args.quiet:
        print "\nloaded grid with {} unsolved:\n{}".format(
            g.number_unsolved(), g.tostring())

    for it in range(1,MAX_ITERATIONS):
        if g.solved():
            break
        last_unsolved = g.number_unsolved()
        g.propagate_all()
        if g.number_unsolved() == last_unsolved:
            print "cannot solve - stalled with {} unsolved\n{}".format(
                g.number_unsolved(), g.tostring())
            exit(0)
        if g.number_unsolved() >0 and not args.quiet:
            print "{} unsolved after iteration #{}:\n{}".format(
                g.number_unsolved(), it, g.tostring())
    iterations = it-1

    # print solution
    if not args.quiet:
        print "found solution after {} iteration{}:".format(
            iterations, ("" if iterations==1 else "s"))
    print g.tostring()


