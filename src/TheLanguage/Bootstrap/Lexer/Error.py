# ----------------------------------------------------------------------
# |
# |  Error.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2021-09-22 15:42:41
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2021
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
import os

from dataclasses import dataclass

import CommonEnvironment
from CommonEnvironment import Interface

# ----------------------------------------------------------------------
_script_fullpath                            = CommonEnvironment.ThisFullpath()
_script_dir, _script_name                   = os.path.split(_script_fullpath)
# ----------------------------------------------------------------------

the_language_output_dir = os.getenv("THE_LANGUAGE_OUTPUT_DIR")
if the_language_output_dir is not None:
    import sys
    sys.path.insert(0, the_language_output_dir)
    from Lexer_TheLanguage.Error_TheLanguage import Error
    sys.path.pop(0)

    USE_THE_LANGUAGE_GENERATED_CODE = True
else:
    USE_THE_LANGUAGE_GENERATED_CODE = False

    # ----------------------------------------------------------------------
    @dataclass(frozen=True)
    class Error(Exception, Interface.Interface):
        """Base class for all lexer-related errors"""

        Line: int
        Column: int

        # ----------------------------------------------------------------------
        def __post_init__(self):
            assert self.Line >= 1, self.Line
            assert self.Column >= 1, self.Column

        # ----------------------------------------------------------------------
        def __str__(self):
            return self.MessageTemplate.format(**self.__dict__)

        # ----------------------------------------------------------------------
        @Interface.abstractproperty
        def MessageTemplate(self):
            """Template used when generating the exception string"""
            raise Exception("Abstract property")  # pragma: no cover
