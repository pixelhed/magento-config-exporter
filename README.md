# Magento Config Exporter

**Magento Config Exporter** is a command-line tool that extracts selected Magento configuration values from the database and saves them as structured YAML files.

It is designed for cases where you configure modules in the Magento Admin, then want to export those settings into version-controlled files for later reuse or import on another environment.

---

## ✨ Features

- Exports values using `bin/magento config:show`
- Supports `--scope` and `--scope-code` (default, stores, websites)
- Reads which config paths to export from a YAML file (`paths.yaml`)
- Writes results into YAML with **structured metadata**:
  ```yaml
  scope: "stores"
  scope_code: "english"
  values:
    "payment/mollie_methods_creditcard/title": "Kredit- oder Debitkarte"
  ```
- All keys and values are consistently quoted
- Default output directory:
  ```
  {magento-dir}/var/magento-config-exporter/
  ```
- Confirmation prompt before writing (skip with `-y` / `--no-interaction`)
- Colourful and user-friendly output

---

## 📦 Requirements

- Python **3.8+**
- `pyyaml` library\
  Install via pip:
  ```bash
  pip install pyyaml
  ```
- A working Magento installation with `bin/magento` available

---

## ⚙️ Installation

1. Clone or copy this repository.
2. Make the script executable:
   ```bash
   chmod +x export_config.py
   ```
3. (Optional) Symlink it into your `~/bin` so it’s globally available:
   ```bash
   ln -s /full/path/to/export_config.py ~/bin/magento-config-exporter
   ```

---

## 🚀 Usage

```bash
magento-config-exporter [options] PATHS_FILE
```

### Required

- `PATHS_FILE` – YAML file with a list of config path prefixes to export.\
  Example:
  ```yaml
  paths:
    - mollie_methods_creditcard
    - mollie_methods_eps
    - mollie_methods_googlepay
    - mollie_methods_klarna
    - mollie_methods_paypal
    - cashondelivery
    - cashonpickup
  ```

### Options

| Short | Long               | Description                                                                       |
| ----- | ------------------ | --------------------------------------------------------------------------------- |
| `-d`  | `--magento-dir`    | Path to Magento installation (default: current directory)                         |
| `-s`  | `--scope`          | Config scope: `default`, `stores`, `websites` (default: `default`)                |
| `-c`  | `--scope-code`     | Scope code (e.g. `english`)                                                       |
| `-o`  | `--output-dir`     | Override output directory (default: `{magento-dir}/var/magento-config-exporter/`) |
| `-y`  | `--no-interaction` | Do not ask for confirmation before exporting                                      |
|       | `--debug`          | Enable debug output                                                               |
| `-h`  | `--help`           | Show help                                                                         |

---

## 📂 Output

- Default location:
  ```
  {magento-dir}/var/magento-config-exporter/
  ```
- Files are named after scope:
  - `default.yaml`
  - `stores-english.yaml`
  - `websites-germany.yaml`

### Example output

```yaml
scope: "stores"
scope_code: "english"
values:
  "payment/mollie_methods_creditcard/title": "Kredit- oder Debitkarte"
  "payment/mollie_methods_creditcard/sort_order": "1"
```

---

## 🖥️ Examples

Export default scope:

```bash
magento-config-exporter paths.yaml
```

Export for store "english":

```bash
magento-config-exporter paths.yaml -s stores -c english
```

Export without confirmation:

```bash
magento-config-exporter paths.yaml -s stores -c english -y
```

Export into a custom directory:

```bash
magento-config-exporter paths.yaml -s websites -c germany -o ~/magento-configs
```

---

## ❌ Error Handling

- If the Magento directory is invalid or `bin/magento` is missing → the script aborts.
- If the scope or scope-code does not exist, Magento prints the error and the script exits.
- If `PATHS_FILE` is missing or empty, the script exits with an error and shows help.

---

## 🔮 Next Steps

This exporter is the **first half** of a configuration workflow:

- Use **Magento Config Exporter** to extract config values with full scope metadata.
- Later, use a complementary **Importer** to apply those YAML files back into another Magento installation via `bin/magento config:set`.

---

