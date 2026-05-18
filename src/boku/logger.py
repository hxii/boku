import inspect
import logging
import os


class Logger:
    class Colors:
        RED = "\033[91m"
        GREEN = "\033[92m"
        YELLOW = "\033[93m"
        BLUE = "\033[94m"
        BOLD = "\033[1m"
        UNDERLINE = "\033[4m"
        RESET = "\033[0m"

    def __init__(self):
        self.color_output = not os.environ.get("NO_COLOR") or True
        self.logger = logging.getLogger("boku")
        self.logger.setLevel(logging.WARNING)
        self.logger.propagate = False
        self.simple_format = "%(message)s"
        self.verbose_format = (
            "%(asctime)s - %(name)s - %(levelname)s - %(caller_filename)s:%(caller_lineno)d - %(message)s"
        )
        console_handler = logging.StreamHandler()
        formatter = self.ColoredFormatter(
            self.simple_format,
            self.color_output,
        )
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

    def set_color(self, color_output: bool) -> None:
        """Set color output."""
        self.color_output = color_output

    def set_verbose(self, verbosity: int) -> None:
        """Set verbosity level."""
        if verbosity >= 2:
            self.logger.handlers[0].setFormatter(self.ColoredFormatter(self.verbose_format, self.color_output))
        if verbosity == 1:
            self.logger.setLevel(logging.INFO)
        elif verbosity >= 2:
            self.logger.setLevel(logging.DEBUG)
        else:
            self.logger.setLevel(logging.WARNING)

    def is_verbose(self) -> bool:
        return self.logger.getEffectiveLevel() <= logging.DEBUG

    def header(self, message: str) -> None:
        """Display a formatted header message."""
        if self.color_output:
            header = f"\n{self.Colors.BOLD}{self.Colors.BLUE}{message}{self.Colors.RESET}\n"
        else:
            header = f"\n{message}\n"

        self._log(logging.NOTSET, header)

    def _log(self, level: int, message: str) -> None:
        """Internal method to handle logging with caller info."""
        extra = {}
        if self.is_verbose():
            current_frame = inspect.currentframe()
            if current_frame and current_frame.f_back and current_frame.f_back.f_back:
                caller_frame = current_frame.f_back.f_back
                filename = os.path.basename(caller_frame.f_code.co_filename)
                lineno = caller_frame.f_lineno
                extra = {"caller_filename": filename, "caller_lineno": lineno}
        self.logger.log(level, message, extra=extra)

    def info(self, message: str) -> None:
        self._log(logging.INFO, message)

    def warning(self, message: str) -> None:
        self._log(logging.WARNING, message)

    def debug(self, message: str) -> None:
        self._log(logging.DEBUG, message)

    def error(self, message: str) -> None:
        self._log(logging.ERROR, message)

    class ColoredFormatter(logging.Formatter):
        def __init__(self, fmt: str, color_output: bool):
            super().__init__(fmt)
            self.color_output = color_output

        def format(self, record: logging.LogRecord):
            if self.color_output:
                if record.levelno == logging.WARNING:
                    record.msg = f"{Logger.Colors.YELLOW}{record.msg}{Logger.Colors.RESET}"
                elif record.levelno == logging.ERROR:
                    record.msg = f"{Logger.Colors.RED}{record.msg}{Logger.Colors.RESET}"
                elif record.levelno == logging.DEBUG:
                    record.msg = f"{Logger.Colors.BLUE}{record.msg}{Logger.Colors.RESET}"
                elif record.levelno == logging.CRITICAL:
                    record.msg = f"{Logger.Colors.BOLD}{Logger.Colors.RED}{record.msg}{Logger.Colors.RESET}"
                elif record.levelno == logging.INFO:
                    record.msg = f"{Logger.Colors.GREEN}{record.msg}{Logger.Colors.RESET}"
            return super().format(record)


logger = Logger()
