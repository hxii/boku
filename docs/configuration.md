# Configuration

[← Back to README](../README.md)

## Location

The configuration directory path in `boku` is taken from (in this order):

1. `BOKU_CONFIG_DIR` environment variable
2. `boku` gets appended to base path, which depends on the OS:

- Windows: `APPDATA` environment variable or `~\\AppData\\Roaming`
- Linux/macOS: `XDG_CONFIG_HOME` environment variable, or `~/.config`

The configuration file itself is `config.yml`.
