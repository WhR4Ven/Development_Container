# Fast DDS Linux Bootstrap

This package provides the necessary tools to bootstrap and uninstall Fast DDS in a Ubuntu system.

* [Install Fast-DDS](#install-fast-dds)
* [Uninstall Fast DDS](#uninstall-fast-dds)

## Install Fast DDS

In the src folder you will find:

- fastcdr
- fastrtps
- fastrtpsgen
- foonathan-memory-vendor

To install Fast DDS and all its dependencies in the system, run `install.sh` (it may require administrative privileges).
Check all the available options with the `--help` flag.

```bash
./install.sh --help
```

In addition, setting `LD_LIBRARY_PATH` to whatever `install-prefix` was chosen during the installation may be required.
When using the default `install-prefix`, `LD_LIBRARY_PATH` may be set as follows:

```bash
export LD_LIBRARY_PATH=/usr/local/lib/
```

## Uninstall Fast DDS

To uninstall all installed components, run the `uninstall.sh script` (it may require administrative privileges).
Check all the available options with the `--help` flag.

```bash
./uninstall.sh --help
```

**CAUTION**: if any of the other components were already installed by other way in the system, they may be removed as well depending on the `install-prefix`.
