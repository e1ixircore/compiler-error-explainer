# data_model.py - simple container for one compiler error.
# It exists so extract_error() output can be passed around as an object
# instead of a loose dict.
class CompilerError:
    def __init__(self, error_type, message, line_number, category, traceback_info):
        self.error_type = error_type          # e.g. "NameError"
        self.message = message                # the interpreter's message
        self.line_number = line_number        # where it happened
        self.category = category              # syntax / runtime (currently always None)
        self.traceback_info = traceback_info  # full traceback text