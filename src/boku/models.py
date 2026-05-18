import argparse


class BokuArgs(argparse.Namespace):
    """Extended Namespace for Boku arguments with proper typing."""

    command: str | None = None
    global_command: str | None = None
    dry_run: bool = False
    """Dry Run - Do not execute any commands."""
    quiet: bool = False
    """Quiet - Do not output anything."""
    verbose: int = 0
    file: str | None = None
    check_only: bool = False
    text_only: bool = False
    trust: bool = False
    working_dir: str | None = None
    """Working directory for task execution."""

    def is_dry_run(self) -> bool:
        """Check if this is a dry run."""
        return self.dry_run

    def is_quiet(self) -> bool:
        """Check if quiet mode is enabled."""
        return self.quiet

    def get_verbosity(self) -> int:
        """Get the verbosity level."""
        return self.verbose or 0
