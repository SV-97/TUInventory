>>> import re
>>> pattern = re.compile(r"(((\+\d{1,3})|(0)) ?([1-9]+) )?((\d+ ?)+)(-\d+)?", re.DEBUG)
MAX_REPEAT 0 1
  SUBPATTERN 1 0 0
    SUBPATTERN 2 0 0
      BRANCH
        SUBPATTERN 3 0 0
          LITERAL 43
          MAX_REPEAT 1 3
            IN
              CATEGORY CATEGORY_DIGIT
      OR
        SUBPATTERN 4 0 0
          LITERAL 48
    MAX_REPEAT 0 1
      LITERAL 32
    SUBPATTERN 5 0 0
      MAX_REPEAT 1 MAXREPEAT
        IN
          RANGE (49, 57)
    LITERAL 32
SUBPATTERN 6 0 0
  MAX_REPEAT 1 MAXREPEAT
    SUBPATTERN 7 0 0
      MAX_REPEAT 1 MAXREPEAT
        IN
          CATEGORY CATEGORY_DIGIT
      MAX_REPEAT 0 1
        LITERAL 32
MAX_REPEAT 0 1
  SUBPATTERN 8 0 0
    LITERAL 45
    MAX_REPEAT 1 MAXREPEAT
      IN
        CATEGORY CATEGORY_DIGIT