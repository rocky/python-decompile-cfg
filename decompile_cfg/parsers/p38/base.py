#  Copyright (c) 2021-2022 Rocky Bernstein
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.

from decompile_cfg.parsers.parse_heads import PythonBaseParser, PythonParserSingle, nop_func
from spark_parser import DEFAULT_DEBUG as PARSER_DEFAULT_DEBUG

class Python38BaseParser(PythonBaseParser):
    def __init__(self, start_symbol, debug_parser:dict=PARSER_DEFAULT_DEBUG):
        super(Python38BaseParser, self).__init__(start_symbol=start_symbol, debug_parser=debug_parser)

    def add_make_function_rule(self, rule, opname, attr, customize):
        """Python 3.3 added a an addtional LOAD_STR before MAKE_FUNCTION and
        this has an effect on many rules.
        """
        new_rule = rule % "LOAD_STR "
        self.add_unique_rule(new_rule, opname, attr, customize)

    @staticmethod
    def call_fn_name(token):
        """Customize CALL_FUNCTION to add the number of positional arguments"""
        if token.attr is not None:
            return "%s_%i" % (token.kind, token.attr)
        else:
            return "%s_0" % (token.kind)

    def remove_rules_38(self):
        self.remove_rules(
            """
           stmt               ::= async_for_stmt37
           stmt               ::= for
           stmt               ::= forelsestmt
           stmt               ::= try_except36
           stmt               ::= async_forelse_stmt

           async_for_stmt     ::= setup_loop expr
                                  GET_AITER
                                  SETUP_EXCEPT GET_ANEXT LOAD_CONST
                                  YIELD_FROM
                                  store
                                  POP_BLOCK JUMP_FORWARD COME_FROM_EXCEPT DUP_TOP
                                  LOAD_GLOBAL COMPARE_OP POP_JUMP_IF_TRUE
                                  END_FINALLY COME_FROM
                                  for_block
                                  COME_FROM
                                  POP_TOP POP_TOP POP_TOP POP_EXCEPT POP_TOP POP_BLOCK
                                  COME_FROM_LOOP
           async_for_stmt37   ::= setup_loop expr
                                  GET_AITER
                                  SETUP_EXCEPT GET_ANEXT
                                  LOAD_CONST YIELD_FROM
                                  store
                                  POP_BLOCK JUMP_BACK COME_FROM_EXCEPT DUP_TOP
                                  LOAD_GLOBAL COMPARE_OP POP_JUMP_IF_TRUE
                                  END_FINALLY for_block COME_FROM
                                  POP_TOP POP_TOP POP_TOP POP_EXCEPT
                                  POP_TOP POP_BLOCK
                                  COME_FROM_LOOP

          async_forelse_stmt ::= setup_loop expr
                                 GET_AITER
                                 SETUP_EXCEPT GET_ANEXT LOAD_CONST
                                 YIELD_FROM
                                 store
                                 POP_BLOCK JUMP_FORWARD COME_FROM_EXCEPT DUP_TOP
                                 LOAD_GLOBAL COMPARE_OP POP_JUMP_IF_TRUE
                                 END_FINALLY COME_FROM
                                 for_block
                                 COME_FROM
                                 POP_TOP POP_TOP POP_TOP POP_EXCEPT POP_TOP POP_BLOCK
                                 else_suite COME_FROM_LOOP

           for                ::= setup_loop expr get_for_iter store for_block POP_BLOCK
           for                ::= setup_loop expr get_for_iter store for_block POP_BLOCK NOP

           for_block          ::= c_stmts_opt COME_FROM_LOOP JUMP_BACK
           forelsestmt        ::= setup_loop expr get_for_iter store for_block POP_BLOCK else_suite
           forelselaststmt    ::= setup_loop expr get_for_iter store for_block POP_BLOCK else_suitec
           forelselaststmtc   ::= setup_loop expr get_for_iter store for_block POP_BLOCK else_suitec

           try_except         ::= SETUP_EXCEPT suite_stmts_opt POP_BLOCK
                                  except_handler opt_come_from_except

           tryfinallystmt     ::= SETUP_FINALLY suite_stmts_opt POP_BLOCK
                                  LOAD_CONST COME_FROM_FINALLY suite_stmts_opt
                                  END_FINALLY
           tryfinally36       ::= SETUP_FINALLY returns
                                  COME_FROM_FINALLY suite_stmts_opt END_FINALLY
           tryfinally_return_stmt ::= SETUP_FINALLY suite_stmts_opt POP_BLOCK
                                      LOAD_CONST COME_FROM_FINALLY
        """
        )

class Python38ParseSingle(Python38BaseParser, PythonParserSingle):
    pass
