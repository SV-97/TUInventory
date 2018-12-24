---------------------hasattr----------------------
 29           0 LOAD_GLOBAL              0 (hasattr)
              2 LOAD_GLOBAL              1 (a)
              4 LOAD_CONST               1 ('timeout')
              6 CALL_FUNCTION            2
              8 POP_JUMP_IF_FALSE       20

 30          10 LOAD_GLOBAL              1 (a)
             12 LOAD_ATTR                2 (timeout)
             14 LOAD_ATTR                3 (reset)
             16 CALL_FUNCTION            0
             18 POP_TOP
        >>   20 LOAD_CONST               0 (None)
             22 RETURN_VALUE
None


-------------------dict-lookup--------------------
 34           0 LOAD_CONST               1 ('timeout')
              2 LOAD_GLOBAL              0 (a)
              4 LOAD_ATTR                1 (__dict__)
              6 COMPARE_OP               6 (in)
              8 POP_JUMP_IF_FALSE       20

 35          10 LOAD_GLOBAL              0 (a)
             12 LOAD_ATTR                2 (timeout)
             14 LOAD_ATTR                3 (reset)
             16 CALL_FUNCTION            0
             18 POP_TOP
        >>   20 LOAD_CONST               0 (None)
             22 RETURN_VALUE
None